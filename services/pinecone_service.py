from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import uuid
import logging
import time
from config.settings import settings

logger = logging.getLogger(__name__)

class PineconeService:
    def __init__(self):
        # Initialize Pinecone with v5 API
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index_name = settings.PINECONE_INDEX_NAME
        self.index = None
        self.embedding_model = None
        
        # Try to connect to existing index or create new one
        try:
            # Check if index exists using list_indexes
            if self.index_name not in self.pc.list_indexes().names():
                logger.warning(f"Index '{self.index_name}' not found. Attempting to create...")
                # Try to create index using standard create_index method
                try:
                    self.pc.create_index(
                        name=self.index_name,
                        dimension=384,  # all-MiniLM-L6-v2 dimension
                        metric='cosine',
                        spec=ServerlessSpec(
                            cloud="aws",
                            region="us-east-1"
                        )
                    )
                    logger.info(f"Created new Pinecone index: {self.index_name}")
                except Exception as create_error:
                    logger.error(f"Could not create index: {str(create_error)}")
                    # Use fallback - disable Pinecone
                    logger.error("No Pinecone indexes available. Pinecone functionality disabled.")
                    self.index = None
                    self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
                    return
            
            # Connect to index
            self.index = self.pc.Index(self.index_name)
            
            # Test connection
            try:
                stats = self.index.describe_index_stats()
                logger.info(f"Connected to Pinecone index: {self.index_name} (vectors: {stats.total_vector_count})")
            except Exception as stats_error:
                logger.warning(f"Could not get index stats: {str(stats_error)}")
                logger.info(f"Connected to Pinecone index: {self.index_name}")
            
        except Exception as e:
            logger.error(f"Could not connect to Pinecone: {str(e)}")
            logger.warning("Pinecone functionality disabled. Using local embeddings only.")
            self.index = None
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        
        logger.info(f"Initialized Pinecone service with index: {self.index_name}")
    
    async def store_chunks(self, chunks: List[str], document_id: str) -> List[str]:
        """Store text chunks as embeddings in Pinecone"""
        if self.index is None:
            logger.warning("Pinecone not available. Returning dummy IDs for chunks.")
            # Return dummy IDs when Pinecone is not available
            return [f"local_{document_id}_{i}_{str(uuid.uuid4())[:8]}" for i in range(len(chunks))]
        
        try:
            # Generate embeddings
            embeddings = self.embedding_model.encode(chunks)
            
            # Prepare vectors for upsert
            vectors = []
            pinecone_ids = []
            
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                pinecone_id = f"{document_id}_{i}_{str(uuid.uuid4())[:8]}"
                pinecone_ids.append(pinecone_id)
                
                vectors.append({
                    "id": pinecone_id,
                    "values": embedding.tolist(),
                    "metadata": {
                        "document_id": document_id,
                        "chunk_index": i,
                        "text": chunk[:1000],  # Store first 1000 chars in metadata
                        "full_text": chunk
                    }
                })
            
            # Upsert vectors to Pinecone
            self.index.upsert(vectors=vectors)
            
            logger.info(f"Stored {len(chunks)} chunks in Pinecone for document {document_id}")
            return pinecone_ids
            
        except Exception as e:
            logger.error(f"Error storing chunks in Pinecone: {str(e)}")
            # Return dummy IDs as fallback
            logger.warning("Falling back to local storage simulation")
            return [f"fallback_{document_id}_{i}_{str(uuid.uuid4())[:8]}" for i in range(len(chunks))]
    
    async def search_similar_chunks(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar chunks based on query"""
        if self.index is None:
            logger.warning("Pinecone not available. Returning empty search results.")
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])
            
            # Search in Pinecone
            search_results = self.index.query(
                vector=query_embedding[0].tolist(),
                top_k=top_k,
                include_metadata=True
            )
            
            # Format results
            relevant_chunks = []
            for match in search_results['matches']:
                relevant_chunks.append({
                    "id": match['id'],
                    "text": match['metadata']['full_text'],
                    "score": match['score'],
                    "chunk_index": match['metadata']['chunk_index'],
                    "document_id": match['metadata']['document_id']
                })
            
            logger.info(f"Found {len(relevant_chunks)} relevant chunks for query")
            return relevant_chunks
            
        except Exception as e:
            logger.error(f"Error searching similar chunks: {str(e)}")
            logger.warning("Returning empty search results due to error")
            return []
    
    async def delete_document_chunks(self, document_id: str):
        """Delete all chunks for a specific document"""
        if self.index is None:
            logger.warning("Pinecone not available. Skipping chunk deletion.")
            return
        
        try:
            # Query all vectors for this document
            query_response = self.index.query(
                vector=[0] * 384,  # Dummy vector for metadata filtering
                filter={"document_id": document_id},
                top_k=10000,
                include_metadata=False
            )
            
            # Extract IDs and delete
            ids_to_delete = [match['id'] for match in query_response['matches']]
            
            if ids_to_delete:
                self.index.delete(ids=ids_to_delete)
                logger.info(f"Deleted {len(ids_to_delete)} chunks for document {document_id}")
            
        except Exception as e:
            logger.error(f"Error deleting document chunks: {str(e)}")
            logger.warning("Continuing without deleting chunks")