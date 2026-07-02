#!/usr/bin/env python3
"""
Автоматично сваляне на продуктови страници от Kaufland
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

def setup_driver():
    """Setup Chrome driver"""
    chrome_options = Options()
    # chrome_options.add_argument('--headless')  # Uncomment to hide browser
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def scroll_to_load_all(driver):
    """Scroll to load all products"""
    print("  Scrolling to load all products...")
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    for i in range(10):  # Max 10 scrolls
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        print(f"    Scroll {i+1}...")
    
    print("  ✓ Finished scrolling")

def download_category_page(driver, category_url, filename):
    """Download a category page"""
    print(f"\n📄 Downloading: {filename}")
    print(f"   URL: {category_url}")
    
    try:
        driver.get(category_url)
        time.sleep(3)
        
        # Wait for products to load
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "k-product-tile"))
            )
        except:
            print("  ⚠️  Warning: Products might not have loaded")
        
        # Scroll to load all products
        scroll_to_load_all(driver)
        
        # Save HTML
        html = driver.page_source
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        
        # Count products
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        product_count = len(soup.select('.k-product-tile'))
        
        print(f"  ✓ Saved {product_count} products to {filename}")
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def main():
    """Main function"""
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║     KAUFLAND BG - АВТОМАТИЧНО СВАЛЯНЕ НА ПРОДУКТОВИ СТРАНИЦИ  ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print()
    
    # Kaufland product categories
    categories = [
        {
            "name": "Всички оферти",
            "url": "https://www.kaufland.bg/aktualni-predlozheniya/oferti.html",
            "filename": "kaufland_oferti_vsichki.html"
        },
        {
            "name": "Месо, Риби, Деликатеси",
            "url": "https://www.kaufland.bg/aktualni-predlozheniya/oferti.html?kloffer-category=Meso_Ribi_Delikates",
            "filename": "kaufland_meso_ribi.html"
        },
        {
            "name": "Млечни продукти",
            "url": "https://www.kaufland.bg/aktualni-predlozheniya/oferti.html?kloffer-category=Mlechni_produkti",
            "filename": "kaufland_mlechni.html"
        },
        {
            "name": "Плодове и Зеленчуци",
            "url": "https://www.kaufland.bg/aktualni-predlozheniya/oferti.html?kloffer-category=Plodove_Zelenchutsi",
            "filename": "kaufland_plodove_zelenchutsi.html"
        },
        {
            "name": "Напитки",
            "url": "https://www.kaufland.bg/aktualni-predlozheniya/oferti.html?kloffer-category=Napitki",
            "filename": "kaufland_napitki.html"
        },
        {
            "name": "Хранителни стоки",
            "url": "https://www.kaufland.bg/aktualni-predlozheniya/oferti.html?kloffer-category=Hranitelni_stoki",
            "filename": "kaufland_hranitelni_stoki.html"
        },
        {
            "name": "Сладко и солено",
            "url": "https://www.kaufland.bg/aktualni-predlozheniya/oferti.html?kloffer-category=Sladko_soleno",
            "filename": "kaufland_sladko_soleno_oferti.html"
        },
        {
            "name": "Нехранителни стоки",
            "url": "https://www.kaufland.bg/aktualni-predlozheniya/oferti.html?kloffer-category=Nehranitelni_stoki",
            "filename": "kaufland_nehranitelni.html"
        },
        {
            "name": "K-Bio",
            "url": "https://www.kaufland.bg/aktualni-predlozheniya/oferti.html?kloffer-category=K-Bio",
            "filename": "kaufland_kbio.html"
        },
        {
            "name": "Бебешки продукти",
            "url": "https://www.kaufland.bg/aktualni-predlozheniya/oferti.html?kloffer-category=Bebeshki_produkti",
            "filename": "kaufland_bebeshki.html"
        }
    ]
    
    print(f"Ще бъдат свалени {len(categories)} категории:\n")
    for i, cat in enumerate(categories, 1):
        print(f"  {i}. {cat['name']}")
    
    print("\n" + "="*70)
    print("Започвам сваляне...")
    print()
    
    driver = setup_driver()
    
    try:
        successful = 0
        failed = 0
        
        for i, category in enumerate(categories, 1):
            print(f"\n[{i}/{len(categories)}] {category['name']}")
            print("─" * 70)
            
            if download_category_page(driver, category['url'], category['filename']):
                successful += 1
            else:
                failed += 1
            
            # Wait between requests
            if i < len(categories):
                print("\n  ⏳ Waiting 3 seconds...")
                time.sleep(3)
        
        print("\n" + "="*70)
        print("✅ ЗАВЪРШЕНО!")
        print(f"   Успешни: {successful}")
        print(f"   Неуспешни: {failed}")
        print("="*70)
        
        print("\n📌 Сега изпълнете:")
        print("   python main.py --local-html kaufland_*.html --output-format both")
        print()
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()

