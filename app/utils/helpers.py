# app/utils/helpers.py
from functools import wraps
from flask import request, jsonify
import time
import logging

logger = logging.getLogger(__name__)

def timed_lru_cache(seconds=600, maxsize=128):
    """
    Decorator that provides an LRU cache with timeout.
    
    Args:
        seconds: Maximum age of cache entry in seconds
        maxsize: Maximum size of the cache
        
    Returns:
        Decorated function with caching
    """
    def decorator(func):
        # Use Python's built-in LRU cache
        from functools import lru_cache
        
        # Caching wrapper
        cached_func = lru_cache(maxsize=maxsize)(func)
        
        # Store time with each call
        cache_info = {'last_clear': time.time()}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check if cache needs clearing
            now = time.time()
            if now - cache_info['last_clear'] > seconds:
                cached_func.cache_clear()
                cache_info['last_clear'] = now
            
            return cached_func(*args, **kwargs)
        
        # Add cache info method
        wrapper.cache_info = cached_func.cache_info
        wrapper.cache_clear = cached_func.cache_clear
        
        return wrapper
    
    return decorator

def validate_request_json(required_fields):
    """
    Decorator to validate JSON request body has required fields
    
    Args:
        required_fields: List of required field names
        
    Returns:
        Decorated function that validates request
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({"error": "Request must be JSON"}), 400
            
            data = request.json
            missing = [field for field in required_fields if field not in data]
            
            if missing:
                return jsonify({
                    "error": f"Missing required fields: {', '.join(missing)}"
                }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def log_request(level=logging.INFO):
    """
    Decorator to log API requests
    
    Args:
        level: Logging level
        
    Returns:
        Decorated function that logs requests
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Log request info
            logger.log(level, f"Request: {request.method} {request.path} from {request.remote_addr}")
            
            # Execute function
            start_time = time.time()
            response = f(*args, **kwargs)
            duration = time.time() - start_time
            
            # Log response info
            status_code = response[1] if isinstance(response, tuple) else 200
            logger.log(level, f"Response: {status_code} in {duration:.2f}s")
            
            return response
        return decorated_function
    return decorator