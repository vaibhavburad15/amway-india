"""
Product Pydantic schemas for API request/response.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class IngredientInProduct(BaseModel):
    ingredient_id: Optional[str] = None
    name: str
    amount: Optional[float] = None
    unit: Optional[str] = None
    daily_value_percent: Optional[float] = None
    benefit: Optional[str] = None


class PricingInfo(BaseModel):
    region: str = "IN"
    currency: str = "INR"
    price: float
    mrp: Optional[float] = None


class ImageInfo(BaseModel):
    url: str
    alt: Optional[str] = ""
    is_primary: bool = False


class AIEnrichment(BaseModel):
    simple_summary: Optional[str] = None
    technical_summary: Optional[str] = None
    health_benefits: List[str] = []
    target_users: List[str] = []
    deficiencies_addressed: List[str] = []
    side_effects: List[str] = []
    last_generated_at: Optional[datetime] = None
    model_version: Optional[str] = None


class ProductBase(BaseModel):
    slug: str
    name: str
    brand: str
    category: str
    subcategory: Optional[str] = None
    pricing: List[PricingInfo] = []
    images: List[ImageInfo] = []
    description_raw: Optional[str] = ""
    ingredients: List[IngredientInProduct] = []
    ai_enrichment: Optional[AIEnrichment] = None
    reviews_summary: Optional[Dict[str, Any]] = None
    status: str = "active"


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    id: str = Field(..., alias="_id")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        populate_by_name = True


class ProductListResponse(BaseModel):
    id: str = Field(..., alias="_id")
    slug: str
    name: str
    brand: str
    category: str
    images: List[ImageInfo] = []
    pricing: List[PricingInfo] = []
    ai_summary: Optional[str] = None
    reviews_summary: Optional[Dict[str, Any]] = None

    class Config:
        populate_by_name = True
