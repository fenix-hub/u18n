# app/api/middleware.py
from flask import Response
from functools import wraps
from typing import Dict, Callable

def add_headers(response: Response, headers_dict: Dict[str, str]) -> Response:
    """Add headers to Flask response."""
    for header_name, header_value in headers_dict.items():
        response.headers[header_name] = header_value
    return response

def apply_rate_limit(f: Callable, rate_limiter, enabled: bool):
    """Rate limiting middleware decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not enabled:
            return f(*args, **kwargs)
        
        # Check rate limit
        pass_check, headers = rate_limiter.check()
        if not pass_check:
            response = {"error": "Rate limit exceeded"}
            return add_headers(response, headers), 429
        
        # Call the original function
        response, status_code = f(*args, **kwargs)
        
        # Add rate limit headers
        return add_headers(response, headers), status_code
    
    return decorated_function

def apply_throttling(f: Callable, request_throttler, enabled: bool):
    """Throttling middleware decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not enabled:
            return f(*args, **kwargs)
        
        # Check throttling
        pass_check, headers = request_throttler.acquire()
        if not pass_check:
            response = {"error": "Service overloaded, try again later"}
            return add_headers(response, headers), 503
        
        try:
            # Call the original function
            response, status_code = f(*args, **kwargs)
            
            # Add throttling headers
            return add_headers(response, headers), status_code
        finally:
            # Always release the resource
            request_throttler.release()
    
    return decorated_function