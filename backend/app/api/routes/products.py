"""
Product routes.
"""
from fastapi import APIRouter, HTTPException, Query
from app.db.mongodb import get_database
from app.ai.llm_client import llm_client
from app.ai.prompts import PRODUCT_SUMMARY_PROMPT, SYSTEM_PROMPT_BASE
from bson import ObjectId
from typing import Optional, List
from datetime import datetime, timezone

router = APIRouter(prefix="/api/products", tags=["Products"])


def _serialize(p):
    p["_id"] = str(p["_id"])
    return p


@router.get("/")
async def list_products(
    q: Optional[str] = None,
    category: Optional[str] = None,
    brand: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
):
    """List products with optional filters."""
    db = get_database()
    query = {"status": "active"}

    if q:
        query["$text"] = {"$search": q}
    if category:
        query["category"] = category
    if brand:
        query["brand"] = {"$regex": f"^{brand}$", "$options": "i"}

    cursor = db.products.find(query).skip(skip).limit(limit)
    products = []
    async for p in cursor:
        products.append(_serialize(p))

    total = await db.products.count_documents(query)
    return {"items": products, "total": total, "skip": skip, "limit": limit}


@router.get("/categories")
async def list_categories():
    """Get unique categories."""
    db = get_database()
    cats = await db.products.distinct("category", {"status": "active"})
    return {"categories": sorted(cats)}


@router.get("/brands")
async def list_brands():
    """Get unique brands."""
    db = get_database()
    brands = await db.products.distinct("brand", {"status": "active"})
    return {"brands": sorted(brands)}


@router.get("/slug/{slug}")
async def get_product_by_slug(slug: str):
    """Get product by SEO slug."""
    db = get_database()
    product = await db.products.find_one({"slug": slug})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return _serialize(product)


@router.get("/{product_id}")
async def get_product(product_id: str):
    """Get product by ID."""
    db = get_database()
    try:
        product = await db.products.find_one({"_id": ObjectId(product_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid product ID")
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return _serialize(product)


@router.post("/{product_id}/summarize")
async def summarize_product(product_id: str, style: str = "simple"):
    """Generate (or fetch cached) AI summary for product."""
    db = get_database()
    try:
        product = await db.products.find_one({"_id": ObjectId(product_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid product ID")
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Return cached if exists
    enrichment = product.get("ai_enrichment") or {}
    if enrichment.get("simple_summary") and style == "simple":
        return {"summary": enrichment["simple_summary"], "cached": True}

    # Generate new
    ingredients_str = ", ".join([ing.get("name", "") for ing in product.get("ingredients", [])])
    prompt = PRODUCT_SUMMARY_PROMPT.format(
        name=product.get("name", ""),
        brand=product.get("brand", ""),
        category=product.get("category", ""),
        ingredients=ingredients_str,
        description=product.get("description_raw", "")[:500],
    )
    summary = llm_client.chat(SYSTEM_PROMPT_BASE, prompt, temperature=0.4)

    # Cache it
    await db.products.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": {
            "ai_enrichment.simple_summary": summary,
            "ai_enrichment.last_generated_at": datetime.now(timezone.utc),
            "ai_enrichment.model_version": "groq-llama-3.3-70b",
        }}
    )
    return {"summary": summary, "cached": False}


@router.post("/compare")
async def compare_products(product_ids: List[str]):
    """Compare 2-4 products side by side."""
    if len(product_ids) < 2 or len(product_ids) > 4:
        raise HTTPException(status_code=400, detail="Provide 2 to 4 product IDs")

    db = get_database()
    products = []
    for pid in product_ids:
        try:
            p = await db.products.find_one({"_id": ObjectId(pid)})
            if p:
                products.append(_serialize(p))
        except Exception:
            continue

    if len(products) < 2:
        raise HTTPException(status_code=404, detail="Not enough valid products to compare")

    return {"products": products}
