import json
import re
from typing import List

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda

from app.services.ollama_client import chat


def _parse_ids(text: str) -> List[int]:
    if not text:
        return []
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if not match:
        return []
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return []


def select_top_tests(url: str, snapshot: dict, test_plan: List[dict]) -> List[dict]:
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Select the 10 most critical tests for a web puzzle game. "
                "Return only a JSON array of ids.",
            ),
            (
                "human",
                "URL: {url}\n"
                "Page title: {title}\n"
                "Tests: {tests}\n"
                "Pick the top 10 ids.",
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
            "tests": test_plan,
        }
    )

    ids = _parse_ids(response)
    if len(ids) < 10:
        return test_plan[:10]
    lookup = {item.get("id"): item for item in test_plan}
    return [lookup[test_id] for test_id in ids if test_id in lookup][:10]
