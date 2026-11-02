from pathlib import Path

PATH = Path('runtime/cbcc/compiler.py')
OLD = "_capability_row('CULTURE_INTERSECTIONALITY',bool(request.get('audience_culture')),culture.get('status','NOT_SUPPLIED'),['Strategy §3/8','Casting/visual/copy implications'],True),"
NEW = "_capability_row('CULTURE_INTERSECTIONALITY',culture.get('status') not in {None,'NOT_SUPPLIED','NO_CULTURE_INPUT'},culture.get('status','NOT_SUPPLIED'),['Strategy §3/8','Casting/visual/copy implications'],True),"

text = PATH.read_text(encoding='utf-8')
count = text.count(OLD)
if count != 1:
    raise SystemExit(f'expected exactly one target line, found {count}')
PATH.write_text(text.replace(OLD, NEW, 1), encoding='utf-8')
print('patched', PATH)
