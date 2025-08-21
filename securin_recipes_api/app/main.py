from fastapi import FastAPI, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from typing import Optional, List, Any, Dict
import json

from .database import get_db
from .models import Recipe
from .schemas import RecipeOut, PaginatedRecipes
from .ingest import ensure_tables

app = FastAPI(title="Securin Recipes API", version="1.0.0")

@app.on_event("startup")
def startup_create_tables():
    ensure_tables()

def _to_recipe_out(row: Recipe) -> RecipeOut:
    nutrients = None
    if row.nutrients_json:
        try:
            nutrients = json.loads(row.nutrients_json)
        except Exception:
            nutrients = None
    return RecipeOut(
        id=row.id,
        cuisine=row.cuisine,
        title=row.title,
        url=row.url,
        rating=row.rating,
        total_time=row.total_time,
        prep_time=row.prep_time,
        cook_time=row.cook_time,
        description=row.description,
        nutrients=nutrients,
        serves=row.serves,
        calories=row.calories,
    )

@app.get("/api/recipes", response_model=PaginatedRecipes)
def list_recipes(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query("rating"),
    order: str = Query("desc"),
    db: Session = Depends(get_db),
):
    sort_map = {
        "rating": Recipe.rating,
        "total_time": Recipe.total_time,
        "title": Recipe.title,
        "calories": Recipe.calories,
        "cuisine": Recipe.cuisine,
        "id": Recipe.id,
    }
    sort_col = sort_map.get(sort_by, Recipe.rating)
    sorter = desc(sort_col) if order.lower() == "desc" else asc(sort_col)

    q = db.query(Recipe).order_by(sorter)
    total = q.count()
    rows = q.offset((page - 1) * limit).limit(limit).all()
    return PaginatedRecipes(
        total=total,
        page=page,
        limit=limit,
        results=[_to_recipe_out(r) for r in rows],
    )

@app.get("/api/recipes/{recipe_id}", response_model=RecipeOut)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    row = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return _to_recipe_out(row)

@app.get("/api/recipes/search", response_model=PaginatedRecipes)
def search_recipes(
    title: Optional[str] = None,
    cuisine: Optional[str] = None,
    min_rating: Optional[float] = Query(None, ge=0, le=5),
    max_total_time: Optional[int] = Query(None, ge=0),
    min_calories: Optional[int] = Query(None, ge=0),
    max_calories: Optional[int] = Query(None, ge=0),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query("rating"),
    order: str = Query("desc"),
    db: Session = Depends(get_db),
):
    sort_map = {
        "rating": Recipe.rating,
        "total_time": Recipe.total_time,
        "title": Recipe.title,
        "calories": Recipe.calories,
        "cuisine": Recipe.cuisine,
        "id": Recipe.id,
    }
    sort_col = sort_map.get(sort_by, Recipe.rating)
    sorter = desc(sort_col) if order.lower() == "desc" else asc(sort_col)

    q = db.query(Recipe)

    if title:
        q = q.filter(Recipe.title.ilike(f"%{title}%"))
    if cuisine:
        q = q.filter(Recipe.cuisine.ilike(f"%{cuisine}%"))
    if min_rating is not None:
        q = q.filter(Recipe.rating >= min_rating)
    if max_total_time is not None:
        q = q.filter(Recipe.total_time <= max_total_time)
    if min_calories is not None:
        q = q.filter(Recipe.calories >= min_calories)
    if max_calories is not None:
        q = q.filter(Recipe.calories <= max_calories)

    q = q.order_by(sorter)
    total = q.count()
    rows = q.offset((page - 1) * limit).limit(limit).all()
    return PaginatedRecipes(
        total=total,
        page=page,
        limit=limit,
        results=[_to_recipe_out(r) for r in rows],
    )
