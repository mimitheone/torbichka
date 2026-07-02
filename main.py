#!/usr/bin/env python3
"""
Kaufland Bulgaria Product Scraper

A web scraper to extract product information and prices from Kaufland Bulgaria PDF brochures.
"""

import argparse
import sys
import time
from pathlib import Path

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent / "src"))

from src.scraper import KauflandScraper
from src.parser import KauflandParser
from src.pdf_parser import KauflandPDFParser
from src.data_saver import DataSaver
from src.logger import setup_logging
from src.utils import estimate_scraping_time
from config.settings import KAUFLAND_BG_URL, MAX_PRODUCTS, PDF_DIR


def main():
    """Main function to run the Kaufland Bulgaria scraper."""
    
    # Setup argument parser
    parser = argparse.ArgumentParser(
        description="Scrape products and prices from Kaufland Bulgaria HTML pages or PDF brochures"
    )
    parser.add_argument(
        "--url", 
        default=KAUFLAND_BG_URL,
        help="URL to scrape (default: Kaufland BG brochures page)"
    )
    parser.add_argument(
        "--max-products",
        type=int,
        default=MAX_PRODUCTS,
        help=f"Maximum number of products to scrape (default: {MAX_PRODUCTS})"
    )
    parser.add_argument(
        "--output-format",
        choices=["json", "csv", "both"],
        default="json",
        help="Output format for scraped data (default: json)"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)"
    )
    parser.add_argument(
        "--no-selenium",
        action="store_true",
        help="Disable Selenium and use only requests library"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        default=True,
        help="Run browser in headless mode (default: True)"
    )
    parser.add_argument(
        "--detailed-scraping",
        action="store_true",
        help="Enable detailed scraping by visiting individual product pages (slower but more complete)"
    )
    parser.add_argument(
        "--full-site",
        action="store_true",
        help="Scrape entire Kaufland website - all categories and all products (ignores --max-products and --url)"
    )
    parser.add_argument(
        "--local-html",
        nargs="+",
        help="Parse local HTML file(s) instead of fetching from web (provide one or more file paths)"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(log_level=args.log_level)
    logger.info("Starting Kaufland Bulgaria product scraper")
    
    if args.local_html:
        logger.info(f"Parsing local HTML files: {args.local_html}")
    else:
        logger.info(f"Target URL: {args.url}")
    
    logger.info(f"Max products: {args.max_products}")
    logger.info(f"Output format: {args.output_format}")
    
    try:
        # Initialize components
        scraper = KauflandScraper()
        parser_instance = KauflandParser()
        data_saver = DataSaver()
        
        all_products = []
        
        # Handle local HTML files
        if args.local_html:
            logger.info("=" * 70)
            logger.info("LOCAL HTML PARSING MODE")
            logger.info(f"Processing {len(args.local_html)} HTML file(s)")
            logger.info("=" * 70)
            
            for html_file in args.local_html:
                logger.info(f"\nProcessing file: {html_file}")
                try:
                    with open(html_file, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    
                    logger.info(f"Loaded {len(html_content)} characters from {html_file}")
                    
                    # Parse products from HTML
                    products = parser_instance.parse_products(html_content)
                    
                    if products:
                        logger.info(f"Found {len(products)} products in {html_file}")
                        # Add source file info to each product
                        for product in products:
                            product['source_file'] = html_file
                        all_products.extend(products)
                    else:
                        logger.warning(f"No products found in {html_file}")
                        
                except FileNotFoundError:
                    logger.error(f"File not found: {html_file}")
                except Exception as e:
                    logger.error(f"Error processing {html_file}: {e}")
            
            if not all_products:
                logger.error("No products found in any HTML file")
                return 1
            
            logger.info(f"\n{'='*70}")
            logger.info(f"COMPLETED HTML PARSING")
            logger.info(f"Total products collected: {len(all_products)}")
            logger.info(f"{'='*70}\n")
            
            products = all_products
        
        # Full site scraping mode
        elif args.full_site:
            logger.info("=" * 70)
            logger.info("FULL SITE SCRAPING MODE ENABLED")
            logger.info("This will scrape ALL products from ALL categories on Metro Bulgaria")
            logger.info("=" * 70)
            
            # Discover all categories
            categories = scraper.discover_categories()
            
            if not categories:
                logger.warning("No categories discovered, using main shop page")
                categories = [{'url': KAUFLAND_BG_URL, 'name': 'Main Shop'}]
            
            logger.info(f"Found {len(categories)} categories to scrape")
            
            # Scrape each category
            for i, category in enumerate(categories, 1):
                logger.info(f"\n{'='*70}")
                logger.info(f"Processing category {i}/{len(categories)}: {category['name']}")
                logger.info(f"URL: {category['url']}")
                logger.info(f"{'='*70}")
                
                try:
                    # Fetch category page with infinite scroll
                    html_content = scraper.fetch_page_selenium(category['url'], scroll_for_products=True)
                    
                    if not html_content:
                        logger.error(f"Failed to fetch category: {category['name']}")
                        continue
                    
                    logger.info(f"Successfully fetched {len(html_content)} characters from {category['name']}")
                    
                    # Parse products from this category
                    category_products = parser_instance.parse_products(html_content)
                    
                    if category_products:
                        logger.info(f"Found {len(category_products)} products in {category['name']}")
                        
                        # Add category info to each product
                        for product in category_products:
                            product['category'] = category['name']
                        
                        all_products.extend(category_products)
                        logger.info(f"Total products collected so far: {len(all_products)}")
                    else:
                        logger.warning(f"No products found in category: {category['name']}")
                    
                    # Small delay between categories
                    time.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Error processing category {category['name']}: {e}")
                    continue
            
            if not all_products:
                logger.error("No products found across all categories")
                return 1
            
            logger.info(f"\n{'='*70}")
            logger.info(f"COMPLETED CATEGORY SCRAPING")
            logger.info(f"Total products collected: {len(all_products)}")
            logger.info(f"{'='*70}\n")
            
            products = all_products
            
        else:
            # Normal single URL scraping mode
            # Estimate scraping time
            estimated_time = estimate_scraping_time(args.max_products)
            logger.info(f"Estimated scraping time: {estimated_time}")
            
            # Fetch webpage content
            logger.info("Fetching webpage content...")
            html_content = scraper.fetch_page(args.url)
            
            if not html_content:
                logger.error("Failed to fetch webpage content")
                return 1
            
            logger.info(f"Successfully fetched {len(html_content)} characters of HTML content")
            
            # Parse products from HTML
            logger.info("Parsing products from HTML content...")
            products = parser_instance.parse_products(html_content)
            
            if not products:
                logger.error("No products found in the webpage")
                return 1
            
            logger.info(f"Found {len(products)} products")
            
            # Limit products if specified
            if args.max_products and len(products) > args.max_products:
                products = products[:args.max_products]
                logger.info(f"Limited to {args.max_products} products")
        
        # Enhanced detailed scraping if requested
        if args.detailed_scraping:
            logger.info("Starting detailed scraping by visiting individual product pages...")
            enhanced_products = []
            
            for i, product in enumerate(products[:args.max_products], 1):
                logger.info(f"Processing product {i}/{len(products[:args.max_products])}: {product.get('name', 'Unknown')}")
                
                product_url = product.get('product_url')
                if product_url:
                    # Fetch individual product page
                    product_html = scraper.fetch_product_page(product_url)
                    if product_html:
                        # Extract detailed information
                        detailed_product = parser_instance.extract_detailed_product_info(product_html, product)
                        enhanced_products.append(detailed_product)
                    else:
                        logger.warning(f"Failed to fetch product page for: {product.get('name')}")
                        enhanced_products.append(product)
                else:
                    logger.warning(f"No product URL found for: {product.get('name')}")
                    enhanced_products.append(product)
                
                # Add small delay between requests to be respectful
                time.sleep(1)
            
            products = enhanced_products
            logger.info(f"Completed detailed scraping for {len(products)} products")
        
        # Validate product data
        logger.info("Validating product data...")
        validated_products = parser_instance.validate_product_data(products)
        logger.info(f"Validated {len(validated_products)} products")
        
        # Save data in requested format(s)
        saved_files = []
        
        if args.output_format in ["json", "both"]:
            logger.info("Saving data to JSON format...")
            json_file = data_saver.save_to_json(validated_products)
            saved_files.append(json_file)
            logger.info(f"Data saved to: {json_file}")
        
        if args.output_format in ["csv", "both"]:
            logger.info("Saving data to CSV format...")
            csv_file = data_saver.save_to_csv(validated_products)
            saved_files.append(csv_file)
            logger.info(f"Data saved to: {csv_file}")
        
        # Generate summary report
        logger.info("Generating summary report...")
        report_file = data_saver.save_summary_report(validated_products)
        saved_files.append(report_file)
        logger.info(f"Summary report saved to: {report_file}")
        
        # Print summary to console
        print(f"\\n{'='*60}")
        print("SCRAPING COMPLETED SUCCESSFULLY")
        print(f"{'='*60}")
        print(f"Products scraped: {len(validated_products)}")
        print(f"Products with prices: {len([p for p in validated_products if p.get('price')])}")
        print(f"Files saved:")
        for file_path in saved_files:
            print(f"  - {file_path}")
        print(f"{'='*60}\\n")
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error occurred: {e}", exc_info=True)
        return 1
    finally:
        # Clean up resources
        try:
            scraper.close()
        except:
            pass


if __name__ == "__main__":
    sys.exit(main())
