#!/usr/bin/env python3
import argparse, json, os, math, re, sys
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.ingest import upsert_from_json, ensure_tables
from app.models import Recipe

def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    parser = argparse.ArgumentParser(description="Load recipes JSON into SQLite DB")
    parser.add_argument("--json", required=True, help="Path to recipes JSON file")
    parser.add_argument("--db", default="./recipes.db", help="SQLite DB path (default: ./recipes.db)")
    args = parser.parse_args()

    
    ensure_tables()

    data = load_json(args.json)

    if isinstance(data, dict):
        
        items = [data[k] for k in sorted(data.keys(), key=lambda x: int(x) if str(x).isdigit() else x)]
    elif isinstance(data, list):
        items = data
    else:
        print("Unsupported JSON structure", file=sys.stderr)
        sys.exit(2)

    db: Session = SessionLocal()
    try:
        count = 0
        for rec in items:
            upsert_from_json(db, rec)
            count += 1
            if count % 100 == 0:
                db.commit()
        db.commit()
        print(f"Inserted {count} recipes")
    finally:
        db.close()

if __name__ == "__main__":
    main()
