# Database Setup for Price Comparison App

База данни за мобилно приложение за сравнение на цени от различни магазини.

## 🗄️ База данни: PostgreSQL

**Защо PostgreSQL?**
- Отлична поддръжка за релационни данни
- Мощни заявки за сравнение и анализ
- Бърза работа с големи обеми данни
- Добра интеграция с мобилни приложения (через API)
- Поддръжка за JSON, full-text search, индексиране

---

## 📊 Схема на базата данни

### Основни таблици:

1. **`stores`** - Магазини (Kaufland, Billa, Lidl, etc.)
2. **`products`** - Продукти (нормализирани за сравнение между магазините)
3. **`product_prices`** - Цени по магазини (история на цените)
4. **`users`** - Потребители (опционално, за user accounts)
5. **`carts`** - Пазарски колички
6. **`cart_items`** - Продукти в количката

### Views (изгледи):

- **`cheapest_prices`** - Най-ниска цена за всеки продукт
- **`product_price_comparison`** - Сравнение на цени във всички магазини

---

## 🚀 Инсталация

### 1. Инсталирай PostgreSQL

**macOS:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Ubuntu/Debian:**
```bash
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### 2. Създай база данни

```bash
# Влез в PostgreSQL
psql postgres

# Създай база данни и потребител
CREATE DATABASE price_comparison;
CREATE USER price_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE price_comparison TO price_user;
\q
```

### 3. Инсталирай Python зависимости

```bash
pip install psycopg2-binary python-dotenv
```

### 4. Създай схемата

```bash
psql -U price_user -d price_comparison -f database/schema.sql
```

### 5. Импортирай данните от Kaufland

```bash
python database/import_data.py \
    data/kaufland_bg_products_20251031_172700.csv \
    --host localhost \
    --port 5432 \
    --database price_comparison \
    --user price_user \
    --password your_password \
    --store-name kaufland \
    --store-display-name "Kaufland"
```

---

## 📱 Използване за мобилно приложение

### Опция 1: REST API (препоръчително)

Използвайте **FastAPI** или **Flask** за създаване на REST API:

```python
# Пример: database/api.py
from fastapi import FastAPI
from database.queries import get_cheapest_prices, get_cart_total

app = FastAPI()

@app.get("/api/products/search")
async def search_products(q: str):
    # Търсене на продукти
    return get_cheapest_prices(q)

@app.get("/api/cart/{cart_id}/optimize")
async def optimize_cart(cart_id: int):
    # Оптимизира количката за най-ниска цена
    return get_cart_optimization(cart_id)

@app.get("/api/cart/{cart_id}/total")
async def get_total(cart_id: int):
    # Връща обща сума на количката
    return get_cart_total(cart_id)
```

### Опция 2: Директна връзка

Мобилното приложение може да се свързва директно с PostgreSQL (непрепоръчително за production).

---

## 🔍 Примерни заявки

Виж `database/example_queries.sql` за примери:
- Най-евтино място за продукт
- Сравнение на цени
- Оптимизация на количка
- Обща сума по магазини
- Търсене на продукти

---

## 🔄 Добавяне на нов магазин

```sql
INSERT INTO stores (name, display_name, website_url)
VALUES ('billa', 'Billa', 'https://www.billa.bg');
```

След това импортирай данните:

```bash
python database/import_data.py \
    data/billa_products.csv \
    --store-name billa \
    --store-display-name "Billa"
```

---

## 📈 Следващи стъпки

1. **API слой** - FastAPI/Flask REST API
2. **Аутентификация** - JWT tokens за потребителите
3. **Кеширане** - Redis за бърз достъп
4. **Алгоритъм за оптимизация** - За разпределение на продуктите между магазините
5. **Уведомления** - За промени в цените
6. **Аналитика** - Статистики за потребителите

---

## 🛠️ Maintenance

### Обновяване на цените

```sql
-- Стари цени автоматично стават inactive при нов импорт
-- Виж product_prices.is_active флаг
```

### Почистване на стари данни

```sql
-- Изтриване на цени по-стари от 30 дни
DELETE FROM product_prices 
WHERE scraped_at < NOW() - INTERVAL '30 days'
  AND is_active = FALSE;
```

### Бекъп

```bash
pg_dump -U price_user price_comparison > backup.sql
```

