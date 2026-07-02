#!/usr/bin/env python3
"""
Пълен цикъл: (по избор) relational_schema → скрапва kaufland_*.html → CSV → upload_relational.

За cron (само нови данни, без DROP на таблиците):
  python3 run_pipeline.py --no-schema >> logs/cron_pipeline.log 2>&1

Първо внедряване (създава/нули таблиците от relational_schema.sql):
  python3 run_pipeline.py

DATABASE_URL в .env (виж .env.example).
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent


def main() -> int:
    parser = argparse.ArgumentParser(description="Скрап + (по избор) схема + качване в PostgreSQL")
    parser.add_argument(
        "--no-schema",
        action="store_true",
        help="Пропусни apply_relational_schema.sql (за cron след първоначално внедряване)",
    )
    parser.add_argument(
        "--scrape-only",
        action="store_true",
        help="Само генерирай CSV, без база",
    )
    parser.add_argument(
        "--upload-only",
        metavar="CSV",
        help="Само качи посочения CSV (без скрап); изисква DATABASE_URL",
    )
    args = parser.parse_args()

    load_dotenv(ROOT / ".env")
    os.chdir(ROOT)

    py = sys.executable

    if args.upload_only:
        if not os.environ.get("DATABASE_URL"):
            print("Липсва DATABASE_URL в .env", file=sys.stderr)
            return 1
        csv_path = Path(args.upload_only)
        if not csv_path.is_file():
            print(f"Няма файл: {csv_path}", file=sys.stderr)
            return 1
        print(f"▶ Качване в БД: {csv_path}")
        return subprocess.run([py, str(ROOT / "upload_relational.py"), str(csv_path)]).returncode

    if not args.scrape_only and not os.environ.get("DATABASE_URL"):
        print(
            "Липсва DATABASE_URL в .env (нужен за схема и upload). За само скрап: --scrape-only",
            file=sys.stderr,
        )
        return 1

    html_files = sorted(ROOT.glob("kaufland_*.html"))
    if not html_files:
        print("Няма kaufland_*.html в root на проекта.", file=sys.stderr)
        return 1

    if not args.no_schema and not args.scrape_only:
        print("▶ Прилагане на relational_schema.sql")
        r = subprocess.run([py, str(ROOT / "apply_relational_schema.py")], cwd=str(ROOT))
        if r.returncode != 0:
            print("Спиране: грешка при схемата", file=sys.stderr)
            return r.returncode

    print(f"▶ Скрапване на {len(html_files)} HTML файла → CSV")
    r = subprocess.run(
        [py, str(ROOT / "main.py"), "--local-html", *[str(p) for p in html_files], "--output-format", "csv"],
        cwd=str(ROOT),
    )
    if r.returncode != 0:
        print("Спиране: грешка при скрапа", file=sys.stderr)
        return r.returncode

    if args.scrape_only:
        print("Готово (само CSV).")
        return 0

    data_dir = ROOT / "data"
    csvs = sorted(
        data_dir.glob("kaufland_bg_products_*.csv"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not csvs:
        print("Няма генериран CSV в data/", file=sys.stderr)
        return 1
    latest = csvs[0]
    print(f"▶ Качване в БД: {latest.name}")
    return subprocess.run([py, str(ROOT / "upload_relational.py"), str(latest)]).returncode


if __name__ == "__main__":
    sys.exit(main())
