from pathlib import Path

path = Path('scripts/check_current_release_package.py')
text = path.read_text(encoding='utf-8')

anchor = "STRICT_REQUIREMENT_CHECKER = 'scripts/check_v0664_requirement_consumer_map.py'\n"
constants = """STRICT_REQUIREMENT_CHECKER = 'scripts/check_v0664_requirement_consumer_map.py'
LOCKED_REQUIREMENT_RANGE = 'REQ-061..REQ-090'
CURRENT_LEDGER_RANGE = 'REQ-001..REQ-090'
LOCKED_EXTENSION_02 = 'references/CONVERSATION_REQUIREMENT_LEDGER_EXTENSION_02.md'
LOCKED_IMPLEMENTATION_PLAN = 'references/LOCKED_IMPLEMENTATION_PLAN_CURRENT.md'
CURRENT_EXECUTION_LEDGER = 'references/REQUIREMENT_EXECUTION_LEDGER_CURRENT.json'
CURRENT_PHASE4_CONSUMER_MAP = 'references/REQUIREMENT_CONSUMER_MAP_CURRENT_PHASE4_ART_DIRECTION_PHOTOGRAPHY_VISUAL_MASTER.json'
CANONICAL_SAME_SOURCE_INVARIANT = 'Canonical same-source invariant'
SAME_SOURCE_AUTHORITIES = (
    LOCKED_EXTENSION_02,
    LOCKED_IMPLEMENTATION_PLAN,
    CURRENT_EXECUTION_LEDGER,
    'references/REQUIREMENT_IMPLEMENTATION_MATRIX_CURRENT.md',
    CURRENT_PHASE4_CONSUMER_MAP,
)
"""
if text.count(anchor) != 1:
    raise SystemExit('STRICT_REQUIREMENT_CHECKER anchor drift')
text = text.replace(anchor, constants, 1)

old_required = """        'references/CONVERSATION_REQUIREMENT_LEDGER_EXTENSION_02.md',
        'references/LOCKED_IMPLEMENTATION_PLAN_CURRENT.md',
        'references/REQUIREMENT_EXECUTION_LEDGER_CURRENT.json',
"""
new_required = """        LOCKED_EXTENSION_02,
        LOCKED_IMPLEMENTATION_PLAN,
        CURRENT_EXECUTION_LEDGER,
        CURRENT_PHASE4_CONSUMER_MAP,
"""
if text.count(old_required) != 1:
    raise SystemExit('locked authority required-path block drift')
text = text.replace(old_required, new_required, 1)

function_anchor = """def _effective_requirement_rows(resources: Path) -> list[dict[str, Any]]:
"""
validation_functions = r'''def validate_locked_requirement_ledger(document: dict[str, Any]) -> list[dict[str, Any]]:
    """Validate the locked REQ-061..REQ-090 authority as a release invariant."""
    issues: list[dict[str, Any]] = []
    if str(document.get('requirement_range') or '') != CURRENT_LEDGER_RANGE:
        issues.append({
            'code': 'LOCKED_REQUIREMENT_LEDGER_RANGE_MISMATCH',
            'actual': document.get('requirement_range') or 'MISSING',
            'expected': CURRENT_LEDGER_RANGE,
        })
    if str(document.get('plan') or '') != LOCKED_IMPLEMENTATION_PLAN:
        issues.append({
            'code': 'LOCKED_REQUIREMENT_LEDGER_PLAN_MISMATCH',
            'actual': document.get('plan') or 'MISSING',
            'expected': LOCKED_IMPLEMENTATION_PLAN,
        })
    if str(document.get('extension_02') or '') != LOCKED_EXTENSION_02:
        issues.append({
            'code': 'LOCKED_REQUIREMENT_LEDGER_EXTENSION_MISMATCH',
            'actual': document.get('extension_02') or 'MISSING',
            'expected': LOCKED_EXTENSION_02,
        })
    rows = [row for row in (document.get('new_requirements') or []) if isinstance(row, dict)]
    ids = [str(row.get('req') or '') for row in rows]
    expected_ids = [f'REQ-{i:03d}' for i in range(61, 91)]
    if ids != expected_ids:
        issues.append({
            'code': 'LOCKED_REQ_061_090_ID_SET_MISMATCH',
            'range': LOCKED_REQUIREMENT_RANGE,
            'actual': ids,
            'expected': expected_ids,
        })
    missing_status = [str(row.get('req') or '') for row in rows if not str(row.get('status') or '').strip()]
    if missing_status:
        issues.append({
            'code': 'LOCKED_REQ_061_090_STATUS_MISSING',
            'range': LOCKED_REQUIREMENT_RANGE,
            'requirements': missing_status,
        })
    return issues


def validate_locked_requirement_authorities(resources: Path) -> list[dict[str, Any]]:
    """Canonical same-source invariant for locked CURRENT requirement authorities."""
    issues: list[dict[str, Any]] = []
    ledger_path = resources / CURRENT_EXECUTION_LEDGER
    if ledger_path.exists():
        issues.extend(validate_locked_requirement_ledger(_load_json(ledger_path)))

    for rel in SAME_SOURCE_AUTHORITIES:
        source = ROOT / rel
        packaged = resources / rel
        if not source.exists():
            issues.append({
                'code': 'CANONICAL_SAME_SOURCE_AUTHORITY_SOURCE_MISSING',
                'invariant': CANONICAL_SAME_SOURCE_INVARIANT,
                'path': rel,
            })
            continue
        if packaged.exists() and source.resolve() != packaged.resolve() and source.read_bytes() != packaged.read_bytes():
            issues.append({
                'code': 'CANONICAL_SAME_SOURCE_AUTHORITY_DRIFT',
                'invariant': CANONICAL_SAME_SOURCE_INVARIANT,
                'path': rel,
            })
    return issues


'''
if text.count(function_anchor) != 1:
    raise SystemExit('_effective_requirement_rows anchor drift')
text = text.replace(function_anchor, validation_functions + function_anchor, 1)

missing_anchor = """            if missing:
                add('REQUIRED_CURRENT_RELEASE_FILE_MISSING', files=missing)

            current_builder_path = resources / CURRENT_BUILDER
"""
missing_replacement = """            if missing:
                add('REQUIRED_CURRENT_RELEASE_FILE_MISSING', files=missing)
            issues.extend(validate_locked_requirement_authorities(resources))

            current_builder_path = resources / CURRENT_BUILDER
"""
if text.count(missing_anchor) != 1:
    raise SystemExit('required file validation anchor drift')
text = text.replace(missing_anchor, missing_replacement, 1)

path.write_text(text, encoding='utf-8')
