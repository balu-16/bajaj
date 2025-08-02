from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.hackrx import router as hackrx_router
from config.settings import settings
from utils.helpers import setup_logging
from contextlib import asynccontextmanager
import logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Global service instances
_pinecone_service = None
_gemini_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services once at startup"""
    global _pinecone_service, _gemini_service
    
    try:
        logger.info("Initializing services at startup...")
        
        # Initialize Pinecone service
        from services.pinecone_service import PineconeService
        _pinecone_service = PineconeService()
        logger.info("Pinecone service initialized")
        
        # Initialize Gemini service
        from services.gemini_service import GeminiService
        _gemini_service = GeminiService()
        logger.info("Gemini service initialized")
        
        logger.info("All services initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {str(e)}")
        raise
    
    yield
    
    # Cleanup (if needed)
    logger.info("Shutting down services...")

app = FastAPI(
    title="LLM-Powered Query Retrieval System",
    description="Intelligent document analysis with Pinecone and Gemini API",
    version="1.0.0",
    lifespan=lifespan
)

def get_pinecone_service():
    """Get the global Pinecone service instance"""
    return _pinecone_service

def get_gemini_service():
    """Get the global Gemini service instance"""
    return _gemini_service

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(hackrx_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "LLM-Powered Query Retrieval System is running!"}

@app.get("/health")
async def health_check():
    try:
        # Test Supabase connection on health check
        from models.database import get_supabase
        supabase = get_supabase()
        logger.info("Supabase connection test successful")
        return {"status": "healthy", "version": "1.0.0", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {"status": "unhealthy", "version": "1.0.0", "database": "disconnected", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    import os
    import sys
    
    # Check if SSL certificates exist for HTTPS
    ssl_keyfile = "localhost.key"
    ssl_certfile = "localhost.crt"
    use_ssl = os.path.exists(ssl_keyfile) and os.path.exists(ssl_certfile)
    
    if use_ssl:
        logger.info("SSL certificates found. Starting server with HTTPS...")
        uvicorn.run(
            "main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=False,
            log_level="info",
            ssl_keyfile=ssl_keyfile,
            ssl_certfile=ssl_certfile
        )
    else:
        logger.info("No SSL certificates found. Starting server with HTTP...")
        uvicorn.run(
            "main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=False,
            log_level="info"
        )