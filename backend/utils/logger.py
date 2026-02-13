import logging
import sys
import redis
import json # Import json for message serialization

from config import settings

# Create a custom logger
logger = logging.getLogger(settings.PROJECT_NAME)
logger.setLevel(settings.LOG_LEVEL)

# Initialize Redis client for LiveFeedHandler
# This should ideally be handled more robustly (e.g., connection pooling, error handling)
# but for now, a direct client is sufficient for demonstration.
try:
    redis_client = redis.StrictRedis.from_url(settings.REDIS_URL, decode_responses=True)
    redis_client.ping() # Test connection
except redis.exceptions.ConnectionError as e:
    logger.error(f"Could not connect to Redis for LiveFeedHandler: {e}")
    redis_client = None

class LiveFeedHandler(logging.Handler):
    """
    A custom logging handler that publishes user-relevant log messages to a Redis channel
    for real-time frontend display.
    """
    def emit(self, record):
        if redis_client is None:
            return # Don't try to publish if Redis is not connected

        try:
            # Only process records that have a 'scan_id' extra field
            if not hasattr(record, 'scan_id'):
                return

            # Filter out internal/technical messages that should not go to the live feed
            # This is a basic filter; it will be refined as needed.
            # We want to exclude debug, internal system messages, stack traces, etc.
            # Also, filter out messages that are clearly internal or already formatted for console
            if record.levelname == 'DEBUG':
                return
            
            # Further filter based on message content for user relevance
            # This list of keywords will need to be expanded and refined.
            user_relevant_keywords = [
                "Target resolved", "Scan Started", "Scan Finished", "Nmap", "SSL Scan",
                "Header Analysis", "Directory Discovery", "SQLMap", "XSS",
                "Vulnerability Detected", "Risk assessment", "Reports generated",
                "WARNING", "ERROR", "COMPLETE", "SUCCESS", "Open Ports Found", "Reflected XSS Detected",
                "SQL injection vulnerability detected", "Wordlist Not Found"
            ]
            
            message_content = record.getMessage()
            
            # Allow all INFO, WARNING, ERROR messages if they contain user-relevant keywords
            # Or if they are INFO, WARNING, ERROR and don't match specific internal patterns
            is_user_relevant = any(keyword.lower() in message_content.lower() for keyword in user_relevant_keywords)
            
            # Explicitly exclude some internal messages that might contain keywords
            if "Tool pipeline built" in message_content:
                return

            if not is_user_relevant and record.levelname not in ['INFO', 'WARNING', 'ERROR']:
                return # Only allow user_relevant or specific levels

            # Format the message for the frontend
            formatted_message = {
                "level": record.levelname.upper(),
                "message": message_content,
                "timestamp": record.asctime
            }
            
            channel = f"scan_live_feed:{record.scan_id}"
            redis_client.publish(channel, json.dumps(formatted_message))

        except Exception as e:
            # Log any errors occurring within the handler itself
            # We don't want the live feed handler to crash the main logging process
            logger.error(f"Error in LiveFeedHandler: {e}")


# Create handlers
c_handler = logging.StreamHandler(sys.stdout)
f_handler = logging.FileHandler(f'{settings.PROJECT_NAME.lower()}.log')
live_feed_handler = LiveFeedHandler() # Instantiate the custom handler

c_handler.setLevel(settings.LOG_LEVEL)
f_handler.setLevel(settings.LOG_LEVEL)
live_feed_handler.setLevel(logging.INFO) # Live feed should generally be INFO level or above

# Create formatters and add it to handlers
log_format = logging.Formatter(
    '%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s:%(lineno)d) - %(message)s'
)
# A simpler format for the live feed, as we're reformatting in the handler
# The LiveFeedHandler creates its own dictionary format, so this formatter isn't strictly used for it
# but good practice to assign one.
live_feed_format = logging.Formatter(
    '[%(levelname)s] %(message)s'
)

c_handler.setFormatter(log_format)
f_handler.setFormatter(log_format)
live_feed_handler.setFormatter(live_feed_format) # Assign formatter to live feed handler

# Add handlers to the logger
if not logger.handlers:
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)
    logger.addHandler(live_feed_handler) # Add the new live feed handler

logger.propagate = False
