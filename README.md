**Private export: includes working credentials. Anyone receiving this archive can use the included Gemini key.**

# MailMate AI — Web app + Gmail extension

## Requirements

Python 3.11 or newer, internet access, and the included Gemini API configuration from
https://aistudio.google.com/apikey. No GPU is needed. For the extension, use
Chrome or Edge on a desktop computer. This private package includes the configured API key, old connection token, logs and Python environment.

## 1. Extract and install

Extract this ZIP completely. Open a terminal in the extracted folder containing
this README and `requirements.txt`. On Windows, run:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

On macOS/Linux:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## 2. Configure Gemini

Open `.streamlit/secrets.toml` in a text editor. The current key is already configured. Replace it only if you want to use a different account. Keep the quotation marks. The template format is:

```toml
GEMINI_API_KEY = "YOUR_API_KEY"
GEMINI_MODEL = "gemini-3.5-flash"
```

Alternatively, set `GEMINI_API_KEY` and `GEMINI_MODEL` in the launch terminal's
environment. Environment values take precedence. Never share your configured
secrets file. Free-tier access depends on your account's quotas and model access.
Submitted text is processed by Gemini; use synthetic/non-confidential text for testing.

## Run the web app

Windows:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

macOS/Linux: `.venv/bin/python -m streamlit run app.py`

Open http://localhost:8501. Paste an email, set reply preferences, and choose
**Analyze & Draft**. Edit, regenerate, copy or download the reply. The Proofread
tab previews corrections before you apply them. Stop the server with Ctrl+C.
`run.ps1` is an optional Windows shortcut if PowerShell permits local scripts.

## Run and install the Gmail extension

The extension requires the included local Python bridge. Loading the extension
alone is not enough. Start the bridge in a terminal and leave it running:

```powershell
.\.venv\Scripts\python.exe extension_server.py
```

macOS/Linux: `.venv/bin/python extension_server.py`

`run-extension.ps1` is an optional Windows shortcut. The bridge runs at
http://127.0.0.1:8765. No connection token or token entry is needed.

1. Open `chrome://extensions` or `edge://extensions`.
2. Enable **Developer mode**.
3. Click **Load unpacked** and select the `extension` subfolder, which contains `manifest.json`.
4. Open the MailMate extension icon. It connects automatically. **Check connection** retries.
5. Open or refresh Gmail after loading the extension.

### Writing fixes directly in Gmail

Click inside the compose/reply body and type. Click **Check writing** next to the
editor. Click a red underlined issue or the writing-fixes badge to see corrections.
Choose an individual fix, **Apply all fixes**, or **Undo fixes**. Typing does not
send AI requests automatically; check again after editing.

### Email analysis and replies

Click the floating **MailMate** button. Use **Read open email** or paste the
message, choose settings, and click **Analyze & Draft**. Review the preview and
click **Insert into Gmail** to replace the selected draft. MailMate never sends
email automatically. Select the intended editor first if multiple drafts are open.
Apply-all and whole-draft insertion use plain text, so review formatting/signatures.

When updating the extension, click **Reload** in the extensions page and refresh
Gmail. Stop the Python bridge with Ctrl+C. See `extension/README.md` for details.

Run the web app and extension bridge in separate terminals if you want both at once.

## Troubleshooting

- **Python not found:** install Python 3.11+ and enable PATH during installation.
- **Module missing:** run the pip command above with this package's `.venv` Python.
- **Local assistant offline:** start `extension_server.py`, then check connection again.
- **Invalid key/quota/model:** check your AI Studio project, usage, key and configured model.
- **Port already used:** stop another MailMate process using port 8501 or 8765, then restart.
- **Gmail editor not found:** open a draft, click its body, and refresh Gmail if needed.
- **Clipboard denied:** select/copy the preview manually or use the web app's download.

This is a local personal-use app, not a public hosted service or Store-published
extension. English is supported. Gmail DOM compatibility may require updates.

## Optional tests

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
```

Tests use fake AI and do not need a key. Browser checks additionally require:

```powershell
.\.venv\Scripts\python.exe -m playwright install chromium
```

Run `.\.venv\Scripts\python.exe tests\extension_browser_check.py` for synthetic Gmail extension checks.

Run `.\.venv\Scripts\python.exe tests\browser_check.py` for web checks (installed Chrome required).

For three explicit synthetic live AI requests, run `.\.venv\Scripts\python.exe tests\live_smoke.py` after configuring your key.

## Included environment

The `.venv` folder is included as requested. Python virtual environments are not portable across computers; if it does not launch, recreate it using the setup commands above. Existing credentials in `.streamlit/secrets.toml` are preserved.
