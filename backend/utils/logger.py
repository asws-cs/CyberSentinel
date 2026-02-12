import logging
import sys
from config import settings

# Create a custom logger
logger = logging.getLogger(settings.PROJECT_NAME)
logger.setLevel(settings.LOG_LEVEL)

# Create handlers
c_handler = logging.StreamHandler(sys.stdout)
f_handler = logging.FileHandler(f'{settings.PROJECT_NAME.lower()}.log')

c_handler.setLevel(settings.LOG_LEVEL)
f_handler.setLevel(settings.LOG_LEVEL)

# Create formatters and add it to handlers
log_format = logging.Formatter(
    '%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s:%(lineno)d) - %(message)s'
)
c_handler.setFormatter(log_format)
f_handler.setFormatter(log_format)

# Add handlers to the logger
if not logger.handlers:
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

logger.propagate = False
