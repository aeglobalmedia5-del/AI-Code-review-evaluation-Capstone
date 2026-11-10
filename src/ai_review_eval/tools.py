from pathlib import Path
from contextvars import ContextVar

_TOOL_CALLS = ContextVar("tool_calls", default=0)
def set_tool_calls(value=0): return _TOOL_CALLS.set(value)
def get_tool_calls(): return _TOOL_CALLS.get()
def reset_tool_calls(token): _TOOL_CALLS.reset(token)
def _record_tool_call(): _TOOL_CALLS.set(_TOOL_CALLS.get() + 1)
from .audit import AuditLogger
from .security import mask_sensitive

RESTRICTED_FILES = {"secrets.py", "production.env", "credentials.json"}

class FileReaderTool:
    def __init__(self, base_dir="data/code_samples", audit=None):
        self.base_dir = Path(base_dir)
        self.audit = audit or AuditLogger()

    async def read_file(self, filename: str, role: str) -> str:
        _record_tool_call()
        allowed = role == "admin" or Path(filename).name not in RESTRICTED_FILES
        self.audit.log_tool(role, "file_reader", filename, "allow" if allowed else "deny")
        if not allowed:
            raise PermissionError(f"RBAC denied access to {filename}")
        path = self.base_dir / filename
        if not path.exists():
            raise FileNotFoundError(filename)
        return mask_sensitive(path.read_text(encoding="utf-8"))

class LinterTool:
    """Small deterministic linter used for a reproducible capstone demo."""
    def __init__(self, audit=None):
        self.audit = audit or AuditLogger()

    async def lint(self, filename: str, code: str, role: str = "reviewer"):
        _record_tool_call()
        self.audit.log_tool(role, "linter", filename, "allow")
        findings = []
        for number, line in enumerate(code.splitlines(), start=1):
            low = line.lower()
            if "eval(" in low:
                findings.append({"file": filename, "line": number, "severity": "high",
                                 "comment": "Avoid eval(); it can execute untrusted input."})
            if any(key in low and "=" in low for key in ("password", "api_key", "secret")):
                findings.append({"file": filename, "line": number, "severity": "critical",
                                 "comment": "Potential hard-coded credential; load secrets from a secure secret manager."})
            if "subprocess.call(" in low and "shell=true" in low:
                findings.append({"file": filename, "line": number, "severity": "high",
                                 "comment": "Avoid shell=True with untrusted input to prevent command injection."})
            if "pickle.loads(" in low:
                findings.append({"file": filename, "line": number, "severity": "high",
                                 "comment": "Unpickling untrusted data can execute arbitrary code."})
        return findings
