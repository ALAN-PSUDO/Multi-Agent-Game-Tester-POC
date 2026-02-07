from __future__ import annotations

import time
from pathlib import Path
from typing import Dict, List

from playwright.sync_api import sync_playwright

from app.services.utils import ensure_dir


def _maybe_click_text(page, text_options: List[str]) -> bool:
    for text in text_options:
        locator = page.get_by_text(text, exact=False)
        if locator.count() > 0:
            try:
                locator.first.click(timeout=2000)
                return True
            except Exception:
                continue
    return False


def _prepare_page(page) -> None:
    _maybe_click_text(page, ["accept", "agree", "ok", "close", "dismiss", "continue"])


def _auto_explore(page) -> str:
    buttons = page.locator("button")
    if buttons.count() > 0:
        buttons.first.click(timeout=3000)
        return "clicked first button"
    links = page.locator("a")
    if links.count() > 0:
        links.first.click(timeout=3000)
        return "clicked first link"
    return "no clickable element found"


def _run_step(page, step: Dict[str, str]) -> str:
    action = step.get("action", "").lower()
    if action == "click_text":
        text = step.get("text", "")
        page.get_by_text(text, exact=False).first.click(timeout=3000)
        return f"click_text:{text}"
    if action == "click_selector":
        selector = step.get("selector", "")
        page.locator(selector).first.click(timeout=3000)
        return f"click_selector:{selector}"
    if action == "input":
        selector = step.get("selector", "")
        value = step.get("value", "")
        page.locator(selector).first.fill(value, timeout=3000)
        return f"input:{selector}"
    if action == "press":
        key = step.get("key", "Enter")
        page.keyboard.press(key)
        return f"press:{key}"
    if action == "wait":
        ms = int(step.get("ms", 1000))
        page.wait_for_timeout(ms)
        return f"wait:{ms}"
    if action == "assert_text":
        expected = step.get("text", "")
        page.get_by_text(expected, exact=False).first.wait_for(timeout=3000)
        return f"assert_text:{expected}"
    return _auto_explore(page)


def execute_tests(
    url: str,
    tests: List[dict],
    run_id: str,
    artifacts_root: Path,
    headless: bool = True,
) -> List[dict]:
    results: List[dict] = []
    run_dir = ensure_dir(artifacts_root / run_id)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=headless, args=["--disable-dev-shm-usage"])
        context = browser.new_context(viewport={"width": 1280, "height": 720})

        for test in tests:
            test_id = test.get("id")
            test_dir = ensure_dir(run_dir / f"test_{test_id}")
            console_logs: List[str] = []
            page = context.new_page()
            page.on("console", lambda msg: console_logs.append(msg.text))
            status = "PASS"
            error = None
            steps_run = []

            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                _prepare_page(page)
                before_path = test_dir / "before.png"
                page.screenshot(path=str(before_path), full_page=True)

                steps = test.get("steps") or []
                if not steps:
                    steps_run.append(_auto_explore(page))
                else:
                    for step in steps:
                        steps_run.append(_run_step(page, step))

                after_path = test_dir / "after.png"
                page.screenshot(path=str(after_path), full_page=True)
                html_path = test_dir / "page.html"
                html_path.write_text(page.content(), encoding="utf-8")

            except Exception as exc:
                status = "FAIL"
                error = str(exc)
            finally:
                page.close()

            results.append(
                {
                    "id": test_id,
                    "title": test.get("title"),
                    "status": status,
                    "error": error,
                    "steps_run": steps_run,
                    "artifacts": {
                        "before": f"/artifacts/{run_id}/test_{test_id}/before.png",
                        "after": f"/artifacts/{run_id}/test_{test_id}/after.png",
                        "html": f"/artifacts/{run_id}/test_{test_id}/page.html",
                        "console": f"/artifacts/{run_id}/test_{test_id}/console.log",
                    },
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                }
            )
            (test_dir / "console.log").write_text("\n".join(console_logs), encoding="utf-8")

        context.close()
        browser.close()

    return results
