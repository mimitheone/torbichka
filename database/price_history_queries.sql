-- Релационен модел (products / product_prices / product_price_history)
-- Примери за приложението: графика и промяна на цената

-- Времева серия за един продукт в Kaufland (shop_id = 1)
-- effective_price = какво плаща клиентът (промо, ако има)
SELECT
    observed_at,
    COALESCE(promo_price, price) AS effective_price,
    price AS list_or_reference_price,
    promo_price,
    currency
FROM product_price_history
WHERE product_id = :product_id
  AND shop_id = 1
ORDER BY observed_at ASC;

-- Последна промяна спрямо предишния запис (за badge „-12%“ и т.н.)
WITH ordered AS (
    SELECT
        product_id,
        observed_at,
        COALESCE(promo_price, price) AS effective,
        LAG(COALESCE(promo_price, price)) OVER (
            PARTITION BY product_id, shop_id ORDER BY observed_at
        ) AS prev_effective
    FROM product_price_history
    WHERE shop_id = 1
)
SELECT
    product_id,
    observed_at,
    effective,
    prev_effective,
    CASE
        WHEN prev_effective IS NULL OR prev_effective = 0 THEN NULL
        ELSE ROUND(100.0 * (prev_effective - effective) / prev_effective, 1)
    END AS pct_change_vs_previous
FROM ordered
WHERE product_id = :product_id
ORDER BY observed_at DESC
LIMIT 5;
