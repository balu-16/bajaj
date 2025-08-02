from config.settings import settings
import logging

logger = logging.getLogger(__name__)

def verify_bearer_token(token: str) -> bool:
    """Verify the bearer token against the configured token"""
    try:
        return token == settings.BEARER_TOKEN
    except Exception as e:
        logger.error(f"Error verifying bearer token: {str(e)}")
        return False

def extract_bearer_token(authorization_header: str) -> str:
    """Extract bearer token from Authorization header"""
    try:
        if not authorization_header or not authorization_header.startswith("Bearer "):
            return ""
        
        return authorization_header.split(" ")[1]
    except Exception as e:
        logger.error(f"Error extracting bearer token: {str(e)}")
        return ""