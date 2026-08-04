"""
Generate Rose Morning Theme's two Chrome Web Store promo tiles:
- Small promo tile: 440 x 280
- Marquee (top) promo tile: 1400 x 560

NOTE (Chrome THEME convention): Promo tiles for a Chrome THEME are
English-only (unlike Chrome EXTENSIONS which require bilingual zh+en).
- Button text vertically centered, font scales with canvas
- Element bottom edge keeps >= 12px safe margin
- Blocks do not overlap
- Even card grid, gap >= 10px
"""

from PIL import Image, ImageDraw, ImageFont
import os

# --- Theme colors (from theme.json) ---
CREAM_BG     = (252, 245, 238)  # #FCF5EE  warm cream toolbar
BLUSH_FRAME  = (251, 232, 231)  # #FBE8E7  soft blush frame
LIGHT_ROSE   = (247, 221, 222)  # #F7DDDE  active tab
SOFT_PINK    = (255, 196, 208)  # #FFC4D0  accent
ROSE         = (214, 122, 140)  # #D67A8C  link / hover
DEEP_ROSE    = (172,  84, 102)  # #AC5466  hover/pressed
TEXT_DARK    = ( 92,  74,  74)  # #5C4A4A  primary text
TEXT_MUTED   = (140, 120, 120)  # #8C7878  secondary text
WHITE        = (255, 255, 255)
PAPER        = (251, 241, 231)  # #FBF1E7  paper card


# --- Fonts (English / sans only; Chrome theme promo is English-only) ---
FONT_PATHS = {
    "sans":   "C:/Windows/Fonts/segoeui.ttf",
    "sans_b": "C:/Windows/Fonts/segoeuib.ttf",
    "sans_sb":"C:/Windows/Fonts/segoeuisl.ttf",  # semilight
}

def load_font(path_key: str, size: int) -> ImageFont.FreeTypeFont:
    p = FONT_PATHS.get(path_key)
    try:
        return ImageFont.truetype(p, size)
    except Exception:
        return ImageFont.load_default()


def measure(draw, text: str, font) -> tuple:
    """返回 (width, height)"""
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def text_size(draw, text, font):
    return measure(draw, text, font)


def fit_text(draw, text, font_key, max_w, max_size, min_size=10):
    """字号自适应: 当 max_w 不够时缩小字号"""
    size = max_size
    while size > min_size:
        f = load_font(font_key, size)
        w, _ = text_size(draw, text, f)
        if w <= max_w:
            return f
        size -= 1
    return load_font(font_key, min_size)


def draw_rounded_rect(draw, xy, radius, fill, outline=None, width=1):
    x1, y1, x2, y2 = xy
    if outline:
        draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)
    else:
        draw.rounded_rectangle(xy, radius=radius, fill=fill)


# ===================================================================
# Chrome thumbnail drawing
# ===================================================================
def draw_chrome_thumbnail(draw, ox, oy, w, h, scale=1.0):
    """Draw a Chrome window thumbnail (browser chrome + simplified NTP).
    scale: zoom ratio, 1.0 = large tile, 0.36 = small tile
    """
    tab_h       = int(34 * scale)
    toolbar_h   = int(40 * scale)
    omnibox_h   = int(28 * scale)
    bookmark_h  = int(30 * scale)

    draw_rounded_rect(draw, (ox, oy, ox + w, oy + h), int(10*scale), CREAM_BG, outline=(225, 200, 200), width=max(1, int(1*scale)))

    cur_y = oy

    # --- Tab strip ---
    draw.rectangle([ox, cur_y, ox + w, cur_y + tab_h], fill=BLUSH_FRAME)
    tab_x = ox + int(6*scale)
    tab_w = int(80*scale)
    tab_h_each = tab_h - int(2*scale)
    for i in range(2):
        tx = tab_x + i * (tab_w + int(4*scale))
        draw_rounded_rect(draw, (tx, cur_y + int(2*scale), tx + tab_w, cur_y + tab_h), int(6*scale), (244, 226, 224))
    active_tx = tab_x + 2 * (tab_w + int(4*scale))
    draw_rounded_rect(draw, (active_tx, cur_y, active_tx + tab_w, cur_y + tab_h + int(4*scale)), int(8*scale), CREAM_BG)
    draw.rectangle([active_tx + int(8*scale), cur_y + tab_h_each + int(2*scale),
                    active_tx + tab_w - int(8*scale), cur_y + tab_h_each + int(5*scale)], fill=SOFT_PINK)
    plus_x = active_tx + tab_w + int(8*scale)
    plus_y = cur_y + int(8*scale)
    plus_size = int(18*scale)
    draw.line([(plus_x + plus_size//2 - int(4*scale), plus_y + plus_size//2),
               (plus_x + plus_size//2 + int(4*scale), plus_y + plus_size//2)], fill=TEXT_MUTED, width=max(1, int(scale*1.5)))
    draw.line([(plus_x + plus_size//2, plus_y + plus_size//2 - int(4*scale)),
               (plus_x + plus_size//2, plus_y + plus_size//2 + int(4*scale))], fill=TEXT_MUTED, width=max(1, int(scale*1.5)))

    cur_y += tab_h

    # --- Toolbar ---
    draw.rectangle([ox, cur_y, ox + w, cur_y + toolbar_h], fill=BLUSH_FRAME)
    cx = ox + int(14*scale)
    cy = cur_y + toolbar_h // 2
    draw.polygon([(cx, cy - int(5*scale)), (cx + int(8*scale), cy), (cx, cy + int(5*scale))], fill=(200, 180, 180))
    cx = ox + int(40*scale)
    draw.ellipse([cx - int(5*scale), cy - int(5*scale), cx + int(5*scale), cy + int(5*scale)], outline=ROSE, width=max(1, int(1.5*scale)))
    omnibox_x = ox + int(70*scale)
    omnibox_w = w - int(140*scale)
    draw_rounded_rect(draw, (omnibox_x, cur_y + int(6*scale),
                              omnibox_x + omnibox_w, cur_y + toolbar_h - int(6*scale)),
                      int(8*scale), WHITE, outline=SOFT_PINK, width=max(1, int(1.5*scale)))
    cx_g = omnibox_x + int(14*scale)
    cy_g = cur_y + toolbar_h // 2
    draw.ellipse([cx_g - int(7*scale), cy_g - int(7*scale), cx_g + int(7*scale), cy_g + int(7*scale)],
                 outline=ROSE, width=max(1, int(1.5*scale)))
    draw.line([(cx_g, cy_g), (cx_g + int(10*scale), cy_g)], fill=ROSE, width=max(1, int(1.5*scale)))
    av_x = ox + w - int(20*scale)
    av_y = cur_y + toolbar_h // 2
    draw.ellipse([av_x - int(8*scale), av_y - int(8*scale), av_x + int(8*scale), av_y + int(8*scale)], fill=ROSE)

    cur_y += toolbar_h

    # --- Bookmarks bar ---
    if bookmark_h > 0:
        draw.rectangle([ox, cur_y, ox + w, cur_y + bookmark_h], fill=PAPER)
        bm_x = ox + int(10*scale)
        bm_y = cur_y + bookmark_h // 2
        chip_w = int(20*scale)
        chip_gap = int(6*scale)
        chip_count = 6
        for i in range(chip_count):
            chx = bm_x + i * (chip_w + chip_gap)
            color = [ROSE, ROSE, SOFT_PINK, (180, 200, 175), (200, 175, 200), (220, 195, 175)][i]
            draw_rounded_rect(draw, (chx, bm_y - int(5*scale), chx + chip_w, bm_y + int(5*scale)),
                              int(3*scale), color)
        cur_y += bookmark_h

    # --- NTP area (simplified): logo + search box + 2x2 cards ---
    ntp_x = ox + int(40*scale)
    ntp_w = w - int(80*scale)
    ntp_y = cur_y + int(20*scale)
    logo_size = int(28*scale)
    lx = ox + w // 2 - logo_size // 2
    ly = ntp_y
    draw_rounded_rect(draw, (lx, ly, lx + logo_size, ly + logo_size), int(6*scale), CREAM_BG, outline=ROSE, width=max(1, int(1.5*scale)))
    search_y = ly + logo_size + int(14*scale)
    search_h = int(40*scale)
    draw_rounded_rect(draw, (ntp_x, search_y, ntp_x + ntp_w, search_y + search_h),
                      int(search_h/2), WHITE, outline=SOFT_PINK, width=max(1, int(1.5*scale)))
    card_y = search_y + search_h + int(20*scale)
    card_gap = int(10*scale)
    card_w = (ntp_w - card_gap) // 2
    card_h = int(50*scale)
    for r in range(2):
        for c in range(2):
            idx = r * 2 + c
            cx_card = ntp_x + c * (card_w + card_gap)
            cy_card = card_y + r * (card_h + card_gap)
            card_color = [BLUSH_FRAME, (240, 226, 220), (245, 220, 220), PAPER][idx]
            draw_rounded_rect(draw, (cx_card, cy_card, cx_card + card_w, cy_card + card_h),
                              int(10*scale), card_color)


# ===================================================================
# Promo tiles (English-only for Chrome themes)
# ===================================================================
def draw_440x280():
    W, H = 440, 280
    img = Image.new("RGB", (W, H), BLUSH_FRAME)
    draw = ImageDraw.Draw(img)

    # --- Left text block ---
    # Title: fit to 200px max width so it doesn't collide with right thumbnail
    title_max_w = 200
    title_en = fit_text(draw, "Rose Morning", "sans_b", title_max_w, 34, min_size=20)
    draw.text((24, 56), "Rose Morning", font=title_en, fill=ROSE)
    sub_en = load_font("sans", 13)
    draw.text((24, 104), "A cream & rose Chrome theme", font=sub_en, fill=TEXT_MUTED)

    # --- CTA button (single line, vertically centered) ---
    btn_x, btn_y = 24, 196
    btn_w, btn_h = 180, 44
    btn_center_y = btn_y + btn_h // 2
    draw_rounded_rect(draw, (btn_x, btn_y, btn_x + btn_w, btn_y + btn_h), 22, ROSE)
    btn_en = load_font("sans_b", 16)
    l_w, l_h = text_size(draw, "Try It Now", btn_en)
    draw.text((btn_x + (btn_w - l_w)//2, btn_center_y - l_h//2), "Try It Now", font=btn_en, fill=WHITE)

    # 验证按钮底边 <= H - 12
    assert btn_y + btn_h <= H - 12, f"按钮底 {btn_y + btn_h} 超出画布 {H - 12}"

    # --- Right Chrome thumbnail ---
    thumb_x, thumb_y = 236, 20
    thumb_w, thumb_h = 192, 240
    draw_chrome_thumbnail(draw, thumb_x, thumb_y, thumb_w, thumb_h, scale=0.55)

    img.save("store-assets/promo/440x280.png", "PNG", optimize=True)
    print(f"[ok] 440x280.png ({W}x{H})")


def draw_1400x560():
    W, H = 1400, 560
    img = Image.new("RGB", (W, H), BLUSH_FRAME)
    draw = ImageDraw.Draw(img)

    # --- Left text block ---
    pad_x = 60
    t_en = load_font("sans_b", 66)
    draw.text((pad_x, 118), "Rose Morning", font=t_en, fill=ROSE)
    s_en = load_font("sans", 22)
    draw.text((pad_x, 214), "A calm morning light for everyday browsing", font=s_en, fill=TEXT_MUTED)

    # --- CTA button (single line, vertically centered) ---
    btn_x, btn_y = pad_x, 360
    btn_w, btn_h = 280, 64
    btn_center_y = btn_y + btn_h // 2
    draw_rounded_rect(draw, (btn_x, btn_y, btn_x + btn_w, btn_y + btn_h), 32, ROSE)
    btn_en = load_font("sans_b", 22)
    l_w, l_h = text_size(draw, "Try It Now", btn_en)
    draw.text((btn_x + (btn_w - l_w)//2, btn_center_y - l_h//2), "Try It Now", font=btn_en, fill=WHITE)

    # --- Decorative tags: feature chips (English-only) ---
    tag_y = btn_y + btn_h + 24
    tag_h = 40
    tag1 = "No Wallpaper"
    tag2 = "Solid Colors"
    tag_font = load_font("sans", 15)
    tag1_w, tag1_h = text_size(draw, tag1, tag_font)
    tag2_w, tag2_h = text_size(draw, tag2, tag_font)
    tag_x = btn_x
    pad_tag_x = 16
    pad_tag_y = 10
    draw_rounded_rect(draw, (tag_x, tag_y, tag_x + tag1_w + pad_tag_x*2, tag_y + tag1_h + pad_tag_y*2),
                      18, BLUSH_FRAME, outline=SOFT_PINK)
    draw.text((tag_x + pad_tag_x, tag_y + pad_tag_y), tag1, font=tag_font, fill=ROSE)
    tag2_x = tag_x + tag1_w + pad_tag_x*2 + 12
    draw_rounded_rect(draw, (tag2_x, tag_y, tag2_x + tag2_w + pad_tag_x*2, tag_y + tag2_h + pad_tag_y*2),
                      18, BLUSH_FRAME, outline=SOFT_PINK)
    draw.text((tag2_x + pad_tag_x, tag_y + pad_tag_y), tag2, font=tag_font, fill=ROSE)

    # 验证按钮底边 <= H - 12
    assert btn_y + btn_h <= H - 12, f"按钮底 {btn_y + btn_h} 超出画布 {H - 12}"

    # --- Right Chrome thumbnail (large, scale 1.0) ---
    thumb_x, thumb_y = 760, 60
    thumb_w, thumb_h = 580, 460
    draw_chrome_thumbnail(draw, thumb_x, thumb_y, thumb_w, thumb_h, scale=1.0)

    img.save("store-assets/promo/1400x560.png", "PNG", optimize=True)
    print(f"[ok] 1400x560.png ({W}x{H})")


if __name__ == "__main__":
    os.makedirs("store-assets/promo", exist_ok=True)
    draw_440x280()
    draw_1400x560()
    print("\n[DONE] promo tiles generated (English-only)")
