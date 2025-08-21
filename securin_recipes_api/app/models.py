from sqlalchemy import Column, Integer, String, Float, Text

from .database import Base

class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cuisine = Column(String, index=True, nullable=True)
    title = Column(String, index=True, nullable=False)
    url = Column(String, nullable=True)
    rating = Column(Float, index=True, nullable=True)
    total_time = Column(Integer, index=True, nullable=True)
    prep_time = Column(Integer, nullable=True)
    cook_time = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    nutrients_json = Column(Text, nullable=True)  
    serves = Column(String, nullable=True)
    calories = Column(Integer, index=True, nullable=True) 