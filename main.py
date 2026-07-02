#!/usr/bin/env python3
"""Kaufland Bulgaria scraper — Flask HTTP service with /run crawler endpoint."""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List

from flask import Flask, jsonify

sys.path.append(str(Path(__file__).parent / "src"))

from config.settings import MAX_PRODUCTS
from src.data_saver import DataSaver
from src.logger import setup_logging
from src.parser import KauflandParser
from src.scraper import KauflandScraper

OFFERS_URL = os.environ.get(
    "SCRAPE_URL",
    "https://www.kaufland.bg/aktualni-predlozheniya/oferti.html",
)

app = Flask(__name__)


def run_crawler() -> Dict[str, Any]:
    """Скрейпва актуалните оферти, валидира и записва CSV (+ JSON)."""
    logger = setup_logging()
    max_products = int(os.environ.get("MAX_PRODUCTS", MAX_PRODUCTS))
    scraper = KauflandScraper()
    saved_files: List[str] = []

    try:
        logger.info("Fetching %s", OFFERS_URL)
        html_content = scraper.fetch_page(OFFERS_URL)
        if not html_content:
            raise RuntimeError("Failed to fetch webpage content")

        parser_instance = KauflandParser()
        products = parser_instance.parse_products(html_content)
        if not products:
            raise RuntimeError("No products found in the webpage")

        if max_products and len(products) > max_products:
            products = products[:max_products]

        validated = parser_instance.validate_product_data(products)
        if not validated:
            raise RuntimeError("No valid products after validation")

        data_saver = DataSaver()
        saved_files.append(data_saver.save_to_json(validated))
        saved_files.append(data_saver.save_to_csv(validated))
        saved_files.append(data_saver.save_summary_report(validated))

        logger.info("Scraped %s products", len(validated))
        return {
            "products": len(validated),
            "files": saved_files,
        }
    finally:
        try:
            scraper.close()
        except Exception:
            pass


@app.get("/")
def health():
    return "OK", 200


@app.get("/run")
def run_crawler_endpoint():
    try:
        result = run_crawler()
        return jsonify({"status": "ok", **result}), 200
    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
