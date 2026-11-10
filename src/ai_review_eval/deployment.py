import json, random
from pathlib import Path
from .config import SETTINGS

def simulate_canary(seed=7):
    random.seed(seed)
    stages = []
    for pct in (10, 50, 100):
        n = pct
        errors = sum(random.random() < 0.02 for _ in range(n))
        latencies = [random.randint(150, 900) for _ in range(n)]
        error_rate = errors/n
        p95 = sorted(latencies)[max(0, int(.95*n)-1)]
        rollback = error_rate > SETTINGS.canary_sla_error_rate or p95 > SETTINGS.canary_sla_p95_ms
        stages.append({"traffic_percent": pct, "requests": n, "error_rate": error_rate,
                       "p95_latency_ms": p95, "sla": "BREACHED" if rollback else "PASS",
                       "action": "ROLLBACK" if rollback else "CONTINUE"})
        if rollback: break
    result = {"sla_definition": "error rate <= 5% and p95 latency <= 5000 ms",
              "stages": stages, "final_status": "ROLLED_BACK" if stages[-1]["action"] == "ROLLBACK" else "COMPLETED"}
    Path("reports/canary_log.json").write_text(json.dumps(result, indent=2))
    return result
