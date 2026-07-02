-- Премахва created_at / updated_at от products (без триене на таблицата).
-- Пусни в Supabase SQL Editor, ако вече имаш данни и не искаш пълен DROP от relational_schema.sql.

ALTER TABLE products DROP COLUMN IF EXISTS created_at;
ALTER TABLE products DROP COLUMN IF EXISTS updated_at;
