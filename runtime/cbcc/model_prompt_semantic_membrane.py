from __future__ import annotations

from copy import deepcopy
import re
from typing import Any, Mapping


_LEAK_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ('EXCEL_SOURCE_AUTHORITY', re.compile(r'(?:excel|xlsx).{0,100}(?:highest authority|source of truth|最高权威|最高真源|真源)|(?:highest authority|source of truth|最高权威|最高真源|真源).{0,100}(?:excel|xlsx)', re.I)),
    ('QA_CHECKLIST_LABEL', re.compile(r'(?:^|[\n。；;])\s*(?:qa|quality assurance|acceptance checklist|验收|质量验收|质量检查)\s*[:：]', re.I)),
    ('MINIMUM_REPAIR_ROUTE', re.compile(r'(?:minimum|minimal|smallest)\s+repair|最小修复|最小责任层|修复优先|repair\s+(?:priority|route|order)', re.I)),
    ('LOCAL_FILE_OR_INTERNAL_SOURCE', re.compile(r'(?:[\\/][^\s]{1,120}\.(?:xlsx?|csv|json|ya?ml|psd|ai|zip)|\b[^\s]{1,120}\.(?:xlsx?|csv)\b)', re.I)),
    ('INTERNAL_ORCHESTRATION', re.compile(r'provider route|authority hash|machine contract|prompt consumption audit|audit status|renderer layer|source binding metadata', re.I)),
    ('EDITABILITY_WORKFLOW', re.compile(r'^(?:editable layers|frozen layers|local edit rule|可编辑层|冻结层|局部编辑规则)\s*[:：]', re.I)),
    ('INTERNAL_REFERENCE_MODE', re.compile(r'^(?:product reference mode|产品参考模式)\s*[:：]', re.I)),
    ('AGENT_STATE', re.compile(r'\b(?:UNRESOLVED_AGENT_DECISION|AGENT_DECISION_REQUIRED|HOST_AGENT_AUTHORED)\b', re.I)),
]


def model_prompt_orchestration_leaks(prompt: str) -> list[dict[str, Any]]:
    text = str(prompt or '')
    issues: list[dict[str, Any]] = []
    for code, pattern in _LEAK_PATTERNS:
        m = pattern.search(text)
        if m:
            issues.append({'code': code, 'match': m.group(0)[:240]})
    return issues


def _split_clauses(line: str) -> list[str]:
    """Split orchestration from visual instructions without treating the whole line as disposable."""
    parts = re.split(r'(?<=[。.!?；;])\s*', str(line or ''))
    return [p.strip() for p in parts if p and p.strip()]


def _strip_source_authority(text: str) -> str:
    out = str(text or '')
    replacements = [
        r'\s*(?:Excel|the Excel|\.xlsx file|spreadsheet)\s*(?:is|as|为|作为)?\s*(?:the\s*)?(?:产品事实)?(?:highest authority|source of truth|最高权威|最高真源|真源)[^。.!?；;]*',
        r'\s*(?:产品事实)?(?:highest authority|source of truth|最高权威|最高真源|真源)\s*(?:为|是|is)?\s*(?:the\s*)?(?:Excel|spreadsheet|[^\s，。；;]+\.xlsx)[^。.!?；;]*',
        r'\s*(?:数字|numbers?)\s*(?:只能|must only|only)\s*(?:来自|come from)?\s*(?:Excel|spreadsheet)[^。.!?；;]*',
    ]
    for pat in replacements:
        out = re.sub(pat, ' ', out, flags=re.I)
    out = re.sub(r'\b(?:source of truth|highest authority)\b', ' ', out, flags=re.I)
    out = re.sub(r'(?:产品事实)?(?:最高权威|最高真源|真源)', ' ', out, flags=re.I)
    return re.sub(r'\s{2,}', ' ', out).strip(' ，,;；。')


def _strip_internal_labels(text: str) -> str:
    out = str(text or '')
    # QA can contain forward-generation constraints. Remove the QA label, not the visual requirement.
    out = re.sub(r'^\s*(?:QA|quality assurance|acceptance checklist|验收|质量验收|质量检查)\s*[:：]\s*', '', out, flags=re.I)
    # Remove project/process nouns while preserving the rest of a mixed visual clause.
    out = re.sub(r'\bAgent Art Direction\b', '', out, flags=re.I)
    out = re.sub(r'\bProduct Truth\b', 'verified product facts', out, flags=re.I)
    out = re.sub(r'产品真源', '已验证商品事实', out)
    out = re.sub(r'Agent\s*策展', '', out, flags=re.I)
    out = re.sub(r'\s{2,}', ' ', out)
    return out.strip(' ，,;；。')


def _pure_orchestration_clause(text: str) -> bool:
    stripped = str(text or '').strip()
    if not stripped:
        return True
    # Repair routing is always post-generation workflow. Drop the repair clause only.
    if re.search(r'(?:minimum|minimal|smallest)\s+repair|最小修复|最小责任层|修复优先|repair\s+(?:priority|route|order)', stripped, flags=re.I):
        return True
    if re.match(r'^(?:editable layers|frozen layers|local edit rule|可编辑层|冻结层|局部编辑规则|product reference mode|产品参考模式)\s*[:：]', stripped, flags=re.I):
        return True
    if re.search(r'provider route|authority hash|machine contract|prompt consumption audit|audit status|renderer layer|source binding metadata', stripped, flags=re.I):
        return True
    if re.search(r'\b(?:UNRESOLVED_AGENT_DECISION|AGENT_DECISION_REQUIRED|HOST_AGENT_AUTHORED)\b', stripped, flags=re.I):
        return True
    return False


def _looks_like_named_internal_product_reference(text: str) -> bool:
    return bool(re.search(
        r'(?:use|使用).{0,100}(?:KIYUU\s+)?(?:K\d{1,4}|SKU[-_ ]?[A-Z0-9]+|asset[-_ ]?\d+).{0,140}(?:reference|参考|包装图|源图|product identity)',
        str(text or ''),
        flags=re.I,
    ))


def _provider_reference_instruction(language: str, *, locked_source: bool = False) -> str:
    cn = str(language or '').upper().startswith('CN')
    if locked_source:
        if cn:
            return '已附带真实商品参考图。保留锁定商品图层；环境、光线、接触阴影、反射、透视与空间关系必须匹配真实商品几何和视角。'
        return 'The real product reference is attached. Preserve the locked product layer; match the environment, lighting, contact shadow, reflections, perspective and spatial relationships to its real geometry and view.'
    if cn:
        return '使用已附带的商品参考图保持真实包装几何、结构、部件与必要包装身份；让商品自然融入当前构图、光线、材质响应和场景，不得凭空增加商品特征、宣称或包装文案。'
    return 'Use the attached product reference images to preserve the real package geometry, structure, components and required packaging identity; integrate the product naturally into the authored composition, lighting, material response and scene, and do not invent product features, claims or package copy.'


def sanitize_model_prompt(
    prompt: str,
    *,
    language: str,
    reference_bound: bool = False,
    locked_source: bool = False,
) -> str:
    """Strip orchestration without deleting authored people/scene/camera/light/CMF/copy instructions.

    The membrane works clause-by-clause. A line is never discarded merely because one neighboring
    clause contains QA/source/revision language. This is critical for dense Art Direction prose where
    commercial, human, camera, lighting and material instructions often share one paragraph.
    """
    raw_lines = str(prompt or '').replace('\r\n', '\n').replace('\r', '\n').split('\n')
    out: list[str] = []
    reference_instruction_needed = False

    for raw in raw_lines:
        stripped_line = str(raw or '').strip()
        if not stripped_line:
            continue
        # Suppress only the mixed editability section label. Pixel-visible approved elements and
        # precision boundaries on following lines are preserved; editable/frozen workflow lines are dropped individually.
        if stripped_line in {'[VISUAL EXECUTION BOUNDARIES / EDITABILITY]', '【视觉执行边界 / 可编辑性】'}:
            continue

        for clause in _split_clauses(stripped_line):
            clause = _strip_source_authority(clause)
            clause = _strip_internal_labels(clause)
            if not clause:
                continue
            if _pure_orchestration_clause(clause):
                continue
            if _looks_like_named_internal_product_reference(clause):
                if reference_bound:
                    reference_instruction_needed = True
                continue
            # A literal project filename that survived source-authority stripping still cannot help the model.
            if re.search(r'\b[^\s]{1,120}\.(?:xlsx?|csv|json|ya?ml|psd|ai|zip)\b', clause, flags=re.I):
                continue
            out.append(clause)

    if reference_bound:
        has_reference_instruction = any(
            re.search(r'(?:attached product reference|附带的商品参考|附带真实商品参考)', row, flags=re.I)
            for row in out
        )
        if reference_instruction_needed or not has_reference_instruction:
            out.insert(1 if out else 0, _provider_reference_instruction(language, locked_source=locked_source))

    compact: list[str] = []
    for row in out:
        row = re.sub(r'\s{2,}', ' ', row).strip()
        if row and (not compact or row != compact[-1]):
            compact.append(row)
    return '\n'.join(compact).strip() + ('\n' if compact else '')


def _provider_reference_bound(bundle: Mapping[str, Any]) -> bool:
    renderer = bundle.get('renderer_recipe') if isinstance(bundle.get('renderer_recipe'), Mapping) else {}
    bindings = renderer.get('source_product_bindings') or []
    for row in bindings:
        if not isinstance(row, Mapping) or not row.get('visible_subject_binding'):
            continue
        locator = row.get('locator') if isinstance(row.get('locator'), Mapping) else {}
        if locator.get('value'):
            return True
    return False


def _locked_source(bundle: Mapping[str, Any]) -> bool:
    renderer = bundle.get('renderer_recipe') if isinstance(bundle.get('renderer_recipe'), Mapping) else {}
    if renderer.get('real_product_master_required'):
        return True
    card = bundle.get('design_card') if isinstance(bundle.get('design_card'), Mapping) else {}
    identity = card.get('product_identity') if isinstance(card.get('product_identity'), Mapping) else {}
    return str(identity.get('product_fidelity') or '').upper() in {'LOCKED_PIXEL', 'LOCKED_SOURCE_COMPOSITE', 'COMPOSITE'}


def finalize_model_prompt_bundle(bundle: Mapping[str, Any]) -> dict[str, Any]:
    """Final public-provider boundary: no later prompt mutation may bypass this membrane."""
    out = deepcopy(dict(bundle))
    reference_bound = _provider_reference_bound(out)
    locked_source = _locked_source(out)

    cn = str(out.get('model_prompt_cn') or out.get('prompt_cn') or '')
    en = str(out.get('model_prompt_en') or out.get('prompt_en') or '')
    cn = sanitize_model_prompt(cn, language='CN', reference_bound=reference_bound, locked_source=locked_source)
    en = sanitize_model_prompt(en, language='EN', reference_bound=reference_bound, locked_source=locked_source)
    out['model_prompt_cn'] = out['prompt_cn'] = cn
    out['model_prompt_en'] = out['prompt_en'] = en

    cn_issues = model_prompt_orchestration_leaks(cn)
    en_issues = model_prompt_orchestration_leaks(en)
    issues = cn_issues + en_issues
    membrane = {
        'status': 'PASS' if not issues else 'FAIL',
        'principle': 'Preserve all authored pixel/frame-changing Art Direction; remove only source/QA/revision/orchestration semantics.',
        'reference_bound': reference_bound,
        'cn_issues': cn_issues,
        'en_issues': en_issues,
    }
    out['model_prompt_semantic_membrane'] = membrane

    audit = deepcopy(dict(out.get('prompt_consumption_audit') or {}))
    checks = list(audit.get('checks') or [])
    checks = [x for x in checks if not (isinstance(x, Mapping) and x.get('decision') == 'final_model_prompt_semantic_membrane')]
    checks.append({
        'decision': 'final_model_prompt_semantic_membrane',
        'required': True,
        'projected': not issues,
        'selected_value': 'NO_ORCHESTRATION_LEAK_WITHOUT_ART_DIRECTION_LOSS',
        'value': membrane,
    })
    audit['checks'] = checks
    missing = list(audit.get('missing_decisions') or [])
    missing = [x for x in missing if x != 'final_model_prompt_semantic_membrane']
    if issues:
        missing.append('final_model_prompt_semantic_membrane')
    audit['missing_decisions'] = list(dict.fromkeys(missing))
    audit['status'] = 'PASS' if not audit['missing_decisions'] else 'INCOMPLETE'
    out['prompt_consumption_audit'] = audit

    if issues:
        out['model_prompt_status'] = 'MODEL_PROMPT_ORCHESTRATION_LEAK'
        out['status'] = 'MODEL_PROMPT_ORCHESTRATION_LEAK'
    return out


def wrap_compile_asset_prompt(compile_fn):
    def compiled(*args, **kwargs):
        return finalize_model_prompt_bundle(compile_fn(*args, **kwargs))
    return compiled
