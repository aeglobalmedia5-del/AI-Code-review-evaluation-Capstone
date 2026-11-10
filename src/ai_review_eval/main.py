import asyncio, json
from pathlib import Path
from .dataset import load_dataset
from .evaluation import run_system, run_ab
from .quality_gate import evaluate_gates
from .redteam import run_redteam
from .deployment import simulate_canary
from .drift import detect_drift
from .security_checks import run_rbac_checks
from .governance import write_governance_artifacts

async def main():
    Path("reports").mkdir(exist_ok=True)
    samples = load_dataset()
    reproducibility, compliance = write_governance_artifacts()
    baseline = await run_system(samples, "single", report_prefix="baseline")
    multi = await run_system(samples, "multi", report_prefix="multi")
    ab = await run_ab(samples)
    redteam = await run_redteam()
    rbac = await run_rbac_checks()
    security = {"rbac_violations": rbac["rbac_violations"],
                "successful_injections": sum(not x["passed"] for x in redteam),
                "redteam_total": len(redteam), "redteam_passed": sum(x["passed"] for x in redteam)}
    canary = simulate_canary()
    drift = detect_drift()
    gate = evaluate_gates(multi, baseline, security)
    summary = {"baseline": baseline, "multi_agent": multi, "prompt_ab_winner": ab["winner"],
               "redteam_passed": sum(x["passed"] for x in redteam),
               "redteam_total": len(redteam), "rbac": rbac, "canary": canary,
               "drift": drift, "release_gate": gate,
               "reproducibility": reproducibility, "compliance_checklist": compliance}
    Path("reports/final_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    print(f"\nRELEASE RECOMMENDATION: {gate['status']}")

if __name__ == "__main__":
    asyncio.run(main())
