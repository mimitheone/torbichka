-- Еднократна миграция за съществуваща база (Supabase SQL editor или psql).
-- След това всеки импорт чрез upload_relational.py добавя ред само при реална промяна на цената.

CREATE TABLE IF NOT EXISTS product_price_history (
    id BIGSERIAL PRIMARY KEY,
    product_id VARCHAR(200) NOT NULL REFERENCES products (id) ON DELETE CASCADE,
    shop_id INTEGER NOT NULL REFERENCES shops (id) ON DELETE RESTRICT,
    observed_at TIMESTAMPTZ NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    promo_price NUMERIC(10, 2),
    currency VARCHAR(10) NOT NULL DEFAULT 'EUR'
);

CREATE INDEX IF NOT EXISTS idx_product_price_history_product_shop_time
    ON product_price_history (product_id, shop_id, observed_at DESC);

COMMENT ON TABLE product_price_history IS 'История на цени при промяна; за графики в приложението.';

-- По желание: еднократен seed от текущите цени (една точка „от днес“ преди да има реални промени)
-- INSERT INTO product_price_history (product_id, shop_id, observed_at, price, promo_price, currency)
-- SELECT product_id, shop_id, updated_at, price, promo_price, currency FROM product_prices;
