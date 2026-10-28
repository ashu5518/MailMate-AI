import json
from types import SimpleNamespace
from unittest.mock import Mock

import httpx
import pytest
from google.genai import errors, types
from gemini_service import GeminiService, ServiceError, SYSTEM, provider_schema
from models import Analysis, Proofreading

ANALYSIS = dict(summary="Report requested.", intent="Document request", urgency="Medium",
                urgency_explanation="The sender asks for tomorrow.", action_items=["Send the report."],
                deadline_text="tomorrow", deadline_evidence="by tomorrow", reply="Thank you for the report request.")


@pytest.fixture(autouse=True)
def isolate_model_configuration(monkeypatch):
    monkeypatch.delenv("GEMINI_MODEL", raising=False)


def service(result=None):
    client = Mock()
    client.models.generate_content.return_value = SimpleNamespace(
        text=json.dumps(result or ANALYSIS), prompt_feedback=None,
        candidates=[SimpleNamespace(finish_reason=types.FinishReason.STOP)])
    return GeminiService("test-key", client=client), client


def test_analysis_and_request_contract():
    api, client = service()
    result = api.analyze_and_draft("Send the report by tomorrow", "Ask for more time", "Sam", "Polite", "Medium")
    assert result.deadline_text == "tomorrow"
    call = client.models.generate_content.call_args.kwargs
    assert call["model"] == "gemini-2.5-flash"
    assert call["config"].response_schema == provider_schema(Analysis)
    assert "additionalProperties" not in call["config"].response_schema
    payload = json.loads(call["contents"])
    assert payload["reply_instructions"] == "Ask for more time"
    assert payload["signature"] == "Sam"
    assert payload["tone"] == "Polite" and payload["length"] == "Medium"
    assert "untrusted data" in SYSTEM and "Never invent" in SYSTEM


def test_missing_deadline():
    api, _ = service({**ANALYSIS, "deadline_text": None, "deadline_evidence": None})
    assert api.analyze_and_draft("Thank you!").deadline_text is None


@pytest.mark.parametrize("changes", [dict(urgency="Critical"), dict(deadline_evidence=None), dict(deadline_evidence="next week"), dict(reply="")])
def test_invalid_analysis(changes):
    api, _ = service({**ANALYSIS, **changes})
    with pytest.raises(ServiceError):
        api.analyze_and_draft("Send by tomorrow")


def test_correct_proofreading_preserves_whitespace():
    text = "Hello Sam,\n\nThank you.\n"
    api, client = service(dict(corrected_text=text, change_explanations=[]))
    assert api.proofread(text).corrected_text == text
    assert client.models.generate_content.call_args.kwargs["config"].response_schema == provider_schema(Proofreading)


@pytest.mark.parametrize("text", ["", "  ", "x" * 20001])
def test_invalid_input_never_calls_api(text):
    api, client = service()
    with pytest.raises(ServiceError):
        api.analyze_and_draft(text)
    with pytest.raises(ServiceError):
        api.proofread(text)
    client.models.generate_content.assert_not_called()


def test_instruction_limit():
    api, client = service()
    with pytest.raises(ServiceError, match="2,000"):
        api.regenerate_reply("Hello", instructions="x" * 2001)
    client.models.generate_content.assert_not_called()


@pytest.mark.parametrize("code, expected", [(401, "access"), (403, "access"), (429, "quota"), (404, "model"), (503, "temporarily")])
def test_api_errors_are_safe(code, expected):
    api, client = service()
    client.models.generate_content.side_effect = errors.APIError(code, {"error": {"message": "secret-email-and-key", "code": code}})
    with pytest.raises(ServiceError, match=expected) as exc:
        api.proofread("Hello")
    assert "secret-email-and-key" not in str(exc.value)


@pytest.mark.parametrize("error, expected", [(httpx.ReadTimeout("private"), "timed out"), (httpx.ConnectError("private"), "connect")])
def test_network_errors(error, expected):
    api, client = service()
    client.models.generate_content.side_effect = error
    with pytest.raises(ServiceError, match=expected):
        api.proofread("Hello")


def test_blocked_empty_and_malformed_responses():
    api, client = service()
    response = client.models.generate_content.return_value
    response.prompt_feedback = SimpleNamespace(block_reason="SAFETY")
    with pytest.raises(ServiceError, match="blocked"):
        api.proofread("Hello")
    response.prompt_feedback = None
    response.text = ""
    with pytest.raises(ServiceError, match="no usable"):
        api.proofread("Hello")
    response.text = "not JSON"
    with pytest.raises(ServiceError, match="invalid response"):
        api.proofread("Hello")


def test_owned_client_timeout_no_retries_and_close(monkeypatch):
    api, client = service(dict(reply="Hello"))
    factory = Mock(return_value=client)
    monkeypatch.setattr("gemini_service.genai.Client", factory)
    GeminiService("test-key").regenerate_reply("Hello")
    options = factory.call_args.kwargs["http_options"]
    assert options.timeout == 60000 and options.retry_options.attempts == 1
    client.close.assert_called_once()
