"""
Helper functions for database queries
Използва се от API слой
"""

from typing import List, Dict, Any, Optional
import psycopg2
from psycopg2.extras import RealDictCursor


class PriceComparisonDB:
    """Database helper for price comparison queries."""
    
    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
    
    def get_connection(self):
        """Get database connection."""
        return psycopg2.connect(**self.db_config)
    
    def search_products(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Търсене на продукти по име или категория.
        Връща най-евтините опции за всеки продукт.
        """
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            cursor.execute(
                """
                SELECT 
                    p.id,
                    p.name,
                    p.weight_unit,
                    p.category,
                    p.description,
                    p.image_url,
                    s.display_name as cheapest_store,
                    cp.price_value as cheapest_price,
                    cp.price_currency,
                    cp.discount_percentage,
                    COUNT(DISTINCT pp.store_id) as available_in_stores
                FROM products p
                LEFT JOIN cheapest_prices cp ON p.id = cp.product_id AND cp.price_rank = 1
                LEFT JOIN stores s ON cp.store_name = s.name
                LEFT JOIN product_prices pp ON p.id = pp.product_id AND pp.is_active = TRUE
                WHERE p.normalized_name LIKE %s
                   OR p.name ILIKE %s
                   OR p.category ILIKE %s
                GROUP BY p.id, p.name, p.weight_unit, p.category, p.description, 
                         p.image_url, s.display_name, cp.price_value, cp.price_currency, cp.discount_percentage
                ORDER BY cp.price_value ASC NULLS LAST
                LIMIT %s
                """,
                (f'%{query.lower()}%', f'%{query}%', f'%{query}%', limit)
            )
            
            return [dict(row) for row in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()
    
    def get_product_prices(self, product_id: int) -> List[Dict[str, Any]]:
        """Връща всички цени за даден продукт във всички магазини."""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            cursor.execute(
                """
                SELECT 
                    s.id as store_id,
                    s.display_name as store,
                    pp.price_value,
                    pp.price_currency,
                    pp.old_price_value,
                    pp.discount_percentage,
                    pp.price_per_kg,
                    pp.scraped_at
                FROM product_prices pp
                INNER JOIN stores s ON pp.store_id = s.id
                WHERE pp.product_id = %s
                  AND pp.is_active = TRUE
                ORDER BY pp.price_value ASC
                """,
                (product_id,)
            )
            
            return [dict(row) for row in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()
    
    def optimize_cart(self, cart_id: int) -> Dict[str, Any]:
        """
        Оптимизира количката - намира най-евтината комбинация от магазини.
        """
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            # Get cheapest options for each product in cart
            cursor.execute(
                """
                WITH cart_cheapest AS (
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
                    WHERE ci.cart_id = %s
                      AND pp.is_active = TRUE
                    GROUP BY ci.id, ci.product_id, ci.quantity
                )
                SELECT 
                    p.name as product_name,
                    p.weight_unit,
                    s.display_name as recommended_store,
                    s.id as store_id,
                    cc.cheapest_price,
                    cc.quantity,
                    (cc.cheapest_price * cc.quantity) as total_for_product,
                    cc.cart_item_id
                FROM cart_cheapest cc
                INNER JOIN products p ON cc.product_id = p.id
                INNER JOIN stores s ON cc.cheapest_store_id = s.id
                ORDER BY cc.cheapest_store_id, p.name
                """,
                (cart_id,)
            )
            
            items = [dict(row) for row in cursor.fetchall()]
            
            # Calculate totals by store
            store_totals = {}
            grand_total = 0
            
            for item in items:
                store_id = item['store_id']
                if store_id not in store_totals:
                    store_totals[store_id] = {
                        'store_name': item['recommended_store'],
                        'items': [],
                        'total': 0
                    }
                
                store_totals[store_id]['items'].append(item)
                store_totals[store_id]['total'] += item['total_for_product']
                grand_total += item['total_for_product']
            
            return {
                'items': items,
                'stores': store_totals,
                'grand_total': grand_total,
                'stores_count': len(store_totals)
            }
        finally:
            cursor.close()
            conn.close()
    
    def get_cart_total(self, cart_id: int) -> Dict[str, Any]:
        """Връща обща сума на количката, разпределена по магазини."""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            cursor.execute(
                """
                SELECT 
                    s.id as store_id,
                    s.display_name as store,
                    COUNT(ci.id) as product_count,
                    SUM(pp.price_value * ci.quantity) as total_price,
                    SUM((COALESCE(pp.old_price_value, pp.price_value) - pp.price_value) * ci.quantity) as total_savings
                FROM cart_items ci
                INNER JOIN product_prices pp ON ci.selected_price_id = pp.id
                INNER JOIN stores s ON pp.store_id = s.id
                WHERE ci.cart_id = %s
                  AND ci.selected_price_id IS NOT NULL
                GROUP BY s.id, s.display_name
                ORDER BY total_price ASC
                """,
                (cart_id,)
            )
            
            stores = [dict(row) for row in cursor.fetchall()]
            
            # Calculate grand total
            grand_total = sum(s['total_price'] for s in stores)
            total_savings = sum(s['total_savings'] for s in stores)
            
            return {
                'stores': stores,
                'grand_total': grand_total,
                'total_savings': total_savings,
                'stores_count': len(stores)
            }
        finally:
            cursor.close()
            conn.close()
    
    def add_to_cart(self, cart_id: int, product_id: int, quantity: int = 1) -> bool:
        """Добавя продукт в количката."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                INSERT INTO cart_items (cart_id, product_id, quantity)
                VALUES (%s, %s, %s)
                ON CONFLICT (cart_id, product_id, store_id) 
                DO UPDATE SET quantity = cart_items.quantity + %s
                """,
                (cart_id, product_id, quantity, quantity)
            )
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error adding to cart: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    
    def update_cart_item_store(self, cart_item_id: int, store_id: int, price_id: int) -> bool:
        """Променя магазина за конкретен продукт в количката."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                UPDATE cart_items
                SET store_id = %s, selected_price_id = %s
                WHERE id = %s
                """,
                (store_id, price_id, cart_item_id)
            )
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error updating cart item: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

