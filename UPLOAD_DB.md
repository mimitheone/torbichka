# Качване на данни в Supabase

## Използване

### От командния ред:

```bash
python3 upload_to_db.py data/kaufland_bg_products_20251031_182226.csv \
  --connection-string "postgresql://postgres:[YOUR-PASSWORD]@db.egokkwvfzvdbbkyotgjx.supabase.co:5432/postgres"
```

### Като Python модул:

```python
from upload_to_db import SupabaseUploader
from pathlib import Path

# Инициализирай uploader
connection_string = "postgresql://postgres:[YOUR-PASSWORD]@db.egokkwvfzvdbbkyotgjx.supabase.co:5432/postgres"
uploader = SupabaseUploader(connection_string)

# Качи CSV файл
uploader.upload_csv(
    Path("data/kaufland_bg_products_20251031_182226.csv"),
    store_name="kaufland",
    display_name="Kaufland"
)

# Затвори връзката
uploader.close()
```

## Какво прави модулът:

1. **Свързва се с базата данни** - използва connection string за Supabase
2. **Създава магазин** - ако не съществува, създава запис за Kaufland в таблицата `stores`
3. **Нормализира продукти** - намира съществуващи продукти или създава нови в таблицата `products`
4. **Качва цени** - вмъква цени в таблицата `product_prices` и маркира старите като неактивни
5. **Обработва данни** - парсва цени, отстъпки, дати на валидност и др.

## Параметри:

- `csv_file` - път до CSV файл с продукти
- `--connection-string` - PostgreSQL connection string (по подразбиране: Supabase URL)
- `--store-name` - идентификатор на магазина (по подразбиране: 'kaufland')
- `--store-display-name` - показвано име (по подразбиране: 'Kaufland')

## Забележки:

- Модулът автоматично пропуска продукти без цена
- Commit-ва на всеки 100 записа за по-добра производителност
- При грешка при един запис, продължава със следващия
- Старите цени се маркират като неактивни (`is_active = FALSE`)

