# MailMate Gmail extension

Chrome/Edge Manifest V3 extension. It uses the existing Python Gemini service
through a loopback bridge restricted to browser-extension requests. Your Gemini API key remains in
the Python environment or ignored `.streamlit/secrets.toml`, never in the extension.

## Install locally

1. In the project terminal, run `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`.
2. Run `.\run-extension.ps1` and leave the terminal open. The bridge listens only on `127.0.0.1:8765`.
3. Open `chrome://extensions` or `edge://extensions`, enable **Developer mode**, choose **Load unpacked**, and select this `extension` directory.
4. Open the extension icon. It connects automatically; no token entry is needed. **Check connection** retries if the local bridge was offline.
5. Open or refresh Gmail. Click the floating **MailMate** button, or choose **Open in Gmail** from the extension popup.

## Use

### Fix writing directly in Gmail

Click inside your Gmail compose/reply editor and type normally. A small **Check writing**
button appears beside the editor. Click it to check the current text without opening
the large MailMate panel. Misspelled words and grammar issues are underlined in red.
Click an underlined phrase or the writing-fixes badge to view replacement options.
Choose a correction to apply it directly in the Gmail editor, or use **Apply all fixes**.
**Undo fixes** restores the text before the most recent correction if you have not
changed the draft afterward. Individual replacements preserve the surrounding editor
content and formatting; applying all replaces the draft with corrected plain text.

Checks are explicit: typing alone does not send text to Gemini or consume quota.
Editing the draft clears outdated underlines; click **Check writing** again to refresh.
If the draft changes while checking, that response is discarded. Suggestions for
insertions or complex multiline replacements may require **Apply all fixes**.

### Analyze and generate replies

- Open a conversation and choose **Read open email**. The last visible message is copied into the panel; review it or paste different text.
- Choose tone/length, optionally add instructions/signature, and click **Analyze & Draft**. The result stays in the panel for editing.
- Click inside the Gmail compose/reply editor you intend to use. **Use Gmail draft** copies its text into the preview for proofreading.
- **Fix spelling & grammar** shows a suggested correction. **Use corrected version** changes only the preview.
- **Insert into Gmail** explicitly replaces the selected compose editor. **Undo insertion** restores its previous text if no subsequent changes occurred. MailMate never clicks Send.
- If the draft changes while AI is working, insertion is blocked. Load the latest draft again. Copy/paste is available when Gmail's editor cannot be detected or edited.

Only explicit actions send text to the local bridge and Gemini. Typing does not
trigger AI calls. Email text is kept in the panel's memory, not extension storage;
refreshing Gmail clears it. No email text or credentials are stored by the extension.
The bridge requires a custom extension-ID header and rejects other website origins;
its CORS policy allows only extension origins. This is a local-use boundary, not
authentication for a public service. No Gmail OAuth or inbox
sync is used. Google's Gemini data processing and quotas still apply.

The web app remains available through `run.ps1`; the pre-extension snapshot is
`webapp-mailmate.zip`, excluding keys, environments, logs, and generated artifacts.

## Limits

English only; Gmail desktop web only. Inline underlining follows an explicit writing
check rather than automatic checks on every keystroke. Gmail's DOM can change, so selectors require ongoing testing.
Multiple compose windows require selecting the intended editor first. Insertion
is plain text and can replace existing signature/formatting; preview before use.
Loading unpacked is for local testing; this is not a Chrome Web Store release.

Remove/reload the extension or refresh Gmail after updating its files. Stop the
bridge with Ctrl+C. The old `.mailmate-extension-token` file is no longer used.

## Verification

Run `python -m pytest -q` using the project's virtual environment for mocked
service and bridge checks. For the actual unpacked extension browser check:

```powershell
.\.venv\Scripts\python.exe -m playwright install chromium
.\.venv\Scripts\python.exe tests\extension_browser_check.py
```

This loads Manifest V3 in Chromium against synthetic Gmail markup with fake AI.
It verifies automatic connection, message capture, preview, inline underlining,
individual fixes, correction acceptance, insertion, undo and changed-draft protection. Real signed-in Gmail compatibility must also
be checked manually; the synthetic fixture does not verify Google's current DOM.
