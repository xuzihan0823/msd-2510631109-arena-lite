from app.adapters.models import MockModelAdapter


def test_mock_adapter_returns_nonempty_answer_without_external_service() -> None:
    answer = MockModelAdapter().ask("2510631109-model-alpha", "Explain TDD", 1.0)

    assert answer.error_type == "none"
    assert answer.text
    assert answer.contestant_id == "2510631109-model-alpha"


def test_mock_adapter_can_model_timeout_empty_and_provider_errors() -> None:
    adapter = MockModelAdapter(
        failures={
            "timeout": "timeout",
            "empty": "empty_response",
            "provider": "provider_error",
        }
    )

    assert adapter.ask("timeout", "prompt", 1.0).error_type == "timeout"
    assert adapter.ask("empty", "prompt", 1.0).error_type == "empty_response"
    assert adapter.ask("provider", "prompt", 1.0).error_type == "provider_error"
