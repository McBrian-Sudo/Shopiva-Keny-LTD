def home(request):
    """Fast public storefront landing page.

    Keep the first paint bounded: the homepage only needs a small curated
    window of products. Catalogue/search pages handle the full inventory.
    """
    try:
        base_products = (
            Product.objects
            .filter(is_active=True)
            .select_related("seller")
            .order_by("-id")
        )
        homepage_products = list(base_products[:24])
        discounted_products = list(base_products.filter(discount_percent__gt=0)[:8])

        featured_products = list(base_products.filter(is_featured=True)[:6])
        seen_ids = {product.id for product in featured_products}

        for product in discounted_products:
            if product.id not in seen_ids and len(featured_products) < 6:
                featured_products.append(product)
                seen_ids.add(product.id)

        for product in homepage_products:
            if product.id not in seen_ids and len(featured_products) < 6:
                featured_products.append(product)
                seen_ids.add(product.id)

        return render(
            request,
            "home.html",
            {
                "products": homepage_products,
                "featured_products": featured_products,
                "discounted_products": discounted_products,
            },
        )
    except Exception:
        logger.exception("SHOPIVA_HOME_REQUEST_FAILED path=%s", request.path)
        raise
