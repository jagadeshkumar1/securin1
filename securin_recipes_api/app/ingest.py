import json, math, re
from typing import Any, Dict
from sqlalchemy.orm import Session
from .models import Recipe
from .database import Base, engine

def parse_int(value):
    if value is None:
        return None
    try:
        if isinstance(value, float) and math.isnan(value):
            return None
    except Exception:
        pass
    if isinstance(value, int):
        return value
    # extract first integer from strings like "389 kcal" or "45 mg"
    if isinstance(value, str):
        m = re.search(r"-?\d+", value.replace(',', ''))
        if m:
            try:
                return int(m.group(0))
            except Exception:
                return None
        return None
    if isinstance(value, float):
        return int(value)
    return None

def to_nullable(v):
    try:
        if isinstance(v, float) and math.isnan(v):
            return None
    except Exception:
        pass
    return v

def extract_calories(nutrients: Dict[str, Any] | None):
    if not nutrients:
        return None
    # Try multiple keys
    for k in ["calories", "calorieContent", "energy", "energyKcal"]:
        if k in nutrients and nutrients[k] is not None:
            return parse_int(nutrients[k])
    return None

def ensure_tables():
    Base.metadata.create_all(bind=engine)

def upsert_from_json(db: Session, data: Dict[str, Any]):
    # incoming dict has keys described in the PDF
    nutrients = data.get("nutrients")
    calories = extract_calories(nutrients) if isinstance(nutrients, dict) else None

    rec = Recipe(
        cuisine=to_nullable(data.get("cuisine")),
        title=data.get("title") if data.get("title") and not isinstance(data.get("title"), float) else "Untitled",
        url=to_nullable(data.get("URL") or data.get("url")),
        rating=to_nullable(data.get("rating")),
        total_time=parse_int(data.get("total_time")),
        prep_time=parse_int(data.get("prep_time")),
        cook_time=parse_int(data.get("cook_time")),
        description=to_nullable(data.get("description")),
        nutrients_json=json.dumps(nutrients) if isinstance(nutrients, dict) else None,
        serves=to_nullable(data.get("serves")),
        calories=calories,
    )
    db.add(rec)
    return rec
