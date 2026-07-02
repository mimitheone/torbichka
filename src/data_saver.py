"""Data saving module for storing scraped product data."""

import json
import csv
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from config.settings import OUTPUT_DIR, OUTPUT_FILENAME
from src.weight_parse import parse_weight_and_measure


class DataSaver:
    """Class for saving scraped product data in various formats."""
    
    def __init__(self, output_dir: str = OUTPUT_DIR):
        self.output_dir = Path(output_dir)
        self.logger = logging.getLogger(__name__)
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _add_timestamp_to_products(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add timestamp to each product."""
        timestamp = datetime.now().isoformat()
        
        for product in products:
            product['scraped_at'] = timestamp
        
        return products
    
    def save_to_json(self, products: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
        """Save products to JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"kaufland_bg_products_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        try:
            # Add timestamps to products
            products_with_timestamp = self._add_timestamp_to_products(products.copy())
            
            # Create metadata
            metadata = {
                "scrape_info": {
                    "timestamp": datetime.now().isoformat(),
                    "total_products": len(products_with_timestamp),
                    "source": "metro.bg",
                    "scraper_version": "1.0.0"
                },
                "products": products_with_timestamp
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Saved {len(products)} products to {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Error saving to JSON: {e}")
            raise
    
    def save_to_csv(self, products: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
        """Save products to CSV file."""
        if not products:
            self.logger.warning("No products to save to CSV")
            return ""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"kaufland_bg_products_{timestamp}.csv"
        
        filepath = self.output_dir / filename
        
        try:
            # Add timestamps to products
            products_with_timestamp = self._add_timestamp_to_products(products.copy())
            
            # Flatten product data for CSV
            flattened_products = []
            for product in products_with_timestamp:
                # Extract old price from discount info
                old_price = ''
                if product.get('discount') and isinstance(product['discount'], dict):
                    old_price_info = product['discount'].get('old_price')
                    if old_price_info and isinstance(old_price_info, dict):
                        old_price_value = old_price_info.get('value', '')
                        old_price_currency = old_price_info.get('currency', '')
                        if old_price_value:
                            old_price = f"{old_price_value} {old_price_currency}"
                
                w_val, w_meas = parse_weight_and_measure(product.get('weight_unit', '') or '')
                flat_product = {
                    'product_id': product.get('product_id', '') or '',         # kaufland_bg:klNr:image_slug — ключ за база
                    'kl_nr': product.get('kl_nr', '') or '',
                    'offer_id': product.get('offer_id', '') or '',
                    'image_id': product.get('image_id', ''),                   # slug от снимката (не е глобално уникален)
                    'name': product.get('name', ''),                           # Име (= API title)
                    'manufacturer': product.get('manufacturer', ''),           # Производител
                    'weight_unit': product.get('weight_unit', ''),             # Грамаж/бройка (суров текст)
                    'weight': w_val if w_val is not None else '',             # API weight (число)
                    'weight_measure': w_meas or '',                           # API weightMeasure
                    'category': product.get('category', ''),                   # тип/вид/под категория
                    'origin': product.get('origin', ''),                       # Произход
                    'grade': product.get('grade', ''),                         # Сорт
                    'price_value': product.get('price', {}).get('value', '') if product.get('price') else '',  # Цена
                    'price_currency': product.get('price_currency', 'EUR'),       # Валута
                    'old_price': old_price,                                    # Стара цена преди отстъпката
                    'price_per_kg': product.get('price_per_kg', ''),           # Цена на килограм
                    'discount': product.get('discount', {}).get('text', '') if product.get('discount') else '',  # Отстъпка
                    'description': product.get('description', ''),             # Описание
                    'availability': product.get('availability', ''),           # Налично/неналично
                    'price_original_text': product.get('price', {}).get('original_text', '') if product.get('price') else '',
                    'image_url': product.get('image_url', ''),
                    'product_url': product.get('product_url', '') or '',
                    'source': product.get('source', ''),
                    'source_file': product.get('source_file', ''),             # От кой HTML файл
                    'scraped_at': product.get('scraped_at', '')
                }
                flattened_products.append(flat_product)
            
            # Write to CSV
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                if flattened_products:
                    fieldnames = flattened_products[0].keys()
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(flattened_products)
            
            self.logger.info(f"Saved {len(products)} products to {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Error saving to CSV: {e}")
            raise
    
    def save_summary_report(self, products: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
        """Save a summary report of the scraped data."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scraping_report_{timestamp}.txt"
        
        filepath = self.output_dir / filename
        
        try:
            total_products = len(products)
            products_with_prices = len([p for p in products if p.get('price')])
            products_with_images = len([p for p in products if p.get('image_url')])
            products_with_descriptions = len([p for p in products if p.get('description')])
            
            # Calculate price statistics
            prices = [p['price']['value'] for p in products if p.get('price') and p['price'].get('value')]
            price_stats = {}
            if prices:
                price_stats = {
                    'min_price': min(prices),
                    'max_price': max(prices),
                    'avg_price': sum(prices) / len(prices),
                    'median_price': sorted(prices)[len(prices) // 2]
                }
            
            report_content = f"""Kaufland Bulgaria Scraping Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

SUMMARY:
========
Total products scraped: {total_products}
Products with prices: {products_with_prices} ({products_with_prices/total_products*100:.1f}%)
Products with images: {products_with_images} ({products_with_images/total_products*100:.1f}%)
Products with descriptions: {products_with_descriptions} ({products_with_descriptions/total_products*100:.1f}%)

PRICE STATISTICS:
================
"""
            
            if price_stats:
                report_content += f"""Minimum price: {price_stats['min_price']:.2f} EUR
Maximum price: {price_stats['max_price']:.2f} EUR
Average price: {price_stats['avg_price']:.2f} EUR
Median price: {price_stats['median_price']:.2f} EUR
"""
            else:
                report_content += "No price data available\n"
            
            report_content += f"""
SAMPLE PRODUCTS:
===============
"""
            
            # Add sample products
            for i, product in enumerate(products[:5]):
                report_content += f"""
Product {i+1}:
  Name: {product.get('name', 'N/A')}
  Price: {product.get('price', {}).get('value', 'N/A')} {product.get('price', {}).get('currency', '')}
  URL: {product.get('product_url', 'N/A')}
"""
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            self.logger.info(f"Saved summary report to {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Error saving summary report: {e}")
            raise
    
    def load_previous_data(self, filename: str) -> List[Dict[str, Any]]:
        """Load previously saved product data."""
        filepath = self.output_dir / filename
        
        if not filepath.exists():
            self.logger.warning(f"File {filepath} does not exist")
            return []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle both old format (list) and new format (dict with metadata)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'products' in data:
                return data['products']
            else:
                self.logger.warning(f"Unexpected data format in {filepath}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error loading data from {filepath}: {e}")
            return []
