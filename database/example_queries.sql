-- Example SQL queries for price comparison app
-- Примери за заявки за мобилното приложение

-- ============================================
-- 1. Най-евтиното място за конкретен продукт
-- ============================================
SELECT 
    p.name,
    p.weight_unit,
    s.display_name as store,
    pp.price_value,
    pp.price_currency,
    pp.discount_percentage,
    pp.price_per_kg
FROM products p
INNER JOIN product_prices pp ON p.id = pp.product_id
INNER JOIN stores s ON pp.store_id = s.id
WHERE p.normalized_name LIKE '%сирене%'
  AND pp.is_active = TRUE
ORDER BY pp.price_value ASC
LIMIT 5;

-- ============================================
-- 2. Сравнение на цени за продукт във всички магазини
-- ============================================
SELECT 
    s.display_name as store,
    pp.price_value,
    pp.price_currency,
    pp.old_price_value,
    pp.discount_percentage,
    pp.price_per_kg,
    pp.scraped_at
FROM products p
INNER JOIN product_prices pp ON p.id = pp.product_id
INNER JOIN stores s ON pp.store_id = s.id
WHERE p.normalized_name LIKE '%мляко%'
  AND pp.is_active = TRUE
ORDER BY pp.price_value ASC;

-- ============================================
-- 3. Оптимално разпределение на продуктите в количката
-- (най-евтина комбинация от магазини)
-- ============================================
WITH cart_total AS (
    SELECT 
        ci.id as cart_item_id,
        ci.product_id,
        ci.quantity,
        MIN(pp.price_value) as cheapest_price,
        (
            SELECT pp2.store_id 
            FROM product_prices pp2 
            WHERE pp2.product_id = ci.product_id 
              AND pp2.price_value = MIN(pp.price_value)
              AND pp2.is_active = TRUE
            LIMIT 1
        ) as cheapest_store_id
    FROM cart_items ci
    INNER JOIN product_prices pp ON ci.product_id = pp.product_id
    WHERE ci.cart_id = 1  -- Replace with actual cart_id
      AND pp.is_active = TRUE
    GROUP BY ci.id, ci.product_id, ci.quantity
)
SELECT 
    p.name as product_name,
    p.weight_unit,
    s.display_name as recommended_store,
    ct.cheapest_price,
    ct.quantity,
    (ct.cheapest_price * ct.quantity) as total_for_product
FROM cart_total ct
INNER JOIN products p ON ct.product_id = p.id
INNER JOIN stores s ON ct.cheapest_store_id = s.id
ORDER BY ct.cheapest_store_id, p.name;

-- ============================================
-- 4. Обща сума на количката по магазини
-- ============================================
SELECT 
    s.display_name as store,
    COUNT(ci.id) as product_count,
    SUM(pp.price_value * ci.quantity) as total_price,
    SUM((pp.old_price_value - pp.price_value) * ci.quantity) as total_savings
FROM cart_items ci
INNER JOIN product_prices pp ON ci.selected_price_id = pp.id
INNER JOIN stores s ON pp.store_id = s.id
WHERE ci.cart_id = 1  -- Replace with actual cart_id
  AND ci.selected_price_id IS NOT NULL
GROUP BY s.id, s.display_name
ORDER BY total_price ASC;

-- ============================================
-- 5. Обща сума на количката (всички продукти)
-- ============================================
SELECT 
    COUNT(DISTINCT ci.store_id) as stores_count,
    COUNT(ci.id) as total_items,
    SUM(pp.price_value * ci.quantity) as grand_total,
    SUM((pp.old_price_value - pp.price_value) * ci.quantity) as total_savings
FROM cart_items ci
INNER JOIN product_prices pp ON ci.selected_price_id = pp.id
WHERE ci.cart_id = 1  -- Replace with actual cart_id
  AND ci.selected_price_id IS NOT NULL;

-- ============================================
-- 6. Търсене на продукти по име/категория
-- ============================================
SELECT 
    p.id,
    p.name,
    p.weight_unit,
    p.category,
    s.display_name as cheapest_store,
    cp.price_value as cheapest_price,
    cp.price_currency,
    COUNT(DISTINCT pp.store_id) as available_in_stores
FROM products p
LEFT JOIN cheapest_prices cp ON p.id = cp.product_id AND cp.price_rank = 1
LEFT JOIN product_prices pp ON p.id = pp.product_id AND pp.is_active = TRUE
WHERE p.normalized_name LIKE '%хляб%'
   OR p.category ILIKE '%хляб%'
GROUP BY p.id, p.name, p.weight_unit, p.category, s.display_name, cp.price_value, cp.price_currency
ORDER BY cp.price_value ASC
LIMIT 20;

-- ============================================
-- 7. Продукти с най-големи отстъпки
-- ============================================
SELECT 
    p.name,
    p.weight_unit,
    s.display_name as store,
    pp.price_value,
    pp.old_price_value,
    pp.discount_percentage,
    ROUND((pp.old_price_value - pp.price_value)::numeric, 2) as savings
FROM products p
INNER JOIN product_prices pp ON p.id = pp.product_id
INNER JOIN stores s ON pp.store_id = s.id
WHERE pp.is_active = TRUE
  AND pp.discount_percentage IS NOT NULL
  AND pp.old_price_value IS NOT NULL
ORDER BY pp.discount_percentage ASC, savings DESC
LIMIT 20;

-- ============================================
-- 8. Статистика по магазин
-- ============================================
SELECT 
    s.display_name as store,
    COUNT(DISTINCT pp.product_id) as unique_products,
    COUNT(pp.id) as total_prices,
    AVG(pp.price_value) as avg_price,
    MIN(pp.price_value) as min_price,
    MAX(pp.price_value) as max_price,
    COUNT(CASE WHEN pp.discount_percentage IS NOT NULL THEN 1 END) as products_on_discount
FROM stores s
LEFT JOIN product_prices pp ON s.id = pp.store_id AND pp.is_active = TRUE
GROUP BY s.id, s.display_name
ORDER BY unique_products DESC;

-- ============================================
-- 9. Продукти които липсват в количката но са в други магазини по-евтино
-- ============================================
WITH cart_products AS (
    SELECT DISTINCT product_id, store_id
    FROM cart_items
    WHERE cart_id = 1
),
cheapest_options AS (
    SELECT 
        product_id,
        store_id,
        price_value,
        ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY price_value ASC) as rank
    FROM product_prices
    WHERE is_active = TRUE
)
SELECT 
    p.name,
    p.weight_unit,
    s_current.display_name as current_store,
    pp_current.price_value as current_price,
    s_cheaper.display_name as cheaper_store,
    co.price_value as cheaper_price,
    (pp_current.price_value - co.price_value) as potential_savings
FROM cart_products cp
INNER JOIN products p ON cp.product_id = p.id
INNER JOIN product_prices pp_current ON cp.product_id = pp_current.product_id 
    AND cp.store_id = pp_current.store_id AND pp_current.is_active = TRUE
INNER JOIN stores s_current ON cp.store_id = s_current.id
INNER JOIN cheapest_options co ON cp.product_id = co.product_id AND co.rank = 1
INNER JOIN stores s_cheaper ON co.store_id = s_cheaper.id
WHERE co.store_id != cp.store_id
  AND co.price_value < pp_current.price_value
ORDER BY potential_savings DESC;

