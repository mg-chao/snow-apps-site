"""Optimize public bitmaps and SVG-embedded bitmaps with lossless WebP.

Requires Pillow with WebP support: python3 -m pip install Pillow
"""
from base64 import b64decode, b64encode
from io import BytesIO
from pathlib import Path
import re

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "docs/public"
RASTERS = {".png", ".jpg", ".jpeg", ".webp"}
DATA_IMAGE = re.compile(r"data:image/(png|jpeg|webp|svg\+xml);base64,([A-Za-z0-9+/=]+)")


def webp(data):
    with Image.open(BytesIO(data)) as source:
        if getattr(source, "n_frames", 1) != 1:
            raise ValueError("Animated images require a separate conversion")
        pixels = source.convert("RGBA")
    output = BytesIO()
    # Maximum lossless effort (equivalent to cwebp -z 9), with alpha RGB preserved.
    pixels.save(output, "WEBP", lossless=True, quality=100, method=6, exact=True)
    encoded = output.getvalue()
    with Image.open(BytesIO(encoded)) as decoded:
        if decoded.size != pixels.size or decoded.convert("RGBA").tobytes() != pixels.tobytes():
            raise ValueError("WebP conversion changed image pixels")
    return encoded


def inline_images(svg):
    def replace(match):
        mime, payload = match.groups()
        data = b64decode(payload, validate=True)
        if mime == "svg+xml":
            encoded = inline_images(data.decode("utf-8")).encode("utf-8")
            if encoded == data:
                return match[0]
        else:
            encoded = webp(data)
            if mime == "webp" and len(encoded) >= len(data):
                return match[0]
            mime = "webp"
        return f"data:image/{mime};base64,{b64encode(encoded).decode('ascii')}"
    return DATA_IMAGE.sub(replace, svg)


def main():
    before = after = 0
    replacements = {}
    for path in sorted(PUBLIC.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in RASTERS | {".svg"}:
            continue
        original = path.read_bytes()
        target = path
        if path.suffix.lower() in RASTERS:
            encoded = webp(original)
            target = path.with_suffix(".webp")
            if target == path and len(encoded) >= len(original):
                encoded = original
            elif target != path and target.exists():
                raise FileExistsError(f"Refusing to overwrite {target}")
        else:
            if b"data:image/" not in original:
                continue
            encoded = inline_images(original.decode("utf-8")).encode("utf-8")
        if encoded != original or target != path:
            target.write_bytes(encoded)
            if target != path:
                replacements["/" + path.relative_to(PUBLIC).as_posix()] = (
                    "/" + target.relative_to(PUBLIC).as_posix()
                )
            print(f"{path.relative_to(ROOT)}: {len(original):,} -> {len(encoded):,} bytes")
        before += len(original)
        after += len(encoded)

    for directory in (ROOT / "docs", ROOT / "theme"):
        for path in directory.rglob("*"):
            if path.suffix not in {".md", ".mdx", ".ts", ".tsx", ".css", ".json", ".svg"}:
                continue
            original = path.read_text()
            updated = original
            for old, new in replacements.items():
                updated = updated.replace(old, new)
            if updated != original:
                path.write_text(updated)

    # Remove replaced sources only after the pages and components use the new URLs.
    for old in replacements:
        (PUBLIC / old.lstrip("/")).unlink()
    print(f"Total: {before:,} -> {after:,} bytes; saved {before - after:,} bytes")


if __name__ == "__main__":
    main()
