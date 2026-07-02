-- Изпълни в Supabase SQL Editor (или psql), ако таблицата вече съществува.
-- Релационен модел (upload_relational.py → таблица products):
ALTER TABLE products DROP COLUMN IF EXISTS vat_included;
ALTER TABLE products DROP COLUMN IF EXISTS price_per_gram;
ALTER TABLE products DROP COLUMN IF EXISTS product_url;
ALTER TABLE products DROP COLUMN IF EXISTS promotion_validity;

-- Проста схема (upload_simple.py → таблица products с image_id):
-- ALTER TABLE products DROP COLUMN IF EXISTS vat_included;
-- ALTER TABLE products DROP COLUMN IF EXISTS price_per_gram;
-- ALTER TABLE products DROP COLUMN IF EXISTS product_url;
-- ALTER TABLE products DROP COLUMN IF EXISTS promotion_validity;

-- Стара схема database/schema.sql:
-- ALTER TABLE products DROP COLUMN IF EXISTS product_url;
-- ALTER TABLE product_prices DROP COLUMN IF EXISTS vat_included;
-- ALTER TABLE product_prices DROP COLUMN IF EXISTS price_per_gram;
-- ALTER TABLE product_prices DROP COLUMN IF EXISTS promotion_validity_start;
-- ALTER TABLE product_prices DROP COLUMN IF EXISTS promotion_validity_end;
