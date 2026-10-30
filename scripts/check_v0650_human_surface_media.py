#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html as htmlmod
import json
import re
from pathlib import Path

CJK = re.compile(r'[\u3400-\u9fff]')
PROSE = re.compile(r'[A-Za-z]{3,}(?:[\s/+\-–—,:;().%0-9]+[A-Za-z]{2,}){3,}')
HUMAN_KEYS = {
    'barcode_status','packaging','source_authority','tradeoff','fact','effect','primary','secondary',
    'gender','income','geography','language','culture','implication','guard','execution','objective','actions',
    'outputs','decision','creative_thesis','composition','material','light_master','camera_master','fidelity',
    'human_inclusion','why','metric','camera','light','production_notes'
}


def has_cn(value) -> bool:
    return bool(CJK.search(str(value)))


def english_prose(value) -> bool:
    s = str(value).strip()
    return len(s) >= 28 and not has_cn(s) and bool(PROSE.search(s))


def companion(obj: dict, key: str) -> bool:
    for candidate in (
        key + '_cn', key.replace('_en', '_cn'), 'cn', 'zh', 'zh_cn',
        'translation_cn', 'meaning_cn', 'chinese_explanation'
    ):
        if candidate in obj and has_cn(obj[candidate]):
            return True
    return False


def walk(obj, path=()):
    issues = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            current = path + (str(key),)
            if isinstance(value, str) and key in HUMAN_KEYS and english_prose(value) and not companion(obj, key):
                issues.append({
                    'code': 'HUMAN_OPERATOR_FIELD_NOT_CHINESE_FIRST',
                    'path': '.'.join(current),
                    'sample': value[:180],
                })
            elif isinstance(value, (dict, list)):
                issues.extend(walk(value, current))
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            issues.extend(walk(value, path + (str(index),)))
    return issues


def audit_package(root: Path) -> dict:
    html_path = root / 'index.html'
    if not html_path.exists():
        return {'status': 'FAIL', 'issue_count': 1, 'issues': [{'code': 'INDEX_MISSING'}]}

    text = html_path.read_text(encoding='utf-8', errors='replace')
    issues = []
    embedded_data = None
    match = re.search(r'<script id=["\']data["\'][^>]*>(.*?)</script>', text, re.S | re.I)
    if match:
        try:
            embedded_data = json.loads(htmlmod.unescape(match.group(1)))
            issues.extend(walk(embedded_data))
        except Exception as exc:
            issues.append({'code': 'EMBEDDED_DATA_PARSE_FAILED', 'detail': str(exc)})

    for tag in re.finditer(r'<(?:img|video|source)\b([^>]*)>', text, re.I):
        attrs = tag.group(1)
        src_match = re.search(r'\b(?:src|poster)=["\']([^"\']+)["\']', attrs, re.I)
        if not src_match:
            continue
        src = src_match.group(1)
        if src.startswith(('data:', 'blob:', 'http://', 'https://')):
            continue
        fallback = re.search(r'(?:data-fallback-src|data-inline-src)=["\']data:', attrs, re.I)
        if not fallback:
            issues.append({'code': 'LOCAL_MEDIA_NOT_STANDALONE_SAFE', 'src': src})

    for phrase in ('<h2>Message Hierarchy</h2>', '<h1>Asset Universe</h1>'):
        if phrase in text:
            issues.append({'code': 'ENGLISH_ONLY_OPERATOR_HEADING', 'sample': phrase})

    if isinstance(embedded_data, dict):
        for asset in embedded_data.get('assets', []):
            prompt_en = str(asset.get('prompt_en', ''))
            if prompt_en and has_cn(prompt_en):
                issues.append({
                    'code': 'MODEL_PROMPT_EN_CONTAINS_CHINESE_EXECUTION_PROSE',
                    'asset': asset.get('id'),
                })

    return {
        'status': 'PASS' if not issues else 'FAIL',
        'issue_count': len(issues),
        'issues': issues,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Audit rendered human language and standalone HTML media portability.')
    parser.add_argument('package_dir')
    parser.add_argument('--output')
    args = parser.parse_args()
    report = audit_package(Path(args.package_dir))
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(payload + '\n', encoding='utf-8')
    print(payload)
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
