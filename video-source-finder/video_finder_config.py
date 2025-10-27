import os
from dotenv import load_dotenv
from typing import List, Dict, Optional, Tuple
import json

# Load environment variables
load_dotenv()

class VideoFinderConfig:
    """Configuration settings for the Video Source Finder"""
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    SERPER_API_KEY = os.getenv("SERPER_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
    SEARCHAPI_API_KEY = os.getenv("SEARCHAPI_API_KEY")
    
    # Model settings
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    CHAT_MODEL = "gpt-3.5-turbo"
    
    # Vector database settings
    CHROMA_PERSIST_DIRECTORY = "./video_chroma_db"
    COLLECTION_NAME = "youtube_transcripts"
    
    # Search settings
    TOP_K_RESULTS = 5
    SIMILARITY_THRESHOLD = 0.7
    MAX_SEARCH_RESULTS = 10
    
    # YouTube settings
    MAX_VIDEO_DURATION = 3600  # 1 hour in seconds
    SUPPORTED_LANGUAGES = ['en', 'pt', 'es']  # English, Portuguese, Spanish
    
    # SearchAPI settings
    SEARCHAPI_BASE_URL = "https://www.searchapi.io/api/v1/search"
    SEARCHAPI_TIMEOUT = 30  # seconds
    SEARCHAPI_RETRY_ATTEMPTS = 3
    
    # Processing settings
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 100
    MAX_TOKENS = 1000
    TEMPERATURE = 0.3
    
    # Output format
    OUTPUT_FORMAT = {
        "video_id": "string",
        "timestamp_start": "HH:MM:SS",
        "timestamp_end": "HH:MM:SS",
        "confidence": "float",
        "transcript_snippet": "string"
    }
