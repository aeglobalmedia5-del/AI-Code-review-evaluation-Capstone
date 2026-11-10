import asyncio, json
from pathlib import Path
from .audit import AuditLogger
from .tools import FileReaderTool, LinterTool, set_tool_calls, get_tool_calls, reset_tool_calls
from .agents import ReaderAgent, ReviewerAgent, CoordinatorAgent, SingleAgentBaseline
from .dataset import load_dataset, validate_dataset
from .metrics import calculate_metrics
from .integrations import run_ragas, run_deepeval

async def run_system(samples, mode="multi", prompt_version="v2", report_prefix="multi", include_judges=True):
    Path("reports").mkdir(exist_ok=True)
    audit_path = Path(f"reports/{report_prefix}_audit.jsonl")
    if audit_path.exists(): audit_path.unlink()
    audit = AuditLogger(str(audit_path))
    reader_tool, linter_tool = FileReaderTool(audit=audit), LinterTool(audit=audit)
    if mode == "multi":
        agent = CoordinatorAgent(ReaderAgent(reader_tool), ReviewerAgent(linter_tool, prompt_version))
    else:
        agent = SingleAgentBaseline(reader_tool, linter_tool)
    semaphore = asyncio.Semaphore(8)
    async def one(sample):
        async with semaphore:
            path = Path("data/code_samples"); path.mkdir(parents=True, exist_ok=True)
            (path / sample.file).write_text(sample.code, encoding="utf-8")
            token = set_tool_calls(0)
            try:
                result = await agent.run(sample.file, sample.role)
                actual_calls = get_tool_calls()
                reset_tool_calls(token)
                review = result["review"]
                expected_calls = 2
                actual_calls = actual_calls
                handoff_ok = (mode != "multi" or result.get("handoff", {}).get("reader_to_reviewer") is True)
                return {"sample_id": sample.sample_id, "file": sample.file, "review": review,
                        "expected": [x.model_dump() for x in sample.expected_findings], "code": sample.code,
                        "tokens": result.get("tokens_estimate", 0), "latency_ms": result.get("latency_ms", 0),
                        "steps": result.get("steps", 0), "tool_calls_ok": actual_calls == expected_calls,
                        "expected_tool_calls": expected_calls, "actual_tool_calls": actual_calls,
                        "handoff_correct": handoff_ok,
                        "completed": isinstance(review, dict) and isinstance(review.get("findings"), list) and handoff_ok}
            except Exception as exc:
                actual_calls = get_tool_calls()
                reset_tool_calls(token)
                return {"sample_id": sample.sample_id, "file": sample.file, "review": {},
                        "expected": [x.model_dump() for x in sample.expected_findings], "code": sample.code,
                        "tokens": 0, "latency_ms": 0, "steps": 0, "tool_calls_ok": False,
                        "expected_tool_calls": 2, "actual_tool_calls": actual_calls, "handoff_correct": False,
                        "completed": False, "error": f"{type(exc).__name__}: {exc}"}
    rows = await asyncio.gather(*(one(s) for s in samples))
    metrics = calculate_metrics(rows)
    metrics["handoff_correctness_rate"] = sum(r["handoff_correct"] for r in rows)/len(rows) if rows else 0.0
    metrics["dataset_validation"] = validate_dataset(samples)
    metrics["mode"] = mode
    metrics["ragas"] = run_ragas(rows) if include_judges else {"status": "NOT_RUN_FOR_PROMPT_AB"}
    metrics["deepeval"] = run_deepeval(rows) if include_judges else {"status": "NOT_RUN_FOR_PROMPT_AB", "task_completion": None}
    # Keep a separate offline completion signal; never label it as DeepEval.
    metrics["task_completion_deepeval"] = metrics["deepeval"].get("task_completion")
    metrics["audit_log"] = {"path": str(audit_path), "exists": audit_path.exists(),
                             "entries": sum(1 for _ in audit_path.open(encoding="utf-8")) if audit_path.exists() else 0}
    Path(f"reports/{report_prefix}_rows.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    Path(f"reports/{report_prefix}_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return metrics

async def run_ab(samples):
    v1 = await run_system(samples, "multi", "v1", "prompt_v1", include_judges=False)
    v2 = await run_system(samples, "multi", "v2", "prompt_v2", include_judges=False)
    winner = "v2" if (v2["f1"], -v2["hallucinated_comments"]) >= (v1["f1"], -v1["hallucinated_comments"]) else "v1"
    result = {"v1": v1, "v2": v2, "winner": winner,
              "justification": "Selected by higher finding F1; hallucinations are used as tie-breaker."}
    Path("reports/prompt_ab.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result
