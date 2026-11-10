import json, hashlib, os
from datetime import datetime, timezone
from pathlib import Path
from .security import mask_sensitive

class AuditLogger:
    def __init__(self, path="reports/audit.jsonl"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def log_tool(self, role, tool, target, decision, details=""):
        row = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "role": role, "tool": tool, "target": target,
            "decision": decision, "details": mask_sensitive(str(details))
        }
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def artifact_fingerprint(paths):
    return {str(p): sha256_file(p) for p in paths if os.path.exists(p)}
