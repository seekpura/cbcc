from pathlib import Path


def patch(path: str, transform):
    p=Path(path)
    text=p.read_text(encoding='utf-8')
    new=transform(text)
    if new==text:
        print(path, 'already repaired')
        return
    p.write_text(new,encoding='utf-8')
    print(path, 'repaired')


def patch_asset_compiler(text: str) -> str:
    old="""'deterministic_copy_overlay':prompt_bundle.get('deterministic_copy_overlay') or {},'parameter_trace':prompt_bundle.get('parameter_trace') or [],'machine_visual_contract':prompt_bundle['machine_visual_contract']"""
    new="""'deterministic_copy_overlay':prompt_bundle.get('deterministic_copy_overlay') or {},'parameter_trace':prompt_bundle.get('parameter_trace') or [],'prompt_consumption_audit':prompt_bundle.get('prompt_consumption_audit') or {},'machine_visual_contract':prompt_bundle['machine_visual_contract']"""
    if old in text:
        return text.replace(old,new)
    if "'prompt_consumption_audit':prompt_bundle.get('prompt_consumption_audit')" in text:
        return text
    raise SystemExit('asset_compiler prompt contract anchor not found')


def patch_delivery_export(text: str) -> str:
    if 'from .delivery_contract import validate_strategy_delivery' not in text:
        text=text.replace(
            'from .human_delivery import compile_upload_center, render_upload_center_md, build_project_hub_md\n',
            'from .human_delivery import compile_upload_center, render_upload_center_md, build_project_hub_md\nfrom .delivery_contract import validate_strategy_delivery\n',1)

    helper_anchor="""def _resolve_output(project: Path, output: Path) -> tuple[Path, Path]:
"""
    helpers="""def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data=json.loads(path.read_text(encoding='utf-8'))
        return data if isinstance(data,dict) else {}
    except Exception:
        return {}


def _prompt_consumption_summary(asset_root: Path) -> dict[str, Any]:
    rows=[]
    if asset_root.exists():
        for contract in sorted(asset_root.glob('*/13_prompt_contract.json')):
            data=_read_json(contract)
            audit=data.get('prompt_consumption_audit') or {}
            asset_id=contract.parent.name
            rows.append({
                'asset_id':asset_id,
                'status':audit.get('status') or 'MISSING',
                'missing_decisions':audit.get('missing_decisions') or (['PROMPT_CONSUMPTION_AUDIT_MISSING'] if not audit else []),
                'checks':audit.get('checks') or [],
            })
    missing=[r for r in rows if r.get('status')!='PASS' or r.get('missing_decisions')]
    return {
        'status':'PASS' if not missing else 'INCOMPLETE',
        'asset_count':len(rows),
        'assets':rows,
        'missing_assets':[r.get('asset_id') for r in missing],
        'principle':'Semantic compression may remove repetition or irrelevant toolbox fields, never a selected execution decision that changes pixels, capture, composite or deterministic post-production.',
    }


def _full_html_depth_check(html_text: str, full: bool) -> dict[str, Any]:
    if not full:
        return {'status':'NOT_REQUIRED_FOR_TASK_SCOPED','missing':[]}
    required=[
        '信息完整度、待确认清单、假设与决策日志',
        '产品真实事实审计与卖点分级表',
        '平台 × 区域 × 人群 × 族裔文化洞察',
        '营销框架与核心策略',
        '视觉总策略与拍摄执行清单',
        '分平台内容矩阵表',
        'RACE传播框架执行表',
        '族裔文化适配检查表',
        '合规、文化敏感与风险清单；评估指标与A/B测试建议；P0/P1/P2执行优先级与下一步需补充信息',
    ]
    missing=[x for x in required if x not in html_text]
    return {'status':'PASS' if not missing else 'INCOMPLETE','required_visible_objects':required,'missing':missing}


"""
    if '_prompt_consumption_summary' not in text:
        if helper_anchor not in text: raise SystemExit('delivery_export helper anchor not found')
        text=text.replace(helper_anchor,helpers+helper_anchor,1)

    required_anchor="""    missing = [str(x) for x in required if not x.exists()]
    if missing:
        raise FileNotFoundError('BLOCKED missing strategy authority: ' + ', '.join(missing))

"""
    required_insert=required_anchor+"""    strategy_authority=_read_json(project / 'artifacts/strategy/strategy_authority.json')
    depth_audit=validate_strategy_delivery(strategy_authority)
    full=depth_audit.get('mode')=='FULL'
    if full and depth_audit.get('status')!='PASS':
        raise RuntimeError('BLOCKED FULL delivery depth contract failed: ' + json.dumps(depth_audit.get('issues') or [], ensure_ascii=False))

"""
    if 'depth_audit=validate_strategy_delivery(strategy_authority)' not in text:
        if required_anchor not in text: raise SystemExit('delivery_export required anchor not found')
        text=text.replace(required_anchor,required_insert,1)

    asset_anchor="""    asset_root = project / 'artifacts/asset_packages'
    if asset_root.exists():
        shutil.copytree(asset_root, package_dir / 'asset_packages')

"""
    asset_insert="""    asset_root = project / 'artifacts/asset_packages'
    prompt_audit=_prompt_consumption_summary(asset_root)
    if full and asset_root.exists() and prompt_audit.get('status')!='PASS':
        raise RuntimeError('BLOCKED FULL prompt consumption audit failed for assets: ' + ', '.join(prompt_audit.get('missing_assets') or []))
    if asset_root.exists():
        shutil.copytree(asset_root, package_dir / 'asset_packages')

    (package_dir / 'FULL_DELIVERY_DEPTH_AUDIT.json').write_text(
        json.dumps(depth_audit, ensure_ascii=False, indent=2), encoding='utf-8'
    )
    (package_dir / 'PROMPT_CONSUMPTION_AUDIT.json').write_text(
        json.dumps(prompt_audit, ensure_ascii=False, indent=2), encoding='utf-8'
    )

"""
    if "package_dir / 'FULL_DELIVERY_DEPTH_AUDIT.json'" not in text:
        if asset_anchor not in text: raise SystemExit('delivery_export asset anchor not found')
        text=text.replace(asset_anchor,asset_insert,1)

    html_anchor="""    html_text = (package_dir / 'index.html').read_text(encoding='utf-8')
    manifest = {
"""
    html_insert="""    html_text = (package_dir / 'index.html').read_text(encoding='utf-8')
    html_depth=_full_html_depth_check(html_text,full)
    if full and html_depth.get('status')!='PASS':
        raise RuntimeError('BLOCKED FULL HTML visible depth objects missing: ' + ', '.join(html_depth.get('missing') or []))
    manifest = {
"""
    if 'html_depth=_full_html_depth_check' not in text:
        if html_anchor not in text: raise SystemExit('delivery_export html anchor not found')
        text=text.replace(html_anchor,html_insert,1)

    manifest_anchor="""        'human_delivery_contract': 'HUMAN_DELIVERY.json',
        'strategy_authority': 'strategy/MASTER_STRATEGY_CN.md',
"""
    manifest_insert="""        'human_delivery_contract': 'HUMAN_DELIVERY.json',
        'full_delivery_depth_audit': 'FULL_DELIVERY_DEPTH_AUDIT.json',
        'prompt_consumption_audit': 'PROMPT_CONSUMPTION_AUDIT.json',
        'strategy_authority': 'strategy/MASTER_STRATEGY_CN.md',
"""
    if "'full_delivery_depth_audit': 'FULL_DELIVERY_DEPTH_AUDIT.json'" not in text:
        if manifest_anchor not in text: raise SystemExit('delivery_export manifest anchor not found')
        text=text.replace(manifest_anchor,manifest_insert,1)

    workspace_anchor="""            'obsolete_phase_rail_absent': 'asset-production-rail' not in html_text and 'asset-phase' not in html_text,
        },
"""
    workspace_insert="""            'obsolete_phase_rail_absent': 'asset-production-rail' not in html_text and 'asset-phase' not in html_text,
            'full_decision_depth': depth_audit.get('status') if full else 'NOT_REQUIRED_FOR_TASK_SCOPED',
            'full_visible_objects': html_depth.get('status'),
            'prompt_execution_continuity': prompt_audit.get('status') if asset_root.exists() else 'NO_ASSETS',
        },
"""
    if "'full_decision_depth': depth_audit.get('status')" not in text:
        if workspace_anchor not in text: raise SystemExit('delivery_export workspace anchor not found')
        text=text.replace(workspace_anchor,workspace_insert,1)
    return text


def patch_delivery_html(text: str) -> str:
    old="""    for i,(name,body) in enumerate(chunks):
        n=str(name).strip()
        if re.match(r'^1[.、\\s]',n):bucket='overview'
        elif re.match(r'^2[.、\\s]',n):bucket='product'
        elif re.match(r'^3[.、\\s]',n) or re.match(r'^8[.、\\s]',n):bucket='market'
        elif re.match(r'^5[.、\\s]',n):bucket='visual'
        elif re.match(r'^[67][.、\\s]',n):bucket='content'
        elif re.match(r'^9[.、\\s]',n):bucket='risk'
        else:bucket='strategy'
        sub=_split_h3_body(body)
        # Long strategy chapters become task pages. Short chapters remain one page.
        if len(sub)>=2:
            for j,(subname,subbody) in enumerate(sub):
                title=_zh_heading(subname)
                key=f'master-{i}-{j}-{_slug(subname)}'
                out[bucket].append({'key':key,'title':title,'secondary':'','html':markdown_to_html(subbody),'source':str(path.relative_to(package_dir)).replace('\\\\','/')})
        else:
            key=f'master-{i}-{_slug(n)}'
            out[bucket].append({'key':key,'title':_zh_heading(n),'secondary':'','html':markdown_to_html(body),'source':str(path.relative_to(package_dir)).replace('\\\\','/')})
"""
    new="""    for i,(name,body) in enumerate(chunks):
        n=str(name).strip()
        # FULL human headings deliberately have no numeric workflow prefix. Route by semantic domain so
        # the SaaS workspace stays object-based while the nine-domain completion contract remains visible.
        if re.match(r'^1[.、\\s]',n) or '信息完整度' in n:bucket='overview'
        elif re.match(r'^2[.、\\s]',n) or '产品真实事实审计' in n or '产品真相与价值' in n:bucket='product'
        elif re.match(r'^3[.、\\s]',n) or re.match(r'^8[.、\\s]',n) or '平台 × 区域 × 人群 × 族裔文化' in n or '族裔文化适配检查表' in n:bucket='market'
        elif re.match(r'^5[.、\\s]',n) or '视觉总策略与拍摄执行清单' in n:bucket='visual'
        elif re.match(r'^[67][.、\\s]',n) or '分平台内容矩阵表' in n or 'RACE传播框架执行表' in n:bucket='content'
        elif re.match(r'^9[.、\\s]',n) or '合规、文化敏感与风险清单' in n:bucket='risk'
        else:bucket='strategy'
        domain_label=_zh_heading(n)
        sub=_split_h3_body(body)
        # Long chapters become task cards, but the parent decision domain is never discarded.
        if len(sub)>=2:
            for j,(subname,subbody) in enumerate(sub):
                subtitle=_zh_heading(subname)
                key=f'master-{i}-{j}-{_slug(subname)}'
                banner=f'<div class="strategy-domain-label"><span>完整交付域</span><b>{html.escape(domain_label)}</b></div>'
                title=domain_label if j==0 else subtitle
                secondary=subtitle if j==0 else domain_label
                out[bucket].append({'key':key,'title':title,'secondary':secondary,'html':banner+markdown_to_html(subbody),'source':str(path.relative_to(package_dir)).replace('\\\\','/')})
        else:
            key=f'master-{i}-{_slug(n)}'
            out[bucket].append({'key':key,'title':domain_label,'secondary':'','html':markdown_to_html(body),'source':str(path.relative_to(package_dir)).replace('\\\\','/')})
"""
    if old in text:
        return text.replace(old,new,1)
    if 'FULL human headings deliberately have no numeric workflow prefix' in text:
        return text
    raise SystemExit('delivery_html master strategy routing anchor not found')


def patch_skill(text: str) -> str:
    marker="""- 完整任务的完成态必须包含真实人类交付 Artifact（自包含 `index.html` + 可编辑源 + 逐资产包 + `DELIVERY_MANIFEST.json` + ZIP）；源码存在或聊天正文不构成 FULL 完成。

"""
    block=marker+"""### FULL Decision-Depth + Prompt Execution Continuity — highest current precedence
- **本节高于下面所有历史版本说明。** 任何 v0.6.21–v0.6.29 关于“框架可选 / scope 动态”的历史段落，只适用于 TASK_SCOPED；不得覆盖 FULL 的九域深度合同。
- FULL 九域不是标题检查：每个域必须包含会改变商业/创意/生产决策的内容。产品层必须清楚区分 Fact / 真实卖点 / 可感知利益 / 情绪价值 / Claim Boundary / A-B-C 证据；区域与用户层必须回答平台×区域×人群×族裔文化 WHY、交叉性、语言/宗教/节庆/支付/物流/法规与禁忌/刻板印象；视觉层必须给可执行构图、HEX/对比、摄影、灯光、CMF、镜头、人物、平台规格与逐资产参数；内容层必须给平台执行字段、RACE、文化校验、CTA、指标、落地/归因；风险层必须给合规、A/B、P0/P1/P2、取舍、下一步与输出自检。
- **深度不等于字数。** 允许删除重复解释、内部 ID、RACE/KPI 元数据和与当前资产无关的摄影 toolbox；禁止删除已有证据边界、区域/用户洞察、策略 WHY/取舍、生产参数或人类可执行动作。
- Canonical Prompt 使用 **Semantic Compression, never Capability Compression**：凡已经选定且会改变像素、摄影、合成或确定性后期的参数，必须进入 Prompt 或明确的 deterministic production instruction。每个激活资产必须输出 `prompt_consumption_audit`，`missing_decisions` 必须为空后才可完成。
- 人物/手部/身体关系一旦进入资产，包容性摄影即为 P0：肤色测光、深肤色暗部保护、按 Prelight 决定的曝光补偿、neutral/white reflector 或 bounce、large soft diffusion、真实发质、体型/年龄/残障自然呈现和 AI 偏见控制必须变成执行语言；不能只留在总策划。
- FULL 最终导出必须重新运行当前 `delivery_contract.validate_strategy_delivery()`，并把 `FULL_DELIVERY_DEPTH_AUDIT.json`、`PROMPT_CONSUMPTION_AUDIT.json` 写入交付包。`index.html` 必须直接可见九域核心对象；宿主自写的一套更短报告不能替代它。

"""
    if '### FULL Decision-Depth + Prompt Execution Continuity — highest current precedence' in text:
        return text
    if marker not in text: raise SystemExit('SKILL current precedence marker not found')
    return text.replace(marker,block,1)


patch('runtime/cbcc/asset_compiler.py',patch_asset_compiler)
patch('runtime/cbcc/delivery_export.py',patch_delivery_export)
patch('runtime/cbcc/delivery_html.py',patch_delivery_html)
patch('SKILL.md',patch_skill)
