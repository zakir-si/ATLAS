const exampleRuns = [
  {name:"baseline",quality:0.85,accelerator_hours:10,peak_memory_gb:18,tokens_per_second:100},
  {name:"candidate-a",quality:0.85,accelerator_hours:7,peak_memory_gb:12,tokens_per_second:130},
  {name:"candidate-b",quality:0.82,accelerator_hours:4,peak_memory_gb:9,tokens_per_second:165}
];
const $ = (id) => document.getElementById(id);
$("runs").value = JSON.stringify(exampleRuns, null, 2);
$("example").addEventListener("click", () => {
  $("runs").value = JSON.stringify(exampleRuns, null, 2);
  $("status").textContent = "Illustrative data loaded. These are not benchmark results.";
  $("status").className = "status";
});
$("select").addEventListener("click", async () => {
  const status = $("status");
  const result = $("result");
  result.hidden = true;
  status.className = "status";
  status.textContent = "Selecting from supplied measurements…";
  try {
    const runs = JSON.parse($("runs").value);
    const response = await fetch("/api/v1/select", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({
        results: runs,
        min_quality: Number($("quality").value),
        max_accelerator_hours: Number($("budget").value)
      })
    });
    const body = await response.json();
    if (!response.ok) throw new Error(body.detail || "Request failed");
    $("selected-name").textContent = body.selected.name;
    $("selected-quality").textContent = body.selected.quality.toFixed(3);
    $("selected-hours").textContent = body.selected.accelerator_hours.toFixed(2);
    $("selected-ratio").textContent = body.quality_per_accelerator_hour.toFixed(4);
    $("selection-note").textContent = body.eligible_run_count + " eligible of " + body.considered_run_count + " supplied runs. This is selection from entered measurements, not a training benchmark.";
    result.hidden = false;
    status.textContent = "Selection complete.";
  } catch (error) {
    status.className = "status error";
    status.textContent = error instanceof Error ? error.message : "Unexpected error.";
  }
});
