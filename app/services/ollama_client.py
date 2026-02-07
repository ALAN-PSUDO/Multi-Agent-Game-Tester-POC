import os
from typing import List, Dict, Optional

import requests


def chat(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    base_url: Optional[str] = None,
    timeout: int = 60,
) -> Optional[str]:
    model = model or os.getenv("OLLAMA_MODEL", "llama3.1")
    base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    url = f"{base_url.rstrip('/')}/api/chat"
    payload = {"model": model, "messages": messages, "stream": False}

    try:
        response = requests.post(url, json=payload, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        return data.get("message", {}).get("content")
    except requests.RequestException:
        return None
