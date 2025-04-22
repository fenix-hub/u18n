# app/services/request_throttler.py
import threading
from threading import Lock
from typing import Dict, Tuple

class RequestThrottler:
    """
    Limits the number of concurrent requests to protect service resources
    """
    def __init__(self, max_concurrent: int):
        self.semaphore = threading.Semaphore(max_concurrent)
        self.lock = Lock()
        self.max_concurrent = max_concurrent
        self.current_requests = 0
    
    def acquire(self) -> Tuple[bool, Dict[str, str]]:
        """
        Try to acquire permission to process a request
        
        Returns:
            Tuple of (allowed: bool, headers: Dict[str, str])
        """
        with self.lock:
            # Try to acquire without blocking
            result = self.semaphore.acquire(blocking=False)
            
            if result:
                self.current_requests += 1
            
            # Prepare headers with throttling information
            headers = {
                'X-Throttle-Limit': f"{self.max_concurrent}",
                'X-Throttle-Usage': f"{self.current_requests}",
                'X-Throttle-Remaining': f"{self.max_concurrent - self.current_requests}" if result else "0"
            }
            
            return result, headers
    
    def release(self) -> None:
        """Release the semaphore after processing a request"""
        with self.lock:
            self.current_requests = max(0, self.current_requests - 1)
            self.semaphore.release()