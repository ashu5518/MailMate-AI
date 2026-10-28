from unittest.mock import patch
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest
from gemini_service import ServiceError
from models import Analysis, Proofreading, Reply
APP_PATH = Path(__file__).resolve().parents[1] / "app.py"

ANALYSIS = Analysis(summary="Report requested", intent="Document request", urgency="Medium",
                    urgency_explanation="Requested tomorrow", action_items=["Send report"],
                    deadline_text="tomorrow", deadline_evidence="by tomorrow", reply="Thank you for your message.")


def button(app, label):
    return next(b for b in app.button if b.label == label)


@pytest.fixture
def app(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    with patch("gemini_service.GeminiService.analyze_and_draft", return_value=ANALYSIS) as analyze, \
         patch("gemini_service.GeminiService.regenerate_reply", return_value=Reply(reply="A new reply.")) as reply, \
         patch("gemini_service.GeminiService.proofread", return_value=Proofreading(corrected_text="Thank you for your message.", change_explanations=["Fixed spelling."])) as proof:
        a = AppTest.from_file(APP_PATH).run()
        assert not a.exception
        yield a, analyze, reply, proof


def draft(a):
    a.text_area(key="email").input("Please send the report by tomorrow.")
    button(a, "Analyze & Draft").click().run()
    assert not a.exception


def test_draft_persists_and_only_explicit_calls(app):
    a, analyze, reply, _ = app
    draft(a)
    analyze.assert_called_once()
    a.text_area(key="reply").input("My edited reply.").run()
    a.selectbox(key="tone").select("Friendly").run()
    assert a.text_area(key="reply").value == "My edited reply."
    analyze.assert_called_once()
    reply.assert_not_called()
    button(a, "Regenerate Reply").click().run()
    assert a.text_area(key="reply").value == "A new reply."
    assert reply.call_args.kwargs["tone"] == "Friendly"
    analyze.assert_called_once()


@pytest.mark.parametrize("key, value, action, expected", [
    ("email", "", "Analyze & Draft", "first"),
    ("email", "x" * 20001, "Analyze & Draft", "20,000"),
    ("instructions", "x" * 2001, "Analyze & Draft", "2,000"),
    ("proof_text", "x" * 20001, "Proofread text", "20,000"),
], ids=["blank-email", "long-email", "long-instructions", "long-proof"])
def test_input_validation(app, key, value, action, expected):
    a, analyze, _, proof = app
    a.text_area(key="email").input("Hello")
    a.text_area(key=key).input(value)
    button(a, action).click().run()
    assert expected in a.error[0].value
    analyze.assert_not_called()
    proof.assert_not_called()
    assert not a.exception


def test_stale_results_and_failure_preserve_draft(app):
    a, analyze, _, _ = app
    draft(a)
    a.text_area(key="reply").input("Keep my edits.").run()
    a.text_area(key="email").input("A different email.").run()
    assert any("earlier email" in w.value for w in a.warning)
    analyze.side_effect = ServiceError("Gemini quota is exhausted. Retry later.")
    button(a, "Analyze & Draft").click().run()
    assert "quota" in a.error[0].value
    assert a.text_area(key="reply").value == "Keep my edits."
    assert a.session_state["analysis"] == ANALYSIS
    assert not a.session_state["busy"]


def test_proofreading_requires_acceptance_and_clear(app):
    a, _, _, proof = app
    draft(a)
    a.text_area(key="reply").input("Thnak you for your message.").run()
    button(a, "Use current reply").click().run()
    button(a, "Proofread text").click().run()
    proof.assert_called_once_with("Thnak you for your message.")
    assert a.text_area(key="reply").value.startswith("Thnak")
    button(a, "Use corrected version").click().run()
    assert a.text_area(key="reply").value == "Thank you for your message."
    a.selectbox(key="tone").select("Polite").run()
    a.selectbox(key="length").select("Detailed").run()
    a.text_input(key="signature").input("Sam").run()
    button(a, "Clear").click().run()
    for key in ("email", "instructions", "reply", "proof_text"):
        assert a.text_area(key=key).value == ""
    assert a.session_state["analysis"] is None
    assert a.session_state["proof_result"] is None
    assert a.selectbox(key="tone").value == "Polite"
    assert a.selectbox(key="length").value == "Detailed"
    assert a.text_input(key="signature").value == "Sam"
    assert not a.exception


def test_stale_correction_cannot_be_applied(app):
    a, _, _, _ = app
    a.text_area(key="proof_text").input("Thnak you").run()
    button(a, "Proofread text").click().run()
    a.text_area(key="proof_text").input("Different text").run()
    assert button(a, "Use corrected version").disabled
    assert any("earlier text" in w.value for w in a.warning)


def test_missing_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setattr("streamlit.secrets", {})
    a = AppTest.from_file(APP_PATH).run()
    a.text_area(key="email").input("Hello")
    button(a, "Analyze & Draft").click().run()
    assert "GEMINI_API_KEY" in a.error[0].value
    assert not a.exception
