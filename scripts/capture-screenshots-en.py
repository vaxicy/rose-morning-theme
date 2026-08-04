#!/usr/bin/env python3
"""Render two English Chrome Web Store screenshots (1280x800) by loading HTML
mockups in headless Chromium and capturing the viewport.

Replaces the old PIL-based generator with a browser-rendered one so that
fonts, spacing, and proportions match a real Chrome window wearing the
Rose Morning theme.

Output:
  store-assets/screenshots/en/rose-morning-ntp.png
  store-assets/screenshots/en/rose-morning-reading.png
"""
import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
MOCKUPS = ROOT / "scripts" / "mockups"
OUT = ROOT / "store-assets" / "screenshots" / "en"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1280, 800


def shoot(page, html_path: Path, out_path: Path):
    page.set_viewport_size({"width": W, "height": H})
    page.goto(html_path.as_uri(), wait_until="networkidle")
    # Give web fonts a moment to settle (networkidle already covers this, but
    # a short wait protects against late font swaps on first run).
    page.wait_for_timeout(400)
    page.screenshot(path=str(out_path), full_page=False, type="png")
    print(f"saved {out_path.relative_to(ROOT)}")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            viewport={"width": W, "height": H},
            device_scale_factor=1,
        )
        page = context.new_page()

        shoot(page, MOCKUPS / "ntp.html",     OUT / "rose-morning-ntp.png")
        shoot(page, MOCKUPS / "reading.html", OUT / "rose-morning-reading.png")

        browser.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"FAIL: {e}", file=sys.stderr)
        sys.exit(1)
