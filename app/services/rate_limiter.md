# Rate Limiter Service (`app/services/rate_limiter.py`)

This service implements rate limiting using the **Token Bucket algorithm** to control the frequency of requests processed by the application.

## Token Bucket Algorithm Explained

The Token Bucket algorithm is a common method for rate limiting. Imagine a bucket that holds tokens. Each token represents permission to process one request.

1.  **Tokens Regenerate**: The bucket is refilled with tokens at a fixed rate (e.g., `requests_per_minute`).
2.  **Bucket Capacity (Burst)**: The bucket has a maximum capacity (`burst`). If the bucket is full, new tokens are discarded. This capacity allows for short bursts of requests exceeding the average rate, as long as tokens have accumulated.
3.  **Request Processing**: When a request arrives, the system checks if there's at least one token in the bucket.
    *   If yes: A token is removed (consumed), and the request is processed.
    *   If no: The request is denied (rate-limited), often with information about when to retry.

## Implementation Details

### Initialization (`__init__`)

```python
# filepath: /workspaces/u18n/app/services/rate_limiter.py
# ...existing code...
class RateLimiter:
    """
    Implements a token bucket algorithm for rate limiting
    """
    def __init__(self, requests_per_minute: int, burst: int):
        self.requests_per_minute = requests_per_minute
        self.burst = burst
        self.tokens = burst # Start with a full bucket
        self.last_check = time.time() # Record initialization time
        self.lock = Lock() # Ensure thread safety
# ...existing code...
```

When a `RateLimiter` instance is created:
*   `requests_per_minute`: Sets the rate at which tokens are added to the bucket.
*   `burst`: Defines the maximum number of tokens the bucket can hold (the burst capacity).
*   `tokens`: Initializes the bucket to be full (`burst` tokens).
*   `last_check`: Stores the timestamp of the last time the token count was updated.
*   `lock`: A `threading.Lock` is created to ensure that token calculations are atomic and safe in multi-threaded environments (like a web server handling concurrent requests).

### Checking the Limit (`check` method)

```python
# filepath: /workspaces/u18n/app/services/rate_limiter.py
# ...existing code...
    def check(self) -> Tuple[bool, Dict[str, str]]:
        """
        Check if a request can be processed under the rate limit
        
        Returns:
            Tuple of (allowed: bool, headers: Dict[str, str])
        """
        with self.lock: # Acquire lock for thread safety
            now = time.time() 
            time_passed = now - self.last_check # Calculate time since last check
            self.last_check = now # Update last check time
            
            # --- Token Calculation ---
            # Calculate how many tokens should be added based on elapsed time
            # (requests_per_minute / 60.0) gives the tokens generated per second.
            tokens_to_add = time_passed * (self.requests_per_minute / 60.0)
            self.tokens += tokens_to_add
            
            # --- Burst Limit Capping ---
            # Ensure the token count does not exceed the burst capacity
            if self.tokens > self.burst:
                self.tokens = self.burst
            
            # --- Header Preparation (Next Step) ---
            # (Code continues to prepare headers and check/consume tokens)
            # ...existing code...
```

The `check` method determines if a request should be allowed:

1.  **Thread Safety**: It acquires the `lock` to prevent race conditions when multiple requests check the limit concurrently.
2.  **Time Calculation**: It calculates `time_passed` in seconds since the last call to `check`.
3.  **Token Regeneration**: It calculates how many tokens should have been generated during `time_passed`. The rate is `requests_per_minute / 60.0` tokens per second. This calculated amount is added to the current `self.tokens`.
4.  **Burst Capping**: It checks if adding the new tokens caused the count to exceed the `self.burst` limit. If so, it caps `self.tokens` at the `self.burst` value. This ensures the bucket doesn't overflow.

The method then proceeds (in the subsequent lines not fully shown in the selection) to prepare informative HTTP headers and determine if `self.tokens >= 1`. If a token is available, it's consumed (`self.tokens -= 1`), and the method returns `True`; otherwise, it returns `False`.