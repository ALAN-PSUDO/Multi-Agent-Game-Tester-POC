from pathlib import Path
from typing import Dict, List, TypedDict

from langgraph.graph import StateGraph, END

from app.agents.executor import run_tests
from app.agents.planner import build_plan
from app.agents.ranker import select_top_tests
from app.agents.validator import build_validation
from app.services.memory_store import add_run_entries, retrieve_related
from app.services.report_builder import build_report
from app.services.snapshotter import capture_snapshot
from app.services.utils import now_ts


class RunState(TypedDict, total=False):
    url: str
    run_id: str
    snapshot: Dict[str, str]
    memory_suggestions: List[dict]
    test_plan: List[dict]
    top_tests: List[dict]
    results: List[dict]
    validations: Dict[str, List[dict]]
    report: Dict
    report_paths: Dict[str, str]


BASE_DIR = Path(__file__).resolve().parents[2]
ARTIFACTS_ROOT = BASE_DIR / "artifacts"
REPORTS_ROOT = BASE_DIR / "reports"


def snapshot_node(state: RunState) -> Dict:
    snapshot = capture_snapshot(state["url"], state["run_id"], ARTIFACTS_ROOT)
    memory = retrieve_related(state["url"], snapshot.get("text", ""))
    return {"snapshot": snapshot, "memory_suggestions": memory}


def planner_node(state: RunState) -> Dict:
    plan = build_plan(state["url"], state["snapshot"], state["memory_suggestions"])
    return {"test_plan": plan}


def ranker_node(state: RunState) -> Dict:
    top_tests = select_top_tests(state["url"], state["snapshot"], state["test_plan"])
    return {"top_tests": top_tests}


def executor_node(state: RunState) -> Dict:
    results = run_tests(state["url"], state["top_tests"], state["run_id"], ARTIFACTS_ROOT)
    return {"results": results}


def validator_node(state: RunState) -> Dict:
    validations = build_validation(
        state["url"],
        state["snapshot"],
        state["top_tests"],
        state["results"],
        state["run_id"],
        ARTIFACTS_ROOT,
    )
    return {"validations": validations}


def report_node(state: RunState) -> Dict:
    total = len(state.get("results", []))
    passed = len([item for item in state.get("results", []) if item.get("status") == "PASS"])
    summary = {"total": total, "passed": passed, "pass_rate": f"{(passed / total * 100):.1f}%" if total else "0%"}
    report = {
        "run_id": state["run_id"],
        "url": state["url"],
        "timestamp": now_ts(),
        "snapshot": state.get("snapshot"),
        "test_plan": state.get("test_plan"),
        "top_tests": state.get("top_tests"),
        "results": state.get("results"),
        "validations": state.get("validations"),
        "summary": summary,
    }
    report_paths = build_report(state["run_id"], report, REPORTS_ROOT)
    add_run_entries(state["url"], state.get("snapshot", {}).get("text", ""), state.get("test_plan", []), state.get("results", []))
    return {"report": report, "report_paths": report_paths}


workflow = StateGraph(RunState)
workflow.add_node("snapshot", snapshot_node)
workflow.add_node("planner", planner_node)
workflow.add_node("ranker", ranker_node)
workflow.add_node("executor", executor_node)
workflow.add_node("validator", validator_node)
workflow.add_node("report", report_node)

workflow.set_entry_point("snapshot")
workflow.add_edge("snapshot", "planner")
workflow.add_edge("planner", "ranker")
workflow.add_edge("ranker", "executor")
workflow.add_edge("executor", "validator")
workflow.add_edge("validator", "report")
workflow.add_edge("report", END)

orchestrator = workflow.compile()


def run_plan_only(url: str, run_id: str) -> Dict:
    snapshot = capture_snapshot(url, run_id, ARTIFACTS_ROOT)
    memory = retrieve_related(url, snapshot.get("text", ""))
    plan = build_plan(url, snapshot, memory)
    top_tests = select_top_tests(url, snapshot, plan)
    return {"snapshot": snapshot, "test_plan": plan, "top_tests": top_tests}


def run_full(url: str, run_id: str) -> Dict:
    state = orchestrator.invoke({"url": url, "run_id": run_id})
    return state
