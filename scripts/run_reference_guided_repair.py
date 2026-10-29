from pathlib import Path

patch = Path('scripts/repair_reference_guided_assets_and_capability_continuity.py')
s = patch.read_text(encoding='utf-8')
bad = '''replace_once(
    'runtime/cbcc/prompt_compiler.py',
    "        'principle':'Semantic compression may remove repetition and irrelevant toolbox fields, but never an already-selected pixel/capture/composite-affecting execution decision.',\\n",
    "        'principle':'Prompt readiness is a production-quality diagnostic, not a project-completion gate. When prompts are requested, preserve the selected execution decisions that actually matter to that production route.',\\n",
)
'''
if bad not in s:
    raise SystemExit('expected brittle principle patch block not found')
s = s.replace(bad, '', 1)
# Apply the same semantic change against the actual compact return line after the main patch runs.
exec(compile(s, str(patch), 'exec'), {'__name__': '__main__'})

p = Path('runtime/cbcc/prompt_compiler.py')
text = p.read_text(encoding='utf-8')
old = "'principle':'Semantic compression may remove repetition and irrelevant toolbox fields, but never an already-selected pixel/capture/composite-affecting execution decision.'"
new = "'principle':'Prompt readiness is a production-quality diagnostic, not a project-completion gate. When prompts are requested, preserve the selected execution decisions that actually matter to that production route.'"
if old not in text:
    raise SystemExit('actual compact prompt audit principle anchor missing')
p.write_text(text.replace(old, new, 1), encoding='utf-8')
print('resilient repair applied')
