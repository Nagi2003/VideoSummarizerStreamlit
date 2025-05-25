from sqlalchemy import Column, Integer, String, Text, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set.")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class TranscriptSummary(Base):
    __tablename__ = "transcript_summary"
    id = Column(Integer, primary_key=True, index=True)
    youtube_url = Column(String(300), nullable=False)
    title = Column(String(300), nullable=False)
    transcript = Column(Text, nullable=False)
    summary = Column(Text, nullable=False)
    created_at = Column(DateTime, default=None)


