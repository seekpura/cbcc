from __future__ import annotations
from pathlib import Path
from datetime import date
from typing import Any
import yaml
from .models import RuleAtom, ResearchAction, stable_hash


def _as_list(v):
    if v is None: return []
    return v if isinstance(v,list) else [v]


def _dedupe(seq):
    out=[]; seen=set()
    for x in seq:
        key=stable_hash(x) if isinstance(x,(dict,list)) else str(x)
        if key not in seen: seen.add(key); out.append(x)
    return out


class PlatformCompiler:
    """Compile family planning knowledge and layered exact site/program/category/surface/locale rules.

    Exact packs are additive overlays only when their declared `match` scope matches the target.
    Generic family packs support planning but never establish exact submission readiness.
    """
    def __init__(self, packs_dir:Path): self.packs_dir=Path(packs_dir)
    def _packs(self):
        for p in self.packs_dir.glob('*.yaml'):
            d=yaml.safe_load(p.read_text(encoding='utf-8')) or {}; d['_path']=str(p); yield d

    @staticmethod
    def _pack_match(pack:dict[str,Any], target:dict[str,Any])->bool:
        if pack.get('platform_family')!=target.get('platform_family'): return False
        site=pack.get('site')
        if site not in {'*',target.get('site')}: return False
        pprogram=pack.get('program')
        if pprogram not in {None,'*',target.get('program')}: return False
        match=pack.get('match') or {}
        for key,target_key in [('category','category'),('locale','primary_locale')]:
            allowed=_as_list(match.get(key))
            val=target.get(target_key)
            if allowed and '*' not in allowed and val not in allowed: return False
        allowed_surfaces=set(_as_list(match.get('surface')))
        requested=set(target.get('surfaces',[]))
        if allowed_surfaces and '*' not in allowed_surfaces and requested and not (allowed_surfaces & requested): return False
        return True

    @staticmethod
    def _specificity(pack:dict[str,Any],target:dict[str,Any])->int:
        score=0
        if pack.get('site')==target.get('site'): score+=20
        if pack.get('program') not in {None,'*'} and pack.get('program')==target.get('program'): score+=8
        match=pack.get('match') or {}
        if match.get('category'): score+=5
        if match.get('locale'): score+=3
        if match.get('surface'): score+=2
        return score

    def resolve_layers(self,target:dict[str,Any]):
        matched=[d for d in self._packs() if self._pack_match(d,target)]
        exact=[d for d in matched if d.get('site')==target.get('site')]
        if exact:
            exact.sort(key=lambda d:self._specificity(d,target))
            return exact,'EXACT'
        generic=[d for d in matched if d.get('site')=='*']
        generic.sort(key=lambda d:self._specificity(d,target))
        if generic: return generic,'FAMILY'
        return [],'NONE'

    def resolve(self,platform_family,site,program=None):
        # Compatibility helper: returns the highest-specificity matching base without category context.
        layers,resolution=self.resolve_layers({'platform_family':platform_family,'site':site,'program':program,'surfaces':[],'category':None,'primary_locale':None})
        return (layers[-1] if layers else None),resolution

    @staticmethod
    def _scope_match(scope:dict[str,Any],target:dict[str,Any])->bool:
        if not scope: return True
        checks={'site':target.get('site'),'program':target.get('program'),'category':target.get('category')}
        for k,val in checks.items():
            allowed=_as_list(scope.get(k))
            if allowed and val not in (None,'') and '*' not in allowed and val not in allowed: return False
        locale=target.get('primary_locale'); allowed=_as_list(scope.get('locale'))
        if allowed and locale not in (None,'') and '*' not in allowed and locale not in allowed: return False
        surfaces=set(target.get('surfaces',[])); allowed=set(_as_list(scope.get('surface')))
        if allowed and surfaces and '*' not in allowed and not (surfaces & allowed): return False
        return True

    @staticmethod
    def _merge_layers(layers:list[dict[str,Any]])->dict[str,Any]:
        out={'pack_ids':[],'status':None,'capabilities':[],'business_capabilities':{},'surfaces':[],'surface_capabilities':[],'rule_atoms':[],'research_required_for':[],'source_records':[],'notes':[]}
        for p in layers:
            out['pack_ids'].append(p.get('pack_id'))
            out['status']=p.get('status') or out['status']
            out['capabilities']+=p.get('capabilities',[]) or []
            out['business_capabilities'].update(p.get('business_capabilities',{}) or {})
            out['surfaces']+=p.get('surfaces',[]) or []
            out['surface_capabilities']+=p.get('surface_capabilities',[]) or []
            out['rule_atoms']+=p.get('rule_atoms',[]) or []
            out['research_required_for']+=p.get('research_required_for',[]) or []
            out['source_records']+=p.get('source_records',[]) or []
            out['notes']+=p.get('notes',[]) or []
        for k in ['capabilities','surfaces','surface_capabilities','rule_atoms','research_required_for','source_records','notes']:
            out[k]=_dedupe(out[k])
        return out

    def compile(self,target:dict, required_rules:list[str]|None=None, as_of:date|None=None):
        as_of=as_of or date.today(); required_rules=required_rules or []
        layers,resolution=self.resolve_layers(target)
        if not layers:
            action=ResearchAction('RA-PLATFORM-PACK','No exact or family platform pack',f"Verify {target['platform_family']} {target['site']} {target.get('program') or ''}",['PLATFORM_COMPILE'])
            return {'status':'RESEARCH_REQUIRED','resolution':'NONE','pack':None,'rules':[],'capabilities':[],'business_capabilities':{},'research_actions':[action.to_dict()]}
        pack=self._merge_layers(layers)
        atoms=[]; expired=[]
        for raw in pack.get('rule_atoms',[]):
            if not self._scope_match(raw.get('scope',{}),target): continue
            exp=date.fromisoformat(raw['expires_at'])
            if exp < as_of:
                expired.append(raw['rule_id']); continue
            atoms.append(RuleAtom(**raw).to_dict())
        ids={r['rule_id'] for r in atoms}; missing=[req for req in required_rules if req not in ids]
        contract_issues=[]
        visible_copy_locales=set(target.get('visible_copy_locales') or [])
        visible_copy_contract_supplied='visible_copy_locales' in target
        for r in atoms:
            payload=r.get('payload') or {}; constraints=payload.get('constraints') or {}
            req_locale=constraints.get('required_visible_copy_locale')
            if req_locale and visible_copy_contract_supplied and req_locale not in visible_copy_locales:
                contract_issues.append(f'VISIBLE_COPY_LOCALE_REQUIRED:{req_locale}')
        requested_surfaces=set(target.get('surfaces',[])); supported_surfaces=set(pack.get('surfaces',[]))
        unsupported_surfaces=sorted(requested_surfaces-supported_surfaces) if supported_surfaces else []
        category_overlay=any((x.get('match') or {}).get('category') for x in layers)
        program_overlay=any(x.get('program') not in {None,'*'} for x in layers)
        overlay_required=[]
        if resolution=='EXACT' and target.get('require_category_pack') and target.get('category') and not category_overlay:
            overlay_required.append(f"CATEGORY_PACK:{target.get('category')}")
        if resolution=='EXACT' and target.get('require_program_pack') and target.get('program') and not program_overlay:
            overlay_required.append(f"PROGRAM_PACK:{target.get('program')}")
        actions=[]; research_reasons=list(missing)+pack.get('research_required_for',[])+overlay_required
        if resolution=='EXACT': research_reasons += [f'SURFACE:{x}' for x in unsupported_surfaces]
        for req in sorted(set(research_reasons+expired)):
            actions.append(ResearchAction('RA-'+stable_hash([target,req])[:10],f'Current verified platform evidence needed: {req}',f"Verify current official {req} for {target['platform_family']} {target['site']} {target.get('program') or ''}",[req]).to_dict())
        if resolution=='FAMILY': status='FAMILY_PLANNING_ONLY'
        elif contract_issues: status='TARGET_CONTRACT_MISMATCH'
        elif missing or unsupported_surfaces or overlay_required: status='RESEARCH_REQUIRED'
        elif pack.get('research_required_for'): status='PLANNING_ONLY_RESEARCH_PENDING'
        else: status='VERIFIED_FOR_REQUEST'
        surface_caps={}
        for s in pack.get('surface_capabilities',[]) or []:
            sid=s.get('surface')
            if sid and (not requested_surfaces or sid in requested_surfaces): surface_caps[sid]=s
        return {
            'status':status,'resolution':resolution,'pack_id':pack['pack_ids'][-1] if len(pack['pack_ids'])==1 else 'COMPOSITE:'+stable_hash(pack['pack_ids'])[:12],
            'applied_pack_ids':pack['pack_ids'],'pack_status':pack.get('status'),'synthetic_for_test':any(bool(x.get('synthetic_for_test')) for x in layers),
            'platform_family':target.get('platform_family'),'site':target.get('site'),'program':target.get('program'),'category':target.get('category'),'primary_locale':target.get('primary_locale'),
            'category_overlay_applied':category_overlay,'program_overlay_applied':program_overlay,'contract_issues':contract_issues,
            'capabilities':pack.get('capabilities',[]),'business_capabilities':pack.get('business_capabilities',{}),'surfaces':pack.get('surfaces',[]),
            'requested_surfaces':sorted(requested_surfaces),'unsupported_surfaces':unsupported_surfaces,'surface_capabilities':surface_caps,
            'rules':atoms,'expired_rule_ids':expired,'research_actions':actions,'source_records':pack.get('source_records',[]),
            'submission_readiness':'ASSESSED' if resolution=='EXACT' and status=='VERIFIED_FOR_REQUEST' else 'NOT_ESTABLISHED',
            'evidence_scope':'SITE_PLUS_MATCHING_OVERLAYS' if resolution=='EXACT' else 'FAMILY_PLANNING'
        }
