"""Loopback bridge restricted to extension requests with a non-simple header."""
from pathlib import Path
import os
import difflib
import re
import threading
import tomllib
from typing import Literal

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from gemini_service import GeminiService, ServiceError

ROOT = Path(__file__).resolve().parent
app = FastAPI(title='MailMate local bridge', docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=['127.0.0.1', 'localhost', 'testserver'])
app.add_middleware(CORSMiddleware, allow_origin_regex=r'chrome-extension://[a-p]{32}',
                   allow_methods=['GET', 'POST'], allow_headers=['Content-Type', 'X-MailMate-Extension'])
gate = threading.Lock()


def authorize(x_mailmate_extension: str = Header(default=''), origin: str = Header(default='')):
    # Ordinary websites cannot send this custom header without a preflight;
    # CORS allows only browser-extension origins, and Host blocks DNS rebinding.
    if not re.fullmatch(r'[a-p]{32}', x_mailmate_extension):
        raise HTTPException(403, 'Use the MailMate browser extension to access this service.')
    if origin and origin != f'chrome-extension://{x_mailmate_extension}':
        raise HTTPException(403, 'This website cannot access the local assistant.')


class EmailInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    email: str = Field(min_length=1, max_length=20000)
    instructions: str = Field(default='', max_length=2000)
    signature: str = Field(default='', max_length=500)
    tone: Literal['Professional', 'Friendly', 'Formal', 'Casual', 'Polite'] = 'Professional'
    length: Literal['Short', 'Medium', 'Detailed'] = 'Short'


class ProofInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    text: str = Field(min_length=1, max_length=20000)


def service():
    path = ROOT / '.streamlit' / 'secrets.toml'
    data = tomllib.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    return GeminiService(os.getenv('GEMINI_API_KEY') or data.get('GEMINI_API_KEY'),
                         os.getenv('GEMINI_MODEL') or data.get('GEMINI_MODEL'))


@app.exception_handler(RequestValidationError)
async def invalid_input(request, exc):
    return JSONResponse(status_code=422, content={'detail': 'Check text length and reply settings. Email/text: 20,000 characters; instructions: 2,000; signature: 500.'})


def perform(operation, data):
    if not gate.acquire(blocking=False):
        raise HTTPException(429, 'Another request is running. Try again when it finishes.')
    try:
        return getattr(service(), operation)(**data).model_dump()
    except ServiceError as exc:
        raise HTTPException(400, str(exc)) from None
    except Exception:
        raise HTTPException(503, 'The local assistant could not complete this request. Retry.') from None
    finally:
        gate.release()


@app.get('/health', dependencies=[Depends(authorize)])
def health():
    return {'status': 'ok', 'version': '1.0'}


@app.post('/analyze', dependencies=[Depends(authorize)])
def analyze(body: EmailInput):
    return perform('analyze_and_draft', body.model_dump())


@app.post('/reply', dependencies=[Depends(authorize)])
def reply(body: EmailInput):
    return perform('regenerate_reply', body.model_dump())


@app.post('/proofread', dependencies=[Depends(authorize)])
def proofread(body: ProofInput):
    result = perform('proofread', body.model_dump())
    result['suggestions'] = proofreading_edits(body.text, result['corrected_text'])
    return result


def proofreading_edits(original, corrected):
    """Word-level edits with JavaScript UTF-16 offsets, including Unicode text."""
    before = list(re.finditer(r'\S+', original))
    after = list(re.finditer(r'\S+', corrected))
    edits = []
    for tag, i, j, a, b in difflib.SequenceMatcher(None,
            [m.group() for m in before], [m.group() for m in after], autojunk=False).get_opcodes():
        if tag == 'equal':
            continue
        start = before[i].start() if i < len(before) else len(original)
        end = before[j-1].end() if j > i else start
        replacement = corrected[after[a].start():after[b-1].end()] if b > a else ''
        if tag == 'insert':
            replacement = replacement + ' ' if i < len(before) else ' ' + replacement
        edits.append({'start': len(original[:start].encode('utf-16-le')) // 2,
                      'end': len(original[:end].encode('utf-16-le')) // 2,
                      'original': original[start:end], 'replacement': replacement})
    return edits


if __name__ == '__main__':
    import uvicorn
    print('MailMate bridge: http://127.0.0.1:8765')
    print('The browser extension connects automatically. No connection token is required.')
    uvicorn.run(app, host='127.0.0.1', port=8765, access_log=False, log_level='warning')
