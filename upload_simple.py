#!/usr/bin/env python3
"""
Прост модул за качване на данни в Supabase - само таблица products.
"""

import csv
import re
import psycopg2
from urllib.parse import urlparse
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def parse_connection_string(conn_str: str) -> Dict[str, str]:
    """Парсва PostgreSQL connection string."""
    parsed = urlparse(conn_str)
    return {
        'host': parsed.hostname,
        'port': parsed.port or 5432,
        'database': parsed.path.lstrip('/'),
        'user': parsed.username,
        'password': parsed.password
    }


def parse_price_value(price_str: str) -> Optional[float]:
    """Парсва цена от стринг."""
    if not price_str:
        return None
    match = re.search(r'(\d+[.,]\d+)', str(price_str))
    if match:
        try:
            return float(match.group(1).replace(',', '.'))
        except ValueError:
            return None
    return None


def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
    """Парсва timestamp."""
    if not timestamp_str:
        return None
    try:
        return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    except:
        return None


class SimpleUploader:
    """Клас за качване на данни в простата products таблица."""
    
    def __init__(self, connection_string: str):
        """Инициализира връзка с базата данни."""
        db_config = parse_connection_string(connection_string)
        self.conn = psycopg2.connect(**db_config)
        self.conn.autocommit = False
        self.cursor = self.conn.cursor()
        logger.info("✅ Свързан с базата данни")
    
    def insert_product(self, row: Dict[str, Any]):
        """Вмъква продукт в таблицата."""
        # Парсва цени
        price_value = parse_price_value(row.get('price_value', ''))
        old_price = parse_price_value(row.get('old_price', '')) if row.get('old_price') else None
        price_per_kg = parse_price_value(row.get('price_per_kg', '')) if row.get('price_per_kg') else None
        
        # Парсва timestamp
        scraped_at = parse_timestamp(row.get('scraped_at', ''))
        if not scraped_at:
            scraped_at = datetime.now()
        
        # product_id (нов формат) или image_id (стари CSV) – primary key в колоната image_id
        image_id = (row.get('product_id') or row.get('image_id') or '').strip()
        if not image_id:
            return False

        # Вмъква или обновява продукт (при дубликат image_id от различни HTML файлове)
        self.cursor.execute(
            """
            INSERT INTO products (
                image_id, name, manufacturer, weight_unit, category, origin, grade,
                price_value, price_currency, old_price,
                price_per_kg, discount,
                description, availability, price_original_text,
                image_url, source, source_file, scraped_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (image_id) DO UPDATE SET
                name = EXCLUDED.name,
                manufacturer = EXCLUDED.manufacturer,
                weight_unit = EXCLUDED.weight_unit,
                category = EXCLUDED.category,
                origin = EXCLUDED.origin,
                grade = EXCLUDED.grade,
                price_value = EXCLUDED.price_value,
                price_currency = EXCLUDED.price_currency,
                old_price = EXCLUDED.old_price,
                price_per_kg = EXCLUDED.price_per_kg,
                discount = EXCLUDED.discount,
                description = EXCLUDED.description,
                availability = EXCLUDED.availability,
                price_original_text = EXCLUDED.price_original_text,
                image_url = EXCLUDED.image_url,
                source = EXCLUDED.source,
                source_file = EXCLUDED.source_file,
                scraped_at = EXCLUDED.scraped_at
            """,
            (
                image_id,
                row.get('name') or None,
                row.get('manufacturer') or None,
                row.get('weight_unit') or None,
                row.get('category') or None,
                row.get('origin') or None,
                row.get('grade') or None,
                price_value,
                row.get('price_currency', 'EUR') or 'EUR',
                old_price,
                price_per_kg,
                row.get('discount') or None,
                row.get('description') or None,
                row.get('availability') or None,
                row.get('price_original_text') or None,
                row.get('image_url') or None,
                row.get('source', 'kaufland.bg') or 'kaufland.bg',
                row.get('source_file') or None,
                scraped_at
            )
        )
        return True
    
    def upload_csv(self, csv_file: Path):
        """Качва CSV файл в базата данни."""
        logger.info(f"📤 Започва качване на {csv_file}")
        
        imported = 0
        skipped = 0
        errors = 0
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row_num, row in enumerate(reader, 1):
                try:
                    # Пропуска ако няма име или цена
                    if not row.get('name') or not row.get('name').strip():
                        skipped += 1
                        continue
                    
                    if not row.get('price_value') or not str(row.get('price_value', '')).strip():
                        skipped += 1
                        continue
                    
                    # Вмъква продукт (пропуска ако няма image_id – primary key)
                    if not self.insert_product(row):
                        skipped += 1
                        continue
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
    import os

    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent / ".env")

    parser = argparse.ArgumentParser(description='Качване на данни в Supabase - проста таблица products')
    parser.add_argument('csv_file', help='Път до CSV файл')
    parser.add_argument(
        '--connection-string',
        default=os.environ.get('DATABASE_URL', ''),
        help='PostgreSQL connection string (или DATABASE_URL в .env)',
    )

    args = parser.parse_args()

    if not args.connection_string:
        parser.error('Задай DATABASE_URL в .env или --connection-string (виж .env.example)')

    uploader = SimpleUploader(args.connection_string)
    
    try:
        uploader.upload_csv(Path(args.csv_file))
    finally:
        uploader.close()


if __name__ == '__main__':
    main()

