import re
from dataclasses import dataclass

SECRET_PATTERNS = [
    re.compile(r'(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*["\']?([A-Za-z0-9_\-]{8,})'),
    re.compile(r'\bAKIA[0-9A-Z]{16}\b'),
]
EMAIL_RE = re.compile(r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b', re.I)

INJECTION_MARKERS = [
    "ignore previous instructions", "reveal the secret", "print the api key",
    "you are now admin", "disregard all rules", "send credentials", "system:", "reveal secrets",
]

def mask_sensitive(text: str) -> str:
    text = EMAIL_RE.sub("[REDACTED_EMAIL]", text)
    for pattern in SECRET_PATTERNS:
        text = pattern.sub(lambda m: (m.group(1) + "=[REDACTED_SECRET]") if m.lastindex and m.lastindex >= 1 else "[REDACTED_SECRET]", text)
    return text

def contains_secret_or_pii(text: str) -> bool:
    if EMAIL_RE.search(text):
        return True
    return any(p.search(text) for p in SECRET_PATTERNS)

def is_injection(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in INJECTION_MARKERS)

@dataclass
class SecurityResult:
    name: str
    passed: bool
    severity: str
    evidence: str
