"""Configuration settings for Metro Bulgaria scraper."""

import os
from dotenv import load_dotenv

load_dotenv()

# Target URL
KAUFLAND_BG_URL = "https://www.kaufland.bg/broshuri.html"
KAUFLAND_LEAFLETS_API = "https://leaflets.kaufland.com"

# Request settings
REQUEST_TIMEOUT = 30
REQUEST_DELAY = 2  # seconds between requests
MAX_RETRIES = 3

# User agent rotation
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

# Output settings
OUTPUT_DIR = "data"
OUTPUT_FILENAME = "kaufland_bg_products.json"
LOG_DIR = "logs"
LOG_FILENAME = "scraper.log"
PDF_DIR = "pdfs"  # Directory for downloaded PDF brochures

# Scraping settings
MAX_PRODUCTS = int(os.getenv("MAX_PRODUCTS", 1000))
ENABLE_SELENIUM = os.getenv("ENABLE_SELENIUM", "false").lower() == "true"
HEADLESS_BROWSER = os.getenv("HEADLESS_BROWSER", "true").lower() == "true"
