import time
import redis.asyncio as redis
from fastapi import Request, HTTPException, status
from typing import Optional

from config import settings
from utils.logger import logger

class RateLimiter:
    """
    A token bucket rate limiter implemented using Redis.
    """
    def __init__(self, capacity: int, refill_rate: float, client: redis.Redis):
        """
        Args:
            capacity: The maximum number of tokens in the bucket.
            refill_rate: The number of tokens to add per second.
            client: An asynchronous Redis client instance.
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.redis = client

    async def is_allowed(self, identifier: str) -> bool:
        """
        Checks if a request from the given identifier is allowed.
        
        Args:
            identifier: A unique identifier for the client (e.g., IP address).
            
        Returns:
            True if the request is allowed, False otherwise.
        """
        bucket_key = f"rate_limit:{identifier}"
        now = time.time()

        # Use a Redis pipeline for atomic operations
        pipe = self.redis.pipeline()
        pipe.hgetall(bucket_key)
        results = await pipe.execute()
        
        bucket = results[0] if results and results[0] else {}
        tokens = float(bucket.get("tokens", self.capacity))
        last_refill = float(bucket.get("last_refill", now))

        # Refill tokens based on elapsed time
        delta = max(0, now - last_refill)
        tokens_to_add = delta * self.refill_rate
        new_tokens = min(self.capacity, tokens + tokens_to_add)

        if new_tokens >= 1:
            # Consume one token
            pipe = self.redis.pipeline()
            pipe.hset(bucket_key, "tokens", new_tokens - 1)
            pipe.hset(bucket_key, "last_refill", now)
            await pipe.execute()
            return True
        else:
            # Not enough tokens, deny request
            # We can still update the bucket state without consuming a token
            pipe = self.redis.pipeline()
            pipe.hset(bucket_key, "tokens", new_tokens)
            pipe.hset(bucket_key, "last_refill", now)
            await pipe.execute()
            return False

# Singleton Redis client for the rate limiter
_redis_client: Optional[redis.Redis] = None

def get_rate_limiter() -> RateLimiter:
    """
    Returns a singleton instance of the RateLimiter.
    """
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
    
    # Example: Allow 10 requests, refill 1 token per second
    return RateLimiter(capacity=10, refill_rate=1.0, client=_redis_client)


async def rate_limit_dependency(request: Request):
    """
    FastAPI dependency that applies rate limiting to an endpoint.
    """
    # Use client's IP address as the identifier
    identifier = request.client.host
    limiter = get_rate_limiter()
    
    if not await limiter.is_allowed(identifier):
        logger.warning(f"Rate limit exceeded for IP: {identifier}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later.",
            headers={"Retry-After": "60"}, # Suggest a 60-second cooldown
        )
