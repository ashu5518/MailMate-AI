"""Real-browser checks using fake AI. Run directly, not through pytest."""
from pathlib import Path
import subprocess
import sys
import time
import urllib.request

from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"


def main():
    ARTIFACTS.mkdir(exist_ok=True)
    with (ARTIFACTS / "browser-server.log").open("w", encoding="utf-8") as log:
        server = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "tests/browser_app.py",
                                   "--server.port", "8502"], cwd=ROOT, stdout=log, stderr=log)
        try:
            for _ in range(60):
                if server.poll() is not None:
                    raise RuntimeError("Browser fixture server failed; inspect artifacts/browser-server.log")
                try:
                    with urllib.request.urlopen("http://127.0.0.1:8502/_stcore/health", timeout=1) as response:
                        if response.status == 200:
                            break
                except OSError:
                    time.sleep(0.25)
            else:
                raise RuntimeError("Browser fixture server did not start")
            with sync_playwright() as p:
                browser = p.chromium.launch(channel="chrome", headless=True)
                context = browser.new_context(viewport={"width": 1440, "height": 1100},
                    permissions=["clipboard-read", "clipboard-write"])
                page = context.new_page()
                page.goto("http://127.0.0.1:8502")
                expect(page.get_by_role("heading", name="MailMate AI", exact=True)).to_be_visible()
                email = page.get_by_role("textbox", name="Email", exact=True)
                email.fill("Hello Sam, please send the report by tomorrow.")
                page.get_by_role("button", name="Analyze & Draft", exact=True).click()
                reply = page.get_by_role("textbox", name="Editable reply", exact=True)
                expect(reply).to_have_value("Hello,\n\nThank you for your message.\n\nSam")
                value = "My edited draft. </script><script>window.BAD=true</script>"
                reply.fill(value)
                reply.press("Tab")
                copy = page.frame_locator('iframe[title="Copy the current reply"]')
                copy.get_by_role("button", name="Copy reply").click()
                expect(copy.locator("#status")).to_have_text(" Copied")
                assert page.evaluate("navigator.clipboard.readText()") == value
                assert not page.evaluate("Boolean(window.BAD)")
                with page.expect_download() as info:
                    page.get_by_role("button", name="Download reply").click()
                download = info.value
                assert Path(download.path()).read_text(encoding="utf-8") == value
                email_box, reply_box = email.bounding_box(), reply.bounding_box()
                assert reply_box["x"] > email_box["x"] + email_box["width"]
                page.get_by_role("heading", name="MailMate AI", exact=True).scroll_into_view_if_needed()
                page.screenshot(path=str(ARTIFACTS / "desktop.png"), full_page=True)
                page.get_by_role("tab", name="Proofread", exact=True).click()
                page.get_by_role("textbox", name="Text to proofread", exact=True).fill("Thnak you.")
                page.get_by_role("button", name="Proofread text", exact=True).click()
                expect(page.get_by_role("button", name="Use corrected version")).to_be_visible()
                page.get_by_role("button", name="Use corrected version").click()
                page.get_by_role("tab", name="Email assistant", exact=True).click()
                expect(reply).to_have_value("Thank you.")
                # Keyboard focus must reach the editor.
                email.focus()
                email.press("Tab")
                assert page.evaluate("document.activeElement.getAttribute('aria-label')") == "Reply instructions (optional)"
                page.set_viewport_size({"width": 390, "height": 844})
                email_box, reply_box = email.bounding_box(), reply.bounding_box()
                assert reply_box["y"] > email_box["y"] + email_box["height"]
                assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
                page.get_by_role("heading", name="MailMate AI", exact=True).scroll_into_view_if_needed()
                page.screenshot(path=str(ARTIFACTS / "mobile.png"), full_page=True)
                print("PASS: desktop/mobile layouts, keyboard focus, clipboard, safe copy, download, proofreading")
                browser.close()
        finally:
            server.terminate()
            try:
                server.wait(timeout=10)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait()


if __name__ == "__main__":
    main()
