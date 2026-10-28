from pathlib import Path
import runpy
import re

# Reuse the staged Strategy override. It intentionally stops at the older asset-return matcher;
# current Asset Architecture is patched below against its actual structure.
try:
    runpy.run_path('.changes/v0624_patch_runner.py', run_name='__main__')
except SystemExit as exc:
    if 'asset architecture return block not found' not in str(exc):
        raise

# The appended Strategy override uses regex for framework parsing and human projection pruning.
p=Path('runtime/cbcc/strategy_depth.py')
s=p.read_text(encoding='utf-8')
if 'import re\n' not in s[:300]:
    s=s.replace('import json\n','import json\nimport re\n',1)
p.write_text(s,encoding='utf-8')

# Patch the current v0.6.23 Asset Architecture without changing the existing decision-audit shape.
p=Path('runtime/cbcc/asset_architecture.py')
s=p.read_text(encoding='utf-8')
s=s.replace(
    "    jobs=list(asset_jobs or [])\n    if not jobs:\n",
    "    jobs=list(asset_jobs or [])\n    asset_scope_active=bool(jobs)\n    if not jobs:\n",
    1,
)
s=s.replace(
    "        if requested_candidates: candidates=requested_candidates\n        qrows=_context_questions(questions,decision_context,category_family)\n",
    "        if requested_candidates: candidates=requested_candidates\n        asset_scope_active=bool(candidates)\n        qrows=_context_questions(questions,decision_context,category_family)\n",
    1,
)
pattern=re.compile(r"            if not candidates:\n                jobs\.append\(\{'consumer_question':q,'surface':'GALLERY','family':'VISUAL'.*?\}\)\n                continue\n",re.S)
s,n=pattern.subn(
    "            if not candidates:\n                # No current visual/video/creator/paid Surface: keep the question in Strategy/Listing; do not manufacture a GALLERY asset.\n                continue\n",
    s,
    count=1,
)
if n!=1:
    raise SystemExit(f'expected one no-candidate asset fallback, replaced {n}')
s=s.replace(
    "    for i,a in enumerate(assets[:-1]):\n        if not a.get('handoff'): a['handoff']=assets[i+1]['asset_id']\n\n",
    "    # List order is presentation only. Asset relationships/handoffs are explicit author decisions.\n\n",
    1,
)
s=s.replace(
    "    uncovered=[x for x in decision_audit if x['coverage_status']=='UNCOVERED']\n    return {\n",
    "    uncovered=[x for x in decision_audit if x['coverage_status']=='UNCOVERED']\n    unrouted_questions=[]\n    if not asset_scope_active:\n        unrouted_questions=[{'question':x.get('question'),'origin':x.get('origin'),'decision_intent':x.get('decision_intent')} for x in _context_questions(questions,decision_context,category_family)]\n    explicit_handoff_count=sum(1 for a in assets if a.get('handoff'))\n    return {\n",
    1,
)
s=s.replace(
    "        'decision_coverage_summary':{\n            'source_shopper_questions':",
    "        'decision_coverage_summary':{\n            'status':'COVERAGE_COMPILED' if asset_scope_active else 'NO_ASSET_SURFACE_IN_CURRENT_SCOPE',\n            'source_shopper_questions':",
    1,
)
s=s.replace(
    "        'category_family':category_family,\n        'curation_basis':",
    "        'asset_scope_active':asset_scope_active,\n        'unrouted_questions':unrouted_questions,\n        'relationship_mode':'EXPLICIT_ONLY',\n        'explicit_handoff_count':explicit_handoff_count,\n        'auto_sequence_authority':False,\n        'category_family':category_family,\n        'curation_basis':",
    1,
)
p.write_text(s,encoding='utf-8')

# Runtime version.
p=Path('runtime/cbcc/compiler.py')
s=p.read_text(encoding='utf-8')
s=s.replace("st.data['runtime_version']='0.6.23-task-scoped-delivery'","st.data['runtime_version']='0.6.24-task-scoped-strategy-asset'",1)
p.write_text(s,encoding='utf-8')

print('v0.6.24 current-tree patch applied')
