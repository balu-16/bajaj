from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List
from controllers.query_controller import QueryController
from utils.auth import verify_bearer_token
from models.database import get_supabase
from supabase import Client

router = APIRouter()
security = HTTPBearer()

# Request/Response models
class QueryRequest(BaseModel):
    documents: str
    questions: List[str]

class QueryResponse(BaseModel):
    answers: List[str]

@router.post("/hackrx/run", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    supabase: Client = Depends(get_supabase),
    authorization: str = Header(None)
):
    """
    Process PDF document and answer natural language questions
    
    Headers required:
    - Content-Type: application/json
    - Accept: application/json
    - Authorization: Bearer 429e00477ed493b1d84caf6b7580ae7d34326355abce267d8395e9cb12a748bc
    """
    
    # Verify bearer token
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    
    token = authorization.split(" ")[1]
    if not verify_bearer_token(token):
        raise HTTPException(status_code=401, detail="Invalid bearer token")
    
    try:
        # Get singleton services from main.py
        from main import get_pinecone_service, get_gemini_service
        pinecone_service = get_pinecone_service()
        gemini_service = get_gemini_service()
        
        # Initialize controller with singleton services
        controller = QueryController(supabase, pinecone_service, gemini_service)
        
        # Process the request
        answers = await controller.process_document_queries(
            pdf_url=request.documents,
            questions=request.questions
        )
        
        return QueryResponse(answers=answers)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")