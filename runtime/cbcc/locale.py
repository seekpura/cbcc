from __future__ import annotations
from typing import Any

SCRIPT_PROFILES={
    'LATN':{'direction':'LTR','line_break':'word','density':'MEDIUM','notes':['Preserve natural word boundaries.','Check mobile line length and hierarchy.']},
    'ARAB':{'direction':'RTL','line_break':'word','density':'MEDIUM','notes':['Use RTL-aware layout.','Keep numerals/Latin product tokens directionally stable.']},
    'HANS':{'direction':'LTR','line_break':'character','density':'HIGH','notes':['Avoid overly tight tracking.','Check punctuation and mixed Latin/CJK spacing.']},
    'HANT':{'direction':'LTR','line_break':'character','density':'HIGH','notes':['Use locale-appropriate glyph forms.','Check punctuation and mixed Latin/CJK spacing.']},
    'JPAN':{'direction':'LTR','line_break':'character','density':'HIGH','notes':['Respect Japanese line-breaking conventions.','Avoid stranded punctuation.']},
    'KORE':{'direction':'LTR','line_break':'syllable_or_word','density':'HIGH','notes':['Check Hangul/Latin spacing.','Prefer native editorial review for visible copy.']},
    'THAI':{'direction':'LTR','line_break':'dictionary','density':'HIGH','notes':['Thai line breaking needs locale-aware segmentation.','Avoid manual spaces as pseudo word breaks.']},
}

def _script(locale:str)->str:
    x=(locale or '').lower()
    if x.startswith('ar'): return 'ARAB'
    if x.startswith(('zh-cn','zh-sg')): return 'HANS'
    if x.startswith(('zh-tw','zh-hk')): return 'HANT'
    if x.startswith('ja'): return 'JPAN'
    if x.startswith('ko'): return 'KORE'
    if x.startswith('th'): return 'THAI'
    return 'LATN'

def typography_profile(locale:str)->dict[str,Any]:
    script=_script(locale); base=SCRIPT_PROFILES[script]
    return {'locale':locale,'script':script,**base,'profile_id':f'{script}-{base["direction"]}'}

def compile_language_profiles(primary:str,support:list[str]|None=None,visible:list[str]|None=None)->dict[str,Any]:
    locales=[]
    for loc in [primary]+list(support or [])+list(visible or []):
        if loc and loc not in locales: locales.append(loc)
    return {'profiles':[typography_profile(x) for x in locales], 'native_review_required':bool(locales), 'transcreation_mode':'MEANING_PRESERVING_NOT_LITERAL_BY_DEFAULT'}
