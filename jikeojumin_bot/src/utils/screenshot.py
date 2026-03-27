from pathlib import Path

from playwright.sync_api import sync_playwright


def capture_page(url: str, save_path: str) -> str:
    path = Path(save_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1800})
        page.goto(url, wait_until="domcontentloaded", timeout=15000)
        page.screenshot(path=str(path), full_page=True)
        browser.close()

    return str(path)
