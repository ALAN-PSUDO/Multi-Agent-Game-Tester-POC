import json
import re
from pathlib import Path
from typing import Dict, List
from urllib.parse import urlparse

from app.services.utils import ensure_dir

BASE_DIR = Path(__file__).resolve().parents[2]
MEMORY_PATH = BASE_DIR / "data" / "memory.json"


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def _similarity(a: str, b: str) -> float:
    a_tokens = _tokenize(a)
    b_tokens = _tokenize(b)
    if not a_tokens or not b_tokens:
        return 0.0
    return len(a_tokens & b_tokens) / len(a_tokens | b_tokens)


def load_memory() -> Dict[str, List[dict]]:
    if not MEMORY_PATH.exists():
        ensure_dir(MEMORY_PATH.parent)
        MEMORY_PATH.write_text(json.dumps({"entries": []}, indent=2), encoding="utf-8")
    return json.loads(MEMORY_PATH.read_text(encoding="utf-8"))


def save_memory(memory: Dict[str, List[dict]]) -> None:
    ensure_dir(MEMORY_PATH.parent)
    MEMORY_PATH.write_text(json.dumps(memory, indent=2), encoding="utf-8")


def retrieve_related(url: str, page_signature: str, limit: int = 5) -> List[dict]:
    memory = load_memory().get("entries", [])
    host = urlparse(url).netloc
    scored = []
    for entry in memory:
        entry_host = urlparse(entry.get("url", "")).netloc
        similarity = _similarity(page_signature, entry.get("page_signature", ""))
        if host and entry_host == host:
            similarity += 0.2
        scored.append((similarity, entry))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [entry for score, entry in scored[:limit] if score > 0]


def add_run_entries(url: str, page_signature: str, test_plan: List[dict], results: List[dict]) -> None:
    memory = load_memory()
    entries = memory.get("entries", [])
    result_lookup = {item.get("id"): item for item in results}
    for test in test_plan:
        result = result_lookup.get(test.get("id"), {})
        entries.append(
            {
                "url": url,
                "page_signature": page_signature,
                "test_case": test,
                "status": result.get("status"),
                "timestamp": result.get("timestamp"),
            }
        )
    memory["entries"] = entries[-500:]
    save_memory(memory)
