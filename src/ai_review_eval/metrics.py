"""Deterministic, offline-safe metrics for the AI code-review capstone."""
import json, math, re
from .security import contains_secret_or_pii


def json_valid_rate(outputs):
    if not outputs: return 0.0
    valid = 0
    for item in outputs:
        try:
            if isinstance(item, dict) and isinstance(item.get("findings"), list) and all(
                isinstance(x, dict) and {"file", "line", "severity", "comment"} <= x.keys()
                for x in item["findings"]
            ): valid += 1
        except Exception: pass
    return valid / len(outputs)


def tool_correctness_rate(expected_calls, actual_calls):
    return min(actual_calls / expected_calls, 1.0) if expected_calls else 1.0


def hallucinated_findings(predicted, source_code, filename=None):
    """Flag invalid line references and findings attached to another file."""
    lines = source_code.splitlines()
    bad = []
    for finding in predicted:
        line = finding.get("line")
        if not isinstance(line, int) or line < 1 or line > len(lines):
            bad.append(finding); continue
        if filename and finding.get("file") not in (None, filename): bad.append(finding)
    return bad


def precision_recall_f1(predicted, expected):
    def key(x):
        return (x.get("file"), x.get("line"), x.get("severity"), re.sub(r"\W+", " ", x.get("comment", "").lower()).strip())
    p, e = {key(x) for x in predicted}, {key(x) for x in expected}
    tp = len(p & e)
    precision = tp / len(p) if p else (1.0 if not e else 0.0)
    recall = tp / len(e) if e else (1.0 if not p else 0.0)
    f1 = 2*precision*recall/(precision+recall) if precision+recall else 0.0
    return precision, recall, f1


def rouge_l_f1(predicted, expected):
    a = " ".join(x.get("comment", "") for x in predicted).split()
    b = " ".join(x.get("comment", "") for x in expected).split()
    if not a and not b: return 1.0
    if not a or not b: return 0.0
    dp = [0]*(len(b)+1)
    for x in a:
        prev = 0
        for j, y in enumerate(b, 1):
            old = dp[j]; dp[j] = prev+1 if x == y else max(dp[j], dp[j-1]); prev = old
    lcs = dp[-1]; p, r = lcs/len(a), lcs/len(b)
    return 2*p*r/(p+r) if p+r else 0.0


def percentile95(values):
    if not values: return 0.0
    vals = sorted(values)
    return vals[max(0, math.ceil(.95*len(vals))-1)]


def calculate_metrics(rows):
    outputs, all_pred, all_expected = [r["review"] for r in rows], [], []
    hallucinations = leaks = 0
    for r in rows:
        pred = r["review"].get("findings", []) if isinstance(r.get("review"), dict) else []
        all_pred.extend(pred); all_expected.extend(r["expected"])
        hallucinations += len(hallucinated_findings(pred, r["code"], r.get("file")))
        leaks += int(contains_secret_or_pii(json.dumps(r.get("review", {}))))
    p, recall, f1 = precision_recall_f1(all_pred, all_expected)
    total_expected = sum(r.get("expected_tool_calls", 2) for r in rows)
    total_actual = sum(r.get("actual_tool_calls", 0) for r in rows)
    completed = sum(bool(r.get("completed")) for r in rows)
    return {
        "valid_json_rate": json_valid_rate(outputs), "precision": p, "recall": recall, "f1": f1,
        "rouge_l_f1": rouge_l_f1(all_pred, all_expected),
        "hallucinated_comments": hallucinations, "secret_or_pii_leaks": leaks,
        "correct_tool_call_rate": tool_correctness_rate(total_expected, total_actual),
        "tool_calls_expected": total_expected, "tool_calls_actual": total_actual,
        "task_completion_offline_rate": completed / len(rows) if rows else 0.0,
        "mean_tokens": sum(r.get("tokens", 0) for r in rows)/len(rows) if rows else 0.0,
        "mean_steps": sum(r.get("steps", 0) for r in rows)/len(rows) if rows else 0.0,
        "p95_latency_ms": percentile95([r.get("latency_ms", 0) for r in rows]),
        "sample_count": len(rows),
    }
