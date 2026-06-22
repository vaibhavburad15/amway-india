"""
Ingredient schemas.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class IngredientAIExplanation(BaseModel):
    purpose: Optional[str] = None
    benefits: List[str] = []
    daily_requirement: Optional[Dict[str, str]] = None
    upper_limit: Optional[str] = None
    side_effects: List[str] = []
    interactions: List[str] = []
    food_sources: List[str] = []


class IngredientBase(BaseModel):
    name: str
    aliases: List[str] = []
    type: str = "vitamin"
    ai_explanation: Optional[IngredientAIExplanation] = None


class IngredientCreate(IngredientBase):
    pass


class IngredientResponse(IngredientBase):
    id: str = Field(..., alias="_id")

    class Config:
        populate_by_name = True
