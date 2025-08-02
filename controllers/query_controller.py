from typing import List
from supabase import Client
from services.pdf_service import PDFService
from services.database_service import DatabaseService
import logging

logger = logging.getLogger(__name__)

class QueryController:
    def __init__(self, supabase: Client, pinecone_service=None, gemini_service=None):
        self.supabase = supabase
        self.pdf_service = PDFService()
        self.pinecone_service = pinecone_service
        self.gemini_service = gemini_service
        self.database_service = DatabaseService(supabase)
    
    async def process_document_queries(self, pdf_url: str, questions: List[str]) -> List[str]:
        """
        Main business logic for processing PDF and answering questions
        
        Flow:
        1. Download and process PDF
        2. Chunk the document
        3. Store embeddings in Pinecone
        4. For each question, retrieve relevant chunks and get LLM answer
        """
        try:
            logger.info(f"Processing document: {pdf_url}")
            
            # Step 1: Check if document already exists
            document = await self.database_service.get_or_create_document(pdf_url)
            
            # Step 2: Download and process PDF if not already processed
            if not await self.database_service.has_chunks(document["id"]):
                logger.info("Processing new document...")
                
                # Download and extract text from PDF
                pdf_text = await self.pdf_service.extract_text_from_url(pdf_url)
                
                # Chunk the document
                chunks = await self.pdf_service.chunk_text(pdf_text)
                
                # Store chunks in Pinecone and database
                await self._store_document_chunks(document["id"], chunks)
            else:
                logger.info("Document already processed, using existing chunks")
            
            # Step 3: Process each question
            answers = []
            for question in questions:
                logger.info(f"Processing question: {question}")
                
                # Store query in database
                query = await self.database_service.create_user_query(document["id"], question)
                
                # Get relevant chunks from Pinecone
                relevant_chunks = await self.pinecone_service.search_similar_chunks(
                    question, top_k=5
                )
                
                # Get answer from Gemini
                answer_text = await self.gemini_service.generate_answer(
                    question, relevant_chunks
                )
                
                # Store answer and clauses in database
                await self.database_service.create_answer_with_clauses(
                    query["id"], answer_text, relevant_chunks
                )
                
                answers.append(answer_text)
            
            logger.info(f"Successfully processed {len(questions)} questions")
            return answers
            
        except Exception as e:
            logger.error(f"Error processing document queries: {str(e)}")
            raise e
    
    async def _store_document_chunks(self, document_id: str, chunks: List[str]):
        """Store document chunks in both Pinecone and database"""
        try:
            # Generate embeddings and store in Pinecone
            chunk_data = await self.pinecone_service.store_chunks(chunks, str(document_id))
            
            # Store chunk metadata in database
            for i, (chunk_text, pinecone_id) in enumerate(zip(chunks, chunk_data)):
                await self.database_service.create_document_chunk(
                    document_id, i, chunk_text, pinecone_id
                )
            
            logger.info(f"Stored {len(chunks)} chunks for document {document_id}")
            
        except Exception as e:
            logger.error(f"Error storing document chunks: {str(e)}")
            raise e