"""Explicit opt-in: sends three synthetic requests, never real mail."""
from pathlib import Path
import os
import sys
import tomllib
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from gemini_service import GeminiService, ServiceError


def main():
    secret_file = Path(__file__).resolve().parents[1] / ".streamlit" / "secrets.toml"
    secrets = tomllib.loads(secret_file.read_text(encoding="utf-8")) if secret_file.exists() else {}
    key = os.getenv("GEMINI_API_KEY") or secrets.get("GEMINI_API_KEY")
    if not key or key == "YOUR_API_KEY":
        print("SKIPPED: no Gemini key configured; live integration remains unverified.")
        return
    api = GeminiService(key, os.getenv("GEMINI_MODEL") or secrets.get("GEMINI_MODEL"))
    email = "Hello Sam, could you send the project report by tomorrow? Regards, Alex"
    try:
        result = api.analyze_and_draft(email, signature="Sam")
        assert result.deadline_text and "tomorrow" in result.deadline_text.lower()
        assert result.reply and result.summary
        assert api.regenerate_reply(email, instructions="Ask for more time", signature="Sam").reply
        assert api.proofread("Thnak you for your mesage.").corrected_text
        print("PASS: live analysis/drafting, regeneration and proofreading. Manually evaluate quality before release.")
    except (ServiceError, AssertionError):
        print("FAIL: live smoke test. Check configuration/quota and review the operation in the app.")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
