#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, html as htmlmod
from pathlib import Path

CJK = re.compile(r'[\u3400-\u9fff]')
PROSE = re.compile(r'[A-Za-z]{3,}(?:[\s/+,\-–—:;().%0-9]+[A-Za-z]{2,}){2,}')

TARGET_FOREIGN_KEYS = {
    'title_en','title_bm','description_en','description_bm','usage_en','usage_bm',
    'warnings_en','warnings_bm','search_terms_en','search_terms_bm','copy_en','copy_bm',
    'name_en','name_bm','product_name_bm','prompt_en'
}
TECH_KEYS = {
    'id','url','path','sha256','checked','inci','source','source_id','barcode','gtin',
    'platform','market','sku','family','deployment','surface','carrier','presence',
    'subject','copy_mode','fidelity','output','grade','class','publish','status','type'
}
TECH_SUFFIXES = ('_id','_url','_path','_sha256')
OPERATOR_ROOTS = {
    'product','strategy','market','intersectionality','claims','visual_master',
    'content_matrix','race','culture','assets','economics','listing'
}

def has_cn(v):
    return bool(CJK.search(str(v)))

def prose(v):
    s = str(v).strip()
    return len(s) >= 18 and bool(PROSE.search(s))

def cn_sibling(obj, key):
    if not isinstance(obj, dict):
        return False
    candidates = [
        key + '_cn', key.replace('_en', '_cn'), key.replace('_bm', '_cn'),
        'cn','zh','zh_cn','translation_cn','meaning_cn','use_cn'
    ]
    return any(k in obj and has_cn(obj[k]) for k in candidates)

def target_foreign_companion(obj, key):
    if key == 'prompt_en':
        return isinstance(obj, dict) and isinstance(obj.get('prompt_cn'), str) and has_cn(obj.get('prompt_cn'))
    return cn_sibling(obj, key)

def is_technical(key):
    return key in TECH_KEYS or key.endswith(TECH_SUFFIXES)

def walk(obj, path=(), root_name=None):
    issues = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = path + (str(k),)
            r = root_name or (str(k) if not path else path[0])
            if isinstance(v, str):
                s = v.strip()
                if k in TARGET_FOREIGN_KEYS:
                    if prose(s) and not target_foreign_companion(obj, k):
                        issues.append({'code':'FOREIGN_FIRST_ITEM_MISSING_CHINESE_COMPANION','path':'.'.join(p),'sample':s[:180]})
                    if k == 'prompt_en' and has_cn(s):
                        issues.append({'code':'MODEL_PROMPT_EN_CONTAINS_CHINESE_EXECUTION_PROSE','path':'.'.join(p)})
                elif r in OPERATOR_ROOTS and not is_technical(k):
                    if prose(s) and not has_cn(s) and not cn_sibling(obj, k):
                        issues.append({'code':'OPERATOR_BUSINESS_PROSE_NOT_CHINESE_CANONICAL','path':'.'.join(p),'sample':s[:180]})
            elif isinstance(v, (dict, list)):
                issues.extend(walk(v, p, r))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            issues.extend(walk(v, path + (str(i),), root_name))
    return issues

def audit(root: Path):
    hp = root / 'index.html'
    issues = []
    if not hp.exists():
        return {'status':'FAIL','issue_count':1,'issues':[{'code':'INDEX_MISSING'}]}
    text = hp.read_text(encoding='utf-8', errors='replace')
    m = re.search(r'<script id=["\']data["\'][^>]*>(.*?)</script>', text, re.S | re.I)
    if m:
        try:
            data = json.loads(htmlmod.unescape(m.group(1)))
            issues.extend(walk(data))
        except Exception as e:
            issues.append({'code':'EMBEDDED_DATA_PARSE_FAILED','detail':str(e)})
    else:
        issues.append({'code':'EMBEDDED_DATA_MISSING_FOR_AUDIT'})

    for tag in re.finditer(r'<(?:img|video|audio|source)\b([^>]*)>', text, re.I):
        attrs = tag.group(1)
        sm = re.search(r'\b(?:src|poster)=["\']([^"\']+)["\']', attrs, re.I)
        if not sm:
            continue
        src = sm.group(1)
        if src.startswith(('data:','blob:','http://','https://')):
            continue
        if not re.search(r'(?:data-fallback-src|data-inline-src)=["\']data:', attrs, re.I):
            issues.append({'code':'LOCAL_MEDIA_NOT_STANDALONE_SAFE','src':src})

    for hm in re.finditer(r'<h[1-4][^>]*>(.*?)</h[1-4]>', text, re.S | re.I):
        raw = re.sub(r'<[^>]+>', ' ', hm.group(1))
        raw = htmlmod.unescape(raw).strip()
        if prose(raw) and not has_cn(raw):
            if raw not in {'Listing','RACE','Product Truth','Asset Universe','Model Prompt EN','Model Prompt CN'}:
                issues.append({'code':'ENGLISH_ONLY_OPERATOR_HEADING','sample':raw[:180]})

    uniq = []
    seen = set()
    for x in issues:
        key = json.dumps(x, ensure_ascii=False, sort_keys=True)
        if key not in seen:
            seen.add(key)
            uniq.append(x)
    return {'status':'PASS' if not uniq else 'FAIL','issue_count':len(uniq),'issues':uniq}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('package_dir')
    ap.add_argument('--output')
    args = ap.parse_args()
    r = audit(Path(args.package_dir))
    s = json.dumps(r, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(s + '\n', encoding='utf-8')
    print(s)
    raise SystemExit(0 if r['status'] == 'PASS' else 1)

if __name__ == '__main__':
    main()
