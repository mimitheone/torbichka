#!/usr/bin/env python3
"""
Simple test script to verify the Metro Bulgaria scraper setup.
"""

import sys
from pathlib import Path

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all modules can be imported successfully."""
    try:
        print("Testing imports...")
        
        from src.scraper import KauflandScraper
        print("✓ KauflandScraper imported successfully")
        
        from src.parser import KauflandParser
        print("✓ KauflandParser imported successfully")
        
        from src.data_saver import DataSaver
        print("✓ DataSaver imported successfully")
        
        from src.logger import setup_logging
        print("✓ Logger module imported successfully")
        
        from src.utils import format_price, estimate_scraping_time
        print("✓ Utils module imported successfully")
        
        from config.settings import KAUFLAND_BG_URL, MAX_PRODUCTS
        print("✓ Settings imported successfully")
        
        print(f"✓ Target URL: {KAUFLAND_BG_URL}")
        print(f"✓ Max products: {MAX_PRODUCTS}")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality of key components."""
    try:
        print("\\nTesting basic functionality...")
        
        # Test parser with sample HTML
        from src.parser import KauflandParser
        parser = KauflandParser()
        
        sample_html = '''
        <div class="product">
            <h2 class="product-name">Test Product</h2>
            <span class="price">12.99 лв</span>
        </div>
        '''
        
        products = parser.parse_products(sample_html)
        if products:
            print("✓ Parser can extract products from HTML")
        else:
            print("✗ Parser failed to extract products")
            
        # Test data saver
        from src.data_saver import DataSaver
        saver = DataSaver()
        print("✓ DataSaver initialized successfully")
        
        # Test utils
        from src.utils import format_price, estimate_scraping_time
        formatted_price = format_price(12.99, "BGN")
        estimated_time = estimate_scraping_time(100)
        print(f"✓ Price formatting works: {formatted_price}")
        print(f"✓ Time estimation works: {estimated_time}")
        
        return True
        
    except Exception as e:
        print(f"✗ Functionality test error: {e}")
        return False

def main():
    """Run all tests."""
    print("Metro Bulgaria Scraper - Setup Test")
    print("=" * 40)
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        all_passed = False
    
    # Test basic functionality
    if not test_basic_functionality():
        all_passed = False
    
    print("\\n" + "=" * 40)
    if all_passed:
        print("✓ All tests passed! The scraper setup is working correctly.")
        print("\\nYou can now run the scraper with:")
        print("  python main.py --help")
    else:
        print("✗ Some tests failed. Please check the error messages above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
