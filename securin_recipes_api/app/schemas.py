from typing import Optional, Dict, Any, List
from pydantic import BaseModel, field_validator

class RecipeBase(BaseModel):
    cuisine: Optional[str] = None
    title: str
    url: Optional[str] = None
    rating: Optional[float] = None
    total_time: Optional[int] = None
    prep_time: Optional[int] = None
    cook_time: Optional[int] = None
    description: Optional[str] = None
    nutrients: Optional[Dict[str, Any]] = None
    serves: Optional[str] = None
    calories: Optional[int] = None

class RecipeOut(RecipeBase):
    id: int
    class Config:
        from_attributes = True  
class PaginatedRecipes(BaseModel):
    total: int
    page: int
    limit: int
    results: List[RecipeOut]
