"""Utility functions for the Metro Bulgaria scraper."""

import time
import random
import functools
from typing import Callable, Any
import logging


def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Decorator to retry function calls on failure."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger = logging.getLogger(func.__module__)
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Function {func.__name__} failed after {max_retries} attempts: {e}")
                        raise
                    
                    wait_time = delay * (backoff ** attempt)
                    logger.warning(f"Function {func.__name__} failed (attempt {attempt + 1}), retrying in {wait_time:.1f}s: {e}")
                    time.sleep(wait_time)
            
            return None
        return wrapper
    return decorator


def rate_limit(calls_per_second: float = 1.0):
    """Decorator to rate limit function calls."""
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        
        return wrapper
    return decorator


def random_delay(min_delay: float = 0.5, max_delay: float = 2.0):
    """Add random delay between function calls."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            time.sleep(random.uniform(min_delay, max_delay))
            return func(*args, **kwargs)
        return wrapper
    return decorator


def format_price(price_value: float, currency: str = "BGN") -> str:
    """Format price value for display."""
    if currency == "BGN":
        return f"{price_value:.2f} лв"
    elif currency == "EUR":
        return f"€{price_value:.2f}"
    elif currency == "USD":
        return f"${price_value:.2f}"
    else:
        return f"{price_value:.2f} {currency}"


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system usage."""
    import re
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove multiple underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')
    return sanitized


def estimate_scraping_time(num_products: int, delay_per_request: float = 2.0) -> str:
    """Estimate total scraping time."""
    total_seconds = num_products * delay_per_request
    
    if total_seconds < 60:
        return f"{total_seconds:.0f} seconds"
    elif total_seconds < 3600:
        minutes = total_seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = total_seconds / 3600
        return f"{hours:.1f} hours"
