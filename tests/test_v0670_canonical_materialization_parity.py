from __future__ import annotations

from pathlib import Path

from runtime.cbcc.canonical_materialization_integrity import (
    audit_asset_semantics,
    audit_visible_copy_markdown,
    audit_asset_directory,
    stamp_prompt_lineage,
    audit_prompt_lineage,
)


def _good_asset():
    return {
        'asset_id':'G07',
        'visual_carrier':'inclusive lifestyle vignette',
        'product_presence':{'state':'SUPPORTING','role':'routine product','why':'show real routine'},
        'subject':'adult Malaysian user with natural skin texture',
        'action_decisive_moment':'pick up tube and prepare to press pump',
        'scene_environment':'ordinary vanity',
        'props_supporting_elements':'mirror edge and towel',
        'composition_spatial_rhythm':'person left/center, product readable in hand',
        'evidence_hierarchy':'product identity + routine semantics',
        'copy_render_route':'HYBRID',
        'camera_optics':'50mm; eye-level; working distance 1.4m; f/4.5; focus on hand-product interaction',
        'lighting':'5400K soft window light + neutral bounce; Prelight waveform check',
        'cmf_material_color':'natural skin, satin tube, clear pump, pale stone, warm cotton',
        'output_surface':'1600×1600 sRGB',
        'business_hypothesis':'A believable routine should reduce perceived distance between product and daily use.',
        'success_metric':'PDP CVR / creator handoff',
        'portfolio_rhythm_delta':'first human scene after object/information frames',
    }


def _shifted_g08():
    return {
        'asset_id':'G08',
        'visual_carrier':'REQUIRED',
        'product_presence':{'state':'REQUIRED','role':'product strongest in step 2','why':'reduce use friction'},
        'subject':'pump and gentle spread gesture',
        'action_decisive_moment':'three sequential moments',
        'scene_environment':'warm-white vanity',
        'props_supporting_elements':'continuous action path',
        'composition_spatial_rhythm':'usage + daytime reminder',
        'evidence_hierarchy':'POST_COMPOSITE',
        'copy_render_route':'3 LANGKAH MUDAH\n01 CUCI WAJAH · 02 SAPUKAN GEL KIYUU · 03 RATAKAN PERLAHAN',
        'camera_optics':'5200K broad soft light, small highlight at contact point',
        'lighting':'warm-white stone, clear pump, natural hands',
        'cmf_material_color':'1600×1600 sRGB',
        'output_surface':'用法清楚可降低酸类产品的不确定与退货/误用。',
        'business_hypothesis':'FAQ reduction / PDP CVR',
        'success_metric':'从单帧 lifestyle 进入动作序列',
        'portfolio_rhythm_delta':'GENERATIVE',
    }


def test_semantic_guard_accepts_named_domain_correct_asset():
    assert audit_asset_semantics(_good_asset()) == []


def test_semantic_guard_rejects_real_k01_positional_shift_pattern():
    issues=audit_asset_semantics(_shifted_g08())
    fields={x['field'] for x in issues}
    assert {'visual_carrier','evidence_hierarchy','copy_render_route','camera_optics','lighting','cmf_material_color','output_surface','business_hypothesis','success_metric','portfolio_rhythm_delta'} <= fields
    assert {x['code'] for x in issues} == {'ASSET_SCHEMA_SEMANTIC_MISMATCH'}


def test_visible_copy_guard_rejects_shifted_language_slots():
    text='''# Visible Copy Block｜G08

**Render route:** 3 LANGKAH MUDAH
01 CUCI WAJAH · 02 SAPUKAN GEL KIYUU
**Locale:** ms-MY primary

## Bahasa Melayu（exact）
3 SIMPLE STEPS
01 CLEANSE · 02 APPLY KIYUU GEL

## English semantic baseline
3步简单使用
01洁面 · 02涂抹KIYUU凝胶

## 中文释义 / 用途
60mm; f/7.1; 15-degree top-down
'''
    issues=audit_visible_copy_markdown(text)
    assert {x['field'] for x in issues} >= {'render_route','english_semantic_baseline','chinese_meaning'}


def test_prompt_cn_en_share_one_canonical_art_direction_lineage():
    asset=_good_asset()
    bundle={'prompt_cn':'中文模型提示词','prompt_en':'English model prompt','design_card':{},'prompt_contract':{}}
    stamped=stamp_prompt_lineage(asset,bundle)
    assert audit_prompt_lineage(asset,stamped)==[]
    assert stamped['canonical_prompt_lineage']==stamped['design_card']['canonical_prompt_lineage']==stamped['prompt_contract']['canonical_prompt_lineage']
    changed=dict(asset);changed['camera_optics']='85mm; eye-level; f/8'
    assert audit_prompt_lineage(changed,stamped)[0]['code']=='PROMPT_CANONICAL_LINEAGE_MISMATCH'


def test_asset_directory_guard_reads_real_delivery_filenames(tmp_path:Path):
    d=tmp_path/'G08';d.mkdir()
    import json
    (d/'11_design_card.json').write_text(json.dumps(_shifted_g08(),ensure_ascii=False),encoding='utf-8')
    (d/'07_visible_copy.md').write_text('''# Visible Copy Block\n\n**Render route:** COPY TEXT\n**Locale:** ms-MY\n\n## Bahasa Melayu（exact）\nMalay\n\n## English semantic baseline\n中文\n\n## 中文释义 / 用途\n60mm f/8\n''',encoding='utf-8')
    issues=audit_asset_directory(d)
    codes={x['code'] for x in issues}
    assert 'ASSET_SCHEMA_SEMANTIC_MISMATCH' in codes
    assert 'VISIBLE_COPY_LANGUAGE_SLOT_MISMATCH' in codes
