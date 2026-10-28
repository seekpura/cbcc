from __future__ import annotations
from dataclasses import dataclass,field,asdict
from typing import Any

FOUNDATION_STATES=['PLANNED','PLAN_LOCKED','SOURCE_BOUND','MASTER_PRODUCED','MASTER_QA_LOCKED']

@dataclass
class FoundationAssetRecord:
    asset_id:str
    role:str
    state:str='PLANNED'
    source_ids:list[str]=field(default_factory=list)
    output_path:str|None=None
    qa:dict[str,Any]=field(default_factory=dict)
    product_fidelity:str='REFERENCE_CONSTRAINED'
    history:list[dict[str,Any]]=field(default_factory=list)
    def to_dict(self): return asdict(self)
    def transition(self,to_state:str,**payload):
        if to_state not in FOUNDATION_STATES: raise ValueError(f'unknown state {to_state}')
        cur=FOUNDATION_STATES.index(self.state); nxt=FOUNDATION_STATES.index(to_state)
        if nxt != cur+1: raise ValueError(f'invalid transition {self.state}->{to_state}')
        if to_state=='SOURCE_BOUND' and not (payload.get('source_ids') or self.source_ids): raise ValueError('SOURCE_BOUND requires source_ids')
        if to_state=='MASTER_PRODUCED' and not (payload.get('output_path') or self.output_path): raise ValueError('MASTER_PRODUCED requires output_path')
        if to_state=='MASTER_QA_LOCKED':
            qa=payload.get('qa') or self.qa
            if not qa or not qa.get('pass'): raise ValueError('MASTER_QA_LOCKED requires qa.pass=true')
        before=self.state
        for k,v in payload.items():
            if hasattr(self,k): setattr(self,k,v)
        self.state=to_state; self.history.append({'from':before,'to':to_state,'payload':payload})
        return self

def required_foundation_roles(needs:dict[str,bool]) -> list[str]:
    """Deterministic role selection from explicit downstream needs, never a fixed capture list."""
    mapping=[('front','PRODUCT_FRONT_MASTER'),('three_quarter','PRODUCT_3Q_MASTER'),('side','PRODUCT_SIDE_MASTER'),('back','PRODUCT_BACK_MASTER'),('package_front','PACKAGE_FRONT_MASTER'),('package_back','PACKAGE_BACK_MASTER'),('contents','CONTENTS_MASTER'),('detail','DETAIL_MASTER'),('cutout','CUTOUT_MASTER'),('texture','TEXTURE_MASTER')]
    return [role for key,role in mapping if bool(needs.get(key))]
