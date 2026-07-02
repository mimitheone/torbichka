#!/usr/bin/env python3
"""
Quick test script for Kaufland PDF scraper
"""

import sys
from pathlib import Path
import os

sys.path.append(str(Path(__file__).parent / "src"))

from src.scraper import KauflandScraper
from src.pdf_parser import KauflandPDFParser
from src.data_saver import DataSaver
from src.logger import setup_logging
from config.settings import PDF_DIR

def main():
    """Test Kaufland PDF scraper."""
    logger = setup_logging(log_level="INFO")
    logger.info("=" * 70)
    logger.info("KAUFLAND BULGARIA PDF BROCHURE SCRAPER")
    logger.info("=" * 70)
    
    try:
        # Initialize components
        scraper = KauflandScraper()
        pdf_parser = KauflandPDFParser()
        data_saver = DataSaver()
        
        # Discover brochures
        logger.info("Discovering Kaufland PDF brochures...")
        brochures = scraper.discover_kaufland_brochures()
        
        if not brochures:
            logger.error("No brochures found!")
            return 1
        
        logger.info(f"Found {len(brochures)} brochures")
        
        all_products = []
        
        # Download and parse each PDF
        for i, brochure in enumerate(brochures, 1):
            logger.info(f"\n{'='*70}")
            logger.info(f"Processing brochure {i}/{len(brochures)}: {brochure['name']}")
            logger.info(f"URL: {brochure['url']}")
            logger.info(f"{'='*70}")
            
            # Download PDF
            pdf_filename = f"{brochure['name']}.pdf"
            pdf_path = os.path.join(PDF_DIR, pdf_filename)
            
            if scraper.download_pdf(brochure['url'], pdf_path):
                # Parse PDF
                logger.info(f"Parsing PDF: {pdf_filename}")
                products = pdf_parser.parse_pdf(pdf_path)
                
                if products:
                    logger.info(f"Extracted {len(products)} products from {brochure['name']}")
                    
                    # Add brochure name to each product
                    for product in products:
                        product['category'] = brochure['name']
                    
                    all_products.extend(products)
                else:
                    logger.warning(f"No products found in {brochure['name']}")
            else:
                logger.error(f"Failed to download {brochure['name']}")
        
        if not all_products:
            logger.error("No products extracted from any brochure!")
            return 1
        
        # Validate products
        logger.info(f"\n{'='*70}")
        logger.info("Validating products...")
        validated_products = pdf_parser.validate_products(all_products)
        logger.info(f"Validated {len(validated_products)} products")
        
        # Save to JSON
        logger.info("Saving data to JSON...")
        json_file = data_saver.save_to_json(validated_products)
        logger.info(f"Data saved to: {json_file}")
        
        # Save to CSV
        logger.info("Saving data to CSV...")
        csv_file = data_saver.save_to_csv(validated_products)
        logger.info(f"Data saved to: {csv_file}")
        
        # Print summary
        print(f"\n{'='*70}")
        print("KAUFLAND SCRAPING COMPLETED SUCCESSFULLY")
        print(f"{'='*70}")
        print(f"Total brochures processed: {len(brochures)}")
        print(f"Total products scraped: {len(validated_products)}")
        print(f"Products with prices: {len([p for p in validated_products if p.get('price')])}")
        print(f"Files saved:")
        print(f"  - {json_file}")
        print(f"  - {csv_file}")
        print(f"{'='*70}\n")
        
        return 0
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1
    finally:
        try:
            scraper.close()
        except:
            pass

if __name__ == "__main__":
    sys.exit(main())



