#!/usr/bin/env python3
"""
Качване в релационен модел: shops, products, product_prices (съвместим с API items + prices).
При промяна на цената спрямо предишния запис в product_prices се добавя ред в
product_price_history (за графики в приложението). Изисква миграция
database/add_product_price_history.sql.
"""

import csv
import json
import logging
import math
import os
import re
import sys
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import urlparse

import psycopg2
import psycopg2.errors
from psycopg2.extras import RealDictCursor

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.weight_parse import parse_weight_and_measure

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

KAUFLAND_SHOP_ID = 1


def parse_connection_string(conn_str: str) -> Dict[str, str]:
    parsed = urlparse(conn_str)
    return {
        "host": parsed.hostname,
        "port": parsed.port or 5432,
        "database": parsed.path.lstrip("/"),
        "user": parsed.username,
        "password": parsed.password,
    }


def parse_price_value(price_str: str) -> Optional[float]:
    if not price_str:
        return None
    match = re.search(r"(\d+[.,]\d+|\d+)", str(price_str))
    if match:
        try:
            return float(match.group(1).replace(",", "."))
        except ValueError:
            return None
    return None


def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
    if not timestamp_str:
        return None
    try:
        return datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
    except ValueError:
        return None


def csv_weight_fields(row: Dict[str, Any]) -> Tuple[Optional[float], Optional[str]]:
    raw_w = (row.get("weight") or "").strip()
    if raw_w:
        try:
            w = float(raw_w.replace(",", "."))
            wm = (row.get("weight_measure") or "").strip() or None
            return w, wm
        except ValueError:
            pass
    return parse_weight_and_measure(row.get("weight_unit") or "")


def csv_product_id(row: Dict[str, Any]) -> str:
    """Нов CSV: product_id; стари файлове: само image_id."""
    return (row.get("product_id") or row.get("image_id") or "").strip()


def _same_price_snapshot(
    prev: Tuple[Any, Any, Any],
    price: float,
    promo_price: Optional[float],
    currency: str,
) -> bool:
    """Сравнява текущия ред в product_prices с новите стойности от CSV."""
    p0, p1, p2 = prev
    cur = (currency or "EUR").strip()
    if (p2 or "EUR").strip() != cur:
        return False
    if abs(float(p0) - float(price)) > 1e-6:
        return False
    op = float(p1) if p1 is not None else None
    if op is None and promo_price is None:
        return True
    if op is None or promo_price is None:
        return False
    return abs(op - float(promo_price)) < 1e-6


def csv_row_to_api_prices(row: Dict[str, Any]) -> Tuple[Optional[float], Optional[float], str]:
    """
    price = референтна цена (при промо: старата), promo_price = текуща промо цена.
    """
    current = parse_price_value(row.get("price_value", "") or "")
    old = parse_price_value(row.get("old_price", "") or "") if row.get("old_price") else None
    currency = (row.get("price_currency") or "EUR").strip() or "EUR"
    if current is None:
        return None, None, currency
    if old is not None and old != current:
        return old, current, currency
    return current, None, currency


class RelationalUploader:
    def __init__(self, connection_string: str, record_price_history: bool = True):
        db_config = parse_connection_string(connection_string)
        self.conn = psycopg2.connect(**db_config)
        self.conn.autocommit = False
        self.cursor = self.conn.cursor()
        self.record_price_history = record_price_history
        logger.info("✅ Свързан с базата данни (релационен модел)")

    def upsert_product(self, row: Dict[str, Any]) -> bool:
        pid = csv_product_id(row)
        if not pid:
            return False

        w, wm = csv_weight_fields(row)
        scraped_at = parse_timestamp(row.get("scraped_at", "")) or datetime.now()
        price_per_kg = parse_price_value(row.get("price_per_kg", "") or "")

        self.cursor.execute(
            """
            INSERT INTO products (
                id, title, weight, weight_measure, description, picture, category,
                manufacturer, origin, grade, availability,
                price_per_kg, discount_text,
                price_original_text, weight_unit_raw, source, source_file, scraped_at
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s,
                %s, %s, %s, %s, %s
            )
            ON CONFLICT (id) DO UPDATE SET
                title = EXCLUDED.title,
                weight = EXCLUDED.weight,
                weight_measure = EXCLUDED.weight_measure,
                description = EXCLUDED.description,
                picture = EXCLUDED.picture,
                category = EXCLUDED.category,
                manufacturer = EXCLUDED.manufacturer,
                origin = EXCLUDED.origin,
                grade = EXCLUDED.grade,
                availability = EXCLUDED.availability,
                price_per_kg = EXCLUDED.price_per_kg,
                discount_text = EXCLUDED.discount_text,
                price_original_text = EXCLUDED.price_original_text,
                weight_unit_raw = EXCLUDED.weight_unit_raw,
                source = EXCLUDED.source,
                source_file = EXCLUDED.source_file,
                scraped_at = EXCLUDED.scraped_at
            """,
            (
                pid,
                row.get("name") or "",
                w,
                wm,
                row.get("description") or None,
                row.get("image_url") or None,
                row.get("category") or None,
                row.get("manufacturer") or None,
                row.get("origin") or None,
                row.get("grade") or None,
                row.get("availability") or None,
                price_per_kg,
                row.get("discount") or None,
                row.get("price_original_text") or None,
                row.get("weight_unit") or None,
                row.get("source", "kaufland.bg") or "kaufland.bg",
                row.get("source_file") or None,
                scraped_at,
            ),
        )
        return True

    def upsert_product_price(
        self,
        product_id: str,
        shop_id: int,
        price: float,
        promo_price: Optional[float],
        currency: str,
        observed_at: datetime,
    ) -> None:
        """Обновява текущата цена; при промяна добавя ред в product_price_history (ако е включено)."""
        self.cursor.execute(
            """
            SELECT price, promo_price, currency FROM product_prices
            WHERE product_id = %s AND shop_id = %s
            """,
            (product_id, shop_id),
        )
        prev = self.cursor.fetchone()

        self.cursor.execute(
            """
            INSERT INTO product_prices (product_id, shop_id, price, promo_price, currency)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (product_id, shop_id) DO UPDATE SET
                price = EXCLUDED.price,
                promo_price = EXCLUDED.promo_price,
                currency = EXCLUDED.currency,
                updated_at = now()
            """,
            (product_id, shop_id, price, promo_price, currency),
        )

        if not self.record_price_history:
            return
        if prev is not None and _same_price_snapshot(prev, price, promo_price, currency):
            return

        try:
            self.cursor.execute(
                """
                INSERT INTO product_price_history (
                    product_id, shop_id, observed_at, price, promo_price, currency
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (product_id, shop_id, observed_at, price, promo_price, currency),
            )
        except psycopg2.errors.UndefinedTable:
            logger.warning(
                "Таблица product_price_history липсва — изпълни database/add_product_price_history.sql "
                "или ползвай --skip-price-history"
            )

    def upload_csv(self, csv_file: Path) -> None:
        logger.info(f"📤 Качване (релационно) на {csv_file}")
        imported = 0
        skipped = 0
        errors = 0

        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row_num, row in enumerate(reader, 1):
                try:
                    if not (row.get("name") or "").strip():
                        skipped += 1
                        continue
                    if not (row.get("price_value") or "").strip():
                        skipped += 1
                        continue

                    pid = csv_product_id(row)
                    if not pid:
                        skipped += 1
                        continue

                    price, promo_price, currency = csv_row_to_api_prices(row)
                    if price is None:
                        skipped += 1
                        continue

                    if not self.upsert_product(row):
                        skipped += 1
                        continue

                    observed_at = parse_timestamp(row.get("scraped_at", "")) or datetime.now()
                    self.upsert_product_price(
                        pid, KAUFLAND_SHOP_ID, price, promo_price, currency, observed_at
                    )
                    imported += 1

                    if imported % 100 == 0:
                        self.conn.commit()
                        logger.info(f"  ⏳ Качени {imported} продукта...")

                except Exception as e:
                    logger.error(f"❌ Ред {row_num}: {e}")
                    self.conn.rollback()
                    errors += 1
                    continue

        self.conn.commit()
        logger.info("✅ Готово!")
        logger.info(f"   📊 Качени редове (продукт + цена Kaufland): {imported}")
        logger.info(f"   ⏭️  Пропуснати: {skipped}")
        logger.info(f"   ❌ Грешки: {errors}")

    def close(self) -> None:
        self.cursor.close()
        self.conn.close()
        logger.info("🔌 Връзката е затворена")


def fetch_items_page(connection_string: str, page: int = 1, size: int = 20) -> Dict[str, Any]:
    """
    Връща JSON като API: items, page, size, totalItems, totalPages.
    """
    if page < 1:
        page = 1
    if size < 1:
        size = 20
    offset = (page - 1) * size
    db_config = parse_connection_string(connection_string)
    conn = psycopg2.connect(**db_config)
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT COUNT(*) AS c FROM products")
            total_items = cur.fetchone()["c"]
            total_pages = math.ceil(total_items / size) if total_items else 0

            cur.execute(
                """
                WITH paged AS (
                    SELECT id
                    FROM products
                    ORDER BY id
                    LIMIT %s OFFSET %s
                )
                SELECT
                    p.id,
                    p.title,
                    p.weight,
                    p.weight_measure,
                    p.description,
                    p.picture,
                    p.category,
                    COALESCE(
                        json_agg(
                            json_build_object(
                                'shopId', pp.shop_id,
                                'shopName', s.name,
                                'price', pp.price,
                                'promoPrice', pp.promo_price,
                                'currency', pp.currency
                            )
                            ORDER BY pp.shop_id
                        ) FILTER (WHERE pp.shop_id IS NOT NULL),
                        '[]'::json
                    ) AS prices
                FROM paged
                JOIN products p ON p.id = paged.id
                LEFT JOIN product_prices pp ON pp.product_id = p.id
                LEFT JOIN shops s ON s.id = pp.shop_id
                GROUP BY p.id, p.title, p.weight, p.weight_measure, p.description, p.picture, p.category
                ORDER BY p.id
                """,
                (size, offset),
            )
            rows = cur.fetchall()

        def _num(v: Union[None, float, int, Decimal]) -> Union[None, float]:
            if v is None:
                return None
            if isinstance(v, Decimal):
                return float(v)
            return float(v)

        def _normalize_prices(raw: Union[str, List]) -> List[Dict[str, Any]]:
            if isinstance(raw, str):
                raw = json.loads(raw)
            out = []
            for pr in raw or []:
                out.append(
                    {
                        "shopId": int(pr["shopId"]),
                        "shopName": pr["shopName"],
                        "price": _num(pr.get("price")),
                        "promoPrice": _num(pr.get("promoPrice")) if pr.get("promoPrice") is not None else None,
                        "currency": pr["currency"],
                    }
                )
            return out

        items = []
        for r in rows:
            item = {
                "id": r["id"],
                "title": r["title"],
                "weight": _num(r["weight"]),
                "weightMeasure": r["weight_measure"],
                "description": r["description"] or "",
                "prices": _normalize_prices(r["prices"]),
                "picture": r["picture"] or "",
                "category": r["category"] or "",
            }
            items.append(item)

        return {
            "items": items,
            "page": page,
            "size": size,
            "totalItems": total_items,
            "totalPages": total_pages,
        }
    finally:
        conn.close()


def main():
    import argparse

    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent / ".env")

    p = argparse.ArgumentParser(description="Качване в shops / products / product_prices")
    p.add_argument("csv_file", nargs="?", help="CSV от скрапера")
    p.add_argument(
        "--connection-string",
        default=os.environ.get("DATABASE_URL", ""),
    )
    p.add_argument("--sample-page", type=int, metavar="PAGE", help="Само изведи JSON страница от БД (без upload)")
    p.add_argument("--sample-size", type=int, default=3, help="Размер на страницата за --sample-page")
    p.add_argument(
        "--skip-price-history",
        action="store_true",
        help="Без запис в product_price_history (само текуща цена в product_prices)",
    )

    args = p.parse_args()

    if not args.connection_string:
        p.error("Задай DATABASE_URL в .env или подай --connection-string (виж .env.example)")

    if args.sample_page is not None:
        out = fetch_items_page(args.connection_string, page=args.sample_page, size=args.sample_size)
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return

    if not args.csv_file:
        p.error("Подай csv_file или --sample-page")

    up = RelationalUploader(
        args.connection_string,
        record_price_history=not args.skip_price_history,
    )
    try:
        up.upload_csv(Path(args.csv_file))
    finally:
        up.close()


if __name__ == "__main__":
    main()
