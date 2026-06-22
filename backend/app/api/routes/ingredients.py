"""
Ingredient routes — list, detail, AI-explain.
"""
from fastapi import APIRouter, HTTPException
from app.db.mongodb import get_database
from app.ai.llm_client import llm_client
from app.ai.prompts import INGREDIENT_EXPLAIN_PROMPT, SYSTEM_PROMPT_BASE
from bson import ObjectId
from typing import Optional
from datetime import datetime, timezone

router = APIRouter(prefix="/api/ingredients", tags=["Ingredients"])


def _serialize(item):
    item["_id"] = str(item["_id"])
    return item


@router.get("/")
async def list_ingredients(type: Optional[str] = None, skip: int = 0, limit: int = 50):
    db = get_database()
    query = {}
    if type:
        query["type"] = type
    cursor = db.ingredients.find(query).skip(skip).limit(limit)
    items = []
    async for ing in cursor:
        items.append(_serialize(ing))
    total = await db.ingredients.count_documents(query)
    return {"items": items, "total": total}


@router.get("/{ingredient_id}")
async def get_ingredient(ingredient_id: str):
    db = get_database()
    try:
        ing = await db.ingredients.find_one({"_id": ObjectId(ingredient_id)})
    except Exception:
        # Try by name
        ing = await db.ingredients.find_one({"name": {"$regex": f"^{ingredient_id}$", "$options": "i"}})
    if not ing:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return _serialize(ing)


@router.post("/explain")
async def explain_ingredient(payload: dict):
    """AI-powered ingredient explanation. Cached in DB."""
    name = payload.get("ingredient_name", "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="ingredient_name required")

    db = get_database()
    # Look up existing
    ing = await db.ingredients.find_one({"name": {"$regex": f"^{name}$", "$options": "i"}})

    # Return cached if available
    if ing and (ing.get("ai_explanation") or {}).get("purpose"):
        return {
            "name": ing["name"],
            "explanation_markdown": ing["ai_explanation"].get("purpose"),
            "cached": True,
        }

    # Generate via LLM
    prompt = INGREDIENT_EXPLAIN_PROMPT.format(ingredient=name)
    explanation = llm_client.chat(SYSTEM_PROMPT_BASE, prompt, temperature=0.3)

    # Save / cache
    if ing:
        await db.ingredients.update_one(
            {"_id": ing["_id"]},
            {"$set": {
                "ai_explanation.purpose": explanation,
                "ai_explanation.last_generated_at": datetime.now(timezone.utc),
            }}
        )
    else:
        await db.ingredients.insert_one({
            "name": name,
            "aliases": [],
            "type": "unknown",
            "ai_explanation": {
                "purpose": explanation,
                "last_generated_at": datetime.now(timezone.utc),
            },
        })

    return {"name": name, "explanation_markdown": explanation, "cached": False}
