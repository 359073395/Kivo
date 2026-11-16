"""Kivo knowledge/tools keep their behavior inside upstream durable chat runs."""
import importlib.util
import json
from pathlib import Path

import httpx
import pytest

from lingxi import model_runtime
from easel.run_store import RunStore

_spec = importlib.util.spec_from_file_location('kivo_recovery_fixtures', Path(__file__).with_name('test_direct_api.py'))
_support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)
sandbox, web = _support.sandbox, _support.web
sse, chunk = _support.sse, _support.chunk
CLIENT = httpx.AsyncClient


@pytest.mark.parametrize('endpoint', ['/api/chat', '/api/chat/stream'])
def test_knowledge_tool_artifact_and_replay_do_not_execute_twice(sandbox, tmp_path, monkeypatch, endpoint):
    monkeypatch.setenv('LINGXI_API_TOOLS', '1')
    monkeypatch.setenv('LINGXI_KNOWLEDGE_AUTO', '1')
    vault = tmp_path / 'vault'
    vault.mkdir()
    (vault / 'knowledge-base.json').write_text('{}', encoding='utf-8')
    monkeypatch.setenv('LINGXI_KNOWLEDGE_ROOT', str(vault))
    monkeypatch.setenv('LINGXI_DATA_ROOT', str(tmp_path / 'knowledge-data'))
    fact = 'Kivo 回归样例：星帆项目的校验标记是蓝松果。'
    response = sandbox.post('/api/knowledge/learn', json={'title': '星帆项目', 'text': fact, 'activate': True})
    assert response.status_code == 200
    monkeypatch.setattr(web, 'ProjectTools', lambda session, **kwargs: model_runtime.ProjectTools(session, root=tmp_path, **kwargs))
    requests = []

    def respond(request):
        body = json.loads(request.content)
        requests.append(body)
        record = RunStore(web.SESSIONS_DIR / 'runs.sqlite3').get('kivo-tools')
        assert record.state == 'running'
        if len(requests) == 1:
            assert '星帆' in body['messages'][0]['content']
            name, arguments = 'knowledge_search', {'query': '星帆项目'}
        elif len(requests) == 2:
            assert '蓝松果' in body['messages'][-1]['content']
            name, arguments = 'save_artifact', {'name': 'result.md', 'text': fact}
        else:
            assert len(requests) == 3
            assert json.loads(body['messages'][-1]['content'])['created'] is True
            return httpx.Response(200, text=sse(chunk('已检索并保存蓝松果'), chunk(finish='stop'), '[DONE]'))
        return httpx.Response(200, text=sse(chunk(tool_calls=[{
            'index': 0, 'id': f'call{len(requests)}', 'function': {'name': name, 'arguments': json.dumps(arguments)}
        }]), chunk(finish='tool_calls'), '[DONE]'))

    monkeypatch.setattr(model_runtime.httpx, 'AsyncClient', lambda **kwargs: CLIENT(transport=httpx.MockTransport(respond), **kwargs))
    body = {'message': '请检索星帆项目并保存结果', 'sessionId': 'kivo-tools-session', 'turnId': 'kivo-tools'}
    response = sandbox.post(endpoint, json=body)
    assert response.status_code == 200, response.text
    assert '蓝松果' in response.text
    state = sandbox.get('/api/chat/jobs/kivo-tools').json()
    assert state['state'] == 'succeeded' and state['backend'] == 'direct_api'
    artifacts = list((tmp_path / 'outputs').rglob('result.md'))
    assert len(artifacts) == 1 and artifacts[0].read_text(encoding='utf-8') == fact
    saved = artifacts[0].read_bytes()
    assert '蓝松果' in sandbox.get('/api/chat/jobs/kivo-tools/stream').text
    assert sandbox.post(endpoint, json=body).status_code == 409
    assert len(requests) == 3 and artifacts[0].read_bytes() == saved


def test_noninteractive_recovery_never_grants_script_permission(sandbox, tmp_path, monkeypatch):
    monkeypatch.setenv('LINGXI_API_TOOLS', '1')
    monkeypatch.setattr(web, 'ProjectTools', lambda session, **kwargs: model_runtime.ProjectTools(session, root=tmp_path, **kwargs))
    calls = []

    async def runner(settings, content, **kwargs):
        allowed = await kwargs['tools'].approve({'purpose': 'test', 'command': 'must not run', 'warning': 'test'})
        calls.append(allowed)
        assert allowed is False
        yield 'token', '需要在交互窗口确认脚本'
        yield 'finish', 'stop'

    monkeypatch.setattr(web, 'stream_agent', runner)
    body = {'message': '运行脚本', 'sessionId': 'permission-session', 'turnId': 'permission-turn'}
    response = sandbox.post('/api/chat', json=body)
    assert response.status_code == 200
    assert sandbox.get('/api/chat/jobs/permission-turn').json()['state'] == 'succeeded'
    assert sandbox.post('/api/chat', json=body).status_code == 409
    assert calls == [False]
