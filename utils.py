import whisper
import yt_dlp
import os
import re
import shutil
from urllib.parse import urlparse, parse_qs
import requests
import dotenv
from math import ceil
from textwrap import wrap
import warnings
warnings.filterwarnings("ignore")
import streamlit as st

dotenv.load_dotenv()

def clean_youtube_url(url):
    parsed = urlparse(url)
    if 'youtu.be' in parsed.netloc:
        video_id = parsed.path[1:]
    else:
        query = parse_qs(parsed.query)
        video_id = query.get("v", [""])[0]
    return f"https://www.youtube.com/watch?v={video_id}"

def get_video_title(url):
    """Fetch YouTube video title and sanitize it for use as a filename."""
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'video').strip()
            # Remove characters not allowed in Windows filenames
            title = re.sub(r'[\\/*?:"<>|#]', '_', title)
            title = title.replace(' ', '_')
            return title
    except Exception as e:
        print(f"Failed to fetch video title: {e}")
        return "video"



def download_youtube_audio(url, filename="audio"):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{filename}.%(ext)s',
        'ffmpeg_location': r'C:/Users/Nagendra/Downloads/ffmpeg-n7.1.1-19-g4c78a357d0-win64-gpl-shared-7.1/bin',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': False,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            print("Downloading audio...")
            ydl.download([url])
            audio_path = f"{filename}.mp3"
            print(f"Audio downloaded: {audio_path}")
            return audio_path
        except Exception as e:
            print(f"Error downloading audio: {e}")
            return None

def transcribe_audio_whisper(audio_path):
    if not os.path.exists(audio_path):
        print(f"Audio file not found: {audio_path}")
        return None
    if not shutil.which("ffmpeg"):
        raise EnvironmentError("ffmpeg not found. Ensure it is in your system PATH.")

    print("Loading Whisper model: base")
    model = whisper.load_model("base")
    print("Transcribing...")
    result = model.transcribe(audio_path,task="translate")
    language = result.get("language", "unknown")
    print(f"Detected language: {language}")

    return result["text"]


def summarize_with_groq(text):
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set.")
    

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that summarizes transcripts."},
            {"role": "user", "content": f"Please summarize the following transcript:\n\n{text}"}
        ],
        "temperature": 0.5
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        raise RuntimeError(f"Groq API error: {response.status_code} - {response.text}")
    result = response.json()
    return result['choices'][0]['message']['content']

def chunk_text(text, max_words=24000):
    """Split transcript into chunks no longer than ~24k words (to fit ~32K tokens)."""
    words = text.split()
    return [' '.join(words[i:i+max_words]) for i in range(0, len(words), max_words)]

def summarize_transcript_conditionally(transcript):
    max_words = 24000 
    if len(transcript.split()) <= max_words:
        return summarize_with_groq(transcript)
    else:
        print("Transcript too long, splitting into chunks...")
        chunks = chunk_text(transcript, max_words=max_words)
        partial_summaries = [summarize_with_groq(chunk) for chunk in chunks]
        combined_summary = "\n\n".join(partial_summaries)
        final_summary = summarize_with_groq(f"Summarize the following combined summaries:\n\n{combined_summary}")
        return final_summary

def youtube_to_transcript_and_summary(youtube_url, cleanup=True):
    url = clean_youtube_url(youtube_url)
    title = get_video_title(url)
    audio_file = download_youtube_audio(url, filename=title)
    if not audio_file:
        return None, None, title
    transcript = transcribe_audio_whisper(audio_file)
    if cleanup and os.path.exists(audio_file):
        os.remove(audio_file)
        print(f"Cleaned up audio file: {audio_file}")
    summary = summarize_transcript_conditionally(transcript) if transcript else None
    return transcript, summary, title

if __name__ == "__main__":
    url = input("Enter YouTube video URL: ")
    print(f"\nProcessing video: {url}")
    transcript, summary, title = youtube_to_transcript_and_summary(url)
    if transcript:
        transcript_file = f"{title}_transcript.txt"
        with open(transcript_file, 'w', encoding='utf-8') as f:
            f.write(transcript)
        print(f"Transcript saved to {transcript_file}")
    else:
        print("Failed to generate transcript.")
    if summary:
        summary_file = f"{title}_summary.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Summary saved to {summary_file}")
    else:
        print("Failed to generate summary.")
