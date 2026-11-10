"""Governance checklist and reproducibility metadata for capstone artifacts."""
import hashlib, json, platform, sys
from pathlib import Path
from datetime import datetime, timezone
from .agents import REVIEWER_PROMPT_V1, REVIEWER_PROMPT_V2
from .config import SETTINGS


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""): h.update(chunk)
    return h.hexdigest()


def write_governance_artifacts():
    Path("reports").mkdir(exist_ok=True)
    dataset = Path("data/golden_dataset_v1.json")
    requirements = Path("requirements.txt")
    metadata = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": sys.version,
        "platform": platform.platform(),
        "model_name": SETTINGS.model_name,
        "prompt_versions": {"v1_sha256": hashlib.sha256(REVIEWER_PROMPT_V1.encode()).hexdigest(),
                            "v2_sha256": hashlib.sha256(REVIEWER_PROMPT_V2.encode()).hexdigest()},
        "golden_dataset": {"path": str(dataset), "sha256": sha256(dataset)} if dataset.exists() else None,
        "requirements": {"path": str(requirements), "sha256": sha256(requirements)} if requirements.exists() else None,
    }
    Path("reports/reproducibility.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    # Checklist records the control and evidence needed; it does not falsely claim
    # legal/compliance certification from this local demo.
    checklist = {
        "GDPR": [
            {"control": "Data minimization", "status": "IMPLEMENTED_DEMO", "evidence": "Synthetic fixtures; outputs and logs are scanned/masked."},
            {"control": "Purpose limitation and lawful basis", "status": "REQUIRES_ORGANIZATION_REVIEW", "evidence": "Must be documented by the project owner."},
            {"control": "Data subject rights and retention", "status": "REQUIRES_ORGANIZATION_REVIEW", "evidence": "Retention/deletion policy is not supplied."}],
        "SOC2": [
            {"control": "Access control / least privilege", "status": "IMPLEMENTED_DEMO", "evidence": "Reviewer/admin RBAC tests."},
            {"control": "Audit logging", "status": "IMPLEMENTED_DEMO", "evidence": "JSONL tool audit logs."},
            {"control": "Change management", "status": "PARTIAL", "evidence": "Prompt and artifact hashes; formal approvals not implemented."}],
        "data_residency": [{"control": "Processing and storage region", "status": "REQUIRES_CONFIGURATION", "evidence": "Confirm provider region, deployment region and log storage region before release."}],
        "disclaimer": "Checklist evidence is a capstone implementation aid, not a GDPR/SOC 2 certification or legal opinion."
    }
    Path("reports/compliance_checklist.json").write_text(json.dumps(checklist, indent=2), encoding="utf-8")
    return metadata, checklist
