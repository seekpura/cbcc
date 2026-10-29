from pathlib import Path
import re


def replace_once(path, old, new):
    p=Path(path); s=p.read_text(encoding='utf-8')
    if old not in s:
        raise SystemExit(f'anchor missing {path}: {old[:180]!r}')
    p.write_text(s.replace(old,new,1),encoding='utf-8')

# Host wrapper: completion must not contradict the nonblocking Prompt authority.
replace_once(
    'scripts/build_plugin_dist.py',
    '4. 每个资产的中英文 Prompt 与其实际策划参数连续，Prompt Consumption Audit 的 `missing decisions = 0`；',
    '4. 若当前任务需要 Prompt / 生图 / Provider 执行，则显示 Prompt Consumption Audit 作为生产准备度；`missing decisions` 形成 `NEEDS_PROMPT_WORK`，但不得阻止资产、策略或项目人类交付完成；',
)
replace_once(
    'scripts/build_plugin_dist.py',
    '- 商品身份、包装、材质、颜色、结构与可见事实必须 source-bound；Claim、Compliance、平台当前证据、Review 与 Completion 按 `resources/SKILL.md` 和 Runtime 合同执行。',
    '- 商品规格、成分、功能、认证、Claim 与其他已验证事实必须 source-bound；产品图、包装图和源文件默认是设计参考，可按已选创意方向重绘/重渲染/风格化，除非当前子任务显式锁定源图。Claim、Compliance、平台当前证据、Review 与 Completion 按 `resources/SKILL.md` 和 Runtime 合同执行。',
)

# Foundation/source defaults: no hidden REFERENCE_CONSTRAINED fallback.
replace_once(
    'runtime/cbcc/compiler.py',
    '    """Bind exact real-product masters to production without copying or pretending missing files exist."""',
    '    """Bind supplied product/source files as design references by default; exact immutable-source semantics are explicit-only."""',
)
replace_once(
    'runtime/cbcc/compiler.py',
    "FoundationAssetRecord(f'FND-{i+1:02d}',role,product_fidelity=request.get('product_fidelity','REFERENCE_CONSTRAINED')).to_dict()",
    "FoundationAssetRecord(f'FND-{i+1:02d}',role,product_fidelity=request.get('product_fidelity','REFERENCE_GUIDED')).to_dict()",
)

# Provider-job policy must follow the selected fidelity/real-product route, not hard-code no substitution.
replace_once(
    'runtime/cbcc/production.py',
    "                'contract_binding_must_not_change':True,'real_product_master_substitution_allowed':False,",
    "                'contract_binding_must_not_change':True,'real_product_master_substitution_allowed':not bool(quality.get('real_product_master_required')),",
)
replace_once(
    'runtime/cbcc/production.py',
    "['source_binding_hash','production_contract_ack'] if str(quality.get('product_fidelity') or '').upper()=='LOCKED_PIXEL' else []",
    "['source_binding_hash','production_contract_ack'] if str(quality.get('product_fidelity') or '').upper() in {'LOCKED_PIXEL','LOCKED_SOURCE_COMPOSITE','COMPOSITE'} else []",
)
replace_once(
    'runtime/cbcc/production.py',
    "        if (fidelity=='LOCKED_PIXEL' and r.get('production_contract_ack') is not True) or ('production_contract_ack' in r and not r.get('production_contract_ack')):",
    "        if (fidelity in {'LOCKED_PIXEL','LOCKED_SOURCE_COMPOSITE','COMPOSITE'} and r.get('production_contract_ack') is not True) or ('production_contract_ack' in r and not r.get('production_contract_ack')):",
)
replace_once(
    'runtime/cbcc/production.py',
    "        if str(qc.get('product_fidelity') or '').upper()=='LOCKED_PIXEL':",
    "        if str(qc.get('product_fidelity') or '').upper() in {'LOCKED_PIXEL','LOCKED_SOURCE_COMPOSITE','COMPOSITE'}:",
)

# Prompt photography: people require inclusive representation, but photo-metering/prelight defaults only on photographic routes.
p=Path('runtime/cbcc/prompt_compiler.py'); s=p.read_text(encoding='utf-8')
old="""    capture_mode=str(explicit.get('capture_mode') or reasoning.get('capture_mode') or asset.get('capture_mode') or '').upper() or None
    human_applicable=_asset_human_applicable(asset)
    inherit_global=bool(explicit.get('inherit_strategy_photography') or reasoning.get('inherit_strategy_photography') or bool(reasoning) or capture_mode=='REAL_PHOTO' or human_applicable)
"""
new="""    capture_mode=str(explicit.get('capture_mode') or reasoning.get('capture_mode') or asset.get('capture_mode') or '').upper() or None
    human_applicable=_asset_human_applicable(asset)
    production_mode=str(asset.get('production_mode') or '').upper()
    photographic_route=bool(
        capture_mode=='REAL_PHOTO'
        or production_mode in {'REAL_PHOTO','REAL_PRODUCT_COMPOSITE','AI_ENVIRONMENT_REAL_PRODUCT','AI_HUMAN_REAL_PRODUCT'}
        or explicit.get('photographic_route')
        or reasoning.get('photographic_route')
    )
    inherit_global=bool(explicit.get('inherit_strategy_photography') or reasoning.get('inherit_strategy_photography') or bool(reasoning) or photographic_route)
"""
if old not in s: raise SystemExit('prompt photographic-route anchor missing')
s=s.replace(old,new,1)
old2="""    if human_applicable:
        # Human representation/exposure is P0 when people appear. Missing per-asset wiring must not
        # make the final Prompt silently lose skin-tone, reflector/diffusion or AI-bias execution.
        inclusive=_merge(_inclusive_human_defaults(), inclusive if isinstance(inclusive,dict) else {'representation_principle':inclusive})
"""
new2="""    if human_applicable and photographic_route:
        # Real / photographic routes consume metering, reflector/diffusion and exposure controls.
        inclusive=_merge(_inclusive_human_defaults(), inclusive if isinstance(inclusive,dict) else {'representation_principle':inclusive})
    elif human_applicable:
        # Illustration/3D/stylized generation keeps representation and bias controls without pretending a camera/prelight exists.
        representation_defaults={
            'body_age_disability':'Represent body type, age and disability naturally when relevant; do not erase task-relevant variation.',
            'ai_bias_controls':'No default whitening, youthifying, slimming, hair-texture homogenization or tokenistic/inspirational framing.',
            'representation_principle':'People exist to perform the real shopper/use task. Identity changes representation choices only when supported; it is not a shortcut to behavior.',
        }
        inclusive=_merge(representation_defaults, inclusive if isinstance(inclusive,dict) else {'representation_principle':inclusive})
"""
if old2 not in s: raise SystemExit('prompt human inclusive anchor missing')
s=s.replace(old2,new2,1)
s=s.replace("    repeatable=bool(explicit.get('repeatable_capture') or reasoning.get('repeatable_capture'))\n", "    repeatable=bool(explicit.get('repeatable_capture') or reasoning.get('repeatable_capture')) if photographic_route else False\n",1)
s=s.replace("    prelight_required=bool(explicit.get('prelight_required')) if 'prelight_required' in explicit else bool(capture_mode=='REAL_PHOTO' and (repeatable or lighting.get('prelight_plan')))\n", "    prelight_required=(bool(explicit.get('prelight_required')) if 'prelight_required' in explicit else bool(capture_mode=='REAL_PHOTO' and (repeatable or lighting.get('prelight_plan')))) if photographic_route else False\n",1)
# Ensure CN prompt can explain the new reference-guided rules instead of leaking English into the human layer.
marker="""        'approved product-specific evidence':'已批准的商品特定证据',
"""
insert="""        'approved product-specific evidence':'已批准的商品特定证据',
        'Use supplied product/source files as design references for the product subject; redraw/rerender is allowed unless an explicit locked-source mode is selected':'使用已提供的产品/源文件作为设计参考；除非显式选择锁定源图模式，否则允许重绘与重新渲染。',
        'Reference-guided mode: supplied product/source files guide design and identity cues; redraw, rerender, stylize, illustrate or recompose as the selected direction requires. Do not present creative changes as verified product facts.':'参考设计模式：已提供的产品/源文件用于指导设计与必要的身份线索；可按已选方向重绘、重渲染、风格化、插画化或重新构图。不得把创作性变化当成已验证商品事实。',
        'Explicit locked-source mode: preserve the supplied product master as an immutable source layer; do not redraw that layer.':'显式锁定源图模式：已提供的产品母图作为不可修改的源图层保留，不得重绘该图层。',
"""
if marker not in s: raise SystemExit('prompt translation marker missing')
s=s.replace(marker,insert,1)
p.write_text(s,encoding='utf-8')

# Video CN mapping: current emitted reference rules need native Chinese; remove old "always real master" authority from active translation map.
p=Path('runtime/cbcc/video_creator.py'); s=p.read_text(encoding='utf-8')
old="""      'Use supplied real product masters/references as identity authority. Do not redraw packaging, logo, printed copy, geometry, proportions or product color.':'以已提供的真实商品母版 / 参考图作为身份权威；不得重画包装、Logo、印刷文字、几何比例或真实产品颜色。',
"""
new="""      'Use supplied real product masters/references as identity authority. Do not redraw packaging, logo, printed copy, geometry, proportions or product color.':'仅在显式锁定源图时，以已提供的商品母版作为不可修改的源图层；普通参考设计模式不适用此约束。',
      'Reference-guided mode: supplied product/source files guide design and identity cues; redraw, rerender, stylize, illustrate or recompose as the selected direction requires. Do not present creative changes as verified product facts.':'参考设计模式：产品/源文件用于指导设计与必要的身份线索；可按方向重绘、重渲染、风格化、插画化或重新构图。不得把创作性变化当成已验证商品事实。',
      'Explicit locked-source mode: preserve the supplied product master as an immutable source layer; do not redraw that layer.':'显式锁定源图模式：保留已提供的产品母图为不可修改的源图层，不得重绘该图层。',
"""
if old not in s: raise SystemExit('video translation old-master anchor missing')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')

# Current top-level authority wording: historical locked-pixel sections remain history, current precedence stays reference-guided/nonblocking.
replace_once(
    'SKILL.md',
    '- **冻结事实与硬边界，Agent 自主决定完成路径。** Product Truth、用户明确锁定、平台/法规硬约束、Claim 证据、真实商品身份/LOCKED PIXEL、目标输出技术规格属于不可擅自改写的边界；研究范围、策略路径、内容范围、资产数量、创意机制、方向数量、构图/摄影/CMF、生产路线和迭代深度属于 Agent 决策。',
    '- **冻结事实与硬边界，Agent 自主决定完成路径。** Product Truth、用户明确锁定、平台/法规硬约束、Claim 证据、目标输出技术规格属于不可擅自改写的边界；只有显式锁定源图时，源图像素/对应身份层才成为生产硬边界。研究范围、策略路径、内容范围、资产数量、创意机制、方向数量、构图/摄影/CMF、生产路线和迭代深度属于 Agent 决策。',
)

# Tests lock the final semantics.
Path('tests/test_final_reference_guided_consistency.py').write_text(r'''from pathlib import Path
import json

from cbcc.compiler import _normalize_source_product_assets
from cbcc.prompt_compiler import _derived_photo_contract
from cbcc.production import _production_quality_contract, materialize_provider_jobs


def test_nonphotographic_human_asset_keeps_representation_without_camera_defaults():
    asset={'asset_id':'A','production_mode':'THREE_D','creative_brief':{'human':'stylized person'}}
    p=_derived_photo_contract(asset, {'sections':{'05_visual_photography_strategy':{'camera':{'focal_length_mm':'85mm'},'lighting_framework':{'cct':'5200K'}}}}, None)
    assert p.get('camera') in ({},None)
    inc=p.get('inclusive_photography') or {}
    assert 'ai_bias_controls' in inc
    assert 'skin_tone_exposure' not in inc
    assert p.get('prelight_required') is False


def test_provider_job_allows_reference_substitution_when_real_master_not_required(tmp_path):
    root=tmp_path/'assets'; d=root/'A'; d.mkdir(parents=True)
    (root/'ASSET_PACKAGE_INDEX.json').write_text(json.dumps({'assets':[{'asset_id':'A'}]}),encoding='utf-8')
    # minimal package files used for hashing/contract reads
    (d/'00_asset_manifest.yaml').write_text('asset_id: A\nstatus: ACTIVATE\nproduction_mode: GRAPHIC_DESIGN\nproduct_fidelity: REFERENCE_GUIDED\nsource_product_assets: []\n',encoding='utf-8')
    for fn in ['03_photography_contract.json','04_layout_contract.json','13_prompt_contract.json']:
        (d/fn).write_text('{}',encoding='utf-8')
    qc=_production_quality_contract(d, {'asset_id':'A','production_mode':'GRAPHIC_DESIGN','product_fidelity':'REFERENCE_GUIDED','source_product_assets':[]})
    assert qc['real_product_master_required'] is False
    run={'assets':[{'asset_id':'A','status':'READY_TO_HANDOFF','package_hash':'x','provider':'HUMAN_OR_DESIGN_PROVIDER','provider_contract':{'adapter':'FILE_HANDOFF'},'production_mode':'GRAPHIC_DESIGN','production_quality_contract':qc,'production_contract_binding':{}}]}
    out=materialize_provider_jobs(root,run,tmp_path/'jobs')
    assert out['job_count']==1
    job=json.loads((tmp_path/'jobs/A/job.json').read_text(encoding='utf-8'))
    assert job['execution_policy']['real_product_master_substitution_allowed'] is True


def test_host_wrapper_does_not_reintroduce_prompt_zero_missing_gate():
    source=Path('scripts/build_plugin_dist.py').read_text(encoding='utf-8')
    assert 'Prompt Consumption Audit 的 `missing decisions = 0`' not in source
    assert 'missing decisions` 形成 `NEEDS_PROMPT_WORK`' in source
''',encoding='utf-8')

print('final reference-guided consistency patch applied')
