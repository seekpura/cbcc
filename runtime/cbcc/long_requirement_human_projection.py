from __future__ import annotations

import json
from typing import Any, Callable


def _fmt(value: Any) -> str:
    if value in (None, '', [], {}):
        return '—'
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def _table(headers: list[str], rows: list[dict[str, Any]]) -> str:
    if not rows:
        return '（当前无数据）'
    head = '| ' + ' | '.join(headers) + ' |\n'
    sep = '| ' + ' | '.join('---' for _ in headers) + ' |\n'
    body = []
    for row in rows:
        vals = []
        for key in headers:
            text = _fmt(row.get(key)).replace('\n', '<br>').replace('|', '\\|')
            vals.append(text)
        body.append('| ' + ' | '.join(vals) + ' |')
    return head + sep + '\n'.join(body)


def _insert_before(md: str, heading: str, block: str) -> str:
    marker = '\n' + heading
    if marker in md:
        return md.replace(marker, '\n' + block.rstrip() + '\n\n' + heading, 1)
    return md.rstrip() + '\n\n' + block.rstrip() + '\n'


def wrap_render_master_strategy_cn(fn: Callable[[dict[str, Any]], str]):
    def rendered(strategy: dict[str, Any]) -> str:
        md = fn(strategy)
        sections = strategy.get('sections') or {}

        info = sections.get('01_information_completeness_assumptions_decisions') or {}
        context_rows = []
        for i, row in enumerate(info.get('decision_log') or []):
            context = row.get('context_why') or {}
            context_rows.append({
                'decision': row.get('what') or f'DECISION-{i+1}',
                'platform': context.get('platform'),
                'region': context.get('region'),
                'audience': context.get('audience'),
                'race_ethnicity_culture': context.get('race_ethnicity_culture'),
            })
        if context_rows:
            block = '\n'.join([
                '### 1.x 平台 × 区域 × 人群 × 族裔文化 WHY',
                _table(['decision', 'platform', 'region', 'audience', 'race_ethnicity_culture'], context_rows),
                f"- 待确认问题：{len(info.get('pending_confirmations') or [])}/{info.get('question_limit') or 10}；完整待确认总数：{info.get('pending_confirmation_total_count', len(info.get('pending_confirmations') or []))}。",
                f"- 继续规则：{_fmt(info.get('continuation_rule'))}",
            ])
            md = _insert_before(md, '## 2.', block)

        content_rows = []
        for row in sections.get('06_platform_content_matrix') or []:
            content_rows.append({
                'platform': row.get('platform'),
                'site': row.get('site'),
                'asset_id': row.get('asset_id'),
                'platform_dimensions': row.get('platform_dimensions'),
                'duration': row.get('duration'),
                'cover_first_frame': row.get('cover_first_frame'),
                'subtitle_strategy': row.get('subtitle_strategy'),
                'music_rights': row.get('music_rights'),
                'traffic_mechanism': row.get('traffic_mechanism'),
                'cta': row.get('cta'),
                'landing_handoff': row.get('landing_handoff'),
                'utm_attribution': row.get('utm_attribution'),
                'race_stage': row.get('race_stage'),
                'culture_adaptation': row.get('culture_adaptation'),
                'taboo_stereotype_check': row.get('taboo_stereotype_check'),
                'why': row.get('why'),
            })
        if content_rows:
            block = '\n'.join([
                '### 6.x 平台执行 / 本地化 / 归因',
                _table([
                    'platform', 'site', 'asset_id', 'platform_dimensions', 'duration', 'cover_first_frame',
                    'subtitle_strategy', 'music_rights', 'traffic_mechanism', 'cta', 'landing_handoff',
                    'utm_attribution', 'race_stage', 'culture_adaptation', 'taboo_stereotype_check', 'why'
                ], content_rows),
            ])
            md = _insert_before(md, '## 7.', block)

        culture_rows = []
        for row in sections.get('08_culture_adaptation_checklist') or []:
            culture_rows.append({
                '文化适配点': row.get('adaptation_point'),
                '依据或假设': row.get('evidence_or_assumption'),
                '包容性表征': row.get('inclusive_representation'),
                '刻板印象与禁忌': row.get('stereotype_taboo_risk'),
                '脚本校验': row.get('script_check'),
                '模特校验': row.get('casting_check'),
                '服化道校验': row.get('wardrobe_grooming_check'),
                '配色校验': row.get('color_check'),
                'CTA校验': row.get('cta_check'),
                '校验结果': row.get('result'),
                '修改动作': row.get('modification'),
                'WHY': row.get('why'),
            })
        if culture_rows:
            block = '\n'.join([
                '### 8.x 族裔文化逐项执行校验',
                _table([
                    '文化适配点', '依据或假设', '包容性表征', '刻板印象与禁忌', '脚本校验', '模特校验',
                    '服化道校验', '配色校验', 'CTA校验', '校验结果', '修改动作', 'WHY'
                ], culture_rows),
            ])
            md = _insert_before(md, '## 9.', block)

        last = sections.get('09_risk_measurement_priority_next_steps') or {}
        p0 = last.get('p0_compliance_claim_checklist') or []
        if p0:
            block = '\n'.join([
                '### 9.x P0 合规 / 宣称证据检查',
                _table(['check_area', 'priority', 'status', 'evidence_refs', 'publication_rule', 'action', 'why'], p0),
            ])
            # Insert before the runtime authority appendix if present; otherwise append.
            md = _insert_before(md, '## 策略推理权威', block)

        return md
    return rendered
