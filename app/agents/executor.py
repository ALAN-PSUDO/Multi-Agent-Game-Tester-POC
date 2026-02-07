from pathlib import Path
from typing import List

from app.services.playwright_runner import execute_tests


def run_tests(url: str, top_tests: List[dict], run_id: str, artifacts_root: Path) -> List[dict]:
    return execute_tests(url, top_tests, run_id, artifacts_root)
