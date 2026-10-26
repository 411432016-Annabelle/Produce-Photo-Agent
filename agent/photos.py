"""Photo checks, JPEG conversion and saving (architecture section 9)."""

import io
import re
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageOps

MAX_BYTES = 20 * 1024 * 1024
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")
JPEG_QUALITY = 90
MAX_NAME_LENGTH = 40
FORBIDDEN_CHARACTERS = re.compile(r'[/\\:*?"<>|\x00-\x1f\x7f]')


class PhotoError(Exception):
    pass


def is_supported_attachment(filename: str, content_type: str | None, size: int) -> bool:
    """Uploaded still images only: no GIFs, videos, other files, or oversized uploads."""
    content_type = (content_type or "").lower()
    return (
        content_type.startswith("image/")
        and content_type != "image/gif"
        and filename.lower().endswith(IMAGE_EXTENSIONS)
        and size <= MAX_BYTES
    )


def to_jpeg(data: bytes) -> bytes:
    """Checks the data is a still image, turns it upright, and re-saves it as JPEG.

    Re-saving drops hidden metadata such as GPS location."""
    try:
        with Image.open(io.BytesIO(data)) as image:
            if getattr(image, "is_animated", False):
                raise PhotoError("photo is animated")
            image = ImageOps.exif_transpose(image)
            if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
                rgba = image.convert("RGBA")
                image = Image.new("RGB", rgba.size, "white")
                image.paste(rgba, mask=rgba.getchannel("A"))
            else:
                image = image.convert("RGB")
            output = io.BytesIO()
            image.save(output, "JPEG", quality=JPEG_QUALITY)
            return output.getvalue()
    except PhotoError:
        raise
    except Exception:
        raise PhotoError("photo could not be opened as an image") from None


def clean_name(name: str) -> str:
    """Makes an item name safe to use inside a filename."""
    name = FORBIDDEN_CHARACTERS.sub(" ", name)
    name = name.replace("..", " ").lstrip(". ")
    name = " ".join(name.split())[:MAX_NAME_LENGTH].strip()
    return name or "Unknown"


def save_photo(photos_dir: Path, when: datetime, item_name: str, jpeg_bytes: bytes) -> Path:
    """Saves as 'YYYY-MM-DD hh-mm-ss ItemName.jpg', adding -2, -3 ... on collision."""
    photos_dir.mkdir(parents=True, exist_ok=True)
    name_part = item_name

    # ==== GUARD 3: safe filename from claude -p item name START ====
    # Path-breaking characters are removed, and the result must stay inside photos/.
    name_part = clean_name(item_name)
    candidate = photos_dir / f"{when:%Y-%m-%d %H-%M-%S} {name_part}.jpg"
    if candidate.resolve().parent != photos_dir.resolve():
        name_part = "Unknown"
    # ==== GUARD 3 END ====

    base = f"{when:%Y-%m-%d %H-%M-%S} {name_part}"
    number = 1
    while True:
        path = photos_dir / (f"{base}.jpg" if number == 1 else f"{base}-{number}.jpg")
        try:
            # "x" mode refuses to overwrite an existing file.
            with open(path, "xb") as file:
                file.write(jpeg_bytes)
            return path
        except FileExistsError:
            number += 1
