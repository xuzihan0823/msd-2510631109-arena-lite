from dataclasses import dataclass
from typing import Literal


ErrorType = Literal["none", "timeout", "empty_response", "provider_error"]


@dataclass(frozen=True)
class ModelAnswer:
    contestant_id: str
    text: str
    latency_ms: int
    error_type: ErrorType


class MockModelAdapter:
    """Deterministic adapter with injectable failures and no external dependency."""

    def __init__(self, failures: dict[str, ErrorType] | None = None) -> None:
        self.failures = failures or {}

    def ask(self, contestant_id: str, prompt: str, timeout_seconds: float) -> ModelAnswer:
        error_type = self.failures.get(contestant_id, "none")
        if error_type == "timeout":
            return ModelAnswer(contestant_id, "", 1000, "timeout")
        if error_type == "empty_response":
            return ModelAnswer(contestant_id, "", 1, "empty_response")
        if error_type == "provider_error":
            return ModelAnswer(contestant_id, "", 1, "provider_error")
        return ModelAnswer(
            contestant_id=contestant_id,
            text=f"Mock answer for: {prompt.strip()}",
            latency_ms=1,
            error_type="none",
        )
