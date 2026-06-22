"""
Prompt templates for various AI tasks.
"""

SYSTEM_PROMPT_BASE = """You are NutriGuide AI, a knowledgeable assistant specialized in supplements, vitamins, minerals, and nutrition.

Core Rules:
1. NEVER diagnose diseases or prescribe treatments
2. ALWAYS recommend consulting a healthcare professional for medical concerns
3. Base answers on scientific evidence; cite when possible
4. Be honest about uncertainty
5. Refuse queries about: dosing for infants/pregnancy, drug interactions (defer to pharmacist), replacing medication
6. Use simple, clear language unless asked for technical depth
"""

PRODUCT_SUMMARY_PROMPT = """Generate a concise, friendly product summary for the following supplement.
Focus on: what it does, who it's for, key benefits.
Keep it under 100 words. Use simple language.

Product Name: {name}
Brand: {brand}
Category: {category}
Ingredients: {ingredients}
Raw Description: {description}

Write the summary:"""

INGREDIENT_EXPLAIN_PROMPT = """Provide a clear explanation of the supplement ingredient '{ingredient}'.

Structure your response with these sections (use markdown headers):
## What it is
## Why we need it
## Health benefits (3-5 bullets)
## Daily requirement (adult)
## Food sources
## Possible side effects
## Important precautions

Keep total length under 350 words. Be evidence-based."""

CHAT_RAG_PROMPT = """You are answering a user's health/supplement question.

Use the following context from our supplement database to inform your answer.
If the context doesn't contain relevant info, say so and provide general guidance.
Always end with a medical disclaimer.

CONTEXT:
{context}

USER QUESTION: {question}

Provide a helpful, evidence-based answer:"""

RECOMMENDATION_PROMPT = """Based on the user profile below, recommend supplements and nutrients.

User Profile:
- Age: {age}
- Gender: {gender}
- Activity Level: {activity_level}
- Goal: {goal}
- Diet: {diet}
- Concerns: {concerns}

Available Products in our database:
{products}

Provide:
1. Top 3 nutrient priorities for this person (with brief reason)
2. Why these matter for their goal
3. General lifestyle tips

Keep it under 250 words. End with disclaimer."""

SAFETY_CHECK_PROMPT = """Determine if the following user query is safe to answer in a supplement-information context.

UNSAFE topics:
- Specific medical diagnosis
- Replacing prescription medication
- Dosing for pregnant women, infants, or specific diseases
- Self-harm or suicide
- Illegal substances

User Query: {query}

Respond with only: SAFE or UNSAFE: <brief reason>"""
