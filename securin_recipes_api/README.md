# Securin Recipes Assignment — FastAPI Solution

This repo parses a recipes JSON file, stores it in a SQLite database, and exposes REST APIs with pagination, sorting, and search filters.

## Tech
- FastAPI + Uvicorn
- SQLAlchemy (SQLite)
- Pydantic

## Setup

```bash
python -m venv .venv
source .venv/bin/activate 
pip install -r requirements.txt
```

## Load Data

Place your JSON file (e.g., `US_recipes.json`) in the project root and run:

```bash
python ingest_cli.py --json US_recipes.json
```

This creates `recipes.db` and inserts all records (with NaN -> NULL). Calories are extracted from `nutrients.calories` if present (e.g., "389 kcal").

## Run API

```bash
uvicorn app.main:app --reload
```

Open Swagger: http://127.0.0.1:8000/docs

## Endpoints

- `GET /api/recipes`  
  Query params: `page`, `limit` (<=100), `sort_by` (`rating|total_time|title|calories|cuisine|id`), `order` (`asc|desc`).

- `GET /api/recipes/{id}` — single recipe

- `GET /api/recipes/search`  
  Filters: `title`, `cuisine`, `min_rating`, `max_total_time`, `min_calories`, `max_calories`  
  Also supports `page`, `limit`, `sort_by`, `order`.

## Examples

Top-rated 10 recipes:
```bash
curl "http://127.0.0.1:8000/api/recipes?limit=10&sort_by=rating&order=desc"
```

Search low-calorie Southern recipes under 30 minutes:
```bash
curl "http://127.0.0.1:8000/api/recipes/search?cuisine=Southern&max_calories=300&max_total_time=30&sort_by=total_time&order=asc"
```

Search by title:
```bash
curl "http://127.0.0.1:8000/api/recipes/search?title=chicken&min_rating=4.5"
```

## Notes
- Nutrients are kept as raw JSON (`nutrients_json`) and calories also extracted to an integer column for fast filtering.
- Any numeric-like string fields are coerced (e.g., `"389 kcal"` -> `389`).
- `NaN` values from the JSON are converted to `NULL`.
