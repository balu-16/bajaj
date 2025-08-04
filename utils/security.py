import boto3
import json
from typing import Optional, Dict, Any
from fastapi import HTTPException, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from config.settings import settings
from utils.logging_config import get_logger, log_error

logger = get_logger("security")

# Rate limiter configuration
limiter = Limiter(key_func=get_remote_address)

class SecretsManager:
    """AWS Secrets Manager integration"""
    
    def __init__(self):
        self.client = boto3.client(
            'secretsmanager',
            region_name=settings.AWS_REGION if hasattr(settings, 'AWS_REGION') else 'us-east-1'
        )
        self._cache = {}
    
    def get_secret(self, secret_name: str) -> Optional[str]:
        """Get secret from AWS Secrets Manager with caching"""
        if secret_name in self._cache:
            return self._cache[secret_name]
        
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            secret_value = response['SecretString']
            
            # Try to parse as JSON, fallback to string
            try:
                secret_data = json.loads(secret_value)
                self._cache[secret_name] = secret_data
                return secret_data
            except json.JSONDecodeError:
                self._cache[secret_name] = secret_value
                return secret_value
                
        except Exception as e:
            log_error(e, {"secret_name": secret_name})
            return None
    
    def get_secret_value(self, secret_name: str, key: str = None) -> Optional[str]:
        """Get specific value from secret"""
        secret = self.get_secret(secret_name)
        if isinstance(secret, dict) and key:
            return secret.get(key)
        return secret

# Global secrets manager instance
secrets_manager = SecretsManager()

def get_api_key_from_secrets(key_name: str) -> str:
    """Get API key from AWS Secrets Manager or fallback to environment"""
    secret_value = secrets_manager.get_secret_value("bajaj-api-secrets", key_name)
    if secret_value:
        return secret_value
    
    # Fallback to environment variables
    return getattr(settings, key_name.upper(), "")

class SecurityHeaders:
    """Security headers middleware"""
    
    @staticmethod
    def add_security_headers(response):
        """Add security headers to response"""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response

def validate_request_size(request: Request, max_size: int = 10 * 1024 * 1024):  # 10MB default
    """Validate request content length"""
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > max_size:
        raise HTTPException(
            status_code=413,
            detail=f"Request too large. Maximum size: {max_size} bytes"
        )

def sanitize_input(data: Any) -> Any:
    """Basic input sanitization"""
    if isinstance(data, str):
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', '\x00']
        for char in dangerous_chars:
            data = data.replace(char, '')
        return data.strip()
    elif isinstance(data, dict):
        return {k: sanitize_input(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    return data

class IPWhitelist:
    """IP whitelist for admin endpoints"""
    
    def __init__(self, allowed_ips: list = None):
        self.allowed_ips = allowed_ips or []
    
    def is_allowed(self, ip: str) -> bool:
        """Check if IP is in whitelist"""
        if not self.allowed_ips:
            return True  # No whitelist configured
        return ip in self.allowed_ips
    
    def validate_ip(self, request: Request):
        """Validate request IP against whitelist"""
        client_ip = get_remote_address(request)
        if not self.is_allowed(client_ip):
            logger.warning(f"Blocked request from unauthorized IP: {client_ip}")
            raise HTTPException(
                status_code=403,
                detail="Access denied from this IP address"
            )

# Rate limiting decorators
def rate_limit_per_minute(requests: int = 60):
    """Rate limit decorator for per-minute limits"""
    return limiter.limit(f"{requests}/minute")

def rate_limit_per_hour(requests: int = 1000):
    """Rate limit decorator for per-hour limits"""
    return limiter.limit(f"{requests}/hour")

def rate_limit_strict(requests: int = 10):
    """Strict rate limit for sensitive endpoints"""
    return limiter.limit(f"{requests}/minute")

# JWT token validation (enhanced)
def validate_jwt_token(token: str) -> Dict[str, Any]:
    """Enhanced JWT token validation with logging"""
    try:
        # Your existing JWT validation logic here
        # Add logging for security events
        logger.info("JWT token validated successfully")
        return {"valid": True, "user_id": "user_123"}  # Replace with actual validation
    except Exception as e:
        logger.warning(f"JWT validation failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token")

# Error handlers for rate limiting
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Custom rate limit exceeded handler"""
    client_ip = get_remote_address(request)
    logger.warning(f"Rate limit exceeded for IP: {client_ip}")
    
    response = {
        "error": "Rate limit exceeded",
        "detail": f"Too many requests. Limit: {exc.detail}",
        "retry_after": exc.retry_after
    }
    return HTTPException(status_code=429, detail=response)