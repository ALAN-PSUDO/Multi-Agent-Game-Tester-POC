import json
import re
from typing import List

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda

from app.services.ollama_client import chat


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


def _default_plan() -> List[dict]:
    return [
        {
            "id": idx,
            "title": f"Explore gameplay flow {idx}",
            "type": "explore",
            "steps": [],
            "expected": "Game responds without errors",
        }
        for idx in range(1, 21)
    ]


def build_plan(url: str, snapshot: dict, memory_suggestions: List[dict]) -> List[dict]:
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a senior QA agent for web puzzle games. "
                "Generate EXACTLY 20 test cases as JSON array. "
                "Each test case must include: id (1..20), title, type, steps, expected. "
                "Steps are objects with action plus fields. "
                "Use actions: click_text, click_selector, input, press, wait, assert_text. "
                "Return only JSON.",
            ),
            (
                "human",
                "URL: {url}\n"
                "Page title: {title}\n"
                "Snapshot text: {snapshot_text}\n"
                "Prior relevant tests: {memory}\n"
                "Generate the 20 test cases now.",
            ),
        ]
    )

    def _call_llm(prompt_value):
        messages = [
            {"role": message.type, "content": message.content}
            for message in prompt_value.messages
        ]
        return chat(messages)

    chain = prompt | RunnableLambda(_call_llm)
    response = chain.invoke(
        {
            "url": url,
            "title": snapshot.get("title"),
            "snapshot_text": snapshot.get("text"),
            "memory": memory_suggestions,
        }
    )

    plan = _parse_json_list(response)
    if len(plan) < 20:
        plan = _default_plan()
    return plan[:20]
