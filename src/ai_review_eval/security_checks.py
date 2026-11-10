import asyncio, json
from pathlib import Path
from .audit import AuditLogger
from .tools import FileReaderTool, RESTRICTED_FILES

async def run_rbac_checks():
    base = Path("data/code_samples")
    base.mkdir(parents=True, exist_ok=True)
    restricted = "production.env"
    (base / restricted).write_text("FAKE_TEST_SECRET=do-not-use-real-secret\n", encoding="utf-8")
    reader = FileReaderTool(base_dir=str(base), audit=AuditLogger("reports/rbac_audit.jsonl"))
    reviewer_denied = False
    admin_allowed = False
    try:
        await reader.read_file(restricted, "reviewer")
    except PermissionError:
        reviewer_denied = True
    try:
        content = await reader.read_file(restricted, "admin")
        admin_allowed = "do-not-use-real-secret" not in content
    except Exception:
        admin_allowed = False
    result = {
        "reviewer_denied_restricted_file": reviewer_denied,
        "admin_allowed_restricted_file": admin_allowed,
        "rbac_violations": int(not reviewer_denied) + int(not admin_allowed),
        "passed": reviewer_denied and admin_allowed
    }
    Path("reports/rbac_results.json").write_text(json.dumps(result, indent=2))
    return result
