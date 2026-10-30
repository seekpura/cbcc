from __future__ import annotations
import json
from pathlib import Path
from runtime.cbcc.canonical_asset_package_lineage import promote_package_lineage


def test_nested_design_card_lineage_is_promoted_losslessly(tmp_path:Path):
    d=tmp_path/'A01';d.mkdir()
    lineage={'schema_version':'cbcc-canonical-art-direction-v1','canonical_art_direction_sha256':'b'*64,'source':'normalized_named_asset_art_direction'}
    path=d/'13_prompt_contract.json'
    path.write_text(json.dumps({'status':'READY','design_card':{'canonical_prompt_lineage':lineage}},ensure_ascii=False),encoding='utf-8')
    result=promote_package_lineage(tmp_path)
    assert result['status']=='PASS'
    saved=json.loads(path.read_text(encoding='utf-8'))
    assert saved['canonical_prompt_lineage']==lineage
    assert saved['design_card']['canonical_prompt_lineage']==lineage


def test_missing_lineage_is_reported_without_inventing_hash(tmp_path:Path):
    d=tmp_path/'A02';d.mkdir()
    path=d/'13_prompt_contract.json';path.write_text(json.dumps({'design_card':{}},ensure_ascii=False),encoding='utf-8')
    result=promote_package_lineage(tmp_path)
    assert result['status']=='INCOMPLETE'
    assert result['missing']==['A02']
    assert 'canonical_prompt_lineage' not in json.loads(path.read_text(encoding='utf-8'))
