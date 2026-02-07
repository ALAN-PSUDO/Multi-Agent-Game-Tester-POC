var statusEl = document.getElementById("status");
var planOutput = document.getElementById("planOutput");
var reportOutput = document.getElementById("reportOutput");
var urlInput = document.getElementById("url");

function setStatus(text) {
  statusEl.textContent = text;
}

function formatJson(data) {
  return JSON.stringify(data, null, 2);
}

function pollStatus(runId) {
  var timer = setInterval(function () {
    fetch("/api/status/" + runId)
      .then(function (response) {
        return response.json();
      })
      .then(function (data) {
        setStatus(data.status + " (" + data.stage + ")");
        if (data.status === "completed") {
          clearInterval(timer);
          reportOutput.innerHTML =
            "Report ready: <a href=\"/reports/" +
            runId +
            "/report.html\" target=\"_blank\">Open report</a>";
        }
        if (data.status === "failed") {
          clearInterval(timer);
          reportOutput.textContent = data.error || "Run failed";
        }
      });
  }, 2000);
}

function plan() {
  setStatus("Planning...");
  fetch("/api/plan", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url: urlInput.value }),
  })
    .then(function (response) {
      return response.json();
    })
    .then(function (data) {
      planOutput.textContent = formatJson({
        test_plan: data.test_plan,
        top_tests: data.top_tests,
      });
      reportOutput.textContent = "Plan ready. You can run the top 10 now.";
      setStatus("Plan complete");
    });
}

function run() {
  setStatus("Starting run...");
  fetch("/api/run", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url: urlInput.value }),
  })
    .then(function (response) {
      return response.json();
    })
    .then(function (data) {
      planOutput.textContent = formatJson({ run_id: data.run_id });
      reportOutput.textContent = "Executing...";
      pollStatus(data.run_id);
    });
}

document.getElementById("planBtn").addEventListener("click", plan);
document.getElementById("runBtn").addEventListener("click", run);
