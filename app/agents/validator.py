import json
import re
from typing import Dict, List

from app.services.ollama_client import chat
from app.services.playwright_runner import execute_tests


def _parse_json_list(text: str) -> List[dict]:
    if not text:
        return []
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if not match:
        return []
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return []


def repeat_check(url: str, tests: List[dict], run_id: str, artifacts_root, repeat_count: int = 3) -> List[dict]:
    subset = tests[:repeat_count]
    if not subset:
        return []
    return execute_tests(url, subset, f"{run_id}_repeat", artifacts_root)


def cross_agent_review(snapshot: dict, tests: List[dict], results: List[dict]) -> List[dict]:
    prompt = (
        "Review the test results for a web puzzle game. "
        "Return JSON array with objects: id, status (PASS/FAIL), notes.\n"
        "Snapshot: {snapshot}\nResults: {results}\n"
    )
    messages = [
        {"role": "system", "content": "You are a strict QA reviewer."},
        {"role": "user", "content": prompt.format(snapshot=snapshot, results=results)},
    ]
    response = chat(messages)
    parsed = _parse_json_list(response)
    if parsed:
        return parsed
    return [
        {"id": item.get("id"), "status": item.get("status", "UNKNOWN"), "notes": "rule-based"}
        for item in results
    ]


def build_validation(
    url: str,
    snapshot: dict,
    top_tests: List[dict],
    results: List[dict],
    run_id: str,
    artifacts_root,
) -> Dict[str, List[dict]]:
    repeat_results = repeat_check(url, top_tests, run_id, artifacts_root)
    cross_results = cross_agent_review(snapshot, top_tests, results)
    return {"repeat": repeat_results, "cross_agent": cross_results}
