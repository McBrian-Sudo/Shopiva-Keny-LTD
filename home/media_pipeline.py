from io import BytesIO
from pathlib import Path

from django.core.files.base import ContentFile


def enhance_product_image(uploaded_file, name_hint="product"):
    """Safely enhance a real seller photo without inventing or altering its identity."""
    try:
        from PIL import Image, ImageEnhance, ImageOps

        uploaded_file.seek(0)
        image = Image.open(uploaded_file)
        image = ImageOps.exif_transpose(image).convert("RGB")

        # Keep marketplace images consistent and lightweight.
        image.thumbnail((1800, 1800), Image.Resampling.LANCZOS)
        image = ImageEnhance.Brightness(image).enhance(1.03)
        image = ImageEnhance.Contrast(image).enhance(1.06)
        image = ImageEnhance.Color(image).enhance(1.04)
        image = ImageEnhance.Sharpness(image).enhance(1.08)

        output = BytesIO()
        image.save(output, format="WEBP", quality=88, method=6)
        output.seek(0)
        safe_name = Path(str(name_hint or "product")).stem[:48] or "product"
        return ContentFile(output.read(), name=f"{safe_name}-shopiva.webp")
    except Exception:
        try:
            uploaded_file.seek(0)
        except Exception:
            pass
        return uploaded_file
