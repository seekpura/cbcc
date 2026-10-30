#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REQUIRED_PACKAGE_CORE = {
    '00_asset_manifest.yaml',
    '00_HUMAN_DESIGN_CARD_CN.md',
    '01_strategy.md',
    '02_visual_spec.md',
    '03_photography_contract.json',
    '04_layout_contract.json',
    '08_copy.md',
    '09_production_notes.md',
    '10_source_trace.md',
    '11_strategy_authority_trace.json',
    '12_design_card.json',
    '14_visible_copy_block.json',
    '15_production_assembly_notes.json',
}


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return {}


def audit_full_requirement_continuity(root: Path) -> dict:
    root = Path(root)
    issues: list[dict] = []

    def add(code: str, **data) -> None:
        issues.append({'code': code, **data})

    project_path = root / 'data' / 'project.json'
    project = _load_json(project_path) if project_path.exists() else {}
    assets = project.get('assets') if isinstance(project.get('assets'), list) else []

    # Mature materialization path versus Host-authored shortcut.
    shortcut_root = root / 'assets'
    mature_root = root / 'asset_packages'
    if shortcut_root.exists() and not mature_root.exists():
        add('HOST_SHORTCUT_ASSET_DIRECTORY', path='assets/', expected='asset_packages/')

    selected_root = mature_root if mature_root.exists() else shortcut_root
    asset_dirs = [p for p in selected_root.iterdir() if p.is_dir()] if selected_root.exists() else []
    incomplete = []
    for asset_dir in asset_dirs:
        files = {p.name for p in asset_dir.iterdir() if p.is_file()}
        missing = sorted(REQUIRED_PACKAGE_CORE - files)
        if missing:
            incomplete.append({'asset': asset_dir.name, 'file_count': len(files), 'missing_core': missing})
    if incomplete:
        add('MATURE_ASSET_PACKAGE_INCOMPLETE', affected=len(incomplete), examples=incomplete[:3])

    # Structured per-asset authority must exist before Prompt compilation.
    if assets:
        no_art = [
            a.get('id') or a.get('asset_id')
            for a in assets
            if not isinstance(a.get('asset_art_direction'), dict) or not a.get('asset_art_direction')
        ]
        if no_art:
            add('STRUCTURED_ASSET_ART_DIRECTION_MISSING', affected=len(no_art), assets=no_art)

        structured_presence = []
        visible_presence = []
        for asset in assets:
            presence = asset.get('product_presence')
            if isinstance(presence, dict) and presence.get('planning_state') and presence.get('presence_why'):
                structured_presence.append(asset)
            raw = str(asset.get('presence') or asset.get('product_presence') or '').strip()
            if raw and not re.search(r'ABSENT|FORBIDDEN|NOT_NEEDED|无商品|不出现商品', raw, re.I):
                visible_presence.append(asset)
        if len(structured_presence) < len(assets):
            add('PRODUCT_PRESENCE_DECISION_NOT_STRUCTURED', structured=len(structured_presence), total=len(assets))
        if len(visible_presence) == len(assets):
            add('PRODUCT_EVERYWHERE_PORTFOLIO', total=len(assets))

        if not any(k in project for k in ('asset_opportunity_universe', 'asset_universe_audit', 'family_coverage', 'opportunity_sweep')):
            add('ASSET_OPPORTUNITY_SWEEP_MISSING')

    # Global production-route regressions.
    visual = project.get('visual') if isinstance(project.get('visual'), dict) else {}
    fidelity = str(visual.get('fidelity') or '')
    if re.search(r'后期合成|只负责背景|exact composite|post.?composite|real source crop', fidelity, re.I):
        add('GLOBAL_POST_COMPOSITE_POLICY', value=fidelity)

    # Detect portfolio-wide no-text / no-product renderer patterns. This is intentionally
    # threshold-based: a few assets may professionally choose these routes.
    prompt_files = list(root.glob('**/05_prompt_CN.txt')) + list(root.glob('**/06_prompt_EN.txt'))
    asset_prompts: dict[str, str] = {}
    for path in prompt_files:
        asset_prompts.setdefault(path.parent.name, '')
        asset_prompts[path.parent.name] += path.read_text(encoding='utf-8', errors='ignore') + '\n'

    no_text, no_product = [], []
    for asset_id, text in asset_prompts.items():
        if re.search(r'不生成[^。\n]{0,40}(?:文字|数字)|不要生成[^。\n]{0,40}(?:文字|数字)|do not generate[^.\n]{0,50}(?:text|numbers)', text, re.I):
            no_text.append(asset_id)
        if re.search(r'不生成[^。\n]{0,40}(?:商品|产品)|不要生成[^。\n]{0,40}(?:商品|产品)|do not generate[^.\n]{0,50}(?:product)', text, re.I):
            no_product.append(asset_id)

    if asset_prompts and len(no_text) >= max(3, int(len(asset_prompts) * 0.6)):
        add('GLOBAL_NO_VISIBLE_COPY_PATTERN', affected=len(no_text), total=len(asset_prompts), assets=sorted(no_text))
    if asset_prompts and len(no_product) >= max(3, int(len(asset_prompts) * 0.4)):
        add('GLOBAL_NO_PRODUCT_GENERATION_PATTERN', affected=len(no_product), total=len(asset_prompts), assets=sorted(no_product))

    # Prompt files do not equal produced assets. Real production/review evidence must exist
    # before FULL production completion can be claimed.
    generated_ext = {'.png', '.jpg', '.jpeg', '.webp', '.mp4', '.mov', '.webm'}
    generated_outputs = [
        p for p in root.rglob('*')
        if p.is_file() and p.suffix.lower() in generated_ext and 'sources' not in p.parts
    ]
    if not generated_outputs:
        add('ACTUAL_GENERATED_OUTPUT_MISSING')

    paths = [p for p in root.rglob('*') if p.is_file()]
    if not any('provider' in p.name.lower() and 'result' in p.name.lower() for p in paths):
        add('PROVIDER_RESULT_MISSING')
    if not any('review' in p.name.lower() for p in paths):
        add('ACTUAL_OUTPUT_REVIEW_MISSING')
    if not any('revision' in p.name.lower() for p in paths):
        add('LOCAL_REVISION_LINEAGE_MISSING')

    # FULL project truth/decision bookkeeping.
    if not any(k in project for k in ('information_completeness', 'assumptions', 'decision_log', 'unknowns')):
        add('INFORMATION_ASSUMPTION_DECISION_LOG_MISSING')

    # Market-price evidence must not become a product-price recommendation while unit economics are missing.
    pricing = project.get('pricing') if isinstance(project.get('pricing'), dict) else {}
    if pricing and re.search(r'MISSING_INPUT|UNKNOWN', str(pricing.get('economics') or ''), re.I) and pricing.get('recommended_test'):
        add('PRICING_RECOMMENDATION_AHEAD_OF_ECONOMICS', recommended_test=pricing.get('recommended_test'))

    # Mature route mechanics are not enough if the information architecture has regressed
    # into a permanent capability taxonomy or if the full Art Direction is hidden.
    html_path = root / 'index.html'
    if html_path.exists():
        page = html_path.read_text(encoding='utf-8', errors='ignore')
        fixed_labels = ['产品事实', '马来市场', '成交策略', '上架文案', '视觉系统', '资产宇宙', '合规证据', '研究来源']
        hits = [label for label in fixed_labels if label in page]
        if len(hits) >= 7:
            add('FIXED_CAPABILITY_MENU_SHELL', hits=len(hits), labels=hits)
        if 'asset_art_direction' not in page and '完整逐资产 Art Direction' not in page:
            add('FULL_ART_DIRECTION_NOT_PROJECTED_TO_HTML')

    return {
        'status': 'PASS' if not issues else 'FAIL',
        'issue_count': len(issues),
        'issues': issues,
        'asset_count': len(assets),
        'prompt_asset_count': len(asset_prompts),
        'principle': 'Rules without consumed real-output evidence are intent, not FULL completion.',
    }


def main() -> int:
    if len(sys.argv) < 2:
        print('usage: check_full_requirement_continuity.py <FULL_PACKAGE_DIR>', file=sys.stderr)
        return 2
    result = audit_full_requirement_continuity(Path(sys.argv[1]))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
