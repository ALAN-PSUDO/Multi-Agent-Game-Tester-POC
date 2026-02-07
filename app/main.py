import threading
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.agents import run_full, run_plan_only
from app.services.utils import now_ts, safe_slug

BASE_DIR = Path(__file__).resolve().parents[1]
REPORTS_ROOT = BASE_DIR / "reports"
ARTIFACTS_ROOT = BASE_DIR / "artifacts"


class RunRequest(BaseModel):
    url: str


runs = {}


def create_run(url: str) -> str:
    run_id = f"{safe_slug(url)}-{now_ts()}"
    runs[run_id] = {"status": "queued", "stage": "queued", "url": url}
    return run_id

app = FastAPI()
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "app" / "static")), name="static")
app.mount("/reports", StaticFiles(directory=str(REPORTS_ROOT)), name="reports")
app.mount("/artifacts", StaticFiles(directory=str(ARTIFACTS_ROOT)), name="artifacts")


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/plan")
def plan_tests(request: RunRequest):
    run_id = create_run(request.url)
    runs[run_id]["stage"] = "planning"
    plan = run_plan_only(request.url, run_id)
    runs[run_id]["status"] = "completed"
    return {"run_id": run_id, **plan}


def _run_pipeline(url: str, run_id: str) -> None:
    try:
        runs[run_id]["status"] = "running"
        runs[run_id]["stage"] = "executing"
        result = run_full(url, run_id)
        runs[run_id]["report"] = result.get("report", {})
        runs[run_id]["status"] = "completed"
        runs[run_id]["stage"] = "report"
    except Exception as exc:
        runs[run_id]["status"] = "failed"
        runs[run_id]["stage"] = "failed"
        runs[run_id]["error"] = str(exc)


@app.post("/api/run")
def run_tests(request: RunRequest):
    run_id = create_run(request.url)
    thread = threading.Thread(target=_run_pipeline, args=(request.url, run_id), daemon=True)
    thread.start()
    return {"run_id": run_id}


@app.get("/api/status/{run_id}")
def run_status(run_id: str):
    if run_id not in runs:
        raise HTTPException(status_code=404, detail="Run not found")
    return runs[run_id]


@app.get("/api/report/{run_id}")
def get_report(run_id: str):
    if run_id not in runs:
        raise HTTPException(status_code=404, detail="Run not found")
    report = runs[run_id].get("report")
    if not report:
        raise HTTPException(status_code=404, detail="Report not ready")
    return report
