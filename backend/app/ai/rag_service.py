"""
Simple RAG service using keyword + text-similarity retrieval over MongoDB.
For a final-year project, this is a pragmatic baseline that can be
upgraded to Atlas Vector Search later.
"""
from app.db.mongodb import get_database
from app.ai.llm_client import llm_client
from app.ai.prompts import CHAT_RAG_PROMPT, SYSTEM_PROMPT_BASE
from typing import List, Dict, Any
import re
import logging

logger = logging.getLogger(__name__)


# Keyword → nutrient mapping for fast intent extraction
HEALTH_KEYWORDS = {
    "tired|fatigue|exhausted|low energy": ["Iron", "Vitamin B12", "Vitamin D", "Magnesium"],
    "immunity|cold|flu|sick often": ["Vitamin C", "Vitamin D", "Zinc"],
    "hair|skin|nails|beauty": ["Biotin", "Vitamin E", "Collagen", "Zinc"],
    "bone|joint|osteo": ["Calcium", "Vitamin D", "Magnesium"],
    "muscle|gym|workout|protein|gain": ["Protein", "Creatine", "BCAA"],
    "heart|cholesterol|cardio": ["Omega 3", "CoQ10", "Magnesium"],
    "brain|memory|focus|concentration": ["Omega 3", "Vitamin B12", "Ginkgo"],
    "sleep|insomnia|rest": ["Magnesium", "Melatonin", "Ashwagandha"],
    "stress|anxiety|calm": ["Ashwagandha", "Magnesium", "B-Complex"],
    "weight loss|fat burn|slim": ["Green Tea Extract", "L-Carnitine", "Protein"],
    "digestion|gut|stomach|bloat": ["Probiotics", "Fiber", "Digestive Enzymes"],
}


def extract_intent_nutrients(query: str) -> List[str]:
    """Quick keyword-based intent extraction."""
    query_lower = query.lower()
    matched = []
    for pattern, nutrients in HEALTH_KEYWORDS.items():
        if re.search(pattern, query_lower):
            matched.extend(nutrients)
    return list(set(matched))


async def retrieve_relevant_products(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Retrieve products relevant to query using text search + nutrient matching."""
    db = get_database()
    products = []

    # Step 1: MongoDB text search
    try:
        cursor = db.products.find(
            {"$text": {"$search": query}},
            {"score": {"$meta": "textScore"}}
        ).sort([("score", {"$meta": "textScore"})]).limit(limit)
        async for p in cursor:
            products.append(p)
    except Exception as e:
        logger.debug(f"Text search fallback: {e}")

    # Step 2: If too few, augment with nutrient-based matching
    if len(products) < limit:
        nutrients = extract_intent_nutrients(query)
        if nutrients:
            existing_ids = {str(p["_id"]) for p in products}
            cursor = db.products.find({
                "ingredients.name": {"$in": nutrients}
            }).limit(limit - len(products))
            async for p in cursor:
                if str(p["_id"]) not in existing_ids:
                    products.append(p)

    return products


def build_context_from_products(products: List[Dict[str, Any]]) -> str:
    """Format products as context for the LLM."""
    if not products:
        return "No specific products found in our database for this query."

    blocks = []
    for i, p in enumerate(products, 1):
        ing_names = ", ".join([ing.get("name", "") for ing in p.get("ingredients", [])][:5])
        summary = (p.get("ai_enrichment") or {}).get("simple_summary") or p.get("description_raw", "")[:200]
        block = (
            f"[{i}] {p.get('name', 'Unknown')} by {p.get('brand', '')}\n"
            f"    Category: {p.get('category', '')}\n"
            f"    Key Ingredients: {ing_names}\n"
            f"    Summary: {summary}\n"
        )
        blocks.append(block)
    return "\n".join(blocks)


async def answer_question(query: str) -> Dict[str, Any]:
    """Main RAG entry point — retrieve + generate."""
    # Retrieve
    products = await retrieve_relevant_products(query, limit=5)
    context = build_context_from_products(products)

    # Generate
    prompt = CHAT_RAG_PROMPT.format(context=context, question=query)
    answer = llm_client.chat(SYSTEM_PROMPT_BASE, prompt, temperature=0.4)

    # Format sources
    sources = [
        {
            "id": str(p["_id"]),
            "name": p.get("name"),
            "brand": p.get("brand"),
            "slug": p.get("slug"),
        }
        for p in products
    ]

    return {
        "answer": answer,
        "sources": sources,
        "matched_nutrients": extract_intent_nutrients(query),
    }
