"""Logging configuration for Metro Bulgaria scraper."""

import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path

from config.settings import LOG_DIR, LOG_FILENAME


def setup_logging(log_level: str = "INFO", log_to_file: bool = True, log_to_console: bool = True) -> logging.Logger:
    """Setup logging configuration for the scraper."""
    
    # Create logs directory if it doesn't exist
    log_dir = Path(LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    if log_to_console:
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    if log_to_file:
        # File handler with rotation
        log_file = log_dir / LOG_FILENAME
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Also create a daily log file
        daily_log_file = log_dir / f"scraper_{datetime.now().strftime('%Y%m%d')}.log"
        daily_handler = logging.FileHandler(daily_log_file, encoding='utf-8')
        daily_handler.setLevel(logging.DEBUG)
        daily_handler.setFormatter(formatter)
        logger.addHandler(daily_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module."""
    return logging.getLogger(name)
