from pydantic import BaseModel, Field
from typing import Literal

Severity = Literal["low", "medium", "high", "critical"]

class Finding(BaseModel):
    file: str
    line: int = Field(ge=1)
    severity: Severity
    comment: str

class ReviewOutput(BaseModel):
    findings: list[Finding]
    summary: str = ""

class Sample(BaseModel):
    sample_id: str
    file: str
    code: str
    role: Literal["reviewer", "admin"] = "reviewer"
    expected_findings: list[Finding] = []
    tags: list[str] = []
