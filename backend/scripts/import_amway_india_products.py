"""
Import all public Amway India products into the local MongoDB products collection.

Run:
    python scripts/import_amway_india_products.py
"""
import argparse
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
from app.services.amway_india import fetch_amway_india_products


def parse_args():
    parser = argparse.ArgumentParser(description="Sync Amway India products into MongoDB.")
    parser.add_argument("--max-products", type=int, default=None, help="Fetch only the first N products.")
    parser.add_argument("--skip-details", action="store_true", help="Use PLP card data only; much faster but less rich.")
    parser.add_argument("--concurrency", type=int, default=6, help="Concurrent PDP detail fetches.")
    parser.add_argument("--no-clear", action="store_true", help="Upsert products without clearing the collection first.")
    parser.add_argument("--dry-run", action="store_true", help="Fetch and print counts without writing to MongoDB.")
    return parser.parse_args()


async def sync_products():
    args = parse_args()

    print("Fetching Amway India product catalog...")
    products = await fetch_amway_india_products(
        include_details=not args.skip_details,
        max_products=args.max_products,
        concurrency=args.concurrency,
    )

    print(f"Fetched {len(products)} products from Amway India.")
    if products:
        print("Sample:")
        for product in products[:5]:
            print(f"  - {product['external_id']}: {product['name']} ({product['brand']})")
    else:
        print("No products were fetched. MongoDB was not changed.")
        return

    if args.dry_run:
        print("Dry run complete. MongoDB was not changed.")
        return

    print(f"Connecting to MongoDB at {settings.MONGODB_URL}...")
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]

    try:
        await client.admin.command("ping")
    except Exception as exc:
        client.close()
        raise RuntimeError("MongoDB connection failed. Make sure MongoDB is running.") from exc

    if not args.no_clear:
        print("Clearing existing products...")
        await db.products.delete_many({})

    if args.no_clear:
        print("Upserting products...")
        for product in products:
            await db.products.update_one(
                {"external_id": product["external_id"]},
                {
                    "$set": {k: v for k, v in product.items() if k != "created_at"},
                    "$setOnInsert": {"created_at": product["created_at"]},
                },
                upsert=True,
            )
    elif products:
        print("Inserting products...")
        await db.products.insert_many(products)

    print("Creating indexes...")
    await db.products.create_index("slug", unique=True)
    await db.products.create_index("external_id", unique=True)
    await db.products.create_index([("name", "text"), ("description_raw", "text")])
    await db.products.create_index("brand")
    await db.products.create_index("category")

    total = await db.products.count_documents({"status": "active"})
    client.close()
    print(f"Done. Active products in MongoDB: {total}")


if __name__ == "__main__":
    asyncio.run(sync_products())
