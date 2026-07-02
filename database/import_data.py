#!/usr/bin/env python3
"""
Import Kaufland CSV data into PostgreSQL database
"""

import csv
import re
import psycopg2
from psycopg2.extras import execute_values
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseImporter:
    """Import scraped data into PostgreSQL database."""
    
    def __init__(self, db_config: Dict[str, str]):
        """
        Initialize database connection.
        
        db_config should contain:
        - host
        - port
        - database
        - user
        - password
        """
        self.conn = psycopg2.connect(**db_config)
        self.conn.autocommit = False
        self.cursor = self.conn.cursor()
    
    def normalize_product_name(self, name: str) -> str:
        """Normalize product name for matching across stores."""
        if not name:
            return ""
        
        # Lowercase
        normalized = name.lower()
        
        # Remove extra spaces
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Remove special characters but keep important ones
        normalized = re.sub(r'[^\w\s-]', '', normalized)
        
        return normalized.strip()
    
    def ensure_store(self, store_name: str, display_name: Optional[str] = None) -> int:
        """Ensure store exists, return store ID."""
        if not display_name:
            display_name = store_name.capitalize()
        
        # Check if exists
        self.cursor.execute(
            "SELECT id FROM stores WHERE name = %s",
            (store_name,)
        )
        result = self.cursor.fetchone()
        
        if result:
            return result[0]
        
        # Create new store
        self.cursor.execute(
            """
            INSERT INTO stores (name, display_name, website_url)
            VALUES (%s, %s, %s)
            RETURNING id
            """,
            (store_name, display_name, f"https://www.{store_name}.bg")
        )
        return self.cursor.fetchone()[0]
    
    def find_or_create_product(self, product_data: Dict[str, Any]) -> int:
        """Find or create product, return product ID."""
        name = product_data.get('name', '')
        weight_unit = product_data.get('weight_unit', '')
        normalized_name = self.normalize_product_name(name)
        
        # Try to find existing product
        self.cursor.execute(
            """
            SELECT id FROM products 
            WHERE normalized_name = %s AND weight_unit = %s
            """,
            (normalized_name, weight_unit)
        )
        result = self.cursor.fetchone()
        
        if result:
            product_id = result[0]
            # Update product info if needed
            self.cursor.execute(
                """
                UPDATE products 
                SET name = %s, description = %s, manufacturer = %s,
                    category = %s, origin = %s, grade = %s,
                    image_url = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (
                    name,
                    product_data.get('description'),
                    product_data.get('manufacturer'),
                    product_data.get('category'),
                    product_data.get('origin'),
                    product_data.get('grade'),
                    product_data.get('image_url'),
                    product_id
                )
            )
            return product_id
        
        # Create new product
        self.cursor.execute(
            """
            INSERT INTO products (
                name, normalized_name, description, manufacturer,
                category, weight_unit, origin, grade, image_url
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                name,
                normalized_name,
                product_data.get('description'),
                product_data.get('manufacturer'),
                product_data.get('category'),
                weight_unit,
                product_data.get('origin'),
                product_data.get('grade'),
                product_data.get('image_url')
            )
        )
        return self.cursor.fetchone()[0]
    
    def parse_discount_percentage(self, discount_text: str) -> Optional[int]:
        """Extract discount percentage from text like '-35%'."""
        if not discount_text:
            return None
        
        match = re.search(r'-?(\d+)\s*%', discount_text)
        if match:
            return -int(match.group(1))  # Negative value for discount
        
        return None
    
    def insert_product_price(self, product_id: int, store_id: int, price_data: Dict[str, Any]):
        """Insert or update product price."""
        # Parse scraped_at
        scraped_at_str = price_data.get('scraped_at', '')
        if scraped_at_str:
            try:
                scraped_at = datetime.fromisoformat(scraped_at_str.replace('Z', '+00:00'))
            except:
                scraped_at = datetime.now()
        else:
            scraped_at = datetime.now()
        
        # Parse discount
        discount_percentage = self.parse_discount_percentage(
            price_data.get('discount', '')
        )
        
        # Parse old price
        old_price_value = None
        if price_data.get('old_price'):
            old_price_match = re.search(r'(\d+[.,]\d+)', price_data['old_price'])
            if old_price_match:
                try:
                    old_price_value = float(old_price_match.group(1).replace(',', '.'))
                except:
                    pass
        
        # Mark old prices as inactive first (for this product-store combo)
        self.cursor.execute(
            "UPDATE product_prices SET is_active = FALSE WHERE product_id = %s AND store_id = %s",
            (product_id, store_id)
        )
        
        # Insert new price
        try:
            self.cursor.execute(
                """
                INSERT INTO product_prices (
                    product_id, store_id, price_value, price_currency,
                    old_price_value, price_per_kg,
                    discount_percentage, discount_text, availability,
                    source_file, scraped_at, is_active
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)
                """,
                (
                    product_id,
                    store_id,
                    price_data.get('price_value'),
                    price_data.get('price_currency', 'BGN'),
                    old_price_value,
                    price_data.get('price_per_kg'),
                    discount_percentage,
                    price_data.get('discount'),
                    price_data.get('availability', 'Неизвестно'),
                    price_data.get('source_file'),
                    scraped_at
                )
            )
        except psycopg2.IntegrityError:
            # Price already exists for this timestamp, skip
            logger.warning(f"Price already exists for product {product_id} at store {store_id}")
            self.conn.rollback()
            self.cursor.execute(
                "UPDATE product_prices SET is_active = FALSE WHERE product_id = %s AND store_id = %s",
                (product_id, store_id)
            )
    
    def import_csv(self, csv_file: Path, store_name: str = 'kaufland', display_name: str = 'Kaufland'):
        """Import products from CSV file."""
        logger.info(f"Importing data from {csv_file}")
        
        # Ensure store exists
        store_id = self.ensure_store(store_name, display_name)
        logger.info(f"Store ID: {store_id}")
        
        imported_count = 0
        skipped_count = 0
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row_num, row in enumerate(reader, 1):
                try:
                    # Skip if no price
                    if not row.get('price_value') or not row['price_value'].strip():
                        skipped_count += 1
                        continue
                    
                    # Find or create product
                    product_id = self.find_or_create_product(row)
                    
                    # Insert price
                    self.insert_product_price(product_id, store_id, row)
                    
                    imported_count += 1
                    
                    # Commit every 100 records
                    if imported_count % 100 == 0:
                        self.conn.commit()
                        logger.info(f"Imported {imported_count} products...")
                
                except Exception as e:
                    logger.error(f"Error importing row {row_num}: {e}")
                    self.conn.rollback()
                    skipped_count += 1
                    continue
        
        # Final commit
        self.conn.commit()
        
        logger.info(f"✅ Import completed!")
        logger.info(f"   Imported: {imported_count}")
        logger.info(f"   Skipped: {skipped_count}")
    
    def close(self):
        """Close database connection."""
        self.cursor.close()
        self.conn.close()


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Import Kaufland CSV to PostgreSQL')
    parser.add_argument('csv_file', help='Path to CSV file')
    parser.add_argument('--host', default='localhost', help='Database host')
    parser.add_argument('--port', type=int, default=5432, help='Database port')
    parser.add_argument('--database', required=True, help='Database name')
    parser.add_argument('--user', required=True, help='Database user')
    parser.add_argument('--password', required=True, help='Database password')
    parser.add_argument('--store-name', default='kaufland', help='Store identifier')
    parser.add_argument('--store-display-name', default='Kaufland', help='Store display name')
    
    args = parser.parse_args()
    
    db_config = {
        'host': args.host,
        'port': args.port,
        'database': args.database,
        'user': args.user,
        'password': args.password
    }
    
    importer = DatabaseImporter(db_config)
    
    try:
        importer.import_csv(
            Path(args.csv_file),
            store_name=args.store_name,
            display_name=args.store_display_name
        )
    finally:
        importer.close()


if __name__ == '__main__':
    main()

