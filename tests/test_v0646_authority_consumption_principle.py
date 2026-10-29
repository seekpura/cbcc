from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def test_authority_map_rejects_file_presence_as_integration_proof():
    text=(ROOT/'prompts/canonical_authority_loading_map.md').read_text(encoding='utf-8')
    assert 'without being selected/consumed does not count as preserved capability' in text
    assert 'changes or constrains Strategy, Curation, Asset, Prompt/Assembly, Human HTML or Measurement/Revision' in text
