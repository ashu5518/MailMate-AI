"""Build three source-only packages with standalone setup guides; never ship secrets."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import tomllib

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'share-packages'
COMMON = ['gemini_service.py', 'models.py', '.streamlit/secrets.toml.example', '.gitignore']
WEB = ['app.py', 'run.ps1', '.streamlit/config.toml', 'tests/test_app.py',
       'tests/browser_app.py', 'tests/browser_check.py', 'tests/evaluation.md']
EXT = ['extension_server.py', 'run-extension.ps1', 'tests/test_extension_server.py',
       'tests/extension_browser_check.py']
TEST_COMMON = ['tests/test_service.py', 'tests/live_smoke.py']
DEPENDENCIES = ['google-genai==2.29.0', 'pydantic==2.14.1']


def guide(web, extension):
    name = 'MailMate AI — ' + ('Web app + Gmail extension' if web and extension else 'Web app' if web else 'Gmail extension')
    text = f'''# {name}

## Requirements

Python 3.11 or newer, internet access, and your own Gemini API key from
https://aistudio.google.com/apikey. No GPU is needed. For the extension, use
Chrome or Edge on a desktop computer. This package contains no API keys or tokens.

## 1. Extract and install

Extract this ZIP completely. Open a terminal in the extracted folder containing
this README and `requirements.txt`. On Windows, run:

```powershell
python -m venv .venv
.\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt
Copy-Item .streamlit\\secrets.toml.example .streamlit\\secrets.toml
```

On macOS/Linux:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

## 2. Configure Gemini

Open `.streamlit/secrets.toml` in a text editor. Replace `YOUR_API_KEY` with your
own key. Keep the quotation marks. The included model configuration is:

```toml
GEMINI_API_KEY = "YOUR_API_KEY"
GEMINI_MODEL = "gemini-3.1-flash-lite"
```

Alternatively, set `GEMINI_API_KEY` and `GEMINI_MODEL` in the launch terminal's
environment. Environment values take precedence. Never share your configured
secrets file. Free-tier access depends on your account's quotas and model access.
Submitted text is processed by Gemini; use synthetic/non-confidential text for testing.

'''
    if web:
        text += '''## Run the web app

Windows:

```powershell
.\\.venv\\Scripts\\python.exe -m streamlit run app.py
```

macOS/Linux: `.venv/bin/python -m streamlit run app.py`

Open http://localhost:8501. Paste an email, set reply preferences, and choose
**Analyze & Draft**. Edit, regenerate, copy or download the reply. The Proofread
tab previews corrections before you apply them. Stop the server with Ctrl+C.
`run.ps1` is an optional Windows shortcut if PowerShell permits local scripts.

'''
    if extension:
        text += '''## Run and install the Gmail extension

The extension requires the included local Python bridge. Loading the extension
alone is not enough. Start the bridge in a terminal and leave it running:

```powershell
.\\.venv\\Scripts\\python.exe extension_server.py
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

'''
    if web and extension:
        text += 'Run the web app and extension bridge in separate terminals if you want both at once.\n\n'
    text += '''## Troubleshooting

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
.\\.venv\\Scripts\\python.exe -m pip install -r requirements-dev.txt
.\\.venv\\Scripts\\python.exe -m pytest -q
```

Tests use fake AI and do not need a key. Browser checks additionally require:

```powershell
.\\.venv\\Scripts\\python.exe -m playwright install chromium
```

'''
    if extension:
        text += 'Run `.\\.venv\\Scripts\\python.exe tests\\extension_browser_check.py` for synthetic Gmail extension checks.\n\n'
    if web:
        text += 'Run `.\\.venv\\Scripts\\python.exe tests\\browser_check.py` for web checks (installed Chrome required).\n\n'
    text += 'For three explicit synthetic live AI requests, run `.\\.venv\\Scripts\\python.exe tests\\live_smoke.py` after configuring your key.\n'
    return text


def build(name, web, extension):
    paths = COMMON + TEST_COMMON + (WEB if web else []) + (EXT if extension else [])
    if extension:
        paths += [p.relative_to(ROOT).as_posix() for p in (ROOT/'extension').rglob('*') if p.is_file()]
    requirements = DEPENDENCIES + (['streamlit==1.65.0'] if web else []) + (['fastapi==0.143.0','uvicorn==0.54.0'] if extension else [])
    target = OUTPUT / f'{name}.zip'
    with ZipFile(target, 'w', ZIP_DEFLATED) as archive:
        for path in sorted(set(paths)):
            archive.write(ROOT/path, f'{name}/{path}')
        archive.writestr(f'{name}/README.md', guide(web, extension))
        archive.writestr(f'{name}/requirements.txt', '\n'.join(requirements)+'\n')
        archive.writestr(f'{name}/requirements-dev.txt', '-r requirements.txt\npytest==9.1.1\nplaywright==1.63.0\n')
    return target


def main():
    OUTPUT.mkdir(exist_ok=True)
    private = []
    secret_path = ROOT / '.streamlit/secrets.toml'
    if secret_path.exists():
        key = tomllib.loads(secret_path.read_text(encoding='utf-8')).get('GEMINI_API_KEY')
        if key and key != 'YOUR_API_KEY': private.append(key.encode())
    token_path = ROOT / '.mailmate-extension-token'
    if token_path.exists(): private.append(token_path.read_bytes().strip())
    for name, web, extension in [('webapp',True,False),('webapp-and-extension',True,True),('extension',False,True)]:
        target = build(name, web, extension)
        with ZipFile(target) as archive:
            assert archive.testzip() is None
            for entry in archive.namelist():
                assert not entry.endswith('/secrets.toml') and '.mailmate-extension-token' not in entry
                data = archive.read(entry)
                assert not any(value and value in data for value in private), 'Private credential found in package'
        print(f'Created and verified {target.name} ({target.stat().st_size:,} bytes)')
    (OUTPUT/'README.md').write_text('''# MailMate share packages

- **webapp.zip** — Streamlit web app only.
- **webapp-and-extension.zip** — Web app, Gmail extension, and local Python bridge.
- **extension.zip** — Gmail extension and required local Python bridge; no Streamlit app.

Each ZIP has its own complete setup README, dependency files, launchers and tests.
Extract the ZIP before setup. Your friend must provide their own Gemini API key.
No API keys, tokens, virtual environments, logs, browser profiles or generated artifacts are included.
''',encoding='utf-8')


if __name__ == '__main__':
    main()
