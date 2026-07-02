"""Web scraper module for Kaufland Bulgaria website."""

import re
import time
import random
import logging
from typing import Optional, Dict, Any, List
import requests
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from config.settings import (
    REQUEST_TIMEOUT, REQUEST_DELAY, MAX_RETRIES, 
    USER_AGENTS, ENABLE_SELENIUM, HEADLESS_BROWSER,
    PDF_DIR
)


class KauflandScraper:
    """Main scraper class for Kaufland Bulgaria website."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.ua = UserAgent()
        self.driver = None
        
        # Setup session headers
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def _get_random_user_agent(self) -> str:
        """Get a random user agent string."""
        try:
            return self.ua.random
        except Exception:
            return random.choice(USER_AGENTS)
    
    def _setup_selenium_driver(self) -> webdriver.Chrome:
        """Setup Selenium Chrome driver with appropriate options."""
        chrome_options = Options()
        
        if HEADLESS_BROWSER:
            chrome_options.add_argument('--headless')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument(f'--user-agent={self._get_random_user_agent()}')
        
        # Disable images for faster loading
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(REQUEST_TIMEOUT)
            return driver
        except Exception as e:
            self.logger.error(f"Failed to setup Selenium driver: {e}")
            raise
    
    def fetch_page_requests(self, url: str) -> Optional[str]:
        """Fetch page content using requests library."""
        for attempt in range(MAX_RETRIES):
            try:
                self.session.headers['User-Agent'] = self._get_random_user_agent()
                
                self.logger.info(f"Fetching page (attempt {attempt + 1}): {url}")
                response = self.session.get(url, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                
                # Add delay between requests
                time.sleep(REQUEST_DELAY + random.uniform(0, 1))
                
                return response.text
                
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt == MAX_RETRIES - 1:
                    self.logger.error(f"All {MAX_RETRIES} attempts failed for URL: {url}")
                    return None
                time.sleep(2 ** attempt)  # Exponential backoff
        
        return None
    
    def fetch_page_selenium(self, url: str, scroll_for_products: bool = True) -> Optional[str]:
        """Fetch page content using Selenium WebDriver."""
        if not self.driver:
            self.driver = self._setup_selenium_driver()
        
        try:
            self.logger.info(f"Fetching page with Selenium: {url}")
            self.driver.get(url)
            
            # Wait for products to load
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "product"))
                )
            except TimeoutException:
                self.logger.warning("Timeout waiting for products to load")
            
            # Scroll to load more products if needed
            if scroll_for_products:
                self._scroll_to_load_all_products()
            else:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            return self.driver.page_source
            
        except WebDriverException as e:
            self.logger.error(f"Selenium error: {e}")
            return None
    
    def _scroll_to_load_all_products(self):
        """Scroll through the page to load all dynamically loaded products."""
        self.logger.info("Scrolling to load all products...")
        
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        max_scroll_attempts = 20  # Limit to prevent infinite scrolling
        
        while scroll_attempts < max_scroll_attempts:
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Wait for new content to load
            time.sleep(2)
            
            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                # Try clicking "Load More" button if it exists
                try:
                    load_more_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                        'button[class*="load"], button[class*="more"], .load-more, .show-more')
                    if load_more_buttons:
                        for button in load_more_buttons:
                            if button.is_displayed():
                                button.click()
                                time.sleep(2)
                                new_height = self.driver.execute_script("return document.body.scrollHeight")
                                break
                except:
                    pass
                
                # If still no change, we've reached the bottom
                if new_height == last_height:
                    break
            
            last_height = new_height
            scroll_attempts += 1
            self.logger.debug(f"Scroll attempt {scroll_attempts}, height: {new_height}")
        
        self.logger.info(f"Finished scrolling after {scroll_attempts} attempts")
    
    def discover_categories(self) -> List[Dict[str, str]]:
        """Discover all product categories on the Metro website."""
        self.logger.info("Discovering product categories...")
        
        if not self.driver:
            self.driver = self._setup_selenium_driver()
        
        try:
            # Go to main shop page
            self.driver.get("https://shop.metro.bg/shop")
            time.sleep(3)
            
            categories = []
            
            # Look for category links
            category_selectors = [
                'nav a[href*="/shop"]',
                '.category a',
                '.categories a',
                '.navigation a[href*="/shop"]',
                'a[href*="category"]'
            ]
            
            category_links = set()
            for selector in category_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        href = element.get_attribute('href')
                        text = element.text.strip()
                        if href and 'shop.metro.bg/shop' in href and text:
                            category_links.add((href, text))
                except:
                    continue
            
            # Convert to list of dictionaries
            for url, name in category_links:
                categories.append({
                    'url': url,
                    'name': name
                })
            
            self.logger.info(f"Discovered {len(categories)} categories")
            return categories
            
        except Exception as e:
            self.logger.error(f"Error discovering categories: {e}")
            return []
    
    def discover_kaufland_brochures(self) -> List[Dict[str, str]]:
        """Discover all Kaufland PDF brochures."""
        self.logger.info("Discovering Kaufland brochures...")
        
        if not self.driver:
            self.driver = self._setup_selenium_driver()
        
        try:
            self.driver.get("https://www.kaufland.bg/broshuri.html")
            time.sleep(5)
            
            html = self.driver.page_source
            
            # Find all PDF links in the page
            pdf_pattern = r'https://[^"\'>\s]+\.pdf'
            pdf_urls = list(set(re.findall(pdf_pattern, html)))
            
            brochures = []
            for pdf_url in pdf_urls:
                # Extract brochure name from URL or nearby text
                name = pdf_url.split('/')[-1].replace('.pdf', '').replace('-', ' ')
                brochures.append({
                    'url': pdf_url,
                    'name': name,
                    'type': 'pdf'
                })
            
            self.logger.info(f"Discovered {len(brochures)} PDF brochures")
            return brochures
            
        except Exception as e:
            self.logger.error(f"Error discovering brochures: {e}")
            return []
    
    def download_pdf(self, url: str, save_path: str) -> bool:
        """Download a PDF file."""
        try:
            self.logger.info(f"Downloading PDF: {url}")
            response = self.session.get(url, timeout=REQUEST_TIMEOUT, stream=True)
            response.raise_for_status()
            
            # Create directory if it doesn't exist
            import os
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            # Save PDF
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self.logger.info(f"Downloaded PDF to: {save_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error downloading PDF {url}: {e}")
            return False
    
    def fetch_page(self, url: str) -> Optional[str]:
        """Fetch page content using the configured method."""
        if ENABLE_SELENIUM:
            return self.fetch_page_selenium(url)
        else:
            return self.fetch_page_requests(url)
    
    def fetch_product_page(self, product_url: str) -> Optional[str]:
        """Fetch individual product page content for detailed information."""
        if not product_url:
            return None
        
        self.logger.info(f"Fetching product page: {product_url}")
        
        if ENABLE_SELENIUM:
            return self.fetch_product_page_selenium(product_url)
        else:
            return self.fetch_page_requests(product_url)
    
    def fetch_product_page_selenium(self, product_url: str) -> Optional[str]:
        """Fetch product page content using Selenium with optimized waiting."""
        if not self.driver:
            self.driver = self._setup_selenium_driver()
        
        try:
            self.driver.get(product_url)
            
            # Wait for product details to load
            try:
                # Try to wait for product details to load
                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "product-details"))
                    )
                except TimeoutException:
                    try:
                        WebDriverWait(self.driver, 3).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "product-info"))
                        )
                    except TimeoutException:
                        WebDriverWait(self.driver, 2).until(
                            EC.presence_of_element_located((By.TAG_NAME, "main"))
                        )
            except TimeoutException:
                self.logger.warning("Timeout waiting for product details to load")
            
            # Small delay to ensure all content is loaded
            time.sleep(1)
            
            return self.driver.page_source
            
        except WebDriverException as e:
            self.logger.error(f"Selenium error fetching product page: {e}")
            return None
    
    def close(self):
        """Clean up resources."""
        if self.driver:
            self.driver.quit()
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
