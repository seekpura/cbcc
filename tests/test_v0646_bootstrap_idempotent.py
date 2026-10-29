from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def test_bootstrap_declares_idempotent_install():
    text=(ROOT/'runtime/cbcc/commercial_continuity_bootstrap.py').read_text(encoding='utf-8')
    assert '_INSTALLED = False' in text or '_INSTALLED=False' in text
    assert 'if _INSTALLED' in text
