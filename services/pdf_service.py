import requests
import PyPDF2
from io import BytesIO
from typing import List
import re
import logging
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config.settings import settings

logger = logging.getLogger(__name__)

class PDFService:
    def __init__(self):
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
        self.session = self._create_robust_session()
    
    def _create_robust_session(self):
        """Create a requests session with retry logic and better error handling"""
        session = requests.Session()
        
        # Define retry strategy
        retry_strategy = Retry(
            total=3,  # Total number of retries
            backoff_factor=1,  # Wait time between retries
            status_forcelist=[429, 500, 502, 503, 504],  # HTTP status codes to retry
            allowed_methods=["HEAD", "GET", "OPTIONS"]  # HTTP methods to retry
        )
        
        # Mount adapter with retry strategy
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set default headers
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        return session
    
    async def extract_text_from_url(self, pdf_url: str) -> str:
        """Download PDF from URL and extract text content"""
        try:
            logger.info(f"Downloading PDF from: {pdf_url}")
            
            # Validate URL format
            if not pdf_url.startswith(('http://', 'https://')):
                raise ValueError(f"Invalid URL format: {pdf_url}")
            
            # Download PDF with robust error handling
            response = None
            max_attempts = 3
            
            for attempt in range(max_attempts):
                try:
                    logger.info(f"Download attempt {attempt + 1}/{max_attempts}")
                    
                    # Use the robust session with timeout
                    response = self.session.get(pdf_url, timeout=60, stream=True)
                    response.raise_for_status()
                    
                    # Check content type
                    content_type = response.headers.get('content-type', '').lower()
                    if 'pdf' not in content_type and 'application/octet-stream' not in content_type:
                        logger.warning(f"Unexpected content type: {content_type}")
                    
                    break  # Success, exit retry loop
                    
                except requests.exceptions.ConnectionError as e:
                    logger.warning(f"Connection error on attempt {attempt + 1}: {str(e)}")
                    if attempt == max_attempts - 1:
                        raise ConnectionError(f"Failed to connect to {pdf_url} after {max_attempts} attempts. Please check your internet connection and the URL.")
                    time.sleep(2 ** attempt)  # Exponential backoff
                    
                except requests.exceptions.Timeout as e:
                    logger.warning(f"Timeout error on attempt {attempt + 1}: {str(e)}")
                    if attempt == max_attempts - 1:
                        raise TimeoutError(f"Request timed out after {max_attempts} attempts. The server may be slow or unreachable.")
                    time.sleep(2 ** attempt)
                    
                except requests.exceptions.HTTPError as e:
                    logger.error(f"HTTP error: {e.response.status_code} - {str(e)}")
                    if e.response.status_code == 404:
                        raise FileNotFoundError(f"PDF not found at URL: {pdf_url}")
                    elif e.response.status_code == 403:
                        raise PermissionError(f"Access denied to PDF: {pdf_url}")
                    else:
                        raise e
                        
                except Exception as e:
                    logger.error(f"Unexpected error on attempt {attempt + 1}: {str(e)}")
                    if attempt == max_attempts - 1:
                        raise e
                    time.sleep(2 ** attempt)
            
            if not response:
                raise Exception("Failed to download PDF after all attempts")
            
            # Extract text from PDF
            logger.info("Extracting text from PDF...")
            pdf_file = BytesIO(response.content)
            
            try:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                
                if len(pdf_reader.pages) == 0:
                    raise ValueError("PDF file appears to be empty or corrupted")
                
                text = ""
                for page_num in range(len(pdf_reader.pages)):
                    try:
                        page = pdf_reader.pages[page_num]
                        page_text = page.extract_text()
                        text += page_text + "\n"
                    except Exception as e:
                        logger.warning(f"Error extracting text from page {page_num + 1}: {str(e)}")
                        continue
                
                if not text.strip():
                    raise ValueError("No text could be extracted from the PDF. The PDF may be image-based or corrupted.")
                
            except PyPDF2.errors.PdfReadError as e:
                raise ValueError(f"Invalid or corrupted PDF file: {str(e)}")
            
            # Clean up text
            text = self._clean_text(text)
            
            logger.info(f"Successfully extracted {len(text)} characters from PDF")
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise e
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,;:!?()-]', '', text)
        
        # Remove multiple consecutive periods
        text = re.sub(r'\.{3,}', '...', text)
        
        return text.strip()
    
    async def chunk_text(self, text: str) -> List[str]:
        """Split text into semantically meaningful chunks"""
        try:
            # Split by sentences first
            sentences = self._split_into_sentences(text)
            
            chunks = []
            current_chunk = ""
            
            for sentence in sentences:
                # If adding this sentence would exceed chunk size
                if len(current_chunk) + len(sentence) > self.chunk_size:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                        
                        # Start new chunk with overlap
                        overlap_text = self._get_overlap_text(current_chunk)
                        current_chunk = overlap_text + " " + sentence
                    else:
                        # Sentence is too long, split it
                        current_chunk = sentence
                else:
                    current_chunk += " " + sentence if current_chunk else sentence
            
            # Add the last chunk
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            logger.info(f"Created {len(chunks)} chunks from text")
            return chunks
            
        except Exception as e:
            logger.error(f"Error chunking text: {str(e)}")
            raise e
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting on periods, exclamation marks, and question marks
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _get_overlap_text(self, text: str) -> str:
        """Get overlap text from the end of current chunk"""
        if len(text) <= self.chunk_overlap:
            return text
        
        # Get last chunk_overlap characters, but try to break at word boundary
        overlap = text[-self.chunk_overlap:]
        space_index = overlap.find(' ')
        
        if space_index != -1:
            return overlap[space_index:].strip()
        
        return overlap