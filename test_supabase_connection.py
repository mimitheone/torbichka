#!/usr/bin/env python3
"""
Проверка на връзката към Supabase PostgreSQL.

Директният URI (db.*.supabase.co:5432) е основно IPv6 — на много мрежи дава Connection refused.
Алтернатива: в таблото Connect → Session pooler → копирай URI в DATABASE_URL или DATABASE_URL_SESSION.
"""

import os
import sys
from pathlib import Path
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")


def _with_sslmode(url: str) -> str:
    url = url.strip()
    if not url:
        return url
    parsed = urlparse(url)
    q = parse_qs(parsed.query)
    if "sslmode" not in {k.lower() for k in q.keys()}:
        q["sslmode"] = ["require"]
    new_query = urlencode(q, doseq=True)
    return urlunparse(parsed._replace(query=new_query))


def _try_connect(label: str, url: str) -> bool:
    import psycopg2

    url = _with_sslmode(url)
    try:
        conn = psycopg2.connect(url, connect_timeout=15)
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            one = cur.fetchone()[0]
        conn.close()
        print(f"OK ({label}): SELECT 1 → {one}")
        return True
    except Exception as e:
        print(f"Неуспех ({label}): {e}")
        return False


def main() -> int:
    direct = os.environ.get("DATABASE_URL", "").strip()
    session = os.environ.get("DATABASE_URL_SESSION", "").strip()

    if not direct and not session:
        print(
            "Липсва DATABASE_URL. Виж .env.example — за Mac/IPv4 ползвай Session pooler URI от Supabase → Connect."
        )
        return 1

    try:
        import psycopg2  # noqa: F401
    except ImportError:
        print("Инсталирай: pip install psycopg2-binary")
        return 1

    tried = []
    if direct:
        tried.append(("DATABASE_URL (директ / както в .env)", direct))
    if session:
        tried.append(("DATABASE_URL_SESSION (pooler)", session))

    for label, url in tried:
        if _try_connect(label, url):
            return 0

    print()
    print("─" * 60)
    print("Директният хост db.*.supabase.co често е само IPv6 → Connection refused на много мрежи.")
    print("Решение:")
    print("  1) Supabase Dashboard → проект → бутон „Connect“")
    print("  2) Избери „Session pooler“ (или Method: Session)")
    print("  3) Копирай URI (user е postgres.ТВОЯТ_REF @ aws-0-...pooler.supabase.com:5432)")
    print("  4) Сложи го в .env като DATABASE_URL=... (или DATABASE_URL_SESSION=... за тест)")
    print("Документация: https://supabase.com/docs/guides/database/connecting-to-postgres")
    print("─" * 60)
    return 1


if __name__ == "__main__":
    sys.exit(main())
