import os
os.environ["STREAMLIT_WATCHER_TYPE"] = "none"

import torch
torch.classes.__path__ = []

import streamlit as st
from ui_config import apply_custom_ui
from utils import youtube_to_transcript_and_summary
import time

# Apply custom UI styles
apply_custom_ui()

# App title
st.title("📺 YouTube Video Summary Generator")

# Input field
url = st.text_input("Enter YouTube Video URL:")

# Generate button
if st.button("Generate"):
    if not url.strip():
        st.warning("Please enter a valid YouTube URL.")
    else:
        with st.spinner("Processing... please wait."):

            transcript, summary, title = youtube_to_transcript_and_summary(url)

        # Proceed only if transcript and summary were generated
        if transcript and summary:
            msg_placeholder = st.empty()
            msg_placeholder.success("Summary and Transcript generated!")
            time.sleep(3)
            msg_placeholder.empty()

            # Display Summary first
            st.subheader("🔍 Summary")
            st.text_area("Summary",value=summary, height=150)

            # Then display Transcript
            st.subheader("📝 Transcript")
            st.text_area("Transcript",value=transcript, height=300)

        else:
            st.error("Transcript generation failed.")
