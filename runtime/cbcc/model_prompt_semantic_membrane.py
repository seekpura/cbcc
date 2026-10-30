from __future__ import annotations

import re
from typing import Any


_SECTION_HEADERS = {
    '[VISUAL EXECUTION BOUNDARIES / EDITABILITY]',
    '【视觉执行边界 / 可编辑性】',
}

_LEAK_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ('EXCEL_SOURCE_AUTHORITY', re.compile(r'(?:excel|xlsx).{0,80}(?:highest authority|source of truth|最高权威|最高真源|真源)|(?:highest authority|source of truth|最高权威|最高真源|真源).{0,80}(?:excel|xlsx)', re.I)),
    ('QA_CHECKLIST', re.compile(r'(?:^|[\n。；;])\s*(?:qa|quality assurance|acceptance checklist|验收|质量验收|质量检查)\s*[:：]', re.I)),
    ('MINIMUM_REPAIR_ROUTE', re.compile(r'(?:minimum|minimal|smallest)\s+repair|最小修复|最小责任层|修复优先|repair\s+(?:priority|route|order)', re.I)),
    ('LOCAL_FILE_OR_INTERNAL_SOURCE', re.compile(r'(?:[\\/][^\s]{1,120}\.(?:xlsx?|csv|json|ya?ml|psd|ai|zip)|\b[^\s]{1,120}\.(?:xlsx?|csv)\b)', re.I)),
    ('INTERNAL_ORCHESTRATION', re.compile(r'provider route|authority hash|machine contract|prompt consumption audit|audit status|renderer layer|source binding metadata', re.I)),
    ('EDITABILITY_WORKFLOW', re.compile(r'^(?:editable layers|frozen layers|local edit rule|可编辑层|冻结层|局部编辑规则)\s*[:：]', re.I)),
    ('INTERNAL_REFERENCE_MODE', re.compile(r'^(?:product reference mode|产品参考模式)\s*[:：]', re.I)),
]


def model_prompt_orchestration_leaks(prompt: str) -> list[dict[str, Any]]:
    text = str(prompt or '')
    issues: list[dict[str, Any]] = []
    for code, pattern in _LEAK_PATTERNS:
        m = pattern.search(text)
        if m:
            issues.append({'code': code, 'match': m.group(0)[:240]})
    return issues


def _drop_orchestration_sections(lines: list[str]) -> list[str]:
    out: list[str] = []
    skipping = False
    for raw in lines:
        line = str(raw or '')
        stripped = line.strip()
        if stripped in _SECTION_HEADERS:
            skipping = True
            continue
        if skipping:
            is_header = (
                (stripped.startswith('[') and stripped.endswith(']'))
                or (stripped.startswith('【') and stripped.endswith('】'))
            )
            if is_header:
                skipping = False
            else:
                continue
        if not skipping:
            out.append(line)
    return out


def _strip_sentence_fragments(text: str) -> str:
    # Project/source authority is an orchestration concern. Remove only the authority clause,
    # leaving surrounding model-visible instructions intact when possible.
    replacements = [
        r'\s*(?:Excel|the Excel|\.xlsx file|spreadsheet)\s*(?:is|as)?\s*(?:the\s*)?(?:highest authority|source of truth)[^。.!?；;]*[。.!?；;]?',
        r'\s*Excel\s*(?:为|作为)?\s*(?:产品事实)?(?:最高权威|最高真源|真源)[^。.!?；;]*[。.!?；;]?',
        r'\s*(?:产品事实)?(?:最高权威|最高真源|真源)\s*(?:为|是)?\s*Excel[^。.!?；;]*[。.!?；;]?',
    ]
    out = text
    for pat in replacements:
        out = re.sub(pat, ' ', out, flags=re.I)
    return re.sub(r'\s{2,}', ' ', out).strip()


def _is_orchestration_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    for code, pattern in _LEAK_PATTERNS:
        if code in {'EXCEL_SOURCE_AUTHORITY'}:
            continue
        if pattern.search(stripped):
            return True
    return False


def _looks_like_named_internal_product_reference(line: str) -> bool:
    # Common Host prose that names an internal SKU/file-like product object instead of describing
    # the actual provider-bound visual reference. We intentionally keep visible brand copy elsewhere.
    return bool(re.search(
        r'(?:use|使用).{0,80}(?:K\d{1,4}|SKU[-_ ]?[A-Z0-9]+|asset[-_ ]?\d+).{0,120}(?:reference|参考|包装图|源图|product identity)',
        line,
        flags=re.I,
    ))


def _provider_reference_instruction(language: str, *, locked_source: bool = False) -> str:
    cn = str(language or '').upper().startswith('CN')
    if locked_source:
        if cn:
            return '已附带真实商品参考图。不要重绘锁定商品图层；生成环境、光线、接触阴影与空间关系时必须与该真实商品几何和视角匹配。'
        return 'The real product reference is attached. Do not redraw the locked product layer; generate the environment, lighting, contact shadow and spatial relationships to match its real geometry and perspective.'
    if cn:
        return '使用已附带的商品参考图保持真实包装几何、结构与必要的包装身份；让商品自然融入当前构图、光线与场景，不得凭空增加商品特征、宣称或包装文案。'
    return 'Use the attached product reference images to preserve the real package geometry, structure and required packaging identity; integrate the product naturally into the current composition, lighting and scene, and do not invent product features, claims or package copy.'


def sanitize_model_prompt(
    prompt: str,
    *,
    language: str,
    reference_bound: bool = False,
    locked_source: bool = False,
) -> str:
    """Keep only model-visible / pixel-changing instructions in a model-facing prompt.

    This is a semantic membrane, not a generic shortening pass. It removes project orchestration,
    source-authority language, QA/review checklists, repair routing and editability metadata while
    preserving visual constraints. If a provider reference is actually bound, opaque SKU/file prose
    is replaced with a provider-visible reference instruction.
    """
    raw_lines = str(prompt or '').replace('\r\n', '\n').replace('\r', '\n').split('\n')
    lines = _drop_orchestration_sections(raw_lines)
    out: list[str] = []
    reference_instruction_needed = False

    for raw in lines:
        line = _strip_sentence_fragments(str(raw or '').strip())
        if not line:
            continue

        if _looks_like_named_internal_product_reference(line):
            if reference_bound:
                reference_instruction_needed = True
            continue

        if _is_orchestration_line(line):
            continue

        # Remove standalone internal fidelity enum labels while preserving direct visual rules that
        # may follow elsewhere in the prompt.
        if re.match(r'^(?:product reference mode|产品参考模式)\s*[:：]', line, flags=re.I):
            continue

        # Product-rule prose from older compilers can mention Agent/Product Truth internals. Replace
        # it with a direct model-facing reference instruction when references are actually bound.
        if re.search(r'Agent Art Direction|Product Truth|truth references only|产品真源|Agent\s+策展', line, flags=re.I):
            if reference_bound and re.search(r'product|商品|包装|reference|参考', line, flags=re.I):
                reference_instruction_needed = True
            # Preserve direct absence command if present; otherwise drop orchestration-heavy line.
            if re.search(r'(?:product is intentionally absent|do not add a packshot|商品.*(?:不出现|缺席)|不要.*商品)', line, flags=re.I):
                cn = str(language or '').upper().startswith('CN')
                out.append('本画面不出现商品主体。' if cn else 'Keep the product absent from this frame.')
            continue

        out.append(line)

    if reference_bound:
        has_reference_instruction = any(
            re.search(r'(?:attached product reference|附带的商品参考|附带真实商品参考)', row, flags=re.I)
            for row in out
        )
        if reference_instruction_needed or not has_reference_instruction:
            # Insert after the first substantive line so reference behavior is visible early without
            # becoming the prompt's project-management preamble.
            idx = 1 if out else 0
            out.insert(idx, _provider_reference_instruction(language, locked_source=locked_source))

    # Remove accidental duplicate adjacent lines and normalize blank-free model prompt prose.
    compact: list[str] = []
    for row in out:
        row = re.sub(r'\s{2,}', ' ', row).strip()
        if row and (not compact or row != compact[-1]):
            compact.append(row)
    return '\n'.join(compact).strip() + ('\n' if compact else '')
