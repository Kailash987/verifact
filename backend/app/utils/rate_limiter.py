"""
Rate limiting utilities for API endpoints.
"""

import time
from typing import Dict, Optional
from collections import defaultdict, deque
from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimiter:
    """
    Simple in-memory rate limiter using sliding window algorithm.
    """
    
    def __init__(self, requests_per_minute: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_minute: Maximum requests allowed per minute
        """
        self.requests_per_minute = requests_per_minute
        self.clients: Dict[str, deque] = defaultdict(deque)
    
    def is_allowed(self, client_id: str) -> bool:
        """
        Check if client is allowed to make a request.
        
        Args:
            client_id: Unique client identifier (IP address)
            
        Returns:
            True if allowed, False otherwise
        """
        now = time.time()
        client_requests = self.clients[client_id]
        
        # Remove old requests (older than 1 minute)
        while client_requests and client_requests[0] < now - 60:
            client_requests.popleft()
        
        # Check if under limit
        if len(client_requests) < self.requests_per_minute:
            client_requests.append(now)
            return True
        
        return False
    
    def get_remaining_requests(self, client_id: str) -> int:
        """
        Get remaining requests for client.
        
        Args:
            client_id: Unique client identifier
            
        Returns:
            Number of remaining requests
        """
        now = time.time()
        client_requests = self.clients[client_id]
        
        # Remove old requests
        while client_requests and client_requests[0] < now - 60:
            client_requests.popleft()
        
        return max(0, self.requests_per_minute - len(client_requests))


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for rate limiting.
    """
    
    def __init__(self, app, rate_limiter: RateLimiter):
        """
        Initialize middleware.
        
        Args:
            app: FastAPI application
            rate_limiter: Rate limiter instance
        """
        super().__init__(app)
        self.rate_limiter = rate_limiter
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request with rate limiting.
        
        Args:
            request: HTTP request
            call_next: Next middleware/endpoint
            
        Returns:
            HTTP response
        """
        # Get client IP
        client_id = request.client.host
        if "x-forwarded-for" in request.headers:
            client_id = request.headers["x-forwarded-for"].split(",")[0].strip()
        
        # Check rate limit
        if not self.rate_limiter.is_allowed(client_id):
            remaining = self.rate_limiter.get_remaining_requests(client_id)
            
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Maximum {self.rate_limiter.requests_per_minute} requests per minute allowed.",
                    "remaining_requests": remaining,
                    "retry_after": 60
                },
                headers={
                    "X-RateLimit-Limit": str(self.rate_limiter.requests_per_minute),
                    "X-RateLimit-Remaining": str(remaining),
                    "X-RateLimit-Retry-After": "60"
                }
            )
        
        # Add rate limit headers to response
        response = await call_next(request)
        remaining = self.rate_limiter.get_remaining_requests(client_id)
        
        response.headers["X-RateLimit-Limit"] = str(self.rate_limiter.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        
        return response


# Global rate limiter instance
rate_limiter = RateLimiter(requests_per_minute=60)
