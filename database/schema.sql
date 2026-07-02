-- Kaufland Price Comparison Database Schema
-- База данни за сравнение на цени от различни магазини

-- Drop existing tables if needed (be careful in production!)
-- DROP TABLE IF EXISTS cart_items CASCADE;
-- DROP TABLE IF EXISTS carts CASCADE;
-- DROP TABLE IF EXISTS product_prices CASCADE;
-- DROP TABLE IF EXISTS products CASCADE;
-- DROP TABLE IF EXISTS stores CASCADE;
-- DROP TABLE IF EXISTS users CASCADE;

-- Stores table - магазини
CREATE TABLE IF NOT EXISTS stores (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,  -- 'kaufland', 'billa', 'lidl', etc.
    display_name VARCHAR(100) NOT NULL,  -- 'Kaufland', 'Billa', 'Lidl'
    website_url VARCHAR(255),
    logo_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products table - продукти (уникални по име + грамаж за нормализация)
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(500) NOT NULL,
    normalized_name VARCHAR(500),  -- Нормализирано име за търсене
    description TEXT,
    manufacturer VARCHAR(200),
    category VARCHAR(200),
    weight_unit VARCHAR(50),  -- '500 г', '1 л', etc.
    origin VARCHAR(100),
    grade VARCHAR(50),
    image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Index for fast searching
    CONSTRAINT unique_product UNIQUE (normalized_name, weight_unit)
);

-- Product prices table - цени по магазини
CREATE TABLE IF NOT EXISTS product_prices (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    store_id INTEGER NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    
    -- Price information
    price_value DECIMAL(10, 2) NOT NULL,
    price_currency VARCHAR(10) DEFAULT 'BGN',
    old_price_value DECIMAL(10, 2),  -- Цена преди отстъпката
    price_per_kg DECIMAL(10, 2),
    
    -- Promotion information
    discount_percentage INTEGER,  -- -35, -20, etc.
    discount_text VARCHAR(50),
    
    -- Metadata
    availability VARCHAR(50) DEFAULT 'Неизвестно',
    source_file VARCHAR(255),
    
    -- When was this price scraped
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,  -- Is this the current price?
    
    -- Ensure one active price per product-store combination
    UNIQUE(product_id, store_id, scraped_at)
);

-- Users table - потребители (ако искате user accounts)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Carts table - пазарски колички
CREATE TABLE IF NOT EXISTS carts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(255),  -- For anonymous users
    name VARCHAR(200),  -- Опционално име на списъка
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cart items - продукти в количката
CREATE TABLE IF NOT EXISTS cart_items (
    id SERIAL PRIMARY KEY,
    cart_id INTEGER NOT NULL REFERENCES carts(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    store_id INTEGER REFERENCES stores(id),  -- NULL = не е избран магазин (оптимално)
    quantity INTEGER DEFAULT 1,
    selected_price_id INTEGER REFERENCES product_prices(id),  -- Конкретна цена която потребителят е избрал
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(cart_id, product_id, store_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_products_normalized_name ON products(normalized_name);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_product_prices_product_id ON product_prices(product_id);
CREATE INDEX IF NOT EXISTS idx_product_prices_store_id ON product_prices(store_id);
CREATE INDEX IF NOT EXISTS idx_product_prices_active ON product_prices(is_active);
CREATE INDEX IF NOT EXISTS idx_product_prices_price_value ON product_prices(price_value);
CREATE INDEX IF NOT EXISTS idx_product_prices_scraped_at ON product_prices(scraped_at DESC);
CREATE INDEX IF NOT EXISTS idx_cart_items_cart_id ON cart_items(cart_id);
CREATE INDEX IF NOT EXISTS idx_cart_items_product_id ON cart_items(product_id);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for auto-updating updated_at
CREATE TRIGGER update_stores_updated_at BEFORE UPDATE ON stores
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_carts_updated_at BEFORE UPDATE ON carts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- View for easiest price comparison (най-ниска цена за всеки продукт)
CREATE OR REPLACE VIEW cheapest_prices AS
SELECT 
    p.id as product_id,
    p.name as product_name,
    p.weight_unit,
    s.name as store_name,
    s.display_name as store_display_name,
    pp.price_value,
    pp.price_currency,
    pp.old_price_value,
    pp.discount_percentage,
    pp.price_per_kg,
    pp.scraped_at,
    ROW_NUMBER() OVER (PARTITION BY p.id ORDER BY pp.price_value ASC) as price_rank
FROM products p
INNER JOIN product_prices pp ON p.id = pp.product_id
INNER JOIN stores s ON pp.store_id = s.id
WHERE pp.is_active = TRUE;

-- View for product price comparison (всички цени за всеки продукт)
CREATE OR REPLACE VIEW product_price_comparison AS
SELECT 
    p.id as product_id,
    p.name as product_name,
    p.weight_unit,
    s.id as store_id,
    s.name as store_name,
    s.display_name as store_display_name,
    pp.price_value,
    pp.price_currency,
    pp.old_price_value,
    pp.discount_percentage,
    pp.price_per_kg,
    pp.scraped_at,
    ROW_NUMBER() OVER (PARTITION BY p.id, s.id ORDER BY pp.scraped_at DESC) as latest_price_rank
FROM products p
INNER JOIN product_prices pp ON p.id = pp.product_id
INNER JOIN stores s ON pp.store_id = s.id
WHERE pp.is_active = TRUE;

