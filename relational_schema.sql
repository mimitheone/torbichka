-- Релационен модел, подравнен с API формата:
-- { "items": [ { "id", "title", "weight", "weightMeasure", "description",
--                "prices": [ { "shopId", "shopName", "price", "promoPrice", "currency" } ],
--                "picture", "category" } ], "page", "size", "totalItems", "totalPages" }
--
-- products.id          -> items[].id
-- products.title       -> items[].title
-- products.weight      -> items[].weight
-- products.weight_measure -> items[].weightMeasure
-- product_prices + shops -> items[].prices[] (една връзка много-на-много: продукт x магазин)

DROP TABLE IF EXISTS product_price_history CASCADE;
DROP TABLE IF EXISTS product_prices CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS shops CASCADE;

CREATE TABLE shops (
    id INTEGER PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(80) UNIQUE
);

-- Kaufland BG като първи магазин (произволен id; добавяш Billa/Lidl с други id)
INSERT INTO shops (id, name, slug) VALUES (1, 'Kaufland', 'kaufland-bg');

CREATE TABLE products (
    id VARCHAR(200) PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    weight NUMERIC(12, 4),
    weight_measure VARCHAR(30),
    description TEXT,
    picture VARCHAR(800),
    category VARCHAR(200),
    manufacturer VARCHAR(200),
    origin VARCHAR(100),
    grade VARCHAR(50),
    availability VARCHAR(50),
    price_per_kg NUMERIC(10, 2),
    discount_text VARCHAR(200),
    price_original_text TEXT,
    weight_unit_raw VARCHAR(200),
    source VARCHAR(100) NOT NULL DEFAULT 'kaufland.bg',
    source_file VARCHAR(255),
    scraped_at TIMESTAMPTZ
);

-- Цени по магазин: price = референтна/стара цена при промо, иначе текуща;
-- promo_price = промоционалната продажна цена (NULL ако няма промо)
CREATE TABLE product_prices (
    product_id VARCHAR(200) NOT NULL REFERENCES products (id) ON DELETE CASCADE,
    shop_id INTEGER NOT NULL REFERENCES shops (id) ON DELETE RESTRICT,
    price NUMERIC(10, 2) NOT NULL,
    promo_price NUMERIC(10, 2),
    currency VARCHAR(10) NOT NULL DEFAULT 'EUR',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (product_id, shop_id)
);

-- История на цените за графики и „промяна спрямо миналия скрейп“
CREATE TABLE product_price_history (
    id BIGSERIAL PRIMARY KEY,
    product_id VARCHAR(200) NOT NULL REFERENCES products (id) ON DELETE CASCADE,
    shop_id INTEGER NOT NULL REFERENCES shops (id) ON DELETE RESTRICT,
    observed_at TIMESTAMPTZ NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    promo_price NUMERIC(10, 2),
    currency VARCHAR(10) NOT NULL DEFAULT 'EUR'
);

CREATE INDEX idx_products_category ON products (category);
CREATE INDEX idx_products_title ON products (title);
CREATE INDEX idx_product_prices_shop ON product_prices (shop_id);
CREATE INDEX idx_product_price_history_product_shop_time
    ON product_price_history (product_id, shop_id, observed_at DESC);

COMMENT ON TABLE shops IS 'Магазини; shopId/shopName в API идват оттук.';
COMMENT ON TABLE products IS 'Каталог продукти (items[] без вложения prices).';
COMMENT ON TABLE product_prices IS 'Цена по продукт и магазин; агрегира се в items[].prices.';
COMMENT ON TABLE product_price_history IS 'Снимки на цени при промяна; за времеви редове в приложението.';
