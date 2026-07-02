"""PDF parser module for extracting product data from Kaufland brochures."""

import re
import logging
from typing import List, Dict, Any, Optional
import pdfplumber
from pathlib import Path


class KauflandPDFParser:
    """Parser class for Kaufland PDF brochures."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text.strip())
    
    def _extract_price(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract price information from text."""
        if not text:
            return None
        
        # Price patterns for Bulgarian
        price_patterns = [
            r'(\d+[.,]\d{2})\s*(?:лв|BGN)',  # 12.99 лв
            r'(\d+)\s*(?:лв|BGN)',  # 12 лв
            r'(\d+[.,]\d{2})',  # Just numbers
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    price_str = match.group(1).replace(',', '.')
                    price_value = float(price_str)
                    
                    return {
                        "value": price_value,
                        "currency": "BGN",
                        "original_text": text.strip()
                    }
                except ValueError:
                    continue
        
        return None
    
    def _extract_discount(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract discount information from text."""
        discount_patterns = [
            r'(?:отстъпка|намаление|промо|promo)\s*[:-]?\s*(\d+)\s*%',  # отстъпка 20%
            r'(\d+)\s*%\s*(?:отстъпка|намаление)',  # 20% отстъпка
            r'[-−]\s*(\d+[.,]?\d*)\s*(?:лв|BGN)',  # - 5.50 лв
        ]
        
        for pattern in discount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return {
                    "text": self._clean_text(text),
                    "value": match.group(1)
                }
        
        return None
    
    def _extract_weight(self, text: str) -> Optional[str]:
        """Extract weight/quantity from text."""
        weight_patterns = [
            r'(\d+[.,]?\d*\s*(?:кг|kg))',
            r'(\d+[.,]?\d*\s*г)',
            r'(\d+[.,]?\d*\s*(?:л|l))',
            r'(\d+[.,]?\d*\s*мл)',
            r'(\d+\s*(?:бр|броя|x))',
        ]
        
        for pattern in weight_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def parse_pdf_page(self, pdf_page) -> List[Dict[str, Any]]:
        """Extract products from a single PDF page."""
        products = []
        
        try:
            # Extract text from the page
            text = pdf_page.extract_text()
            if not text:
                return products
            
            # Split into lines and blocks
            lines = text.split('\n')
            
            current_product = None
            for line in lines:
                line = self._clean_text(line)
                if not line or len(line) < 3:
                    continue
                
                # Check if this line contains a price (likely a product)
                price = self._extract_price(line)
                if price:
                    # If we have a current product, save it
                    if current_product and current_product.get('name'):
                        products.append(current_product)
                    
                    # Start a new product
                    current_product = {
                        'name': None,
                        'price': price,
                        'weight_unit': self._extract_weight(line),
                        'discount': self._extract_discount(line),
                        'manufacturer': None,
                        'category': None,
                        'origin': None,
                        'grade': None,
                        'description': None,
                        'availability': 'Налично',  # Assume available if in brochure
                        'price_currency': 'BGN',
                        'image_url': None,
                        'source': 'kaufland.bg',
                        'scraped_at': None
                    }
                    
                    # Try to extract product name from the same line
                    # Usually format is: "Product Name  12.99 лв"
                    name_part = re.sub(r'\d+[.,]\d{2}\s*(?:лв|BGN).*$', '', line).strip()
                    if name_part and len(name_part) > 3:
                        current_product['name'] = name_part
                
                elif current_product and not current_product.get('name'):
                    # This might be the product name on a separate line
                    if len(line) > 5 and not line.isdigit():
                        current_product['name'] = line
                
                elif current_product:
                    # Additional info for current product
                    if not current_product.get('description'):
                        current_product['description'] = line
                    else:
                        current_product['description'] += ' ' + line
            
            # Don't forget the last product
            if current_product and current_product.get('name'):
                products.append(current_product)
        
        except Exception as e:
            self.logger.error(f"Error parsing PDF page: {e}")
        
        return products
    
    def parse_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract all products from a PDF brochure."""
        self.logger.info(f"Parsing PDF: {pdf_path}")
        all_products = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                self.logger.info(f"PDF has {len(pdf.pages)} pages")
                
                for page_num, page in enumerate(pdf.pages, 1):
                    self.logger.debug(f"Processing page {page_num}/{len(pdf.pages)}")
                    products = self.parse_pdf_page(page)
                    
                    if products:
                        self.logger.info(f"Found {len(products)} products on page {page_num}")
                        all_products.extend(products)
        
        except Exception as e:
            self.logger.error(f"Error parsing PDF {pdf_path}: {e}")
        
        self.logger.info(f"Total products extracted from PDF: {len(all_products)}")
        return all_products
    
    def validate_products(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate and clean extracted products."""
        valid_products = []
        
        for product in products:
            # Must have at least a name or price
            if not product.get('name') and not product.get('price'):
                continue
            
            # Clean up description
            if product.get('description'):
                desc = product['description']
                if len(desc) > 200:  # Limit description length
                    product['description'] = desc[:200] + '...'
            
            valid_products.append(product)
        
        self.logger.info(f"Validated {len(valid_products)} out of {len(products)} products")
        return valid_products



