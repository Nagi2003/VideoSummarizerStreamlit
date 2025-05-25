import os
os.environ["STREAMLIT_WATCHER_TYPE"] = "none"

import torch
torch.classes.__path__ = []  

import streamlit as st
from ui_config import apply_custom_ui
from models import SessionLocal, TranscriptSummary, engine, Base
from sqlalchemy.exc import SQLAlchemyError
from utils import youtube_to_transcript_and_summary
from datetime import datetime
import time

# Apply custom UI styles
apply_custom_ui()

# Initialize the database
Base.metadata.create_all(bind=engine)

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
            msg_placeholder.success("Summary and Transcript generating!")
            time.sleep(3)
            msg_placeholder.empty()

            # Display Summary first
            st.subheader("🔍 Summary")
            st.text_area(label="Summary", value=summary, height=150)

            # Then display Transcript
            st.subheader("📝 Transcript")
            st.text_area(label="Transcript", value=transcript, height=300)

            try:
                db = SessionLocal()
                record = TranscriptSummary(
                    youtube_url=url,
                    title=title,
                    transcript=transcript,
                    summary=summary,
                    created_at=datetime.utcnow()
                )
                db.add(record)
                db.commit()
                db.close()

                db_msg = st.empty()
                db_msg.success("Transcript and summary have been saved to the database.")
                time.sleep(5)
                db_msg.empty()

            except SQLAlchemyError as e:
                st.error(f"Database error: {e}")

        else:
            st.error("Transcript generation failed.")
