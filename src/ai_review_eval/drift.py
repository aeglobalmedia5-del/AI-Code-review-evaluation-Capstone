import json
from pathlib import Path
from statistics import mean

def detect_drift():
    # Synthetic traffic replay: quality is stable for 10 requests, then drops.
    traffic = [{"request": i+1, "quality": (0.94 if i < 10 else 0.68),
                "prompt_version": "v2", "model_version": "local-deterministic-reviewer"}
               for i in range(20)]
    baseline = mean(x["quality"] for x in traffic[:10])
    threshold = baseline - 0.10
    drift_rows = [x for x in traffic if x["quality"] < threshold]
    start = drift_rows[0]["request"] if drift_rows else None
    result = {
        "baseline_quality": baseline, "drift_threshold": threshold,
        "drift_started_at_request": start,
        "drift_type": "data drift (synthetic traffic distribution shift)",
        "explanation": "The quality drop appears in the incoming traffic stream while prompt and model versions remain unchanged. It is therefore classified as a traffic/data distribution drift rather than a code or configuration regression.",
        "incident_note": {"impact": "Review quality fell from the baseline to 0.68 after request 10.",
                          "root_cause": "Synthetic replay introduces a changed input distribution.",
                          "corrective_action": "Quarantine affected traffic, inspect the changed sample distribution, add representative golden cases, and rerun gates."}
    }
    Path("reports/drift_incident.json").write_text(json.dumps(result, indent=2))
    return result
