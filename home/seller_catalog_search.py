"""Search/presentation layer for the expanded Shopiva seller catalogue."""

from .shopiva_seller_catalog import ALL_CATALOG_ROWS


def catalog_search_choices(limit=4000):
    """Return readable datalist values: Product — Brand — Category."""
    return [
        (key, f"{product} — {brand} — {category}")
        for key, category, brand, product in ALL_CATALOG_ROWS[:limit]
    ]


def resolve_catalog_item(value):
    """Resolve a datalist selection or free-text search to the best catalogue row."""
    text = str(value or "").strip()
    if not text or text.upper().startswith("CUSTOM PRODUCT"):
        return None

    # Exact key, useful when a future UI submits the internal key directly.
    for key, category, brand, product in ALL_CATALOG_ROWS:
        if key.casefold() == text.casefold():
            return {"key": key, "category": category, "brand": brand, "name": product}

    # Human-readable datalist selection: Product — Brand — Category.
    parts = [part.strip() for part in text.split("—") if part.strip()]
    product_hint = parts[0] if parts else text
    brand_hint = parts[1].casefold() if len(parts) > 1 else ""
    category_hint = parts[2].casefold() if len(parts) > 2 else ""
    needle = product_hint.casefold()

    candidates = []
    for key, category, brand, product in ALL_CATALOG_ROWS:
        product_cf = product.casefold()
        brand_cf = brand.casefold()
        category_cf = category.casefold()
        if needle == product_cf:
            score = 0
        elif needle in product_cf:
            score = 1
        elif needle in f"{product_cf} {brand_cf} {category_cf}":
            score = 2
        else:
            continue
        if brand_hint and brand_hint not in brand_cf:
            score += 10
        if category_hint and category_hint not in category_cf:
            score += 5
        candidates.append((score, len(product), key, category, brand, product))

    if not candidates:
        return None
    candidates.sort(key=lambda row: (row[0], row[1], row[2]))
    _, _, key, category, brand, product = candidates[0]
    return {"key": key, "category": category, "brand": brand, "name": product}
