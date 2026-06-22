"""
Seed the local MongoDB database with reference data and Amway India products.
Run: python scripts/seed_database.py
"""
import sys
import os
import re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from app.core.config import settings
from app.services.amway_india import fetch_amway_india_products

NOW = datetime.now(timezone.utc)


def _brand_slug(name: str) -> str:
    return re.sub(r"-{2,}", "-", re.sub(r"[^a-z0-9]+", "-", name.lower())).strip("-")


def _brands_from_products(products):
    return [
        {
            "slug": _brand_slug(brand),
            "name": brand,
            "country": "India",
            "description": "Brand listed in the official Amway India product catalog.",
        }
        for brand in sorted({p["brand"] for p in products if p.get("brand")})
    ]


# ============ INGREDIENTS ============
INGREDIENTS = [
    {
        "name": "Vitamin D3",
        "aliases": ["Cholecalciferol", "Vit D3"],
        "type": "vitamin",
        "ai_explanation": {
            "purpose": "Vitamin D3 is essential for calcium absorption, bone health, and immune function.",
            "benefits": ["Strong bones", "Immune support", "Mood regulation", "Muscle function"],
            "daily_requirement": {"adult": "600-800 IU"},
            "upper_limit": "4000 IU",
            "side_effects": ["Nausea at high doses", "Kidney issues with excess"],
            "food_sources": ["Fatty fish", "Egg yolks", "Fortified milk", "Sunlight exposure"],
        },
    },
    {
        "name": "Vitamin B12",
        "aliases": ["Cobalamin", "Cyanocobalamin"],
        "type": "vitamin",
        "ai_explanation": {
            "purpose": "B12 is crucial for nerve function, DNA synthesis, and red blood cell formation.",
            "benefits": ["Energy production", "Brain health", "Prevents anemia", "Nerve health"],
            "daily_requirement": {"adult": "2.4 mcg"},
            "side_effects": ["Generally safe; rare allergic reactions"],
            "food_sources": ["Meat", "Fish", "Eggs", "Dairy", "Fortified cereals"],
        },
    },
    {
        "name": "Vitamin C",
        "aliases": ["Ascorbic Acid"],
        "type": "vitamin",
        "ai_explanation": {
            "purpose": "Powerful antioxidant supporting immunity, collagen synthesis, and iron absorption.",
            "benefits": ["Immune boost", "Skin health", "Antioxidant protection", "Iron absorption"],
            "daily_requirement": {"adult_male": "90 mg", "adult_female": "75 mg"},
            "upper_limit": "2000 mg",
            "side_effects": ["Stomach upset", "Diarrhea at high doses"],
            "food_sources": ["Citrus fruits", "Bell peppers", "Strawberries", "Broccoli"],
        },
    },
    {
        "name": "Iron",
        "aliases": ["Ferrous sulfate", "Fe"],
        "type": "mineral",
        "ai_explanation": {
            "purpose": "Iron is essential for hemoglobin production and oxygen transport in blood.",
            "benefits": ["Prevents anemia", "Boosts energy", "Cognitive function"],
            "daily_requirement": {"adult_male": "8 mg", "adult_female": "18 mg"},
            "upper_limit": "45 mg",
            "side_effects": ["Constipation", "Nausea", "Dark stools"],
            "food_sources": ["Red meat", "Spinach", "Lentils", "Fortified cereals"],
        },
    },
    {
        "name": "Calcium",
        "aliases": ["Ca"],
        "type": "mineral",
        "ai_explanation": {
            "purpose": "The most abundant mineral in the body; vital for bones, teeth, and muscle function.",
            "benefits": ["Bone strength", "Muscle contraction", "Nerve signaling", "Blood clotting"],
            "daily_requirement": {"adult": "1000 mg"},
            "upper_limit": "2500 mg",
            "side_effects": ["Constipation", "Kidney stones at high doses"],
            "food_sources": ["Dairy", "Leafy greens", "Almonds", "Sardines"],
        },
    },
    {
        "name": "Zinc",
        "aliases": ["Zn"],
        "type": "mineral",
        "ai_explanation": {
            "purpose": "Trace mineral supporting immunity, wound healing, and DNA synthesis.",
            "benefits": ["Immune support", "Skin health", "Wound healing", "Taste & smell"],
            "daily_requirement": {"adult_male": "11 mg", "adult_female": "8 mg"},
            "upper_limit": "40 mg",
            "side_effects": ["Nausea", "Reduced copper absorption at high doses"],
            "food_sources": ["Oysters", "Beef", "Pumpkin seeds", "Chickpeas"],
        },
    },
    {
        "name": "Magnesium",
        "aliases": ["Mg"],
        "type": "mineral",
        "ai_explanation": {
            "purpose": "Involved in 300+ enzymatic reactions; supports muscle, nerve, and bone health.",
            "benefits": ["Better sleep", "Muscle relaxation", "Stress reduction", "Heart health"],
            "daily_requirement": {"adult_male": "400 mg", "adult_female": "310 mg"},
            "upper_limit": "350 mg (from supplements)",
            "side_effects": ["Diarrhea at high doses"],
            "food_sources": ["Dark chocolate", "Nuts", "Seeds", "Leafy greens"],
        },
    },
    {
        "name": "Omega 3",
        "aliases": ["EPA", "DHA", "Fish Oil"],
        "type": "fatty_acid",
        "ai_explanation": {
            "purpose": "Essential fatty acids critical for brain, heart, and eye health.",
            "benefits": ["Heart health", "Brain function", "Reduces inflammation", "Eye health"],
            "daily_requirement": {"adult": "250-500 mg EPA+DHA"},
            "side_effects": ["Fishy aftertaste", "Mild GI upset"],
            "food_sources": ["Fatty fish", "Flaxseed", "Walnuts", "Chia seeds"],
        },
    },
    {
        "name": "Protein",
        "aliases": ["Whey Protein", "Casein"],
        "type": "macronutrient",
        "ai_explanation": {
            "purpose": "Building block of muscle, enzymes, and hormones.",
            "benefits": ["Muscle growth", "Recovery", "Satiety", "Immune function"],
            "daily_requirement": {"adult": "0.8-1.2 g/kg body weight"},
            "side_effects": ["Excess may strain kidneys"],
            "food_sources": ["Chicken", "Eggs", "Lentils", "Greek yogurt", "Whey powder"],
        },
    },
    {
        "name": "Biotin",
        "aliases": ["Vitamin B7", "Vitamin H"],
        "type": "vitamin",
        "ai_explanation": {
            "purpose": "B-vitamin important for hair, skin, nails, and metabolism.",
            "benefits": ["Healthy hair", "Strong nails", "Skin health", "Energy metabolism"],
            "daily_requirement": {"adult": "30 mcg"},
            "side_effects": ["Generally safe; may interfere with lab tests"],
            "food_sources": ["Eggs", "Almonds", "Sweet potato", "Salmon"],
        },
    },
    {
        "name": "Creatine",
        "aliases": ["Creatine Monohydrate"],
        "type": "amino_acid",
        "ai_explanation": {
            "purpose": "Stored in muscles; rapidly produces energy for short, intense exercise.",
            "benefits": ["Increased strength", "Muscle gain", "Improved performance"],
            "daily_requirement": {"athlete": "3-5 g/day"},
            "side_effects": ["Water retention", "Mild GI upset"],
            "food_sources": ["Red meat", "Fish (small amounts)"],
        },
    },
    {
        "name": "BCAA",
        "aliases": ["Branched Chain Amino Acids", "Leucine", "Isoleucine", "Valine"],
        "type": "amino_acid",
        "ai_explanation": {
            "purpose": "Essential amino acids that support muscle protein synthesis and reduce fatigue.",
            "benefits": ["Reduced muscle soreness", "Better workout performance", "Muscle preservation"],
            "daily_requirement": {"athlete": "5-10 g/day"},
            "side_effects": ["Generally well tolerated"],
            "food_sources": ["Eggs", "Chicken", "Whey protein"],
        },
    },
    {
        "name": "Ashwagandha",
        "aliases": ["Withania somnifera"],
        "type": "herb",
        "ai_explanation": {
            "purpose": "Adaptogenic herb used in Ayurveda for stress relief and vitality.",
            "benefits": ["Reduces stress", "Better sleep", "Improved focus", "Energy"],
            "daily_requirement": {"adult": "300-600 mg extract"},
            "side_effects": ["Drowsiness", "Avoid in pregnancy"],
            "food_sources": ["Not naturally in food; supplement form"],
        },
    },
    {
        "name": "Probiotics",
        "aliases": ["Lactobacillus", "Bifidobacterium"],
        "type": "other",
        "ai_explanation": {
            "purpose": "Beneficial bacteria that support gut health and immunity.",
            "benefits": ["Digestive health", "Immune support", "Reduced bloating"],
            "daily_requirement": {"adult": "1-10 billion CFU"},
            "side_effects": ["Initial bloating", "Generally safe"],
            "food_sources": ["Yogurt", "Kefir", "Kimchi", "Sauerkraut"],
        },
    },
    {
        "name": "Vitamin E",
        "aliases": ["Tocopherol"],
        "type": "vitamin",
        "ai_explanation": {
            "purpose": "Fat-soluble antioxidant protecting cells from oxidative damage.",
            "benefits": ["Skin health", "Antioxidant protection", "Eye health"],
            "daily_requirement": {"adult": "15 mg"},
            "upper_limit": "1000 mg",
            "side_effects": ["Bleeding risk at high doses"],
            "food_sources": ["Almonds", "Sunflower seeds", "Spinach", "Avocado"],
        },
    },
]


# ============ PRODUCTS ============
PRODUCTS = [
    {
        "slug": "nutrilite-daily-multivitamin",
        "name": "Nutrilite Daily Multivitamin",
        "brand": "Amway",
        "category": "Multivitamin",
        "subcategory": "Daily Essentials",
        "pricing": [{"region": "IN", "currency": "INR", "price": 1899, "mrp": 2199}],
        "images": [{
            "url": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=600",
            "alt": "Nutrilite Daily",
            "is_primary": True
        }],
        "description_raw": "Nutrilite Daily provides 13 essential vitamins and 8 minerals plus a concentrated blend of plant nutrients from 5 plants. Supports overall wellness, immunity, and energy.",
        "ingredients": [
            {"name": "Vitamin D3", "amount": 400, "unit": "IU", "benefit": "Bone Health"},
            {"name": "Vitamin B12", "amount": 6, "unit": "mcg", "benefit": "Energy & Nerve Function"},
            {"name": "Vitamin C", "amount": 60, "unit": "mg", "benefit": "Immunity"},
            {"name": "Iron", "amount": 18, "unit": "mg", "benefit": "Blood Formation"},
            {"name": "Calcium", "amount": 162, "unit": "mg", "benefit": "Bone Strength"},
            {"name": "Zinc", "amount": 15, "unit": "mg", "benefit": "Immune Support"},
            {"name": "Vitamin E", "amount": 30, "unit": "IU", "benefit": "Antioxidant"},
        ],
        "ai_enrichment": {
            "simple_summary": "Nutrilite Daily is a comprehensive multivitamin from Amway providing 13 vitamins and 8 minerals daily. It's designed for adults seeking overall wellness, energy, and immune support. Ideal for busy professionals, students, and anyone with an irregular diet.",
            "health_benefits": ["Boosts immunity", "Supports energy production", "Improves bone health", "Aids metabolism", "Antioxidant protection"],
            "target_users": ["Working professionals", "Students", "Adults 18-50", "Vegetarians (check label)"],
            "deficiencies_addressed": ["Vitamin D deficiency", "B12 deficiency", "Iron deficiency", "Zinc deficiency"],
            "side_effects": ["May cause mild stomach upset if taken on empty stomach", "Iron may cause constipation in some"],
            "model_version": "seed-data",
            "last_generated_at": NOW,
        },
        "reviews_summary": {"avg": 4.3, "count": 1247},
        "status": "active",
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "slug": "herbalife-formula-1-shake",
        "name": "Herbalife Formula 1 Nutritional Shake Mix",
        "brand": "Herbalife",
        "category": "Meal Replacement",
        "subcategory": "Weight Management",
        "pricing": [{"region": "IN", "currency": "INR", "price": 2599, "mrp": 2999}],
        "images": [{
            "url": "https://images.unsplash.com/photo-1622484212850-eb596d769edc?w=600",
            "alt": "Herbalife Formula 1",
            "is_primary": True
        }],
        "description_raw": "Healthy meal in a glass. Provides essential nutrients with protein and fiber. Helps with weight management and balanced nutrition.",
        "ingredients": [
            {"name": "Protein", "amount": 17, "unit": "g", "benefit": "Muscle & Satiety"},
            {"name": "Vitamin C", "amount": 30, "unit": "mg", "benefit": "Immunity"},
            {"name": "Calcium", "amount": 350, "unit": "mg", "benefit": "Bone Health"},
            {"name": "Iron", "amount": 4, "unit": "mg", "benefit": "Energy"},
            {"name": "Vitamin B12", "amount": 1.5, "unit": "mcg", "benefit": "Metabolism"},
        ],
        "ai_enrichment": {
            "simple_summary": "Herbalife Formula 1 is a protein-rich meal replacement shake designed for weight management and balanced nutrition. With 17g protein and 21 essential nutrients per serving, it's popular for those seeking convenient meal solutions.",
            "health_benefits": ["Weight management", "Convenient nutrition", "Muscle support", "Sustained energy"],
            "target_users": ["Adults managing weight", "Busy professionals", "People skipping meals"],
            "deficiencies_addressed": ["Protein gaps", "Multi-nutrient gaps"],
            "side_effects": ["May cause bloating initially", "Not a substitute for whole foods long-term"],
            "model_version": "seed-data",
            "last_generated_at": NOW,
        },
        "reviews_summary": {"avg": 4.1, "count": 892},
        "status": "active",
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "slug": "gnc-mega-men-multivitamin",
        "name": "GNC Mega Men Sport Multivitamin",
        "brand": "GNC",
        "category": "Multivitamin",
        "subcategory": "Men's Health",
        "pricing": [{"region": "IN", "currency": "INR", "price": 2199, "mrp": 2499}],
        "images": [{
            "url": "https://images.unsplash.com/photo-1550572017-edd951aa8f56?w=600",
            "alt": "GNC Mega Men",
            "is_primary": True
        }],
        "description_raw": "Premium multivitamin formulated for active men. Supports muscle function, energy, and recovery.",
        "ingredients": [
            {"name": "Vitamin D3", "amount": 1000, "unit": "IU", "benefit": "Bone & Immunity"},
            {"name": "Vitamin B12", "amount": 100, "unit": "mcg", "benefit": "Energy"},
            {"name": "Zinc", "amount": 15, "unit": "mg", "benefit": "Testosterone & Immunity"},
            {"name": "Magnesium", "amount": 100, "unit": "mg", "benefit": "Muscle Recovery"},
            {"name": "BCAA", "amount": 1000, "unit": "mg", "benefit": "Muscle Support"},
            {"name": "Vitamin C", "amount": 250, "unit": "mg", "benefit": "Antioxidant"},
        ],
        "ai_enrichment": {
            "simple_summary": "GNC Mega Men Sport is a powerful multivitamin tailored for active men. It combines essential vitamins with BCAAs and antioxidants to support muscle recovery, energy levels, and overall male health.",
            "health_benefits": ["Enhanced energy", "Muscle recovery", "Immune support", "Antioxidant protection"],
            "target_users": ["Active men", "Gym-goers", "Athletes", "Men 18-45"],
            "deficiencies_addressed": ["Vitamin D", "B12", "Zinc", "Magnesium"],
            "side_effects": ["Bright yellow urine (harmless, due to B vitamins)"],
            "model_version": "seed-data",
            "last_generated_at": NOW,
        },
        "reviews_summary": {"avg": 4.5, "count": 2104},
        "status": "active",
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "slug": "muscleblaze-whey-protein",
        "name": "MuscleBlaze Biozyme Performance Whey",
        "brand": "MuscleBlaze",
        "category": "Protein Supplement",
        "subcategory": "Whey Protein",
        "pricing": [{"region": "IN", "currency": "INR", "price": 3499, "mrp": 4199}],
        "images": [{
            "url": "https://images.unsplash.com/photo-1593095948071-474c5cc2989d?w=600",
            "alt": "MuscleBlaze Whey",
            "is_primary": True
        }],
        "description_raw": "Premium whey protein with enhanced absorption. 25g protein per scoop with added digestive enzymes.",
        "ingredients": [
            {"name": "Protein", "amount": 25, "unit": "g", "benefit": "Muscle Growth"},
            {"name": "BCAA", "amount": 5500, "unit": "mg", "benefit": "Recovery"},
            {"name": "Creatine", "amount": 0, "unit": "g", "benefit": "Energy"},
        ],
        "ai_enrichment": {
            "simple_summary": "MuscleBlaze Biozyme is a high-quality whey protein with 25g protein per serving and digestive enzymes for better absorption. Ideal for muscle building, post-workout recovery, and athletes.",
            "health_benefits": ["Muscle growth", "Faster recovery", "Improved performance", "Better protein absorption"],
            "target_users": ["Gym-goers", "Bodybuilders", "Athletes", "Those with high protein needs"],
            "deficiencies_addressed": ["Protein gaps in diet"],
            "side_effects": ["May cause bloating in lactose-sensitive individuals"],
            "model_version": "seed-data",
            "last_generated_at": NOW,
        },
        "reviews_summary": {"avg": 4.4, "count": 5612},
        "status": "active",
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "slug": "himalaya-ashwagandha",
        "name": "Himalaya Ashwagandha Capsules",
        "brand": "Himalaya",
        "category": "Herbal Supplement",
        "subcategory": "Stress Relief",
        "pricing": [{"region": "IN", "currency": "INR", "price": 199, "mrp": 250}],
        "images": [{
            "url": "https://images.unsplash.com/photo-1626202373052-9c2b9f73ed3d?w=600",
            "alt": "Himalaya Ashwagandha",
            "is_primary": True
        }],
        "description_raw": "Traditional Ayurvedic herb for stress relief, vitality, and mental clarity.",
        "ingredients": [
            {"name": "Ashwagandha", "amount": 250, "unit": "mg", "benefit": "Stress Relief"},
        ],
        "ai_enrichment": {
            "simple_summary": "Himalaya Ashwagandha is a trusted Ayurvedic supplement using a standardized root extract. It's widely used to manage stress, improve sleep quality, and boost overall vitality.",
            "health_benefits": ["Reduces stress", "Better sleep", "Improved focus", "Enhanced vitality"],
            "target_users": ["Stressed professionals", "Adults with sleep issues", "Anyone seeking calm"],
            "deficiencies_addressed": ["Stress-related fatigue"],
            "side_effects": ["May cause drowsiness", "Avoid during pregnancy", "Consult doctor if on thyroid medication"],
            "model_version": "seed-data",
            "last_generated_at": NOW,
        },
        "reviews_summary": {"avg": 4.2, "count": 1834},
        "status": "active",
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "slug": "now-foods-vitamin-d3",
        "name": "NOW Foods Vitamin D3 5000 IU",
        "brand": "NOW Foods",
        "category": "Vitamin",
        "subcategory": "Vitamin D",
        "pricing": [{"region": "IN", "currency": "INR", "price": 899, "mrp": 1099}],
        "images": [{
            "url": "https://images.unsplash.com/photo-1576602976047-174e57a47881?w=600",
            "alt": "NOW Foods D3",
            "is_primary": True
        }],
        "description_raw": "High-potency vitamin D3 for bone health, immune support, and overall wellness.",
        "ingredients": [
            {"name": "Vitamin D3", "amount": 5000, "unit": "IU", "benefit": "Bone & Immunity"},
        ],
        "ai_enrichment": {
            "simple_summary": "NOW Foods Vitamin D3 5000 IU is a high-potency single-ingredient supplement ideal for those with confirmed vitamin D deficiency, limited sun exposure, or living in northern climates.",
            "health_benefits": ["Strong bones", "Immune support", "Mood regulation", "Calcium absorption"],
            "target_users": ["Adults with D deficiency", "Office workers", "Elderly", "People in cold climates"],
            "deficiencies_addressed": ["Vitamin D deficiency"],
            "side_effects": ["Excess can cause nausea, weakness — stay under 4000 IU long-term unless doctor advised"],
            "model_version": "seed-data",
            "last_generated_at": NOW,
        },
        "reviews_summary": {"avg": 4.7, "count": 3421},
        "status": "active",
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "slug": "optimum-nutrition-fish-oil",
        "name": "Optimum Nutrition Fish Oil Omega 3",
        "brand": "Optimum Nutrition",
        "category": "Omega 3",
        "subcategory": "Fish Oil",
        "pricing": [{"region": "IN", "currency": "INR", "price": 1299, "mrp": 1599}],
        "images": [{
            "url": "https://images.unsplash.com/photo-1559757175-5700dde675bc?w=600",
            "alt": "ON Fish Oil",
            "is_primary": True
        }],
        "description_raw": "High-quality fish oil with EPA and DHA for heart, brain, and joint health.",
        "ingredients": [
            {"name": "Omega 3", "amount": 1000, "unit": "mg", "benefit": "Heart & Brain Health"},
        ],
        "ai_enrichment": {
            "simple_summary": "Optimum Nutrition Fish Oil provides 1000mg of omega-3 fatty acids per softgel, including EPA and DHA. Supports cardiovascular health, brain function, and reduces inflammation.",
            "health_benefits": ["Heart health", "Brain function", "Reduced inflammation", "Eye health"],
            "target_users": ["Adults of all ages", "Those with low fish intake", "People with joint pain"],
            "deficiencies_addressed": ["Omega-3 deficiency"],
            "side_effects": ["Fishy aftertaste", "Mild GI upset"],
            "model_version": "seed-data",
            "last_generated_at": NOW,
        },
        "reviews_summary": {"avg": 4.5, "count": 2876},
        "status": "active",
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "slug": "muscleblaze-creatine",
        "name": "MuscleBlaze Creatine Monohydrate",
        "brand": "MuscleBlaze",
        "category": "Performance",
        "subcategory": "Creatine",
        "pricing": [{"region": "IN", "currency": "INR", "price": 799, "mrp": 999}],
        "images": [{
            "url": "https://images.unsplash.com/photo-1579722821273-0f6c1b5d0c14?w=600",
            "alt": "Creatine",
            "is_primary": True
        }],
        "description_raw": "Pure micronized creatine monohydrate for strength, power, and muscle gains.",
        "ingredients": [
            {"name": "Creatine", "amount": 3, "unit": "g", "benefit": "Strength & Power"},
        ],
        "ai_enrichment": {
            "simple_summary": "MuscleBlaze Creatine Monohydrate is one of the most researched supplements for strength athletes. 3g per serving helps increase power output, strength, and muscle mass.",
            "health_benefits": ["Increased strength", "Better workout performance", "Muscle growth", "Recovery"],
            "target_users": ["Strength athletes", "Bodybuilders", "Sprinters", "Gym-goers"],
            "deficiencies_addressed": ["Creatine stores in muscle"],
            "side_effects": ["Water retention", "Mild bloating initially"],
            "model_version": "seed-data",
            "last_generated_at": NOW,
        },
        "reviews_summary": {"avg": 4.6, "count": 4231},
        "status": "active",
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "slug": "amway-nutrilite-vitamin-c",
        "name": "Nutrilite Natural C",
        "brand": "Amway",
        "category": "Vitamin",
        "subcategory": "Vitamin C",
        "pricing": [{"region": "IN", "currency": "INR", "price": 1499, "mrp": 1799}],
        "images": [{
            "url": "https://images.unsplash.com/photo-1607619056574-7b8d3ee536b2?w=600",
            "alt": "Nutrilite Vitamin C",
            "is_primary": True
        }],
        "description_raw": "Natural Vitamin C from acerola cherries with citrus bioflavonoids.",
        "ingredients": [
            {"name": "Vitamin C", "amount": 250, "unit": "mg", "benefit": "Immunity & Antioxidant"},
        ],
        "ai_enrichment": {
            "simple_summary": "Nutrilite Natural C delivers 250mg of vitamin C from natural sources like acerola cherries. Supports immune function, skin health, and acts as a powerful antioxidant.",
            "health_benefits": ["Immune support", "Collagen synthesis", "Antioxidant defense", "Iron absorption"],
            "target_users": ["Frequent travelers", "Students during exam season", "Those prone to colds"],
            "deficiencies_addressed": ["Vitamin C deficiency"],
            "side_effects": ["Stomach upset at high doses", "Generally very safe"],
            "model_version": "seed-data",
            "last_generated_at": NOW,
        },
        "reviews_summary": {"avg": 4.4, "count": 1567},
        "status": "active",
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "slug": "healthkart-biotin",
        "name": "HealthKart HK Vitals Biotin",
        "brand": "HealthKart",
        "category": "Beauty Supplement",
        "subcategory": "Hair & Skin",
        "pricing": [{"region": "IN", "currency": "INR", "price": 399, "mrp": 599}],
        "images": [{
            "url": "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=600",
            "alt": "Biotin",
            "is_primary": True
        }],
        "description_raw": "Biotin supplement for healthy hair, skin, and nails.",
        "ingredients": [
            {"name": "Biotin", "amount": 10000, "unit": "mcg", "benefit": "Hair & Nail Health"},
        ],
        "ai_enrichment": {
            "simple_summary": "HK Vitals Biotin provides 10,000mcg of biotin per serving to support healthy hair growth, stronger nails, and clearer skin. Popular among those experiencing hair thinning.",
            "health_benefits": ["Hair growth", "Stronger nails", "Skin health", "Energy metabolism"],
            "target_users": ["Adults with hair concerns", "Post-pregnancy women", "Stressed individuals"],
            "deficiencies_addressed": ["Biotin deficiency"],
            "side_effects": ["Generally safe", "May interfere with thyroid lab tests"],
            "model_version": "seed-data",
            "last_generated_at": NOW,
        },
        "reviews_summary": {"avg": 4.0, "count": 987},
        "status": "active",
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "slug": "yakult-probiotics",
        "name": "Yakult Probiotic Drink",
        "brand": "Yakult",
        "category": "Probiotic",
        "subcategory": "Gut Health",
        "pricing": [{"region": "IN", "currency": "INR", "price": 80, "mrp": 80}],
        "images": [{
            "url": "https://images.unsplash.com/photo-1572490122747-3968b75cc699?w=600",
            "alt": "Yakult",
            "is_primary": True
        }],
        "description_raw": "Probiotic drink with billions of live beneficial bacteria for gut health.",
        "ingredients": [
            {"name": "Probiotics", "amount": 6.5, "unit": "billion CFU", "benefit": "Gut Health"},
        ],
        "ai_enrichment": {
            "simple_summary": "Yakult is a daily probiotic drink containing 6.5 billion live Lactobacillus casei bacteria. Supports digestive health, immunity, and may help with regular bowel movements.",
            "health_benefits": ["Digestive health", "Immune support", "Better gut bacteria balance"],
            "target_users": ["Adults with digestive issues", "Post-antibiotics users", "General wellness"],
            "deficiencies_addressed": ["Gut flora imbalance"],
            "side_effects": ["Initial bloating", "Contains sugar"],
            "model_version": "seed-data",
            "last_generated_at": NOW,
        },
        "reviews_summary": {"avg": 4.3, "count": 6543},
        "status": "active",
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "slug": "centrum-women",
        "name": "Centrum Women Multivitamin",
        "brand": "Centrum",
        "category": "Multivitamin",
        "subcategory": "Women's Health",
        "pricing": [{"region": "IN", "currency": "INR", "price": 1199, "mrp": 1499}],
        "images": [{
            "url": "https://images.unsplash.com/photo-1631549916768-4119b2e5f926?w=600",
            "alt": "Centrum Women",
            "is_primary": True
        }],
        "description_raw": "Complete multivitamin formulated specifically for women's health needs.",
        "ingredients": [
            {"name": "Iron", "amount": 18, "unit": "mg", "benefit": "Energy"},
            {"name": "Calcium", "amount": 300, "unit": "mg", "benefit": "Bone Health"},
            {"name": "Vitamin D3", "amount": 800, "unit": "IU", "benefit": "Bone & Immunity"},
            {"name": "Vitamin B12", "amount": 6, "unit": "mcg", "benefit": "Energy & Brain"},
            {"name": "Biotin", "amount": 40, "unit": "mcg", "benefit": "Hair & Skin"},
            {"name": "Vitamin C", "amount": 60, "unit": "mg", "benefit": "Immunity"},
        ],
        "ai_enrichment": {
            "simple_summary": "Centrum Women is tailored for women's unique nutritional needs, with extra iron, calcium, and biotin. Supports energy, bone health, beauty, and immunity in a single daily tablet.",
            "health_benefits": ["Energy support", "Bone strength", "Healthy hair & skin", "Immunity"],
            "target_users": ["Women 18-50", "Menstruating women", "Working professionals"],
            "deficiencies_addressed": ["Iron deficiency", "Vitamin D", "B12", "Calcium"],
            "side_effects": ["May cause mild GI upset", "Iron may cause constipation"],
            "model_version": "seed-data",
            "last_generated_at": NOW,
        },
        "reviews_summary": {"avg": 4.4, "count": 2890},
        "status": "active",
        "created_at": NOW,
        "updated_at": NOW,
    },
]


# ============ BRANDS ============
BRANDS = [
    {"slug": "amway", "name": "Amway", "country": "USA", "description": "Global health and wellness brand."},
    {"slug": "herbalife", "name": "Herbalife", "country": "USA", "description": "Nutrition and weight management."},
    {"slug": "gnc", "name": "GNC", "country": "USA", "description": "Premium health and wellness products."},
    {"slug": "muscleblaze", "name": "MuscleBlaze", "country": "India", "description": "Sports nutrition brand."},
    {"slug": "himalaya", "name": "Himalaya", "country": "India", "description": "Ayurvedic and herbal wellness."},
    {"slug": "now-foods", "name": "NOW Foods", "country": "USA", "description": "Natural supplements since 1968."},
    {"slug": "optimum-nutrition", "name": "Optimum Nutrition", "country": "USA", "description": "Sports nutrition leader."},
    {"slug": "healthkart", "name": "HealthKart", "country": "India", "description": "Health and fitness products."},
    {"slug": "centrum", "name": "Centrum", "country": "USA", "description": "Trusted multivitamin brand."},
    {"slug": "yakult", "name": "Yakult", "country": "Japan", "description": "Probiotic specialist."},
]


# ============ DEFICIENCIES ============
DEFICIENCIES = [
    {
        "name": "Vitamin D Deficiency",
        "icon": "☀️",
        "symptoms": ["Fatigue", "Bone pain", "Muscle weakness", "Mood changes", "Hair loss"],
        "causes": ["Limited sun exposure", "Dark skin", "Older age", "Indoor lifestyle"],
        "solutions": ["Sunlight exposure 15-20 min/day", "Vitamin D3 supplements", "Fortified foods"],
        "related_nutrients": ["Vitamin D3"],
    },
    {
        "name": "Iron Deficiency Anemia",
        "icon": "🩸",
        "symptoms": ["Extreme fatigue", "Pale skin", "Shortness of breath", "Cold hands and feet", "Headaches"],
        "causes": ["Inadequate diet", "Heavy menstruation", "Poor absorption", "Pregnancy"],
        "solutions": ["Iron-rich foods (red meat, lentils)", "Iron supplements with vitamin C", "Cooking in iron pans"],
        "related_nutrients": ["Iron", "Vitamin C"],
    },
    {
        "name": "Vitamin B12 Deficiency",
        "icon": "🧠",
        "symptoms": ["Fatigue", "Memory issues", "Tingling in hands/feet", "Mood changes", "Pale skin"],
        "causes": ["Vegan/vegetarian diet", "Age 50+", "Gut absorption issues", "Certain medications"],
        "solutions": ["B12 supplements", "Fortified foods", "B12 injections (if severe)"],
        "related_nutrients": ["Vitamin B12"],
    },
    {
        "name": "Calcium Deficiency",
        "icon": "🦴",
        "symptoms": ["Muscle cramps", "Brittle nails", "Tooth decay", "Numbness in fingers"],
        "causes": ["Low dairy intake", "Vitamin D deficiency", "Aging", "Certain medications"],
        "solutions": ["Dairy products", "Leafy greens", "Calcium supplements with vitamin D"],
        "related_nutrients": ["Calcium", "Vitamin D3"],
    },
    {
        "name": "Magnesium Deficiency",
        "icon": "💤",
        "symptoms": ["Muscle twitches", "Poor sleep", "Anxiety", "High blood pressure", "Fatigue"],
        "causes": ["Processed food diet", "Stress", "Excessive alcohol", "Diabetes"],
        "solutions": ["Nuts and seeds", "Dark chocolate", "Magnesium supplements", "Leafy greens"],
        "related_nutrients": ["Magnesium"],
    },
    {
        "name": "Zinc Deficiency",
        "icon": "🛡️",
        "symptoms": ["Weak immunity", "Slow wound healing", "Hair loss", "Loss of taste/smell", "Skin issues"],
        "causes": ["Vegetarian diet", "Digestive disorders", "Pregnancy", "Alcoholism"],
        "solutions": ["Oysters, beef, pumpkin seeds", "Zinc supplements", "Whole grains"],
        "related_nutrients": ["Zinc"],
    },
]


async def seed():
    print(f"🌱 Connecting to MongoDB at {settings.MONGODB_URL}...")
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]

    # Test
    try:
        await client.admin.command("ping")
        print(f"✅ Connected to database: {settings.MONGODB_DB_NAME}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("Make sure MongoDB is running locally (check MongoDB Compass).")
        return

    print("\nFetching Amway India products...")
    products = await fetch_amway_india_products()
    if not products:
        print("No Amway India products were fetched. Database was not changed.")
        client.close()
        return
    brands = _brands_from_products(products)
    print(f"Fetched {len(products)} products across {len(brands)} brands.")

    # Clear existing
    print("\n🧹 Clearing existing collections...")
    await db.products.delete_many({})
    await db.ingredients.delete_many({})
    await db.brands.delete_many({})
    await db.deficiencies.delete_many({})

    # Insert ingredients
    print(f"📦 Inserting {len(INGREDIENTS)} ingredients...")
    await db.ingredients.insert_many(INGREDIENTS)

    # Insert brands
    print(f"🏢 Inserting {len(brands)} Amway India brands...")
    if brands:
        await db.brands.insert_many(brands)

    # Insert deficiencies
    print(f"⚠️  Inserting {len(DEFICIENCIES)} deficiencies...")
    await db.deficiencies.insert_many(DEFICIENCIES)

    # Insert products
    print(f"💊 Inserting {len(products)} Amway India products...")
    await db.products.insert_many(products)

    # Create indexes
    print("\n📇 Creating indexes...")
    await db.products.create_index("slug", unique=True)
    await db.products.create_index("external_id", unique=True)
    await db.products.create_index([("name", "text"), ("description_raw", "text")])
    await db.products.create_index("brand")
    await db.products.create_index("category")
    await db.ingredients.create_index("name", unique=True)
    await db.brands.create_index("slug", unique=True)
    await db.users.create_index("email", unique=True)

    # Summary
    print("\n" + "=" * 50)
    print("✅ DATABASE SEEDED SUCCESSFULLY")
    print("=" * 50)
    print(f"  Products:      {await db.products.count_documents({})}")
    print(f"  Ingredients:   {await db.ingredients.count_documents({})}")
    print(f"  Brands:        {await db.brands.count_documents({})}")
    print(f"  Deficiencies:  {await db.deficiencies.count_documents({})}")
    print("\n🔍 Open MongoDB Compass and connect to:")
    print(f"   {settings.MONGODB_URL}")
    print(f"   Database: {settings.MONGODB_DB_NAME}")
    print("=" * 50)

    client.close()


if __name__ == "__main__":
    asyncio.run(seed())
