# LLM-Powered Intelligent Query-Retrieval System

A FastAPI backend that processes PDF documents and answers natural language questions using Pinecone vector database and Gemini API.

## Features

- PDF document processing and chunking
- Vector embeddings storage in Pinecone
- Natural language query processing with Gemini API
- Structured JSON responses with clause justification
- PostgreSQL/Supabase database integration
- Bearer token authentication

## Setup Instructions

1. **Clone and Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your actual API keys and database credentials
   ```

3. **Required API Keys**
   - Supabase URL and API Key
   - Pinecone API Key and Environment
   - Google Gemini API Key

4. **Run the Server**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## API Usage

### Endpoint
```
POST /api/v1/hackrx/run
```

### Headers
```
Content-Type: application/json
Accept: application/json
Authorization: Bearer 429e00477ed493b1d84caf6b7580ae7d34326355abce267d8395e9cb12a748bc
```

### Sample Request
```json
{
  "documents": "https://sample-link.com/policy.pdf",
  "questions": [
    "What is the waiting period for cataract surgery?",
    "Does this policy cover maternity expenses?"
  ]
}
```

### Sample Response
```json
{
  "answers": [
    "Cataract surgery has a 2-year waiting period.",
    "Yes, maternity is covered after 24 months of continuous coverage."
  ]
}
```

## Testing with cURL

```bash
curl -X POST "http://localhost:8000/api/v1/hackrx/run" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "Authorization: Bearer 429e00477ed493b1d84caf6b7580ae7d34326355abce267d8395e9cb12a748bc" \
  -d '{
    "documents": "https://sample-link.com/policy.pdf",
    "questions": [
      "What is the waiting period for cataract surgery?",
      "Does this policy cover maternity expenses?"
    ]
  }'
```

## Project Structure

```
├── main.py                 # FastAPI application entry point
├── config/
│   └── settings.py         # Configuration and environment variables
├── models/
│   └── database.py         # Supabase models and connection
├── routes/
│   └── hackrx.py          # API routes
├── controllers/
│   └── query_controller.py # Business logic
├── services/
│   ├── pdf_service.py      # PDF processing
│   ├── pinecone_service.py # Vector database operations
│   ├── gemini_service.py   # LLM integration
│   └── database_service.py # Database operations
├── utils/
│   ├── auth.py            # Authentication utilities
│   └── helpers.py         # Helper functions
├── requirements.txt
├── .env.example
└── README.md
```