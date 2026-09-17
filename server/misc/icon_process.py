from PIL import Image, ImageOps, UnidentifiedImageError
from io import BytesIO


def process_icon(file, thumbnail_size=512):
    try:
        img = Image.open(file, formats=["JPEG", "PNG", "WEBP", "ICO"])
        img.load()
    except (UnidentifiedImageError, OSError):
        raise ValueError("Invalid image")

    if img.width > 4096 or img.height > 4096:
        raise ValueError("Image too large")

    img = ImageOps.exif_transpose(img)
    img = img.convert("RGB")
    img.thumbnail((thumbnail_size, thumbnail_size))

    output = BytesIO()
    img.save(output, "JPEG", quality=85)

    return output.getvalue()
