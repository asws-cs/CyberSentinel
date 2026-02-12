import redis.asyncio as redis
import asyncio
from typing import AsyncGenerator

from config import settings
from utils.logger import logger

class LiveOutputPublisher:
    """
    Publishes messages to a Redis channel.
    """
    def __init__(self, redis_client):
        self.redis_client = redis_client

    async def publish(self, channel: str, message: str):
        try:
            await self.redis_client.publish(channel, message)
        except Exception as e:
            logger.error(f"Failed to publish message to channel '{channel}': {e}")

class LiveOutputSubscriber:
    """
    Subscribes to a Redis channel and yields messages.
    """
    def __init__(self, redis_client):
        self.redis_client = redis_client

    async def subscribe(self, channel: str) -> AsyncGenerator[str, None]:
        try:
            pubsub = self.redis_client.pubsub()
            await pubsub.subscribe(channel)
            logger.info(f"Subscribed to Redis channel: {channel}")
            
            while True:
                # The timeout is important to prevent blocking indefinitely
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message and isinstance(message.get("data"), bytes):
                    yield message['data'].decode('utf-8')
                await asyncio.sleep(0.01) # Small sleep to prevent busy-waiting
        except asyncio.CancelledError:
            logger.info(f"Subscription to channel '{channel}' cancelled.")
        except Exception as e:
            logger.error(f"Error in Redis subscription for channel '{channel}': {e}")
        finally:
            if 'pubsub' in locals() and pubsub:
                await pubsub.unsubscribe(channel)
                logger.info(f"Unsubscribed from Redis channel: {channel}")


# Singleton instances
_redis_client = None
_publisher = None

def get_live_output_publisher() -> LiveOutputPublisher:
    """
    Returns a singleton instance of the LiveOutputPublisher.
    """
    global _redis_client, _publisher
    if _redis_client is None:
        _redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
    if _publisher is None:
        _publisher = LiveOutputPublisher(_redis_client)
    return _publisher

async def get_live_output_subscriber() -> LiveOutputSubscriber:
    """
    Returns a new subscriber instance for a client.
    """
    # Each subscriber needs its own connection for pub/sub
    subscriber_redis = redis.Redis.from_url(settings.REDIS_URL, decode_responses=False)
    return LiveOutputSubscriber(subscriber_redis)
