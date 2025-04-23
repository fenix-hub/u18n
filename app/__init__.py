# app/__init__.py
import logging
import sys # Import sys to output logs to stdout

logger = logging.getLogger(__name__) # Keep the logger instance

def setup_logging(config):
    """Configure application logging based on the loaded config."""
    log_level = config.get('logging', {}).get('level', 'INFO').upper()
    log_format = config.get('logging', {}).get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Get the root logger
    root_logger = logging.getLogger()

    # Remove existing handlers to avoid duplicate logs if re-configured
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Configure the root logger
    root_logger.setLevel(log_level)

    # Create a handler (e.g., StreamHandler to log to console)
    # Use sys.stdout to ensure compatibility with containers/Gunicorn
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)

    # Create formatter and add it to the handler
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)

    # Add the handler to the root logger
    root_logger.addHandler(handler)

    logger.info(f"Logging configured with level: {log_level}")

# The logger instance is still available for use in this module if needed
# logger.info("App package initialized") # Example log