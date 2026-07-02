# torbichka

Kaufland Bulgaria product scraper — извлича продукти и цени от kaufland.bg, качва в Supabase.

## Features

- **Local HTML Parsing**: Parse local HTML files from Kaufland website
- **PDF Brochure Support**: Extract products from PDF brochures
- **Flexible Scraping**: Supports both requests-based and Selenium-based web scraping
- **Multiple Output Formats**: Save data as JSON, CSV, or both
- **Kaufland-Specific Parsing**: Optimized for Kaufland's HTML structure (k-product-tile, k-price-tag)
- **Discount Tracking**: Captures discounts, old prices, and promotion periods
- **Price per Kilogram**: Automatically extracts price per kg for products
- **Comprehensive Logging**: Detailed logging with rotation and daily logs
- **Data Validation**: Validates and cleans scraped data
- **Summary Reports**: Generates detailed scraping reports with statistics

## Project Structure

```
kaufland-bg-scraper/
├── src/
│   ├── __init__.py          # Package initialization
│   ├── scraper.py           # Web scraping functionality
│   ├── parser.py            # HTML parsing and data extraction
│   ├── pdf_parser.py        # PDF brochure parsing
│   ├── data_saver.py        # Data saving in various formats
│   ├── logger.py            # Logging configuration
│   └── utils.py             # Utility functions
├── config/
│   └── settings.py          # Configuration settings
├── data/                    # Output directory for scraped data
├── pdfs/                    # Downloaded PDF brochures
├── logs/                    # Log files directory
├── tests/                   # Test files
├── main.py                  # Main entry point
├── test_kaufland.py         # PDF scraper test
├── test_setup.py            # Setup verification test
├── requirements.txt         # Python dependencies
├── env.example              # Environment variables example
└── README.md               # This file
```

## Installation

1. **Clone or download the project:**
   ```bash
   cd metro-bg-scraper
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment (optional):**
   ```bash
   cp env.example .env
   # Edit .env file with your preferred settings
   ```

## Usage

### Basic Usage

Parse local HTML files (recommended):

```bash
python main.py --local-html kaufland_sladko_soleno.html --output-format both
```

Parse multiple HTML files at once:

```bash
python main.py --local-html *.html --output-format both
```

### Advanced Usage

```bash
# Scrape from web with custom parameters
python main.py --max-products 500 --output-format both --log-level DEBUG

# Use a specific URL
python main.py --url "https://www.kaufland.bg/broshuri.html"

# Parse specific local HTML files
python main.py --local-html page1.html page2.html page3.html

# Run with visible browser (non-headless)
python main.py --headless
```

### Command Line Arguments

- `--local-html`: Parse local HTML file(s) instead of fetching from web (provide one or more file paths)
- `--url`: Target URL to scrape (default: Kaufland BG brochures page)
- `--max-products`: Maximum number of products to scrape (default: 1000)
- `--output-format`: Output format - json, csv, or both (default: json)
- `--log-level`: Logging level - DEBUG, INFO, WARNING, ERROR (default: INFO)
- `--no-selenium`: Disable Selenium WebDriver, use requests only
- `--headless`: Run browser in headless mode (default: true)

## Configuration

### Environment Variables

You can configure the scraper using environment variables or a `.env` file:

```bash
MAX_PRODUCTS=1000           # Maximum products to scrape
ENABLE_SELENIUM=false       # Use Selenium WebDriver
HEADLESS_BROWSER=true       # Run browser headlessly
REQUEST_TIMEOUT=30          # Request timeout in seconds
REQUEST_DELAY=2             # Delay between requests
MAX_RETRIES=3               # Maximum retry attempts
LOG_LEVEL=INFO              # Logging level
```

### Settings File

Advanced configuration can be done in `config/settings.py`:

- Request timeouts and delays
- User agent rotation
- Output file naming
- Selenium browser options

## Output

The scraper generates several types of output:

### JSON Format
```json
{
  "scrape_info": {
    "timestamp": "2024-01-15T10:30:00",
    "total_products": 150,
    "source": "metro.bg",
    "scraper_version": "1.0.0"
  },
  "products": [
    {
      "name": "Product Name",
      "price": {
        "value": 12.99,
        "currency": "BGN",
        "original_text": "12.99 лв"
      },
      "image_url": "https://...",
      "product_url": "https://...",
      "description": "Product description",
      "source": "metro.bg",
      "scraped_at": "2024-01-15T10:30:00"
    }
  ]
}
```

### CSV Format
Flattened data with columns: name, price_value, price_currency, image_url, product_url, description, source, scraped_at

### Summary Report
Text file with scraping statistics, price analysis, and sample products.

## Logging

The scraper maintains comprehensive logs:

- **Console output**: Real-time progress information
- **Rotating logs**: `logs/scraper.log` with automatic rotation (10MB, 5 backups)
- **Daily logs**: `logs/scraper_YYYYMMDD.log` for each day

## Legal and Ethical Considerations

**Important**: Before using this scraper, please:

1. **Check robots.txt**: Review https://www.kaufland.bg/robots.txt
2. **Read Terms of Service**: Ensure compliance with Kaufland Bulgaria's terms
3. **Use local files when possible**: Parsing local HTML files is the most respectful approach
4. **Respect rate limits**: The scraper includes delays, but be mindful of server load
5. **Use responsibly**: Don't overload the target website
6. **Consider alternatives**: Check if Kaufland Bulgaria offers an official API

## Troubleshooting

### Common Issues

1. **No products found**:
   - The website structure may have changed
   - Check if the URL is accessible
   - Try enabling Selenium with `--enable-selenium`

2. **Selenium WebDriver errors**:
   - Install ChromeDriver: `brew install chromedriver` (macOS) or download from Google
   - Ensure Chrome browser is installed
   - Try running with `--headless false` for debugging

3. **Request timeouts**:
   - Increase timeout in `config/settings.py`
   - Check internet connection
   - Website might be blocking requests

4. **Empty price data**:
   - Website structure may have changed
   - Check parser selectors in `src/parser.py`

### Debug Mode

Run with debug logging to see detailed information:

```bash
python main.py --log-level DEBUG
```

## Development

### Adding New Features

1. **New parsing logic**: Modify `src/parser.py`
2. **Additional output formats**: Extend `src/data_saver.py`
3. **New scraping methods**: Update `src/scraper.py`

### Testing

Run basic functionality test:

```bash
python -c "from src.parser import MetroParser; print('Parser imported successfully')"
```

## Dependencies

- **requests**: HTTP library for web requests
- **beautifulsoup4**: HTML parsing
- **lxml**: XML/HTML parser (faster than html.parser)
- **selenium**: Web browser automation
- **fake-useragent**: User agent rotation
- **python-dotenv**: Environment variable management

## License

This project is for educational and personal use. Please respect the target website's terms of service and robots.txt file.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs in the `logs/` directory
3. Enable debug logging for more information

---

**Disclaimer**: This scraper is provided as-is for educational purposes. Users are responsible for ensuring compliance with applicable laws and website terms of service.
