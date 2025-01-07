"""
Logging configuration module.
"""

# imports
import logging
from typing import Optional
from pathlib import Path

# app imports
from usbills_app.config import AppConfig, get_config


def create_logger(
    name: str,
    level: Optional[str] = None,
    format_string: Optional[str] = None,
    app_config: Optional[AppConfig] = None,
) -> logging.Logger:
    """
    Create a logger with the given name and configuration.

    Args:
        name (str): The logger name
        level (Optional[str]): The log level, e.g., DEBUG, INFO. If None, use app_config
        format_string (Optional[str]): Custom format string. If None, use default
        app_config (Optional[AppConfig]): App configuration. If None, load from file

    Returns:
        logging.Logger: Configured logger instance
    """
    # Get app config if not provided
    if app_config is None:
        app_config = get_config()

    # Use app config log level if not specified
    if level is None:
        level = app_config.log_level

    # Create logger
    logger = logging.getLogger(name)

    # Set level
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    for handler in logger.handlers:
        logger.removeHandler(handler)

    # Create file handler by default
    # handler = logging.StreamHandler(sys.stdout)
    try:
        log_file_path = Path(app_config.log_file)
        log_file_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Error creating log file: {e}")
        log_file_path = Path("usbills.log")

    # get handler with absolute path to log file
    handler = logging.FileHandler(log_file_path)
    handler.setLevel(getattr(logging, level.upper()))

    # Set format
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    formatter = logging.Formatter(format_string)
    handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(handler)

    return logger


# Create the default app logger
LOGGER = create_logger(__name__)
