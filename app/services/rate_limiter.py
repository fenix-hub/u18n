# app/services/rate_limiter.py
import time
from threading import Lock
from typing import Dict, Tuple

class RateLimiter:
    """
    Implements a token bucket algorithm for rate limiting
    """
    def __init__(self, requests_per_minute: int, burst: int):
        self.requests_per_minute = requests_per_minute
        self.burst = burst
        self.tokens = burst
        self.last_check = time.time()
        self.lock = Lock()
    
    def check(self) -> Tuple[bool, Dict[str, str]]:
        """
        Check if a request can be processed under the rate limit
        
        Returns:
            Tuple of (allowed: bool, headers: Dict[str, str])
        """
        with self.lock:
            now = time.time()
            time_passed = now - self.last_check
            self.last_check = now
            
            # Add tokens based on time passed
            self.tokens += time_passed * (self.requests_per_minute / 60.0)
            
            # Cap tokens to burst limit
            if self.tokens > self.burst:
                self.tokens = self.burst
            
            # Prepare headers with rate limit information
            headers = {
                'X-RateLimit-Limit': f"{self.requests_per_minute}",
                'X-RateLimit-Remaining': f"{self.tokens:.1f}",
                'X-RateLimit-Reset': f"{int(60 * (1 - (self.tokens / self.requests_per_minute)))}",
            }
            
            # Check if we have at least 1 token
            if self.tokens >= 1:
                self.tokens -= 1
                return True, headers
            else:
                # Calculate wait time until next token is available
                wait_time = (1 - self.tokens) * (60 / self.requests_per_minute)
                headers['Retry-After'] = f"{int(wait_time)}"
                return False, headers