from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))

import cbcc.cli as cli
from cbcc.provider_surface import host_execution_contract


class _FakeSurface:
    def __init__(self):
        self.calls = []

    def execute_local_revision(self, project_dir, revision_id, *, asset_ids=None, adapter_id=None, policy=None):
        self.calls.append({
            'project_dir': str(project_dir),
            'revision_id': revision_id,
            'asset_ids': asset_ids,
            'adapter_id': adapter_id,
            'max_attempts': policy.max_attempts,
            'max_polls_per_attempt': policy.max_polls_per_attempt,
        })
        return {'status': 'LOCAL_REVISION_PROVIDER_EXECUTION_COMPLETE', 'revision_id': revision_id, 'jobs': []}


def test_revision_execute_cli_routes_to_local_revision_provider_surface(tmp_path, monkeypatch, capsys):
    surface = _FakeSurface()
    monkeypatch.setattr(cli, 'provider_execution_surface_from_environment', lambda: surface)

    assert cli.main([
        'revision-execute',
        '--project-dir', str(tmp_path),
        '--revision-id', 'LR-PHASE8-CLI',
        '--asset-id', 'AST-1',
        '--adapter-id', 'EPV_HOST_CALLBACK_V1',
        '--max-attempts', '2',
        '--max-polls', '3',
    ]) == 0

    assert surface.calls == [{
        'project_dir': str(tmp_path),
        'revision_id': 'LR-PHASE8-CLI',
        'asset_ids': ['AST-1'],
        'adapter_id': 'EPV_HOST_CALLBACK_V1',
        'max_attempts': 2,
        'max_polls_per_attempt': 3,
    }]
    assert 'LOCAL_REVISION_PROVIDER_EXECUTION_COMPLETE' in capsys.readouterr().out


def test_revision_execute_is_declared_in_host_execution_contract():
    contract = host_execution_contract()
    assert 'revision-execute' in contract['commands']
