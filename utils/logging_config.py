import sys
import json
from loguru import logger
import structlog
from typing import Any, Dict

def setup_logging():
    """Configure structured logging for the application"""
    
    # Remove default loguru handler
    logger.remove()
    
    # Configure loguru with JSON formatting
    logger.add(
        sys.stdout,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
        level="INFO",
        serialize=True,  # JSON output
        backtrace=True,
        diagnose=True
    )
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

def get_logger(name: str = None):
    """Get a configured logger instance"""
    if name:
        return logger.bind(service=name)
    return logger

def log_request(request_id: str, method: str, path: str, **kwargs):
    """Log HTTP request with structured data"""
    logger.info(
        "HTTP Request",
        request_id=request_id,
        method=method,
        path=path,
        **kwargs
    )

def log_response(request_id: str, status_code: int, duration_ms: float, **kwargs):
    """Log HTTP response with structured data"""
    logger.info(
        "HTTP Response",
        request_id=request_id,
        status_code=status_code,
        duration_ms=duration_ms,
        **kwargs
    )

def log_error(error: Exception, context: Dict[str, Any] = None):
    """Log error with context"""
    logger.error(
        f"Error: {str(error)}",
        error_type=type(error).__name__,
        context=context or {},
        exc_info=True
    )

def log_database_operation(operation: str, table: str, duration_ms: float = None, **kwargs):
    """Log database operations"""
    logger.info(
        "Database Operation",
        operation=operation,
        table=table,
        duration_ms=duration_ms,
        **kwargs
    )

def log_external_api_call(service: str, endpoint: str, status_code: int = None, duration_ms: float = None, **kwargs):
    """Log external API calls"""
    logger.info(
        "External API Call",
        service=service,
        endpoint=endpoint,
        status_code=status_code,
        duration_ms=duration_ms,
        **kwargs
    )