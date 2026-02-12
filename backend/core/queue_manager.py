import json
from typing import Dict, Any, Optional
import redis.asyncio as redis
from utils.helpers import to_json
from utils.logger import logger
from config import settings

class TaskQueue:
    def __init__(self, host: str, port: int, db: int):
        self.host = host
        self.port = port
        self.db = db
        self.redis_client = None
        self.queue_name = "scan_queue"

    async def connect(self):
        """
        Initializes and connects the Redis client.
        """
        try:
            self.redis_client = redis.Redis(host=self.host, port=self.port, db=self.db, decode_responses=True)
            await self.redis_client.ping()
            logger.info("Redis client connected successfully.")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {type(e).__name__}: {e}")
            self.redis_client = None # Ensure it's None on failure

    async def enqueue_task(self, task: Dict[str, Any]):
        """
        Adds a task to the queue.
        """
        if not self.redis_client:
            logger.error("Attempted to enqueue task but Redis client is not connected.")
            return
        try:
            await self.redis_client.lpush(self.queue_name, to_json(task))
            logger.info(f"Enqueued task: {task['scan_id']}")
        except Exception as e:
            logger.error(f"Failed to enqueue task: {type(e).__name__}: {e}")

    async def dequeue_task(self) -> Optional[Dict[str, Any]]:
        """
        Removes and returns a task from the queue.
        Returns None if the queue is empty.
        """
        if not self.redis_client:
            logger.error("Attempted to dequeue task but Redis client is not connected.")
            return None
        try:
            task_json = await self.redis_client.rpop(self.queue_name)
            if task_json:
                task = json.loads(task_json)
                logger.info(f"Dequeued task: {task['scan_id']}")
                return task
            return None
        except Exception as e:
            logger.error(f"Failed to dequeue task: {type(e).__name__}: {e}")
            return None

    async def get_queue_size(self) -> int:
        """
        Gets the current size of the queue.
        """
        if not self.redis_client:
            logger.error("Attempted to get queue size but Redis client is not connected.")
            return 0
        try:
            return await self.redis_client.llen(self.queue_name)
        except Exception as e:
            logger.error(f"Failed to get queue size: {type(e).__name__}: {e}")
            return 0

# Global queue instance
task_queue: Optional[TaskQueue] = None

async def initialize_queue():
    """
    Initializes the global task queue.
    """
    global task_queue
    if task_queue is None:
        task_queue = TaskQueue(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
        )
        await task_queue.connect()
        logger.info("Task queue initialized.")

def get_queue() -> TaskQueue:
    """
    Returns the global task queue instance.
    """
    if task_queue is None:
        raise RuntimeError("Task queue has not been initialized. Call initialize_queue() first.")
    return task_queue
