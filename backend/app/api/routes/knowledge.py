"""
Knowledge Hub routes — educational content on vitamins, minerals, deficiencies.
"""
from fastapi import APIRouter, HTTPException
from app.db.mongodb import get_database
from typing import Optional

router = APIRouter(prefix="/api/knowledge", tags=["Knowledge Hub"])


def _serialize(item):
    item["_id"] = str(item["_id"])
    return item


@router.get("/vitamins")
async def list_vitamins():
    db = get_database()
    cursor = db.ingredients.find({"type": "vitamin"})
    items = []
    async for ing in cursor:
        items.append(_serialize(ing))
    return {"items": items}


@router.get("/minerals")
async def list_minerals():
    db = get_database()
    cursor = db.ingredients.find({"type": "mineral"})
    items = []
    async for ing in cursor:
        items.append(_serialize(ing))
    return {"items": items}


@router.get("/deficiencies")
async def list_deficiencies():
    db = get_database()
    cursor = db.deficiencies.find({})
    items = []
    async for d in cursor:
        items.append(_serialize(d))
    return {"items": items}


@router.get("/health-goals")
async def list_health_goals():
    """Static list of common health goals."""
    return {
        "goals": [
            {"key": "immunity", "name": "Immunity Boost", "icon": "🛡️"},
            {"key": "weight_loss", "name": "Weight Loss", "icon": "⚖️"},
            {"key": "muscle_gain", "name": "Muscle Gain", "icon": "💪"},
            {"key": "energy", "name": "Energy & Fatigue", "icon": "⚡"},
            {"key": "heart", "name": "Heart Health", "icon": "❤️"},
            {"key": "bone", "name": "Bone Health", "icon": "🦴"},
            {"key": "wellness", "name": "General Wellness", "icon": "🌿"},
            {"key": "sleep", "name": "Better Sleep", "icon": "😴"},
        ]
    }
