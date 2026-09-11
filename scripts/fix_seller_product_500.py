from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
VIEWS = ROOT / "home" / "views.py"
text = VIEWS.read_text(encoding="utf-8")

# Add logger import once.
if "import logging\n" not in text:
    text = "import logging\n" + text
if "logger = logging.getLogger(__name__)" not in text:
    marker = "from .forms import CustomerRegistrationForm"
    if marker in text:
        text = text.replace(marker, "logger = logging.getLogger(__name__)\n\n" + marker, 1)
    else:
        text = text.replace("from django.db import transaction\n", "from django.db import transaction\n\nlogger = logging.getLogger(__name__)\n", 1)

add_old = '''    if request.method == "POST":\n        form = SellerProductForm(request.POST, request.FILES)\n        if form.is_valid():\n            product = form.save(commit=False)\n            product.seller = seller\n            product.is_active = True\n            product.save()\n            messages.success(request, f"{product.name} is now listed on Shopiva.")\n            return redirect("seller_dashboard")\n'''
add_new = '''    if request.method == "POST":\n        form = SellerProductForm(request.POST, request.FILES)\n        if form.is_valid():\n            product = form.save(commit=False)\n            product.seller = seller\n            product.is_active = True\n            try:\n                product.save()\n            except Exception as exc:\n                # Do not turn a product listing into a generic 500 when the\n                # external image storage provider is unavailable/misconfigured.\n                # Save the product without the optional image and tell the seller\n                # exactly what happened.\n                logger.exception("Seller product image upload failed", exc_info=exc)\n                product.image = None\n                product.save(update_fields=[\n                    "name", "description", "category", "sku", "price",\n                    "stock_quantity", "discount_percent", "promo_text",\n                    "is_active", "is_featured", "seller",\n                ])\n                messages.warning(\n                    request,\n                    "Product listed successfully, but the image could not be uploaded. "\n                    "The image-storage connection needs attention; you can edit the product and try the image again.",\n                )\n            else:\n                messages.success(request, f"{product.name} is now listed on Shopiva.")\n            return redirect("seller_dashboard")\n'''

if add_old not in text:
    raise SystemExit("seller_product_add block not found")
text = text.replace(add_old, add_new, 1)

edit_old = '''    if request.method == "POST":\n        form = SellerProductForm(request.POST, request.FILES, instance=product)\n        if form.is_valid():\n            form.save()\n            messages.success(request, f"{product.name} has been updated.")\n            return redirect("seller_dashboard")\n'''
edit_new = '''    if request.method == "POST":\n        form = SellerProductForm(request.POST, request.FILES, instance=product)\n        if form.is_valid():\n            updated_product = form.save(commit=False)\n            try:\n                updated_product.save()\n            except Exception as exc:\n                logger.exception("Seller product image update failed", exc_info=exc)\n                # Preserve the existing image when a replacement upload fails.\n                updated_product.image = Product.objects.get(pk=product.pk).image\n                updated_product.save(update_fields=[\n                    "name", "description", "category", "sku", "price",\n                    "stock_quantity", "discount_percent", "promo_text",\n                    "is_active", "is_featured", "seller",\n                ])\n                messages.warning(\n                    request,\n                    "Product details were updated, but the new image could not be uploaded. "\n                    "The previous image was kept.",\n                )\n            else:\n                messages.success(request, f"{updated_product.name} has been updated.")\n            return redirect("seller_dashboard")\n'''
if edit_old not in text:
    raise SystemExit("seller_product_edit block not found")
text = text.replace(edit_old, edit_new, 1)

VIEWS.write_text(text, encoding="utf-8")
print("Seller product 500 safeguard applied.")
