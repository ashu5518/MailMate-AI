from unittest.mock import Mock
from fastapi.testclient import TestClient
import pytest
import extension_server as bridge
from gemini_service import ServiceError
from models import Reply


@pytest.fixture
def client(monkeypatch):
    api=Mock()
    api.regenerate_reply.return_value=Reply(reply='Thank you.')
    monkeypatch.setattr(bridge, 'service', lambda:api)
    with TestClient(bridge.app) as c:
        yield c,api


HEADERS={'X-MailMate-Extension':'a'*32}


def test_requires_extension_header(client):
    c,api=client
    assert c.get('/health').status_code==403
    assert c.post('/reply',json={'email':'Hello'}).status_code==403
    api.regenerate_reply.assert_not_called()
    assert c.get('/health',headers=HEADERS).json()['status']=='ok'
    assert c.get('/health',headers={**HEADERS,'Origin':'https://evil.example'}).status_code==403
    assert c.options('/health',headers={'Origin':'https://evil.example','Access-Control-Request-Method':'GET','Access-Control-Request-Headers':'X-MailMate-Extension'}).status_code==400
    assert c.get('/health',headers={**HEADERS,'Origin':'chrome-extension://'+'a'*32}).status_code==200


def test_reply_and_safe_errors(client):
    c,api=client
    assert c.post('/reply',json={'email':'Hello'},headers=HEADERS).json()=={'reply':'Thank you.'}
    api.regenerate_reply.side_effect=ServiceError('Gemini quota exhausted.')
    response=c.post('/reply',json={'email':'Hello'},headers=HEADERS)
    assert response.status_code==400 and 'quota' in response.json()['detail']


def test_rejects_oversized_and_unknown_fields(client):
    c,api=client
    for payload in [{'email':'x'*20001},{'email':'Hello','api_key':'secret'}]:
        response=c.post('/reply',json=payload,headers=HEADERS)
        assert response.status_code==422
        assert 'secret' not in response.text
    api.regenerate_reply.assert_not_called()


def test_rejects_other_hosts_and_concurrent_calls(client):
    c,_=client
    assert c.get('/health',headers={**HEADERS,'host':'evil.example'}).status_code==400
    bridge.gate.acquire()
    try:
        assert c.post('/reply',json={'email':'Hello'},headers=HEADERS).status_code==429
    finally:
        bridge.gate.release()


def test_inline_word_edits_and_unicode_offsets():
    text='👋 Thnak you for your mesage.'
    result=bridge.proofreading_edits(text,'👋 Thank you for your message.')
    assert result[0]['start']==3
    assert result[0]['original']=='Thnak' and result[0]['replacement']=='Thank'
    assert result[1]['original']=='mesage.' and result[1]['replacement']=='message.'
    assert bridge.proofreading_edits('Already correct.','Already correct.')==[]
