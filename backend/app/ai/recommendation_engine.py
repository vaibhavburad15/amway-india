"""
Rule-based + AI-assisted supplement recommendation engine.
"""
from app.db.mongodb import get_database
from app.ai.llm_client import llm_client
from app.ai.prompts import RECOMMENDATION_PROMPT, SYSTEM_PROMPT_BASE
from typing import List, Dict, Any


# Goal → priority nutrients mapping
GOAL_NUTRIENTS = {
    "weight_loss": ["Protein", "Green Tea Extract", "L-Carnitine", "Fiber", "B-Complex"],
    "muscle_gain": ["Protein", "Creatine", "BCAA", "Vitamin D", "Zinc"],
    "immunity": ["Vitamin C", "Vitamin D", "Zinc", "Elderberry"],
    "wellness": ["Multivitamin", "Omega 3", "Vitamin D", "Probiotics"],
    "energy": ["Vitamin B12", "Iron", "CoQ10", "Magnesium", "B-Complex"],
    "heart": ["Omega 3", "CoQ10", "Magnesium", "Vitamin K2"],
    "bone": ["Calcium", "Vitamin D", "Magnesium", "Vitamin K2"],
}

# Diet-based extras
DIET_NUTRIENTS = {
    "vegan": ["Vitamin B12", "Iron", "Vitamin D", "Omega 3 (algal)"],
    "vegetarian": ["Vitamin B12", "Iron", "Omega 3"],
    "non-veg": [],
}

# Activity adjustments
ACTIVITY_NUTRIENTS = {
    "athlete": ["Protein", "Electrolytes", "BCAA", "Magnesium"],
    "active": ["Protein", "Magnesium", "Vitamin D"],
    "sedentary": ["Multivitamin", "Vitamin D"],
}


def compute_priority_nutrients(profile: Dict[str, Any]) -> List[str]:
    """Compute priority nutrients based on user profile."""
    nutrients = set()
    nutrients.update(GOAL_NUTRIENTS.get(profile["goal"], []))
    nutrients.update(DIET_NUTRIENTS.get(profile["diet"], []))
    nutrients.update(ACTIVITY_NUTRIENTS.get(profile["activity_level"], []))

    # Age-based
    if profile["age"] >= 50:
        nutrients.update(["Calcium", "Vitamin D", "Vitamin B12"])
    if profile["age"] <= 25 and profile.get("gender") == "female":
        nutrients.add("Iron")

    # Concerns
    for concern in profile.get("concerns", []):
        c = concern.lower()
        if "fatigue" in c or "tired" in c:
            nutrients.update(["Iron", "Vitamin B12", "Vitamin D"])
        if "hair" in c or "skin" in c:
            nutrients.update(["Biotin", "Zinc", "Vitamin E"])
        if "joint" in c:
            nutrients.update(["Vitamin D", "Calcium", "Omega 3"])
        if "sleep" in c:
            nutrients.update(["Magnesium", "Melatonin"])
        if "stress" in c:
            nutrients.update(["Ashwagandha", "Magnesium", "B-Complex"])

    return list(nutrients)


async def find_matching_products(nutrients: List[str], limit: int = 6) -> List[Dict[str, Any]]:
    """Find products containing the priority nutrients."""
    db = get_database()
    cursor = db.products.find({
        "ingredients.name": {"$in": nutrients},
        "status": "active",
    }).limit(limit)

    products = []
    async for p in cursor:
        # Score: count matching ingredients
        matches = [ing["name"] for ing in p.get("ingredients", []) if ing.get("name") in nutrients]
        p["match_score"] = len(matches)
        p["matched_ingredients"] = matches
        products.append(p)

    # Sort by score
    products.sort(key=lambda x: x["match_score"], reverse=True)
    return products


async def generate_recommendation(profile: Dict[str, Any]) -> Dict[str, Any]:
    """Main recommendation generator."""
    # Step 1: Compute nutrients
    nutrients = compute_priority_nutrients(profile)

    # Step 2: Find matching products
    products = await find_matching_products(nutrients, limit=6)

    # Step 3: AI explanation
    product_summary = "\n".join([
        f"- {p['name']} ({p['brand']}): contains {', '.join(p['matched_ingredients'][:3])}"
        for p in products[:4]
    ]) or "No matching products in current database."

    prompt = RECOMMENDATION_PROMPT.format(
        age=profile["age"],
        gender=profile["gender"],
        activity_level=profile["activity_level"],
        goal=profile["goal"],
        diet=profile["diet"],
        concerns=", ".join(profile.get("concerns", [])) or "none",
        products=product_summary,
    )
    explanation = llm_client.chat(SYSTEM_PROMPT_BASE, prompt, temperature=0.5)

    # Format products for response
    rec_products = [
        {
            "id": str(p["_id"]),
            "slug": p.get("slug"),
            "name": p.get("name"),
            "brand": p.get("brand"),
            "category": p.get("category"),
            "matched_ingredients": p.get("matched_ingredients", []),
            "images": p.get("images", []),
            "pricing": p.get("pricing", []),
        }
        for p in products
    ]

    return {
        "recommended_products": rec_products,
        "explanation": explanation,
        "suggested_nutrients": nutrients,
    }
