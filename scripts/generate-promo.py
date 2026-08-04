"""
生成 Rose Morning Theme 的两个 Chrome Web Store 宣传图块
- 小型宣传图块: 440 x 280
- 顶部宣传图块: 1400 x 560

规范:
- 双语(中 + 英同一张图)
- 按钮文字垂直居中, 字号缩放
- 段落底边留 >= 12px 安全边距
- 区块不重叠
- 卡片偶数网格, gap >= 10px
"""

from PIL import Image, ImageDraw, ImageFont
import os

# --- 主题色 (来自 theme.json) ---
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


# --- 字体 (尝试加载系统中文字体; 失败回退到 PIL 默认) ---
FONT_PATHS = {
    "sans":   "C:/Windows/Fonts/segoeui.ttf",
    "sans_b": "C:/Windows/Fonts/segoeuib.ttf",
    "sans_sb":"C:/Windows/Fonts/segoeuisl.ttf",  # semilight
    "cn":     "C:/Windows/Fonts/msyh.ttc",        # 微软雅黑
    "cn_b":   "C:/Windows/Fonts/msyhbd.ttc",
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
# Chrome 缩略图绘制
# ===================================================================
def draw_chrome_thumbnail(draw, ox, oy, w, h, scale=1.0):
    """画一个 Chrome 窗口缩略图 (browser chrome + NTP 简化版)
    scale: 缩放比例, 1.0 = 大图用, 0.36 = 小图用
    """
    # 缩放后的尺寸
    tab_h       = int(34 * scale)
    toolbar_h   = int(40 * scale)
    omnibox_h   = int(28 * scale)
    bookmark_h  = int(30 * scale)
    ntp_indicator_h = int(72 * scale)

    # 窗口整体背景
    draw_rounded_rect(draw, (ox, oy, ox + w, oy + h), int(10*scale), CREAM_BG, outline=(225, 200, 200), width=max(1, int(1*scale)))

    cur_y = oy

    # --- Tab strip ---
    draw.rectangle([ox, cur_y, ox + w, cur_y + tab_h], fill=BLUSH_FRAME)
    tab_x = ox + int(6*scale)
    tab_w = int(80*scale)
    tab_h_each = tab_h - int(2*scale)
    # 两个 inactive tab
    for i in range(2):
        tx = tab_x + i * (tab_w + int(4*scale))
        draw_rounded_rect(draw, (tx, cur_y + int(2*scale), tx + tab_w, cur_y + tab_h), int(6*scale), (244, 226, 224))
    # active tab (新标签页)
    active_tx = tab_x + 2 * (tab_w + int(4*scale))
    draw_rounded_rect(draw, (active_tx, cur_y, active_tx + tab_w, cur_y + tab_h + int(4*scale)), int(8*scale), CREAM_BG)
    # active tab 底边玫粉
    draw.rectangle([active_tx + int(8*scale), cur_y + tab_h_each + int(2*scale),
                    active_tx + tab_w - int(8*scale), cur_y + tab_h_each + int(5*scale)], fill=SOFT_PINK)
    # 新开 + 按钮
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
    # back arrow (灰)
    cx = ox + int(14*scale)
    cy = cur_y + toolbar_h // 2
    draw.polygon([(cx, cy - int(5*scale)), (cx + int(8*scale), cy), (cx, cy + int(5*scale))], fill=(200, 180, 180))
    # refresh (玫粉)
    cx = ox + int(40*scale)
    draw.ellipse([cx - int(5*scale), cy - int(5*scale), cx + int(5*scale), cy + int(5*scale)], outline=ROSE, width=max(1, int(1.5*scale)))
    # omnibox
    omnibox_x = ox + int(70*scale)
    omnibox_w = w - int(140*scale)
    draw_rounded_rect(draw, (omnibox_x, cur_y + int(6*scale),
                              omnibox_x + omnibox_w, cur_y + toolbar_h - int(6*scale)),
                      int(8*scale), WHITE, outline=SOFT_PINK, width=max(1, int(1.5*scale)))
    # Google G (简化)
    cx_g = omnibox_x + int(14*scale)
    cy_g = cur_y + toolbar_h // 2
    draw.ellipse([cx_g - int(7*scale), cy_g - int(7*scale), cx_g + int(7*scale), cy_g + int(7*scale)],
                 outline=ROSE, width=max(1, int(1.5*scale)))
    draw.line([(cx_g, cy_g), (cx_g + int(10*scale), cy_g)], fill=ROSE, width=max(1, int(1.5*scale)))
    # L 头像 (右侧)
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

    # --- NTP area (极简): logo + 搜索框 + 4 卡片 2x2 ---
    ntp_x = ox + int(40*scale)
    ntp_w = w - int(80*scale)
    ntp_y = cur_y + int(20*scale)
    # Logo (圆角方形描边)
    logo_size = int(28*scale)
    lx = ox + w // 2 - logo_size // 2
    ly = ntp_y
    draw_rounded_rect(draw, (lx, ly, lx + logo_size, ly + logo_size), int(6*scale), CREAM_BG, outline=ROSE, width=max(1, int(1.5*scale)))
    # 搜索框
    search_y = ly + logo_size + int(14*scale)
    search_h = int(40*scale)
    draw_rounded_rect(draw, (ntp_x, search_y, ntp_x + ntp_w, search_y + search_h),
                      int(search_h/2), WHITE, outline=SOFT_PINK, width=max(1, int(1.5*scale)))
    # 卡片 2x2
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
# Promo 图块
# ===================================================================
def draw_440x280():
    W, H = 440, 280
    img = Image.new("RGB", (W, H), BLUSH_FRAME)
    draw = ImageDraw.Draw(img)

    # --- 左侧文案区 ---
    # 标题: "玫瑰早晨"  (中文)
    title_zh = load_font("cn_b", 30)
    draw.text((24, 60), "玫瑰早晨", font=title_zh, fill=ROSE)
    # 标题: "Rose Morning" (英文)
    title_en = load_font("sans_b", 22)
    draw.text((24, 100), "Rose Morning", font=title_en, fill=TEXT_DARK)
    # 副标题
    sub_zh = load_font("cn", 12)
    draw.text((24, 138), "柔粉晨光中的 Chrome 主题", font=sub_zh, fill=TEXT_MUTED)
    sub_en = load_font("sans", 11)
    draw.text((24, 158), "A cream & rose Chrome theme", font=sub_en, fill=TEXT_MUTED)

    # --- CTA 按钮 (双语, 垂直居中) ---
    btn_x, btn_y = 24, 200
    btn_w, btn_h = 188, 44
    btn_center_y = btn_y + btn_h // 2
    draw_rounded_rect(draw, (btn_x, btn_y, btn_x + btn_w, btn_y + btn_h), 22, ROSE)
    # 中文 (顶部)
    btn_zh = load_font("cn_b", 14)
    btn_en = load_font("sans_b", 11)
    zh_w, zh_h = text_size(draw, "立即使用 · Try It Now".split(" · ")[0], btn_zh)
    en_w, en_h = text_size(draw, "Try It Now", btn_en)
    # 单行布局, 居中显示
    label_w, label_h = text_size(draw, "立即体验 · Try It Now", btn_zh)
    # 改为两行布局避免太宽
    label1, label2 = "立即体验", "Try It Now"
    l1w, l1h = text_size(draw, label1, btn_zh)
    l2w, l2h = text_size(draw, label2, btn_en)
    line_gap = 2
    total_h = l1h + line_gap + l2h
    top_y = btn_center_y - total_h // 2
    draw.text((btn_x + (btn_w - l1w)//2, top_y), label1, font=btn_zh, fill=WHITE)
    draw.text((btn_x + (btn_w - l2w)//2, top_y + l1h + line_gap), label2, font=btn_en, fill=WHITE)

    # 验证按钮底边 <= H - 12
    assert btn_y + btn_h <= H - 12, f"按钮底 {btn_y + btn_h} 超出画布 {H - 12}"

    # --- 右侧 Chrome 缩略图 ---
    thumb_x, thumb_y = 240, 20
    thumb_w, thumb_h = 188, 240
    draw_chrome_thumbnail(draw, thumb_x, thumb_y, thumb_w, thumb_h, scale=0.55)

    img.save("store-assets/promo/440x280.png", "PNG", optimize=True)
    print(f"[ok] 440x280.png ({W}x{H})")


def draw_1400x560():
    W, H = 1400, 560
    img = Image.new("RGB", (W, H), BLUSH_FRAME)
    draw = ImageDraw.Draw(img)

    # --- 左侧文案区 ---
    pad_x = 60
    # 主标题中文
    t_zh = load_font("cn_b", 64)
    draw.text((pad_x, 110), "玫瑰早晨", font=t_zh, fill=ROSE)
    # 主标题英文
    t_en = load_font("sans_b", 48)
    draw.text((pad_x, 196), "Rose Morning", font=t_en, fill=TEXT_DARK)
    # 副标题中文
    s_zh = load_font("cn", 22)
    draw.text((pad_x, 280), "柔粉晨光中的 Chrome 主题 · Cream & Rose", font=s_zh, fill=TEXT_MUTED)
    # 副标题英文
    s_en = load_font("sans", 18)
    draw.text((pad_x, 314), "A calm morning light for everyday browsing", font=s_en, fill=TEXT_MUTED)

    # --- CTA 按钮 (双语, 垂直居中) ---
    btn_x, btn_y = pad_x, 410
    btn_w, btn_h = 280, 64
    btn_center_y = btn_y + btn_h // 2
    draw_rounded_rect(draw, (btn_x, btn_y, btn_x + btn_w, btn_y + btn_h), 32, ROSE)
    btn_zh = load_font("cn_b", 22)
    btn_en = load_font("sans_b", 16)
    label1, label2 = "立即体验", "Try It Now"
    l1w, l1h = text_size(draw, label1, btn_zh)
    l2w, l2h = text_size(draw, label2, btn_en)
    line_gap = 4
    total_h = l1h + line_gap + l2h
    top_y = btn_center_y - total_h // 2
    draw.text((btn_x + (btn_w - l1w)//2, top_y), label1, font=btn_zh, fill=WHITE)
    draw.text((btn_x + (btn_w - l2w)//2, top_y + l1h + line_gap), label2, font=btn_en, fill=WHITE)

    # --- 装饰小元素: 二级标签 ---
    tag_y = btn_y + btn_h + 20
    tag_h = 30
    tag1 = "中英双语 · Bilingual"
    tag2 = "纯色主题 · No Wallpaper"
    tag_font_zh = load_font("cn", 13)
    tag_font_en = load_font("sans", 12)
    tag1_w, tag1_h = text_size(draw, tag1, tag_font_zh)
    tag2_w, tag2_h = text_size(draw, tag2, tag_font_zh)
    tag_x = btn_x
    # 两个 tag 紧贴
    pad_tag_x = 12
    pad_tag_y = 6
    draw_rounded_rect(draw, (tag_x, tag_y, tag_x + tag1_w + pad_tag_x*2, tag_y + tag1_h + pad_tag_y*2),
                      14, BLUSH_FRAME, outline=SOFT_PINK)
    draw.text((tag_x + pad_tag_x, tag_y + pad_tag_y), tag1, font=tag_font_zh, fill=ROSE)
    tag2_x = tag_x + tag1_w + pad_tag_x*2 + 10
    draw_rounded_rect(draw, (tag2_x, tag_y, tag2_x + tag2_w + pad_tag_x*2, tag_y + tag2_h + pad_tag_y*2),
                      14, BLUSH_FRAME, outline=SOFT_PINK)
    draw.text((tag2_x + pad_tag_x, tag_y + pad_tag_y), tag2, font=tag_font_zh, fill=ROSE)

    # 验证按钮底边 <= H - 12
    assert btn_y + btn_h <= H - 12, f"按钮底 {btn_y + btn_h} 超出画布 {H - 12}"

    # --- 右侧 Chrome 缩略图 (大图 1.0 scale) ---
    thumb_x, thumb_y = 760, 60
    thumb_w, thumb_h = 580, 460
    draw_chrome_thumbnail(draw, thumb_x, thumb_y, thumb_w, thumb_h, scale=1.0)

    img.save("store-assets/promo/1400x560.png", "PNG", optimize=True)
    print(f"[ok] 1400x560.png ({W}x{H})")


if __name__ == "__main__":
    os.makedirs("store-assets/promo", exist_ok=True)
    draw_440x280()
    draw_1400x560()
    print("\n[DONE] 两张宣传图生成完成")
