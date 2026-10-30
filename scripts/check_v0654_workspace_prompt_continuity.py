#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path


def audit(package_dir: Path) -> dict:
    package_dir = Path(package_dir)
    index = package_dir / 'index.html'
    issues=[]
    if not index.exists():
        return {'status':'FAIL','issue_count':1,'issues':[{'code':'INDEX_MISSING','detail':'index.html missing'}]}
    text=index.read_text('utf-8',errors='replace')
    asset_root=package_dir/'asset_packages'
    prompt_assets=[]
    all_assets=[]
    if asset_root.exists():
        for d in sorted(asset_root.iterdir()):
            if not d.is_dir():
                continue
            all_assets.append(d.name)
            if (d/'05_prompt_CN.txt').exists() or (d/'06_prompt_EN.txt').exists():
                prompt_assets.append(d.name)

    current_shell='data-workspace-shell="cbcc-commercial-v1"' in text
    legacy_routed=(
        'hashchange' in text and 'location.hash' in text and
        ('asset/' in text or 'data-route="asset/' in text) and
        ('id="main"' in text or 'class="workspace"' in text)
    )
    if not (current_shell or legacy_routed):
        issues.append({'code':'MATURE_ROUTED_WORKSPACE_LOST','detail':'Human HTML no longer matches cbcc-commercial-v1 or the mature routed interaction floor.'})

    if all_assets:
        missing_routes=[aid for aid in all_assets if f'asset/{aid}' not in text]
        if missing_routes:
            issues.append({'code':'ASSET_DETAIL_ROUTES_MISSING','detail':missing_routes})

    if prompt_assets:
        cn_projected=('Model Prompt CN' in text) or ('prompt_cn' in text) or ('中文模型提示词' in text) or ('中文规范生产提示词' in text)
        en_projected=('Model Prompt EN' in text) or ('prompt_en' in text) or ('英文模型提示词' in text) or ('英文 / 生成模型执行提示词' in text)
        if not cn_projected:
            issues.append({'code':'PROMPT_CN_NOT_PROJECTED_TO_HUMAN_HTML','detail':f'{len(prompt_assets)} assets contain 05_prompt_CN.txt but Human HTML exposes no CN prompt surface.'})
        if not en_projected:
            issues.append({'code':'PROMPT_EN_NOT_PROJECTED_TO_HUMAN_HTML','detail':f'{len(prompt_assets)} assets contain 06_prompt_EN.txt but Human HTML exposes no EN prompt surface.'})
        dedicated_prompt_surface=('data-route="prompts"' in text) or ('提示词工作台' in text) or ('Prompt Lab' in text) or ('prompt-lab' in text)
        per_asset_prompt_access=('asset/' in text) and cn_projected and en_projected
        if not (dedicated_prompt_surface or per_asset_prompt_access):
            issues.append({'code':'PROMPT_INTERACTIVE_SURFACE_MISSING','detail':'Prompt files exist but no dedicated prompt workspace or per-asset prompt lens is exposed.'})

    numbered_hits=sum(1 for s in ['01 信息完整度','02 产品事实审计','03 平台 × 区域 × 人群 × 族裔文化','04 营销框架与核心策略','05 视觉总策略','06 分平台内容矩阵','07 RACE','08 族裔文化','09 合规'] if s in text)
    if numbered_hits >= 6 and not current_shell and not ('asset/' in text):
        issues.append({'code':'FIXED_NINE_SECTION_REPLACEMENT_SHELL','detail':'Detected a numbered hard-rule report shell replacing the mature project-authored workspace.'})

    return {
        'status':'PASS' if not issues else 'FAIL',
        'issue_count':len(issues),
        'asset_count':len(all_assets),
        'prompt_asset_count':len(prompt_assets),
        'workspace_signature':'cbcc-commercial-v1' if current_shell else ('legacy-mature-routed' if legacy_routed else 'unknown/replaced'),
        'issues':issues,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('package_dir')
    ap.add_argument('--json-out')
    ns=ap.parse_args()
    result=audit(Path(ns.package_dir))
    out=json.dumps(result,ensure_ascii=False,indent=2)
    print(out)
    if ns.json_out:
        Path(ns.json_out).write_text(out+'\n',encoding='utf-8')
    raise SystemExit(0 if result['status']=='PASS' else 1)


if __name__=='__main__':
    main()
