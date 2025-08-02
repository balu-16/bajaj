from supabase import Client
from models.database import (
    get_supabase, Tables, DocumentModel, UserQueryModel, 
    DocumentChunkModel, AnswerModel, AnswerClauseModel, DeviceModel
)
from typing import List, Dict, Any, Optional
import logging
import uuid
from datetime import datetime
from utils.timezone_utils import get_ist_timestamp

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self, supabase: Client = None):
        self.supabase = supabase or get_supabase()
    
    async def get_or_create_document(self, url: str) -> Dict[str, Any]:
        """Get existing document or create new one"""
        try:
            # Check if document already exists
            response = self.supabase.table(Tables.DOCUMENTS).select("*").eq("url", url).execute()
            
            if response.data:
                document = response.data[0]
                logger.info(f"Found existing document: {document['id']}")
                return document
            
            # Create new document
            new_document = {
                "id": str(uuid.uuid4()),
                "url": url,
                "uploaded_at": get_ist_timestamp()
            }
            
            response = self.supabase.table(Tables.DOCUMENTS).insert(new_document).execute()
            
            if response.data:
                document = response.data[0]
                logger.info(f"Created new document: {document['id']}")
                return document
            else:
                raise Exception("Failed to create document")
            
        except Exception as e:
            logger.error(f"Error getting/creating document: {str(e)}")
            raise e
    
    async def has_chunks(self, document_id: str) -> bool:
        """Check if document has chunks stored"""
        try:
            response = self.supabase.table(Tables.DOCUMENT_CHUNKS).select("id").eq("document_id", document_id).execute()
            return len(response.data) > 0
            
        except Exception as e:
            logger.error(f"Error checking document chunks: {str(e)}")
            return False
    
    async def create_document_chunk(
        self, 
        document_id: str, 
        chunk_index: int, 
        chunk_text: str, 
        pinecone_id: str
    ) -> Dict[str, Any]:
        """Create a new document chunk"""
        try:
            chunk_data = {
                "id": str(uuid.uuid4()),
                "document_id": document_id,
                "chunk_index": chunk_index,
                "chunk_text": chunk_text,
                "pinecone_id": pinecone_id,
                "created_at": get_ist_timestamp()
            }
            
            response = self.supabase.table(Tables.DOCUMENT_CHUNKS).insert(chunk_data).execute()
            
            if response.data:
                return response.data[0]
            else:
                raise Exception("Failed to create document chunk")
            
        except Exception as e:
            logger.error(f"Error creating document chunk: {str(e)}")
            raise e
    
    async def create_user_query(self, document_id: str, query_text: str) -> Dict[str, Any]:
        """Create a new user query"""
        try:
            query_data = {
                "id": str(uuid.uuid4()),
                "document_id": document_id,
                "query_text": query_text,
                "created_at": get_ist_timestamp()
            }
            
            response = self.supabase.table(Tables.USER_QUERIES).insert(query_data).execute()
            
            if response.data:
                query = response.data[0]
                logger.info(f"Created user query: {query['id']}")
                return query
            else:
                raise Exception("Failed to create user query")
            
        except Exception as e:
            logger.error(f"Error creating user query: {str(e)}")
            raise e
    
    async def create_answer_with_clauses(
        self, 
        query_id: str, 
        answer_text: str, 
        relevant_chunks: List[Dict[str, Any]],
        decision: Optional[str] = None,
        amount: Optional[float] = None
    ) -> Dict[str, Any]:
        """Create answer with associated clauses"""
        try:
            # Create answer
            answer_data = {
                "id": str(uuid.uuid4()),
                "query_id": query_id,
                "answer_text": answer_text,
                "decision": decision,
                "amount": amount,
                "created_at": get_ist_timestamp()
            }
            
            response = self.supabase.table(Tables.ANSWERS).insert(answer_data).execute()
            
            if not response.data:
                raise Exception("Failed to create answer")
            
            answer = response.data[0]
            
            # Create answer clauses
            clauses_data = []
            for chunk_data in relevant_chunks:
                # Find the corresponding chunk in database
                chunk_response = self.supabase.table(Tables.DOCUMENT_CHUNKS).select("id").eq("pinecone_id", chunk_data['id']).execute()
                
                if chunk_response.data:
                    chunk = chunk_response.data[0]
                    clause_data = {
                        "id": str(uuid.uuid4()),
                        "answer_id": answer['id'],
                        "chunk_id": chunk['id'],
                        "clause_text": chunk_data['text'][:1000],  # Limit clause text
                        "similarity_score": chunk_data['score'],
                        "created_at": get_ist_timestamp()
                    }
                    clauses_data.append(clause_data)
            
            if clauses_data:
                self.supabase.table(Tables.ANSWER_CLAUSES).insert(clauses_data).execute()
            
            logger.info(f"Created answer with {len(clauses_data)} clauses")
            return answer
            
        except Exception as e:
            logger.error(f"Error creating answer with clauses: {str(e)}")
            raise e
    
    async def get_document_chunks(self, document_id: str) -> List[Dict[str, Any]]:
        """Get all chunks for a document"""
        try:
            response = self.supabase.table(Tables.DOCUMENT_CHUNKS).select("*").eq("document_id", document_id).order("chunk_index").execute()
            return response.data or []
            
        except Exception as e:
            logger.error(f"Error getting document chunks: {str(e)}")
            return []
    
    async def get_query_history(self, document_id: str) -> List[Dict[str, Any]]:
        """Get query history for a document"""
        try:
            # Get queries
            queries_response = self.supabase.table(Tables.USER_QUERIES).select("*").eq("document_id", document_id).order("created_at", desc=True).execute()
            
            result = []
            for query in queries_response.data or []:
                query_data = {
                    "id": query["id"],
                    "query_text": query["query_text"],
                    "created_at": query["created_at"],
                    "answers": []
                }
                
                # Get answers for this query
                answers_response = self.supabase.table(Tables.ANSWERS).select("*").eq("query_id", query["id"]).execute()
                
                for answer in answers_response.data or []:
                    answer_data = {
                        "id": answer["id"],
                        "answer_text": answer["answer_text"],
                        "decision": answer["decision"],
                        "amount": answer["amount"],
                        "created_at": answer["created_at"],
                        "clauses": []
                    }
                    
                    # Get clauses for this answer
                    clauses_response = self.supabase.table(Tables.ANSWER_CLAUSES).select("*").eq("answer_id", answer["id"]).execute()
                    
                    for clause in clauses_response.data or []:
                        clause_data = {
                            "clause_text": clause["clause_text"],
                            "similarity_score": clause["similarity_score"]
                        }
                        answer_data["clauses"].append(clause_data)
                    
                    query_data["answers"].append(answer_data)
                
                result.append(query_data)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting query history: {str(e)}")
            return []
    
    async def get_all_devices(self) -> List[Dict[str, Any]]:
        """Get all devices from the devices table"""
        try:
            response = self.supabase.table(Tables.DEVICES).select("*").execute()
            return response.data or []
            
        except Exception as e:
            logger.error(f"Error getting devices: {str(e)}")
            return []
    
    async def create_device(self, name: str, device_type: str, status: str = "active") -> Dict[str, Any]:
        """Create a new device"""
        try:
            device_data = {
                "id": str(uuid.uuid4()),
                "name": name,
                "type": device_type,
                "status": status,
                "created_at": get_ist_timestamp()
            }
            
            response = self.supabase.table(Tables.DEVICES).insert(device_data).execute()
            
            if response.data:
                return response.data[0]
            else:
                raise Exception("Failed to create device")
            
        except Exception as e:
            logger.error(f"Error creating device: {str(e)}")
            raise e
    
    async def get_device_by_id(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get a device by ID"""
        try:
            response = self.supabase.table(Tables.DEVICES).select("*").eq("id", device_id).execute()
            
            if response.data:
                return response.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Error getting device by ID: {str(e)}")
            return None