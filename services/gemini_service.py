import google.generativeai as genai
from typing import List, Dict, Any
import logging
from config.settings import settings

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        # Configure Gemini API
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        
        logger.info(f"Initialized Gemini service with model: {settings.GEMINI_MODEL}")
    
    async def generate_answer(self, question: str, relevant_chunks: List[Dict[str, Any]]) -> str:
        """Generate answer using Gemini API based on question and relevant chunks"""
        try:
            # Prepare context from relevant chunks
            context = self._prepare_context(relevant_chunks)
            
            # Create prompt
            prompt = self._create_prompt(question, context)
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            # Extract and clean answer
            answer = response.text.strip()
            
            logger.info(f"Generated answer for question: {question[:50]}...")
            return answer
            
        except Exception as e:
            logger.error(f"Error generating answer with Gemini: {str(e)}")
            # Return a fallback answer
            return f"Unable to generate answer for the question: {question}"
    
    def _prepare_context(self, relevant_chunks: List[Dict[str, Any]]) -> str:
        """Prepare context from relevant chunks"""
        context_parts = []
        
        for i, chunk in enumerate(relevant_chunks, 1):
            context_parts.append(f"[Clause {i}] (Similarity: {chunk['score']:.3f})\n{chunk['text']}\n")
        
        return "\n".join(context_parts)
    
    def _create_prompt(self, question: str, context: str) -> str:
        """Create a structured prompt for Gemini"""
        prompt = f"""
You are an intelligent document analysis assistant. Your task is to answer questions based on the provided document clauses.

INSTRUCTIONS:
1. Analyze the provided clauses carefully
2. Answer the question directly and concisely
3. Base your answer ONLY on the information provided in the clauses
4. If the information is not available in the clauses, state that clearly
5. Include relevant clause references in your answer when applicable
6. Provide specific details like waiting periods, coverage amounts, conditions, etc.

QUESTION: {question}

RELEVANT CLAUSES:
{context}

ANSWER: Provide a clear, direct answer based on the clauses above. Include specific details and reference the relevant clause information.
"""
        return prompt
    
    async def analyze_decision(self, question: str, answer: str, context: str) -> Dict[str, Any]:
        """Analyze the answer to extract decision, amount, and other structured data"""
        try:
            analysis_prompt = f"""
Analyze the following insurance/policy question and answer to extract structured information:

QUESTION: {question}
ANSWER: {answer}
CONTEXT: {context}

Extract the following information in JSON format:
{{
    "decision": "approved/rejected/needs_review/not_applicable",
    "amount": null or numeric value if mentioned,
    "waiting_period": null or period if mentioned,
    "conditions": ["list", "of", "conditions"],
    "coverage_type": "type of coverage if applicable"
}}

Provide only the JSON response:
"""
            
            response = self.model.generate_content(analysis_prompt)
            
            # Try to parse JSON response
            import json
            try:
                analysis = json.loads(response.text.strip())
                return analysis
            except json.JSONDecodeError:
                # Return default structure if JSON parsing fails
                return {
                    "decision": "not_applicable",
                    "amount": None,
                    "waiting_period": None,
                    "conditions": [],
                    "coverage_type": None
                }
                
        except Exception as e:
            logger.error(f"Error analyzing decision: {str(e)}")
            return {
                "decision": "not_applicable",
                "amount": None,
                "waiting_period": None,
                "conditions": [],
                "coverage_type": None
            }