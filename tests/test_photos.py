import io
from datetime import datetime

import pytest
from PIL import Image

from agent.photos import PhotoError, clean_name, is_supported_attachment, save_photo, to_jpeg
from tests.helpers import jpeg_bytes

WHEN = datetime(2026, 10, 26, 14, 3, 27)


@pytest.mark.parametrize("raw, cleaned", [
    ("Banana", "Banana"),
    ("../../Desktop/x", "Desktop x"),
    ("a/b\\c:d", "a b c d"),
    ("...", "Unknown"),
    ("", "Unknown"),
    ("  Red   apple\n", "Red apple"),
    ('Bad*?"<>|name', "Bad name"),
    ("x" * 60, "x" * 40),
])
def test_clean_name(raw, cleaned):
    assert clean_name(raw) == cleaned


def test_filename_and_collisions(tmp_path):
    photos = tmp_path / "photos"
    first = save_photo(photos, WHEN, "Banana", b"1")
    second = save_photo(photos, WHEN, "Banana", b"2")
    third = save_photo(photos, WHEN, "Banana", b"3")
    assert [p.name for p in (first, second, third)] == [
        "2026-10-26 14-03-27 Banana.jpg",
        "2026-10-26 14-03-27 Banana-2.jpg",
        "2026-10-26 14-03-27 Banana-3.jpg",
    ]
    assert first.read_bytes() == b"1"


def test_hostile_name_stays_inside_photos(tmp_path):
    photos = tmp_path / "photos"
    path = save_photo(photos, WHEN, "../../../etc/passwd", b"x")
    assert path.parent == photos
    assert list(tmp_path.iterdir()) == [photos]


def test_png_with_transparency_becomes_jpeg():
    output = io.BytesIO()
    Image.new("RGBA", (10, 10), (255, 0, 0, 0)).save(output, "PNG")
    with Image.open(io.BytesIO(to_jpeg(output.getvalue()))) as image:
        assert image.format == "JPEG"
        assert image.getpixel((5, 5)) == pytest.approx((255, 255, 255), abs=3)


def test_metadata_is_dropped_and_photo_turned_upright():
    image = Image.new("RGB", (40, 20), "green")
    exif = image.getexif()
    exif[0x0112] = 6  # orientation: rotate 90°
    exif[0x010F] = "TestCam"  # camera make, standing in for any hidden metadata
    output = io.BytesIO()
    image.save(output, "JPEG", exif=exif)
    with Image.open(io.BytesIO(to_jpeg(output.getvalue()))) as converted:
        assert converted.size == (20, 40)
        assert not converted.getexif()


def test_animated_and_broken_images_are_rejected():
    frames = [Image.new("RGB", (5, 5), c) for c in ("red", "blue")]
    output = io.BytesIO()
    frames[0].save(output, "WEBP", save_all=True, append_images=frames[1:])
    with pytest.raises(PhotoError):
        to_jpeg(output.getvalue())
    with pytest.raises(PhotoError):
        to_jpeg(b"definitely not an image")


@pytest.mark.parametrize("filename, content_type, size, expected", [
    ("a.jpg", "image/jpeg", 1000, True),
    ("a.PNG", "image/png", 1000, True),
    ("a.webp", "image/webp", 1000, True),
    ("a.gif", "image/gif", 1000, False),
    ("a.mp4", "video/mp4", 1000, False),
    ("a.pdf", "application/pdf", 1000, False),
    ("a.jpg", None, 1000, False),
    ("a.jpg", "image/jpeg", 21 * 1024 * 1024, False),
])
def test_supported_attachments(filename, content_type, size, expected):
    assert is_supported_attachment(filename, content_type, size) is expected


def test_jpeg_helper_is_valid():
    assert to_jpeg(jpeg_bytes())[:2] == b"\xff\xd8"
