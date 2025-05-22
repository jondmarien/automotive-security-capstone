"""Hardware utilities package.

This package contains various utility modules for the hardware abstraction layer,
including logging, reporting, and other helper functions.
"""
import logging
import os
from typing import Optional, Union

from .logger import EdgeLogger
from .logger import logger as edge_logger


def configure_logging(
    level: Union[int, str] = logging.INFO,
    log_file: Optional[str] = None,
    log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5
) -> None:
    """Configure logging for the application.
    
    Args:
        level: Logging level (e.g., 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        log_file: Optional path to a log file. If not provided, logs to console only.
        log_format: Format string for log messages.
        max_bytes: Maximum log file size in bytes before rotation.
        backup_count: Number of backup log files to keep.
    """
    # Convert string log level to int if needed
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    formatter = logging.Formatter(log_format)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Add file handler if log_file is specified
    if log_file:
        # Create directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Configure the edge logger
    edge_logger.log_level = level


def setup_logging(level: Union[int, str] = logging.INFO) -> None:
    """Set up basic logging configuration.
    
    This is a convenience wrapper around configure_logging with default settings.
    
    Args:
        level: Logging level (e.g., 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
    """
    configure_logging(level=level)


# Re-export the logger instance
logger = edge_logger

__all__ = [
    'EdgeLogger',
    'configure_logging',
    'logger',
    'setup_logging',
]