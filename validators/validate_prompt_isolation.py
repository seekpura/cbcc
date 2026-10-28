#!/usr/bin/env python3
import sys,re,json
text=open(sys.argv[1],encoding='utf-8').read()
patterns={
 'workflow_state':r'\b(TRUTH_READY|STRATEGY_READY|LISTING_READY|ASSET_MAP_READY|COMPILED)\b',
 'qa_serialization':r'(?i)\bQA_REPORT\b|\bSELF-CHECK\b',
 'internal_source_ids':r'\b(?:SRC|CLM|REQ)-[A-Z0-9_-]+\b',
 'version_chatter':r'(?i)\bversion\s*[:=]\s*v?\d'
}
hits={k:re.findall(v,text) for k,v in patterns.items() if re.search(v,text)}
print(json.dumps({'pass':not hits,'hits':hits},ensure_ascii=False,indent=2)); sys.exit(1 if hits else 0)
