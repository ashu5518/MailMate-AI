"""Browser-only fixture. Uses deterministic fake AI, never the real API."""
from pathlib import Path
import runpy
import sys
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from models import Analysis, Proofreading, Reply


def analyze(**kwargs):
    email = kwargs["email"]
    deadline = "tomorrow" if "tomorrow" in email else None
    return Analysis(summary="The sender requests a response.", intent="Request", urgency="Medium",
                    urgency_explanation="Review the sender's request.", action_items=["Review request."],
                    deadline_text=deadline, deadline_evidence=deadline,
                    reply="Hello,\n\nThank you for your message.\n\nSam")


with patch("gemini_service.GeminiService.__init__", return_value=None), \
     patch("gemini_service.GeminiService.analyze_and_draft", side_effect=analyze), \
     patch("gemini_service.GeminiService.regenerate_reply", return_value=Reply(reply="Thank you for the update.")), \
     patch("gemini_service.GeminiService.proofread", return_value=Proofreading(corrected_text="Thank you.", change_explanations=["Corrected spelling."])):
    runpy.run_path(str(Path(__file__).resolve().parents[1] / "app.py"), run_name="__main__")
