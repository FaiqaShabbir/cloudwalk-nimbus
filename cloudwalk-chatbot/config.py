import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration settings
class Config:
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Model settings
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    CHAT_MODEL = "gpt-3.5-turbo"
    
    # Vector database settings
    CHROMA_PERSIST_DIRECTORY = "./chroma_db"
    COLLECTION_NAME = "cloudwalk_knowledge"
    
    # RAG settings
    TOP_K_RESULTS = 3
    SIMILARITY_THRESHOLD = 0.7
    
    # Chat settings
    MAX_TOKENS = 500
    TEMPERATURE = 0.7
