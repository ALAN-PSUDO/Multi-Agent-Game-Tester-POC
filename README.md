# Multi-Agent-Game-Tester-POC

Simple POC that plans and runs tests for web puzzle/math games using LangChain + Playwright.

## Quick Start (most people)

### 1) Install

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
sudo npx playwright install-deps
playwright install chromium
```

### 2) Start the local model (Ollama)

```bash
ollama run llama3.1
export OLLAMA_MODEL=llama3.1
export OLLAMA_BASE_URL=http://localhost:11434
```

### 3) Start the API

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000` and click **Generate Plan** then **Run Top 10**.

## Where results go

- Report HTML: `reports/<run_id>/report.html`
- Report JSON: `reports/<run_id>/report.json`
- Artifacts: `artifacts/<run_id>/`

## Optional: run with curl

```bash
# Plan only
curl -X POST http://localhost:8000/api/plan \
	-H "Content-Type: application/json" \
	-d '{"url":"https://play.ezygamers.com/"}'

# Run top 10
curl -X POST http://localhost:8000/api/run \
	-H "Content-Type: application/json" \
	-d '{"url":"https://play.ezygamers.com/"}'

# Poll status
curl http://localhost:8000/api/status/<run_id>
```