from __future__ import annotations

import os
from pathlib import Path

from playwright.sync_api import sync_playwright


def capture_page(url: str, save_path: str) -> str:
    path = Path(save_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    storage_state = os.getenv("PLAYWRIGHT_STORAGE_STATE") or None

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=storage_state)
        page = context.new_page()
        page.set_viewport_size({"width": 1440, "height": 1800})
        page.goto(url, wait_until="domcontentloaded", timeout=20000)
        page.screenshot(path=str(path), full_page=True)
        context.close()
        browser.close()

    return str(path)
