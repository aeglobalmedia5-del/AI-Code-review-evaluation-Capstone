from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    max_tokens_per_review: int = int(os.getenv("MAX_TOKENS_PER_REVIEW", "6000"))
    p95_latency_ms: int = int(os.getenv("P95_LATENCY_MS", "5000"))
    reviewer_json_threshold: float = 0.95
    correct_tool_call_threshold: float = 0.90
    coordinator_completion_threshold: float = 0.85
    efficiency_multiplier: float = 3.0
    canary_sla_error_rate: float = 0.05
    canary_sla_p95_ms: float = 5000
    llm_provider: str = os.getenv("LLM_PROVIDER", "mock")
    model_name: str = os.getenv("MODEL_NAME", "local-deterministic-reviewer")

SETTINGS = Settings()
