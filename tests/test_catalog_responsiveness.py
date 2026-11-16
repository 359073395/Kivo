import asyncio
from pathlib import Path
import sys
import threading

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'web'))
import app as web


def test_slow_catalog_does_not_block_status_event_loop(monkeypatch):
    started, release = threading.Event(), threading.Event()
    def slow_catalog():
        started.set()
        assert release.wait(3)
        return [{'name': 'test'}]
    monkeypatch.setattr(web, 'get_skills', slow_catalog)
    monkeypatch.setattr(web, 'list_personas', lambda: [])
    monkeypatch.setattr(web, '_direct_api_enabled', lambda: True)
    monkeypatch.setattr(web, '_harness_settings', lambda: {'runtime': 'api'})
    monkeypatch.setattr(web, 'read_settings', lambda _: {})
    monkeypatch.setattr(web, 'api_config', lambda _: ('base', 'model', 'key'))
    async def scenario():
        request = asyncio.create_task(web.api_status())
        try:
            assert await asyncio.to_thread(started.wait, 2)
            # This timer must run while the catalog thread is still waiting.
            await asyncio.sleep(.01)
        finally:
            release.set()
        assert (await request)['skills'] == [{'name': 'test'}]
    asyncio.run(scenario())


def test_catalog_cache_refreshes_docs_and_configuration(tmp_path, monkeypatch):
    file = tmp_path / 'builtin/example/SKILL.md'
    file.parent.mkdir(parents=True)
    file.write_text('---\ndescription: first\nlayer: create\n---\nbody', encoding='utf-8')
    monkeypatch.setattr(web, 'SKILLS_DIR', tmp_path)
    monkeypatch.setattr(web, 'SKILL_API_REQUIREMENTS', {'example': ['KEY']})
    ready = {'value': False}
    monkeypatch.setattr(web, '_read_env', lambda: {})
    monkeypatch.setattr(web, '_skill_api_configured', lambda *_: ready['value'])
    web._skill_summary.cache_clear()
    first = web.get_skills()
    assert first[0]['description'] == 'first' and not first[0]['apiConfigured']
    ready['value'] = True
    assert web.get_skills()[0]['apiConfigured']
    assert web._skill_summary.cache_info().hits == 1
    file.write_text('---\ndescription: changed description\nlayer: discover\n---\nbody', encoding='utf-8')
    changed = web.get_skills()[0]
    assert changed['description'] == 'changed description'
    assert changed['layer'] == 'discover'
    file.unlink()
    assert web.get_skills() == []
