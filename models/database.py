from supabase import create_client, Client
from config.settings import settings
from typing import Dict, Any, List, Optional
import uuid
import logging

logger = logging.getLogger(__name__)

class SupabaseClient:
    """Supabase client wrapper for database operations"""
    
    def __init__(self):
        try:
            # Create Supabase client with basic configuration
            self.client: Client = create_client(
                settings.SUPABASE_URL, 
                settings.SUPABASE_KEY
            )
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {str(e)}")
            raise
    
    def get_client(self) -> Client:
        """Get the Supabase client instance"""
        return self.client

# Global Supabase client instance - initialize lazily
_supabase_client = None

def get_supabase() -> Client:
    """Dependency to get Supabase client"""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = SupabaseClient()
    return _supabase_client.get_client()

# Table names (these should match your Supabase table names)
class Tables:
    DOCUMENTS = "documents"
    USER_QUERIES = "user_queries"
    DOCUMENT_CHUNKS = "document_chunks"
    ANSWERS = "answers"
    ANSWER_CLAUSES = "answer_clauses"
    DEVICES = "devices"  # Added devices table

# Data models (Pydantic-like structures for type hints)
class DocumentModel:
    def __init__(self, id: str = None, url: str = None, uploaded_at: str = None):
        self.id = id or str(uuid.uuid4())
        self.url = url
        self.uploaded_at = uploaded_at

class UserQueryModel:
    def __init__(self, id: str = None, document_id: str = None, query_text: str = None, created_at: str = None):
        self.id = id or str(uuid.uuid4())
        self.document_id = document_id
        self.query_text = query_text
        self.created_at = created_at

class DocumentChunkModel:
    def __init__(self, id: str = None, document_id: str = None, chunk_index: int = None, 
                 chunk_text: str = None, pinecone_id: str = None, created_at: str = None):
        self.id = id or str(uuid.uuid4())
        self.document_id = document_id
        self.chunk_index = chunk_index
        self.chunk_text = chunk_text
        self.pinecone_id = pinecone_id
        self.created_at = created_at

class AnswerModel:
    def __init__(self, id: str = None, query_id: str = None, answer_text: str = None, 
                 decision: str = None, amount: float = None, created_at: str = None):
        self.id = id or str(uuid.uuid4())
        self.query_id = query_id
        self.answer_text = answer_text
        self.decision = decision
        self.amount = amount
        self.created_at = created_at

class AnswerClauseModel:
    def __init__(self, id: str = None, answer_id: str = None, chunk_id: str = None, 
                 clause_text: str = None, similarity_score: float = None, created_at: str = None):
        self.id = id or str(uuid.uuid4())
        self.answer_id = answer_id
        self.chunk_id = chunk_id
        self.clause_text = clause_text
        self.similarity_score = similarity_score
        self.created_at = created_at

class DeviceModel:
    def __init__(self, id: str = None, name: str = None, type: str = None, 
                 status: str = None, created_at: str = None):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.type = type
        self.status = status
        self.created_at = created_at