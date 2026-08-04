#!/usr/bin/env python3
"""Generate the Rose Morning Theme icon (128x128 PNG).

Minimal flat design: warm cream rounded square with a simple abstract
sunrise + rose petal symbol. No text, no letters, no complicated details.
"""
from PIL import Image, ImageDraw

SIZE = 128
BG = (252, 245, 238)          # warm cream white
BLUSH = (251, 232, 231)       # soft blush pink
ROSE = (255, 196, 208)        # gentle pink highlight
DARK = (92, 74, 74)           # soft dark brown
RADIUS = 28


def rounded_square(draw, box, radius, fill):
    draw.rounded_rectangle(box, radius=radius, fill=fill)


def main():
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Cream rounded-square background
    rounded_square(draw, [0, 0, SIZE - 1, SIZE - 1], RADIUS, BG)

    # Abstract sunrise: a soft rose arc rising from the lower area
    cx = SIZE // 2
    arc_bbox = [cx - 40, 36, cx + 40, 116]
    draw.arc(arc_bbox, start=200, end=340, fill=ROSE, width=8)

    # Soft rose petal / light shape: a small filled circle as the morning sun
    sun_r = 18
    draw.ellipse(
        [cx - sun_r, 58 - sun_r, cx + sun_r, 58 + sun_r],
        fill=ROSE,
    )

    # Subtle blush horizon line for grounding
    draw.line([cx - 44, 100, cx + 44, 100], fill=BLUSH, width=6)

    img.save("store-assets/icon.png")
    print("Saved store-assets/icon.png")


if __name__ == "__main__":
    main()
