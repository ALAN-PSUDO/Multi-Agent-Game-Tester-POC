from pathlib import Path
from typing import Dict

from playwright.sync_api import sync_playwright

from app.services.utils import ensure_dir


def capture_snapshot(url: str, run_id: str, artifacts_root: Path, headless: bool = True) -> Dict[str, str]:
    run_dir = ensure_dir(artifacts_root / run_id / "snapshot")
    screenshot_path = run_dir / "page.png"
    html_path = run_dir / "page.html"

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=headless, args=["--disable-dev-shm-usage"])
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        title = page.title()
        text = page.evaluate("""() => document.body ? document.body.innerText : ''""")
        trimmed_text = (text or "")[:4000]
        page.screenshot(path=str(screenshot_path), full_page=True)
        html_path.write_text(page.content(), encoding="utf-8")
        context.close()
        browser.close()

    return {
        "url": url,
        "title": title,
        "text": trimmed_text,
        "screenshot": f"/artifacts/{run_id}/snapshot/page.png",
        "html": f"/artifacts/{run_id}/snapshot/page.html",
    }
