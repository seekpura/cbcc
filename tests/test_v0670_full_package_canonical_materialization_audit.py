from __future__ import annotations
import json
from pathlib import Path

from runtime.cbcc.canonical_materialization_package_audit import wrap_audit_host_full_package


def _base(_package:Path): return {'status':'PASS','issues':[]}


def test_final_package_boundary_rejects_k01_style_semantic_copy_lineage_and_html_regressions(tmp_path:Path):
    d=tmp_path/'asset_packages'/'G08';d.mkdir(parents=True)
    card={
      'asset_id':'G08','visual_carrier':'REQUIRED','product_presence':{'state':'REQUIRED','role':'routine','why':'reduce friction'},
      'evidence_hierarchy':'POST_COMPOSITE','copy_render_route':'3 LANGKAH MUDAH\n01 CUCI WAJAH',
      'camera_optics':'5200K broad soft light','lighting':'warm-white stone, clear pump, natural hands',
      'cmf_material_color':'1600×1600 sRGB','output_surface':'用法清楚可降低酸类产品的不确定与退货/误用。',
      'business_hypothesis':'FAQ reduction / PDP CVR','success_metric':'从单帧 lifestyle 进入动作序列','portfolio_rhythm_delta':'GENERATIVE'
    }
    (d/'11_design_card.json').write_text(json.dumps(card,ensure_ascii=False),encoding='utf-8')
    (d/'07_visible_copy.md').write_text('''# Visible Copy Block｜G08

**Render route:** 3 LANGKAH MUDAH
01 CUCI WAJAH
**Locale:** ms-MY primary

## Bahasa Melayu（exact）
3 SIMPLE STEPS

## English semantic baseline
3步简单使用

## 中文释义 / 用途
60mm; f/7.1; 15-degree top-down
''',encoding='utf-8')
    (d/'12_prompt_contract.json').write_text(json.dumps({'copy_render_route':'3 LANGKAH MUDAH'},ensure_ascii=False),encoding='utf-8')

    data={
      'listing':{'description_en':'English','key_points':[{'en':'x'}],'attributes':{'Brand':'X'},'package_contents':{'en':'x'},'faq':[{'q_bm':'q'}]},
      'strategy':{'strategy':{'value_proposition':'v','message_hierarchy':['m'],'priority_tradeoff':[{'level':'P0'}]}},
      'market':{'platform_rules':[{'rule':'r'}],'why':{'platform':'p'}},
      'visual':{'palette':{'x':'#fff'},'contrast':'c','typography':'t','platform':'p','inclusive':'i','shot_list':['s']},
      'content':{'rows':[{'cover':'c','subtitle':'s','music':'m','traffic':'t','landing':'l'}]},
      'race':{'rows':[{'stage':'Research'},{'stage':'Action'},{'stage':'Communication'},{'stage':'Evaluation'}]},
      'culture':{'rows':[{'dimension':'language'}]},
      'compliance':{'other_risks':[{'risk':'r'}],'self_check':[{'item':'是否编造事实'}]},
      'ads':{'objective':'o','economics_boundary':'e','landing':'l','attribution':'a','failure_diagnosis':['f']},
      'reviews':{'status':'NO_DATA'},'sources':{'sources':[{'url':'https://example.com'}]},
      'assets':[{'id':'G08','card':card}],
    }
    renderer="function malaysia(){return DATA.listing.description_bm}; $('#search').addEventListener('input',e=>DATA.assets.filter(x=>x.id)); function copyText(x){navigator.clipboard.writeText(x)}"
    (tmp_path/'index.html').write_text('<script>const DATA='+json.dumps(data,ensure_ascii=False)+';'+renderer+'</script>',encoding='utf-8')

    result=wrap_audit_host_full_package(_base)(tmp_path)
    codes={x['code'] for x in result['issues']}
    assert result['status']=='INCOMPLETE'
    assert 'ASSET_SCHEMA_SEMANTIC_MISMATCH' in codes
    assert 'VISIBLE_COPY_LANGUAGE_SLOT_MISMATCH' in codes
    assert 'PROMPT_CONTRACT_COPY_ROUTE_INVALID' in codes
    assert 'PROMPT_CANONICAL_LINEAGE_MISSING' in codes
    assert 'HTML_LISTING_PROJECTION_INCOMPLETE' in codes
    assert 'RACE_PLATFORM_FIELD_MISSING' in codes
    assert 'CULTURE_EXECUTION_COLUMNS_MISSING' in codes
    assert 'WORKSPACE_COPY_BINDING_MISSING' in codes
    assert 'WORKSPACE_SEARCH_SCOPE_INCOMPLETE' in codes


def test_persisted_lineage_inside_prompt_contract_design_card_counts_as_same_source_proof(tmp_path:Path):
    d=tmp_path/'asset_packages'/'G01';d.mkdir(parents=True)
    lineage={'schema_version':'cbcc-canonical-art-direction-v1','canonical_art_direction_sha256':'a'*64,'source':'normalized_named_asset_art_direction'}
    card={
      'asset_id':'G01','visual_carrier':'source product portrait','product_presence':{'state':'HERO_REQUIRED','role':'hero','why':'identity'},
      'evidence_hierarchy':'pack geometry','copy_render_route':'NO_VISIBLE_COPY','camera_optics':'85mm; f/8; focus on pack','lighting':'5200K soft key + fill','cmf_material_color':'warm-white satin tube + clear pump','output_surface':'1600×1600 sRGB','business_hypothesis':'source packshot should improve identity confidence','success_metric':'PDP CTR','portfolio_rhythm_delta':'quiet factual opener'
    }
    (d/'12_design_card.json').write_text(json.dumps(card,ensure_ascii=False),encoding='utf-8')
    (d/'13_prompt_contract.json').write_text(json.dumps({'design_card':{'canonical_prompt_lineage':lineage}},ensure_ascii=False),encoding='utf-8')
    result=wrap_audit_host_full_package(_base)(tmp_path)
    assert 'PROMPT_CANONICAL_LINEAGE_MISSING' not in {x['code'] for x in result['issues']}
