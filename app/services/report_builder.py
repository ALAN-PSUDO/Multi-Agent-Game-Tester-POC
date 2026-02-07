import json
from pathlib import Path
from typing import Dict

from app.services.utils import ensure_dir, write_text


def build_report(run_id: str, report: Dict, reports_root: Path) -> Dict[str, str]:
    report_dir = ensure_dir(reports_root / run_id)
    json_path = report_dir / "report.json"
    html_path = report_dir / "report.html"

    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    write_text(html_path, _render_html(report))
    return {"json": str(json_path), "html": str(html_path)}


def _render_html(report: Dict) -> str:
    tests = report.get("top_tests", [])
    results = {item.get("id"): item for item in report.get("results", [])}
    snapshot = report.get("snapshot", {})
    snapshot_img = snapshot.get("screenshot", "")
    snapshot_html = snapshot.get("html", "")
    rows = []
    for test in tests:
        result = results.get(test.get("id"), {})
        status = result.get("status", "UNKNOWN")
        before = result.get("artifacts", {}).get("before", "")
        after = result.get("artifacts", {}).get("after", "")
        rows.append(
            f"<tr><td>{test.get('id')}</td><td>{test.get('title')}</td><td>{status}</td>"
            f"<td><a href='{before}' target='_blank'>before</a></td>"
            f"<td><a href='{after}' target='_blank'>after</a></td></tr>"
        )

    rows_html = "\n".join(rows) or "<tr><td colspan='5'>No tests executed</td></tr>"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Run Report {report.get('run_id')}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; background: #f7f7f7; }}
    h1 {{ margin-bottom: 0.5rem; }}
    table {{ width: 100%; border-collapse: collapse; background: #fff; }}
    th, td {{ padding: 0.75rem; border-bottom: 1px solid #e0e0e0; text-align: left; }}
    th {{ background: #fafafa; }}
    .meta {{ margin-bottom: 1.5rem; }}
  </style>
</head>
<body>
  <h1>Multi-Agent Game Tester Report</h1>
  <div class="meta">
    <div><strong>Run ID:</strong> {report.get('run_id')}</div>
    <div><strong>URL:</strong> {report.get('url')}</div>
    <div><strong>Pass Rate:</strong> {report.get('summary', {}).get('pass_rate', 'n/a')}</div>
  </div>
  <h2>Snapshot</h2>
  <div class="meta">
    <a href="{snapshot_img}" target="_blank">Screenshot</a> |
    <a href="{snapshot_html}" target="_blank">HTML</a>
  </div>
  <h2>Top Tests</h2>
  <table>
    <thead>
      <tr><th>ID</th><th>Title</th><th>Status</th><th>Before</th><th>After</th></tr>
    </thead>
    <tbody>
      {rows_html}
    </tbody>
  </table>
</body>
</html>
"""
