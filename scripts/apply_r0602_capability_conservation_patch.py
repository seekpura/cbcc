from pathlib import Path

PATH = Path('runtime/cbcc/compiler.py')

CULTURE_OLD = "_capability_row('CULTURE_INTERSECTIONALITY',bool(request.get('audience_culture')),culture.get('status','NOT_SUPPLIED'),['Strategy §3/8','Casting/visual/copy implications'],True),"
CULTURE_NEW = "_capability_row('CULTURE_INTERSECTIONALITY',culture.get('status') not in {None,'NOT_SUPPLIED','NO_CULTURE_INPUT'},culture.get('status','NOT_SUPPLIED'),['Strategy §3/8','Casting/visual/copy implications'],True),"
POSITIONING_OLD = "_capability_row('POSITIONING_MESSAGE',True,'COMPILED',['Strategy §4 Positioning/Message','Listing Strategy','Platform Content Matrix','Asset Portfolio'],bool(core.get('positioning'))),"
POSITIONING_NEW = "_capability_row('POSITIONING_MESSAGE',True,'COMPILED',['Strategy §4 Positioning/Message','Per-asset 01_strategy.md / 11_strategy_authority_trace when assets are compiled'],bool(core.get('positioning'))),"

text = PATH.read_text(encoding='utf-8')

if CULTURE_OLD in text:
    if text.count(CULTURE_OLD) != 1:
        raise SystemExit('culture target is not unique')
    text = text.replace(CULTURE_OLD, CULTURE_NEW, 1)
elif CULTURE_NEW not in text:
    raise SystemExit('culture target not found in old or repaired form')

if text.count(POSITIONING_OLD) != 1:
    raise SystemExit(f'expected exactly one positioning target, found {text.count(POSITIONING_OLD)}')
text = text.replace(POSITIONING_OLD, POSITIONING_NEW, 1)

PATH.write_text(text, encoding='utf-8')
print('patched', PATH)
