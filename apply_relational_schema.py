#!/usr/bin/env python3
"""Изпълнява relational_schema.sql в PostgreSQL (Supabase)."""

import os
import re
import sys
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent


def _split_statements(sql: str) -> list[str]:
    """Премахва пълни редове с -- и дели на команди по ; в край на ред."""
    lines = []
    for line in sql.splitlines():
        s = line.strip()
        if s.startswith("--"):
            continue
        lines.append(line)
    text = "\n".join(lines)
    parts = []
    buf = []
    for line in text.splitlines():
        buf.append(line)
        if line.rstrip().endswith(";"):
            stmt = "\n".join(buf).strip()
            if stmt:
                parts.append(stmt.rstrip(";").strip() + ";")
            buf = []
    if buf:
        tail = "\n".join(buf).strip()
        if tail:
            parts.append(tail if tail.endswith(";") else tail + ";")
    return parts


def main() -> int:
    load_dotenv(ROOT / ".env")
    import argparse

    p = argparse.ArgumentParser(description="Прилага relational_schema.sql")
    p.add_argument(
        "--connection-string",
        default=os.environ.get("DATABASE_URL", ""),
        help="PostgreSQL URL или задай DATABASE_URL в .env",
    )
    p.add_argument(
        "--schema-file",
        type=Path,
        default=ROOT / "relational_schema.sql",
    )
    args = p.parse_args()
    if not args.connection_string:
        print("Липсва DATABASE_URL в .env или --connection-string", file=sys.stderr)
        return 1

    sql_text = args.schema_file.read_text(encoding="utf-8")
    statements = _split_statements(sql_text)
    conn = psycopg2.connect(args.connection_string)
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            for i, stmt in enumerate(statements, 1):
                cur.execute(stmt)
        print(f"OK: изпълнени {len(statements)} SQL команди от {args.schema_file.name}")
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
