import logging
import logging.handlers

PAPERTRAIL_HOST = 'logs5.papertrailapp.com'
PAPERTRAIL_PORT = 25720

# Create a logger with the desired name
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set the logging level

# File handler to log locally
file_handler = logging.FileHandler('log.txt')
file_formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
file_handler.setFormatter(file_formatter)

# SysLogHandler for Papertrail logging
papertrail_handler = logging.handlers.SysLogHandler(address=(PAPERTRAIL_HOST, PAPERTRAIL_PORT))
papertrail_formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
papertrail_handler.setFormatter(papertrail_formatter)

# Add both handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(papertrail_handler)

def getLogger(name):
    return logging.getLogger(name)

# Example usage of the logger
# logger.debug("This is a debug message")
# logger.info("This is an info message")
# logger.warning("This is a warning message")
# logger.error("This is an error message")
# logger.critical("This is a critical message")