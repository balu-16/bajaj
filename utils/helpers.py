import logging
import sys
from typing import Any, Dict, List
import re
import uuid

# Configure logging
def setup_logging():
    """Setup application logging"""
    import os
    
    # Create logs directory if it doesn't exist
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(os.path.join(logs_dir, 'app.log'))
        ]
    )

def sanitize_text(text: str) -> str:
    """Sanitize text for safe processing"""
    if not text:
        return ""
    
    # Remove control characters
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def generate_unique_id() -> str:
    """Generate a unique identifier"""
    return str(uuid.uuid4())

def truncate_text(text: str, max_length: int = 1000) -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."

def validate_url(url: str) -> bool:
    """Validate if string is a valid URL"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return url_pattern.match(url) is not None

def format_response(data: Any, status: str = "success", message: str = "") -> Dict[str, Any]:
    """Format API response consistently"""
    return {
        "status": status,
        "message": message,
        "data": data
    }

def extract_numbers_from_text(text: str) -> List[float]:
    """Extract numeric values from text"""
    # Pattern to match numbers (including decimals and percentages)
    number_pattern = r'\b\d+(?:\.\d+)?(?:%|\s*(?:years?|months?|days?|dollars?|\$))?\b'
    
    matches = re.findall(number_pattern, text, re.IGNORECASE)
    numbers = []
    
    for match in matches:
        try:
            # Remove non-numeric characters except decimal point
            clean_number = re.sub(r'[^\d.]', '', match)
            if clean_number:
                numbers.append(float(clean_number))
        except ValueError:
            continue
    
    return numbers

def extract_time_periods(text: str) -> List[str]:
    """Extract time periods from text"""
    # Pattern to match time periods
    time_pattern = r'\b\d+\s*(?:years?|months?|days?|weeks?)\b'
    
    matches = re.findall(time_pattern, text, re.IGNORECASE)
    return matches

def calculate_similarity_threshold(scores: List[float], percentile: float = 0.7) -> float:
    """Calculate similarity threshold based on score distribution"""
    if not scores:
        return 0.5
    
    scores_sorted = sorted(scores, reverse=True)
    index = int(len(scores_sorted) * percentile)
    
    return scores_sorted[min(index, len(scores_sorted) - 1)]