from pathlib import Path
from types import SimpleNamespace

import pytest
from web import app as web


def test_config_replacement_uses_the_resolved_file_directory(tmp_path, monkeypatch):
    physical = tmp_path / 'redirected/model.env'
    physical.parent.mkdir()
    physical.write_text('OLD=value\n', encoding='utf-8')
    monkeypatch.setattr(web, 'ENV_FILE', SimpleNamespace(resolve=lambda: physical))
    web._replace_env_contents('MODEL=verified\n')
    assert physical.read_text(encoding='utf-8') == 'MODEL=verified\n'
    assert not list(physical.parent.glob('*.tmp'))


def test_failed_config_replacement_preserves_previous_settings(tmp_path, monkeypatch):
    destination = tmp_path / 'model.env'
    destination.write_text('MODEL=previous\n', encoding='utf-8')
    monkeypatch.setattr(web, 'ENV_FILE', destination)

    def fail_replace(*args):
        raise OSError('simulated rename failure')

    monkeypatch.setattr(Path, 'replace', fail_replace)
    with pytest.raises(OSError, match='simulated rename failure'):
        web._replace_env_contents('MODEL=new\n')
    assert destination.read_text(encoding='utf-8') == 'MODEL=previous\n'
    assert not list(tmp_path.glob('*.tmp'))
