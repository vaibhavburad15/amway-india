"""
Chat & recommendation schemas.
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    session_id: str
    sources: List[Dict[str, Any]] = []
    disclaimer: str = "⚠️ Educational information only. Not medical advice. Consult a healthcare professional."


class RecommendationRequest(BaseModel):
    age: int
    gender: str  # male/female/other
    activity_level: str  # sedentary/active/athlete
    goal: str  # weight_loss/muscle_gain/immunity/wellness/energy
    diet: str  # veg/vegan/non-veg
    concerns: List[str] = []  # ["fatigue", "hair_loss", "joint_pain"]


class RecommendationResponse(BaseModel):
    recommended_products: List[Dict[str, Any]] = []
    explanation: str
    suggested_nutrients: List[str] = []
    disclaimer: str = "⚠️ For educational purposes only. Consult a doctor before starting supplements."


class IngredientExplainRequest(BaseModel):
    ingredient_name: str


class ProductSummaryRequest(BaseModel):
    product_id: str
    style: str = "simple"  # simple/technical/eli15
