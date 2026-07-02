-- Проста схема - само таблица products

DROP TABLE IF EXISTS products CASCADE;

CREATE TABLE products (
    image_id VARCHAR(200) PRIMARY KEY,   -- Уникален ID от URL на снимката (напр. 01004080_P)
    name VARCHAR(500) NOT NULL,
    manufacturer VARCHAR(200),
    weight_unit VARCHAR(50),
    category VARCHAR(200),
    origin VARCHAR(100),
    grade VARCHAR(50),
    price_value DECIMAL(10, 2),
    price_currency VARCHAR(10) DEFAULT 'EUR',
    old_price DECIMAL(10, 2),
    price_per_kg DECIMAL(10, 2),
    discount VARCHAR(50),
    description TEXT,
    availability VARCHAR(50),
    price_original_text VARCHAR(100),
    image_url VARCHAR(500),
    source VARCHAR(100) DEFAULT 'kaufland.bg',
    source_file VARCHAR(255),
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индекси за по-бързо търсене
CREATE INDEX idx_products_name ON products(name);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_manufacturer ON products(manufacturer);
CREATE INDEX idx_products_price_value ON products(price_value);
CREATE INDEX idx_products_scraped_at ON products(scraped_at DESC);

