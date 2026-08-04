#!/usr/bin/env python3
"""Generate 4 candidate icon designs for Vanilla Rose Theme and a side-by-side preview.

All designs use a cream rounded-square background + rose/deep-rose palette,
matching the theme.json colors. No letters/abbreviations (per icon rules).
"""
from PIL import Image, ImageDraw
import math

SIZE = 128
BG = (252, 245, 238)          # warm cream white
BLUSH = (251, 232, 231)       # soft blush pink
ROSE = (255, 196, 208)        # gentle pink highlight
DEEP = (214, 122, 140)        # deep rose
DARK = (92, 74, 74)           # soft dark brown
LEAF = (180, 200, 150)        # muted sage green
RADIUS = 28


def new_canvas():
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, SIZE - 1, SIZE - 1], radius=RADIUS, fill=BG)
    return img, d


def _petal(d, cx, cy, r, angle_deg, fill, outline=None):
    """Draw a single rounded petal pointing outward at angle_deg (0=right)."""
    a = math.radians(angle_deg)
    dx, dy = math.cos(a), math.sin(a)
    tip = (cx + dx * r * 1.6, cy + dy * r * 1.6)
    # control points perpendicular to petal axis
    px, py = -dy, dx
    c1 = (cx + dx * r * 0.6 + px * r * 0.9, cy + dy * r * 0.6 + py * r * 0.9)
    c2 = (cx + dx * r * 0.6 - px * r * 0.9, cy + dy * r * 0.6 - py * r * 0.9)
    base_w = r * 0.55
    b1 = (cx + px * base_w, cy + py * base_w)
    b2 = (cx - px * base_w, cy - py * base_w)
    d.polygon([b1, c1, tip, c2, b2], fill=fill, outline=outline)


def design_A():
    """Blooming rose: 5-petal spiral rose + 3 small leaves."""
    img, d = new_canvas()
    cx, cy = 64, 60
    # outer petals (deep rose) then inner (rose) to create spiral depth
    outer = [i * 72 for i in range(5)]
    for ang in outer:
        _petal(d, cx, cy, 17, ang, DEEP, outline=(192, 100, 116))
    inner = [i * 72 + 36 for i in range(5)]
    for ang in inner:
        _petal(d, cx, cy, 12, ang, ROSE)
    # center core
    d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=BLUSH)
    # leaves
    for lx, ly, la in [(30, 96, 200), (98, 96, -20), (64, 108, 90)]:
        _petal(d, lx, ly, 9, la, LEAF, outline=(150, 175, 120))
    return img


def design_B():
    """Rose bud on stem with leaves."""
    img, d = new_canvas()
    # stem
    d.line([64, 70, 64, 110], fill=LEAF, width=6)
    # leaves
    _petal(d, 46, 96, 12, 200, LEAF, outline=(150, 175, 120))
    _petal(d, 82, 96, 12, -20, LEAF, outline=(150, 175, 120))
    # bud: layered teardrop petals
    cx, cy = 64, 54
    d.polygon([(cx - 16, cy + 14), (cx, cy - 22), (cx + 16, cy + 14)],
              fill=DEEP, outline=(192, 100, 116))
    d.polygon([(cx - 11, cy + 12), (cx, cy - 12), (cx + 11, cy + 12)],
              fill=ROSE)
    d.polygon([(cx - 6, cy + 10), (cx, cy - 4), (cx + 6, cy + 10)],
              fill=BLUSH)
    return img


def design_C():
    """Vanilla custard cup with a floating rose petal."""
    img, d = new_canvas()
    # cup body (trapezoid)
    d.polygon([(40, 50), (88, 50), (82, 104), (46, 104)],
              fill=(255, 250, 244), outline=(224, 210, 200))
    # custard top
    d.ellipse([40, 46, 88, 62], fill=ROSE)
    d.ellipse([44, 48, 84, 58], fill=(255, 214, 222))
    # cup rim
    d.line([40, 50, 88, 50], fill=DEEP, width=3)
    # floating rose petal above cup
    cx, cy = 64, 34
    _petal(d, cx, cy, 11, 90, DEEP, outline=(192, 100, 116))
    _petal(d, cx, cy, 7, 90, ROSE)
    # small leaf accent
    _petal(d, 50, 40, 7, 200, LEAF, outline=(150, 175, 120))
    return img


def design_D():
    """Abstract geometric rose: concentric petal arcs."""
    img, d = new_canvas()
    cx, cy = 64, 64
    # concentric arcs suggesting a spiral rose
    for i, (col, w) in enumerate([(DEEP, 9), (ROSE, 8), (BLUSH, 7)]):
        r = 46 - i * 12
        bbox = [cx - r, cy - r, cx + r, cy + r]
        d.arc(bbox, start=250, end=470, fill=col, width=w)
    # center dot
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=DEEP)
    return img


def build_preview():
    pad = 24
    label_h = 26
    cell = SIZE + pad * 2
    names = ["A 绽放玫瑰", "B 花苞茎叶", "C 香草奶冻", "D 几何玫瑰"]
    designs = [design_A(), design_B(), design_C(), design_D()]
    cols = 2
    rows = 2
    W = cols * cell
    H = rows * (cell + label_h) + pad
    canvas = Image.new("RGBA", (W, H), (235, 228, 228, 255))
    d = ImageDraw.Draw(canvas)
    try:
        from PIL import ImageFont
        font = ImageFont.truetype("msyh.ttc", 16)
    except Exception:
        font = ImageFont.load_default()
    for idx, (name, icon) in enumerate(zip(names, designs)):
        r, c = divmod(idx, cols)
        x = c * cell + pad
        y = r * (cell + label_h) + pad
        canvas.paste(icon, (x, y), icon)
        d.text((x + SIZE // 2, y + SIZE + 4), name,
               fill=(60, 48, 48), font=font, anchor="mm")
    canvas.save("store-assets/icon-preview.png")
    print("Saved store-assets/icon-preview.png")

    # also save each individually
    for name, icon in zip(["A", "B", "C", "D"], designs):
        icon.save(f"store-assets/icon-candidate-{name}.png")
    print("Saved store-assets/icon-candidate-{A,B,C,D}.png")


if __name__ == "__main__":
    build_preview()
