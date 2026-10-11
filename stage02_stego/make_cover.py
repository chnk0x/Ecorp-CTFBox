#!/usr/bin/env python3
"""
Generate a plausible "company event" cover JPEG for EC-02.

Steghide hides data in the DCT coefficients of a JPEG, so the cover needs
enough visual detail to carry the payload. A flat, single-colour image gives
very little capacity, so this draws a textured scene instead.

Usage:  python3 make_cover.py output.jpg
"""

import random
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

WIDTH, HEIGHT = 1280, 720
SEED = 104  # fixed seed so rebuilds produce the same cover


def build(path):
    random.seed(SEED)
    img = Image.new("RGB", (WIDTH, HEIGHT), (28, 36, 54))
    draw = ImageDraw.Draw(img)

    # Background gradient
    for y in range(HEIGHT):
        shade = int(28 + (y / HEIGHT) * 45)
        draw.line([(0, y), (WIDTH, y)], fill=(shade, shade + 8, shade + 26))

    # Conference-room shapes: a stage block and a back wall panel
    draw.rectangle([0, int(HEIGHT * 0.62), WIDTH, HEIGHT], fill=(44, 52, 72))
    draw.rectangle(
        [int(WIDTH * 0.08), int(HEIGHT * 0.12),
         int(WIDTH * 0.92), int(HEIGHT * 0.55)],
        fill=(52, 62, 88), outline=(78, 92, 124), width=3,
    )

    # Banner text on the back panel
    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 58
        )
    except OSError:
        font = ImageFont.load_default()
    draw.text(
        (int(WIDTH * 0.14), int(HEIGHT * 0.26)),
        "E CORP  |  ANNUAL TOWN HALL",
        fill=(196, 208, 232), font=font,
    )

    # Silhouettes of an audience, for texture in the lower half
    for _ in range(38):
        cx = random.randint(20, WIDTH - 20)
        cy = random.randint(int(HEIGHT * 0.68), int(HEIGHT * 0.95))
        r = random.randint(16, 30)
        tone = random.randint(18, 40)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(tone, tone + 4, tone + 12))
        draw.rectangle(
            [cx - int(r * 1.5), cy + r, cx + int(r * 1.5), cy + int(r * 3.4)],
            fill=(tone - 4, tone, tone + 10),
        )

    # Ceiling lights
    for _ in range(14):
        lx = random.randint(0, WIDTH)
        ly = random.randint(0, int(HEIGHT * 0.1))
        rr = random.randint(6, 14)
        draw.ellipse([lx - rr, ly - rr, lx + rr, ly + rr], fill=(220, 224, 236))

    # Fine random noise: raises DCT complexity, which increases stego capacity
    px = img.load()
    for _ in range(90000):
        x = random.randint(0, WIDTH - 1)
        y = random.randint(0, HEIGHT - 1)
        r, g, b = px[x, y]
        d = random.randint(-14, 14)
        px[x, y] = (
            max(0, min(255, r + d)),
            max(0, min(255, g + d)),
            max(0, min(255, b + d)),
        )

    img = img.filter(ImageFilter.GaussianBlur(0.4))
    # quality=92: high enough to keep capacity, low enough to look like a photo
    img.save(path, "JPEG", quality=92, optimize=False)
    print(f"      wrote {path} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: make_cover.py output.jpg")
    build(sys.argv[1])
