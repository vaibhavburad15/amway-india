"""
Fetch and normalize Amway India product data.
"""
from __future__ import annotations

import asyncio
import html
import json
import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional
from urllib.parse import quote, urljoin

import httpx

logger = logging.getLogger(__name__)

AMWAY_BASE_URL = "https://www.amway.in"
SHOP_PATH = "/shop/c/shop"
PLP_ENDPOINT = "/api/dnd/PLP/getUpdatedProductData"
PDP_ENDPOINT_PREFIX = "/api/dnd/PDP"
DEFAULT_PAGE_SIZE = 12


class AmwayIndiaError(RuntimeError):
    """Raised when Amway India product data cannot be fetched."""


def _extract_next_data(page_html: str) -> Dict[str, Any]:
    match = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
        page_html,
        re.S,
    )
    if not match:
        raise AmwayIndiaError("Amway India page did not contain __NEXT_DATA__")
    return json.loads(match.group(1))


def _strip_html(value: Optional[str]) -> str:
    if not value:
        return ""
    text = re.sub(r"</(p|li|div|br|tr|h[1-6])>", "\n", value, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\n\s+", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _extract_list_items(value: Optional[str]) -> List[str]:
    if not value:
        return []
    items = re.findall(r"<li[^>]*>(.*?)</li>", value, flags=re.I | re.S)
    return [item for item in (_strip_html(i) for i in items) if item]


def _slugify(value: str) -> str:
    value = html.unescape(value or "").lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value)
    return value.strip("-")


def _compact(items: Iterable[Optional[str]]) -> List[str]:
    seen = set()
    output: List[str] = []
    for item in items:
        if not item:
            continue
        cleaned = re.sub(r"\s+", " ", str(item)).strip()
        key = cleaned.casefold()
        if cleaned and key not in seen:
            seen.add(key)
            output.append(cleaned)
    return output


def _money(value: Any) -> Optional[float]:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = re.sub(r"[^0-9.]", "", value)
        if cleaned:
            return float(cleaned)
    return None


def _feature_values(product: Dict[str, Any], feature_name: str) -> List[str]:
    output: List[str] = []
    for classification in product.get("classifications") or []:
        for feature in classification.get("features") or []:
            if str(feature.get("name", "")).casefold() != feature_name.casefold():
                continue
            for value in feature.get("featureValues") or []:
                output.append(value.get("value") or value.get("code"))
    return _compact(output)


def _sections(product: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    sections: Dict[str, Dict[str, Any]] = {}
    for section in product.get("productSections") or []:
        if section.get("visibleForCurrentUser") is False:
            continue
        code = section.get("sectionTypeCode") or section.get("sectionType")
        if code:
            sections[str(code).lower()] = section
    return sections


def _section_text(section: Optional[Dict[str, Any]]) -> str:
    if not section:
        return ""
    parts = [
        section.get("content"),
        section.get("preText"),
        section.get("postText"),
    ]
    return "\n".join(_strip_html(part) for part in parts if part).strip()


def _summary_from_text(text: str, limit: int = 700) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    sentences = re.split(r"(?<=[.!?])\s+", text)
    summary = ""
    for sentence in sentences:
        candidate = f"{summary} {sentence}".strip()
        if len(candidate) > limit:
            break
        summary = candidate
    return summary or f"{text[:limit].rstrip()}..."


def _parse_amount(value: str) -> Dict[str, Any]:
    value = re.sub(r"\s+", " ", value or "").strip()
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*([a-zA-Z]+|mcg|mg|g|kg|ml|l|IU|%)", value)
    if not match:
        return {"amount": None, "unit": value}
    return {"amount": float(match.group(1)), "unit": match.group(2)}


def _extract_ingredients(product: Dict[str, Any]) -> List[Dict[str, Any]]:
    sections = _sections(product)
    ingredient_section = sections.get("ingredients")
    ingredients: List[Dict[str, Any]] = []

    for row in (ingredient_section or {}).get("specificationTable") or []:
        name = _strip_html(row.get("ingredientName"))
        if not name:
            continue
        per_serving = ""
        daily_value = None
        for item in row.get("values") or []:
            label = str(item.get("name", ""))
            item_value = str(item.get("value", ""))
            if "rda" in label.casefold() or "%dv" in label.casefold():
                pct_match = re.search(r"([0-9]+(?:\.[0-9]+)?)", item_value)
                daily_value = float(pct_match.group(1)) if pct_match else None
            elif not per_serving:
                per_serving = item_value

        parsed = _parse_amount(per_serving)
        ingredients.append({
            "name": name,
            "amount": parsed["amount"],
            "unit": parsed["unit"],
            "daily_value_percent": daily_value,
            "benefit": "Listed by Amway India",
        })

    if ingredients:
        return ingredients

    return [
        {
            "name": name,
            "amount": None,
            "unit": "",
            "benefit": "Listed by Amway India",
        }
        for name in _feature_values(product, "Ingredients")
    ]


def _pick_best_rendition(renditions: List[Dict[str, Any]]) -> Optional[str]:
    if not renditions:
        return None

    def score(item: Dict[str, Any]) -> int:
        width = item.get("assetFormat", {}).get("width") or 0
        preferred = {800: 5, 560: 4, 600: 4, 515: 3, 375: 2, 200: 1}
        return preferred.get(width, 0) * 10000 + int(width)

    best = sorted(renditions, key=score, reverse=True)[0]
    return best.get("url")


def _extract_images(product: Dict[str, Any]) -> List[Dict[str, Any]]:
    urls: List[str] = []

    for gallery_item in product.get("amwayGallery") or []:
        url = _pick_best_rendition(gallery_item.get("renditions") or [])
        if url:
            urls.append(url)

    lynx = product.get("lynxPicture") or {}
    url = _pick_best_rendition(lynx.get("renditions") or [])
    if url:
        urls.append(url)

    for image in product.get("images") or []:
        if image.get("url"):
            urls.append(image["url"])

    return [
        {"url": url, "alt": product.get("name", "Amway India product"), "is_primary": i == 0}
        for i, url in enumerate(_compact(urls))
    ]


def _category(product: Dict[str, Any]) -> tuple[str, Optional[str]]:
    crumbs = [
        crumb.get("name")
        for crumb in product.get("indBreadcrumbs") or []
        if crumb.get("name")
        and not crumb.get("active")
        and crumb.get("name") not in {"Home", "Shop"}
    ]
    product_types = _feature_values(product, "Product Type")
    category = crumbs[0] if crumbs else (product_types[0] if product_types else "Amway India")
    subcategory = crumbs[-1] if len(crumbs) > 1 else (product_types[0] if product_types else None)
    return category, subcategory


def _product_slug(product: Dict[str, Any]) -> str:
    code = str(product.get("code") or product.get("alias") or "").lower()
    path = str(product.get("url") or "")
    source_slug = ""
    if "/p/" in path:
        source_slug = path.split("/p/", 1)[0].strip("/").split("/")[-1]
    source_slug = _slugify(source_slug or product.get("name") or code)
    return f"{source_slug}-{code}" if code else source_slug


def normalize_amway_product(product: Dict[str, Any]) -> Dict[str, Any]:
    """Convert an Amway India PLP/PDP product into the app's product schema."""
    now = datetime.now(timezone.utc)
    sections = _sections(product)
    category, subcategory = _category(product)
    product_url = urljoin(AMWAY_BASE_URL, product.get("url") or "")

    detail_text = _section_text(sections.get("details"))
    features_text = _section_text(sections.get("features"))
    benefits_text = _section_text(sections.get("benefits"))
    usage_text = _section_text(sections.get("suggested"))
    ingredients_text = _section_text(sections.get("ingredients"))
    description_parts = [
        product.get("summary"),
        product.get("description"),
        detail_text,
        features_text,
        benefits_text,
        usage_text,
        ingredients_text,
    ]
    description = "\n\n".join(_compact(_strip_html(part) for part in description_parts))

    price = product.get("price") or {}
    retail_price = product.get("retailPrice") or {}
    selling_price = _money(price.get("value") or price.get("formattedValue"))
    mrp = _money(retail_price.get("value") or retail_price.get("formattedValue"))
    if mrp is None:
        mrp = selling_price

    benefits = _compact(
        _extract_list_items((sections.get("benefits") or {}).get("content"))
        + _extract_list_items((sections.get("features") or {}).get("content"))
        + [item.get("name") for item in product.get("needsCategories") or []]
    )
    target_users = _compact(
        _feature_values(product, "Goals")
        + [item.get("question") for item in product.get("faqs") or [] if "who" in str(item.get("question", "")).casefold()]
    )
    preferences = _feature_values(product, "Product Preference")

    reviews_count = int(product.get("numberOfReviews") or 0)
    average_rating = product.get("averageRating") or product.get("rating")

    normalized: Dict[str, Any] = {
        "slug": _product_slug(product),
        "name": product.get("name") or product.get("code") or "Amway India Product",
        "brand": product.get("brand") or "Amway India",
        "brand_id": _slugify(product.get("brand") or "amway-india"),
        "category": category,
        "subcategory": subcategory,
        "pricing": ([{
            "region": "IN",
            "currency": price.get("currencyIso") or product.get("priceCurrency") or "INR",
            "price": selling_price,
            "mrp": mrp,
        }] if selling_price is not None else []),
        "images": _extract_images(product),
        "description_raw": description,
        "ingredients": _extract_ingredients(product),
        "ai_enrichment": {
            "simple_summary": _summary_from_text(detail_text or description),
            "health_benefits": benefits[:12],
            "target_users": target_users[:12],
            "deficiencies_addressed": [],
            "side_effects": [],
            "preferences": preferences,
            "model_version": "amway-india-source",
            "last_generated_at": now,
        },
        "reviews_summary": {
            "avg": float(average_rating or 0),
            "count": reviews_count,
        },
        "status": "active",
        "source": {
            "name": "Amway India",
            "url": product_url,
            "external_id": product.get("code") or product.get("alias"),
            "last_synced_at": now,
        },
        "external_id": product.get("code") or product.get("alias"),
        "amway_size": product.get("amwaySize"),
        "country_of_origin": product.get("countryOfOrigin"),
        "stock": product.get("stock"),
        "is_out_of_stock": bool(product.get("isOutOfStock") or product.get("isOOS")),
        "created_at": now,
        "updated_at": now,
    }

    return normalized


class AmwayIndiaClient:
    def __init__(
        self,
        *,
        concurrency: int = 6,
        timeout: float = 30.0,
        base_url: str = AMWAY_BASE_URL,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.concurrency = concurrency
        self._app_variables: Optional[Dict[str, Any]] = None
        self._authorization: Optional[str] = None
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(timeout, connect=10.0),
            limits=httpx.Limits(max_connections=max(concurrency + 2, 8)),
            headers={
                "Accept": "application/json, text/plain, */*",
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Safari/537.36"
                ),
            },
        )

    async def __aenter__(self) -> "AmwayIndiaClient":
        await self.bootstrap()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

    async def close(self) -> None:
        await self._client.aclose()

    async def bootstrap(self) -> None:
        response = await self._client.get(SHOP_PATH, headers={"Accept": "text/html"})
        response.raise_for_status()
        data = _extract_next_data(response.text)
        self._app_variables = data["props"]["pageProps"]["appVariables"]
        self._authorization = self._client.cookies.get("CAT")
        if not self._authorization:
            raise AmwayIndiaError("Amway India anonymous CAT token was not issued")

    async def _post_json(self, path: str, payload: Dict[str, Any], referer: str) -> Dict[str, Any]:
        if not self._app_variables or not self._authorization:
            await self.bootstrap()

        referer_url = urljoin(self.base_url, quote(str(referer), safe="/:?=&%"))
        response = await self._client.post(
            path,
            json=payload,
            headers={
                "authorization": self._authorization or "",
                "Origin": self.base_url,
                "Referer": referer_url,
            },
        )
        if response.status_code in {401, 403}:
            await self.bootstrap()
            response = await self._client.post(
                path,
                json=payload,
                headers={
                    "authorization": self._authorization or "",
                    "Origin": self.base_url,
                    "Referer": referer_url,
                },
            )
        response.raise_for_status()
        return response.json()

    async def fetch_listing_page(self, page: int, size: int = DEFAULT_PAGE_SIZE) -> Dict[str, Any]:
        payload = {
            "appVariables": self._app_variables,
            "categoryCode": "shop",
            "queryParam": ":popularity",
            "page": page,
            "size": size,
        }
        data = await self._post_json(PLP_ENDPOINT, payload, SHOP_PATH)
        return data.get("categoryData") or data.get("PLPState", {}).get("categoryData") or {}

    async def fetch_listing_products(
        self,
        *,
        size: int = DEFAULT_PAGE_SIZE,
        max_products: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        first_page = await self.fetch_listing_page(0, size=size)
        pagination = first_page.get("pagination") or {}
        total_pages = int(pagination.get("totalPages") or 1)
        pages = [first_page]

        async def fetch_page(page: int) -> Dict[str, Any]:
            return await self.fetch_listing_page(page, size=size)

        if total_pages > 1:
            pages.extend(await asyncio.gather(*(fetch_page(page) for page in range(1, total_pages))))

        products_by_code: Dict[str, Dict[str, Any]] = {}
        for page_data in pages:
            for product in page_data.get("products") or []:
                code = product.get("code")
                if code and code not in products_by_code:
                    products_by_code[code] = product
                if max_products and len(products_by_code) >= max_products:
                    return list(products_by_code.values())
        return list(products_by_code.values())

    async def fetch_product_detail(self, product_or_url: Dict[str, Any] | str) -> Dict[str, Any]:
        path = product_or_url if isinstance(product_or_url, str) else product_or_url.get("url")
        if not path:
            raise AmwayIndiaError("Product does not include an Amway India URL")
        payload = {"withCredentials": True, "appVariables": self._app_variables}
        encoded_path = quote(str(path), safe="/:?=&%")
        data = await self._post_json(f"{PDP_ENDPOINT_PREFIX}{encoded_path}", payload, str(path))
        product = data.get("PDPState", {}).get("productData") or data.get("productData")
        if not product:
            raise AmwayIndiaError(f"No PDP product data returned for {path}")
        return product

    async def fetch_products(
        self,
        *,
        include_details: bool = True,
        max_products: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        listing_products = await self.fetch_listing_products(max_products=max_products)
        if not include_details:
            return [normalize_amway_product(product) for product in listing_products]

        semaphore = asyncio.Semaphore(self.concurrency)

        async def fetch_and_normalize(product: Dict[str, Any]) -> Dict[str, Any]:
            async with semaphore:
                try:
                    detail = await self.fetch_product_detail(product)
                    return normalize_amway_product({**product, **detail})
                except Exception as exc:
                    logger.warning("Using listing data for %s after PDP fetch failed: %s", product.get("code"), exc)
                    return normalize_amway_product(product)

        return await asyncio.gather(*(fetch_and_normalize(product) for product in listing_products))


async def fetch_amway_india_products(
    *,
    include_details: bool = True,
    max_products: Optional[int] = None,
    concurrency: int = 6,
) -> List[Dict[str, Any]]:
    async with AmwayIndiaClient(concurrency=concurrency) as client:
        return await client.fetch_products(include_details=include_details, max_products=max_products)
