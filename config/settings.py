from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Supabase Configuration
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    
    # Pinecone
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "llm-query-retrieval")
    
    # Gemini API
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    
    # Authentication
    BEARER_TOKEN: str = os.getenv("BEARER_TOKEN", "429e00477ed493b1d84caf6b7580ae7d34326355abce267d8395e9cb12a748bc")
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # SSL Configuration
    SSL_ENABLED: bool = os.getenv("SSL_ENABLED", "False").lower() == "true"
    SSL_KEYFILE: str = os.getenv("SSL_KEYFILE", "localhost.key")
    SSL_CERTFILE: str = os.getenv("SSL_CERTFILE", "localhost.crt")
    
    # Deployment
    BASE_URL: str = os.getenv("BASE_URL", "https://bajaj-9p8i.onrender.com")
    
    # Timezone Configuration
    TIMEZONE: str = os.getenv("TIMEZONE", "Asia/Kolkata")  # Indian Standard Time
    
    # Embedding model
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Chunk settings
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    class Config:
        env_file = ".env"

settings = Settings()