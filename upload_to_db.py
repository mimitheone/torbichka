#!/usr/bin/env python3
"""
Кратък модул за качване на данни в Supabase PostgreSQL база данни.
"""

import csv
import re
import psycopg2
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def parse_connection_string(conn_str: str) -> Dict[str, str]:
    """Парсва PostgreSQL connection string."""
    # Формат: postgresql://user:password@host:port/database
    parsed = urlparse(conn_str)
    
    return {
        'host': parsed.hostname,
        'port': parsed.port or 5432,
        'database': parsed.path.lstrip('/'),
        'user': parsed.username,
        'password': parsed.password
    }


def normalize_product_name(name: str) -> str:
    """Нормализира име на продукт за търсене."""
    if not name:
        return ""
    normalized = name.lower()
    normalized = re.sub(r'\s+', ' ', normalized)
    normalized = re.sub(r'[^\w\s-]', '', normalized)
    return normalized.strip()


def parse_price_value(price_str: str) -> Optional[float]:
    """Парсва цена от стринг."""
    if not price_str:
        return None
    # Извлича число от стринг като "27.49" или "27,49"
    match = re.search(r'(\d+[.,]\d+)', str(price_str))
    if match:
        try:
            return float(match.group(1).replace(',', '.'))
        except ValueError:
            return None
    return None


def parse_discount_percentage(discount_str: str) -> Optional[int]:
    """Извлича процент отстъпка от стринг като '-35%'."""
    if not discount_str:
        return None
    match = re.search(r'-?(\d+)\s*%', str(discount_str))
    if match:
        return -int(match.group(1))
    return None


class SupabaseUploader:
    """Клас за качване на данни в Supabase."""
    
    def __init__(self, connection_string: str):
        """Инициализира връзка с базата данни."""
        db_config = parse_connection_string(connection_string)
        self.conn = psycopg2.connect(**db_config)
        self.conn.autocommit = False
        self.cursor = self.conn.cursor()
        logger.info("✅ Свързан с базата данни")
    
    def ensure_store(self, store_name: str = 'kaufland', display_name: str = 'Kaufland') -> int:
        """Осигурява че магазинът съществува, връща store_id."""
        self.cursor.execute("SELECT id FROM stores WHERE name = %s", (store_name,))
        result = self.cursor.fetchone()
        
        if result:
            return result[0]
        
        self.cursor.execute(
            """
            INSERT INTO stores (name, display_name, website_url)
            VALUES (%s, %s, %s)
            RETURNING id
            """,
            (store_name, display_name, 'https://www.kaufland.bg')
        )
        store_id = self.cursor.fetchone()[0]
        self.conn.commit()
        logger.info(f"✅ Създаден магазин: {display_name} (ID: {store_id})")
        return store_id
    
    def find_or_create_product(self, row: Dict[str, Any]) -> int:
        """Намира или създава продукт, връща product_id."""
        name = row.get('name', '').strip()
        weight_unit = row.get('weight_unit', '').strip() or None
        normalized_name = normalize_product_name(name)
        
        # Търси съществуващ продукт
        self.cursor.execute(
            """
            SELECT id FROM products 
            WHERE normalized_name = %s AND (weight_unit = %s OR (%s IS NULL AND weight_unit IS NULL))
            """,
            (normalized_name, weight_unit, weight_unit)
        )
        result = self.cursor.fetchone()
        
        if result:
            product_id = result[0]
            # Обновява информацията за продукта
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
                    row.get('description') or None,
                    row.get('manufacturer') or None,
                    row.get('category') or None,
                    row.get('origin') or None,
                    row.get('grade') or None,
                    row.get('image_url') or None,
                    product_id
                )
            )
            return product_id
        
        # Създава нов продукт
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
                row.get('description') or None,
                row.get('manufacturer') or None,
                row.get('category') or None,
                weight_unit,
                row.get('origin') or None,
                row.get('grade') or None,
                row.get('image_url') or None
            )
        )
        return self.cursor.fetchone()[0]
    
    def insert_price(self, product_id: int, store_id: int, row: Dict[str, Any]):
        """Вмъква цена за продукт."""
        price_value = parse_price_value(row.get('price_value', ''))
        if not price_value:
            return
        
        # Парсва стара цена
        old_price_value = None
        old_price_str = row.get('old_price', '')
        if old_price_str:
            old_price_value = parse_price_value(old_price_str)
        
        # Парсва отстъпка
        discount_percentage = parse_discount_percentage(row.get('discount', ''))
        discount_text = row.get('discount', '') or None
        
        # Парсва цена на кг
        price_per_kg = None
        if row.get('price_per_kg'):
            price_per_kg = parse_price_value(str(row.get('price_per_kg')))
        
        # Парсва scraped_at
        scraped_at = datetime.now()
        if row.get('scraped_at'):
            try:
                scraped_at = datetime.fromisoformat(
                    row['scraped_at'].replace('Z', '+00:00')
                )
            except:
                pass
        
        # Маркира старите цени като неактивни
        self.cursor.execute(
            """
            UPDATE product_prices 
            SET is_active = FALSE 
            WHERE product_id = %s AND store_id = %s
            """,
            (product_id, store_id)
        )
        
        # Вмъква нова цена
        try:
            self.cursor.execute(
                """
                INSERT INTO product_prices (
                    product_id, store_id, price_value, price_currency,
                    old_price_value, price_per_kg, discount_percentage,
                    discount_text,
                    availability, source_file, scraped_at, is_active
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)
                """,
                (
                    product_id,
                    store_id,
                    price_value,
                    row.get('price_currency', 'BGN'),
                    old_price_value,
                    price_per_kg,
                    discount_percentage,
                    discount_text,
                    row.get('availability', 'Неизвестно') or 'Неизвестно',
                    row.get('source_file') or None,
                    scraped_at
                )
            )
        except psycopg2.IntegrityError as e:
            logger.warning(f"Цената вече съществува за продукт {product_id}: {e}")
            self.conn.rollback()
    
    def upload_csv(self, csv_file: Path, store_name: str = 'kaufland', display_name: str = 'Kaufland'):
        """Качва CSV файл в базата данни."""
        logger.info(f"📤 Започва качване на {csv_file}")
        
        # Осигурява магазин
        store_id = self.ensure_store(store_name, display_name)
        
        imported = 0
        skipped = 0
        errors = 0
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row_num, row in enumerate(reader, 1):
                try:
                    # Пропуска ако няма цена
                    if not row.get('price_value') or not str(row.get('price_value', '')).strip():
                        skipped += 1
                        continue
                    
                    # Намира или създава продукт
                    product_id = self.find_or_create_product(row)
                    
                    # Вмъква цена
                    self.insert_price(product_id, store_id, row)
                    
                    imported += 1
                    
                    # Commit на всеки 100 записа
                    if imported % 100 == 0:
                        self.conn.commit()
                        logger.info(f"  ⏳ Качени {imported} продукта...")
                
                except Exception as e:
                    logger.error(f"❌ Грешка при ред {row_num}: {e}")
                    self.conn.rollback()
                    errors += 1
                    continue
        
        # Финален commit
        self.conn.commit()
        
        logger.info("✅ Качването завърши!")
        logger.info(f"   📊 Качени: {imported}")
        logger.info(f"   ⏭️  Пропуснати: {skipped}")
        logger.info(f"   ❌ Грешки: {errors}")
    
    def close(self):
        """Затваря връзката с базата данни."""
        self.cursor.close()
        self.conn.close()
        logger.info("🔌 Връзката е затворена")


def main():
    """Главна функция за използване от командния ред."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Качване на данни в Supabase')
    parser.add_argument('csv_file', help='Път до CSV файл')
    parser.add_argument(
        '--connection-string',
        default='postgresql://postgres:[YOUR-PASSWORD]@db.egokkwvfzvdbbkyotgjx.supabase.co:5432/postgres',
        help='PostgreSQL connection string'
    )
    parser.add_argument('--store-name', default='kaufland', help='Име на магазина')
    parser.add_argument('--store-display-name', default='Kaufland', help='Показвано име на магазина')
    
    args = parser.parse_args()
    
    uploader = SupabaseUploader(args.connection_string)
    
    try:
        uploader.upload_csv(
            Path(args.csv_file),
            store_name=args.store_name,
            display_name=args.store_display_name
        )
    finally:
        uploader.close()


if __name__ == '__main__':
    main()

