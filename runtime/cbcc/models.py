from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any
import hashlib, json

def stable_hash(value: Any) -> str:
    raw=json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"),default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

@dataclass
class CommerceEntity:
    entity_id: str
    kind: str
    name: str
    facts: dict[str,Any]=field(default_factory=dict)
    parent_id: str|None=None
    source_ids: list[str]=field(default_factory=list)
    def to_dict(self): return asdict(self)

@dataclass
class AssetLanguageContract:
    primary_locale: str
    support_locales: list[str]=field(default_factory=list)
    visible_copy_locales: list[str]=field(default_factory=list)
    script_subtitle_locales: list[str]=field(default_factory=list)
    prompt_instruction_locale: str='zh-CN'
    visible_copy_mode: str='TARGET_NATIVE'
    source_lineage: list[str]=field(default_factory=list)
    delivery_locale: str='zh-CN'
    def to_dict(self): return asdict(self)

@dataclass
class TargetContext:
    target_id: str
    market: str
    jurisdiction: str
    platform_family: str
    site: str
    program: str|None
    surfaces: list[str]
    category: str|None
    language: AssetLanguageContract
    rule_status: str='UNRESOLVED'
    source_ids: list[str]=field(default_factory=list)
    def to_dict(self):
        d=asdict(self); return d

@dataclass
class OfferEconomics:
    currency: str
    price: float|None=None
    landed_cost: float|None=None
    platform_fee: float|None=None
    fulfillment: float|None=None
    affiliate_commission: float|None=None
    ad_cost: float|None=None
    tax: float|None=None
    refund_allowance: float|None=None
    contribution: float|None=None
    status: str='INSUFFICIENT_DATA'
    def calculate(self):
        if self.price is None: return self
        costs=[self.landed_cost,self.platform_fee,self.fulfillment,self.affiliate_commission,self.ad_cost,self.tax,self.refund_allowance]
        if any(x is None for x in costs):
            self.status='INSUFFICIENT_DATA'; self.contribution=None
        else:
            self.contribution=round(self.price-sum(costs),6); self.status='CALCULATED_FROM_INPUTS'
        return self
    def to_dict(self): return asdict(self)

@dataclass
class DecisionTrace:
    race_stage: str
    shopper_question: str
    decision_job: str
    evidence_ids: list[str]=field(default_factory=list)
    framework_signals: dict[str,Any]=field(default_factory=dict)
    rationale: str=''
    def to_dict(self): return asdict(self)

@dataclass
class ContentObject:
    object_id: str
    kind: str
    family: str
    curation_job: str
    target_id: str
    surface: str|None
    required: bool
    status: str='PLANNED'
    payload: dict[str,Any]=field(default_factory=dict)
    source_ids: list[str]=field(default_factory=list)
    claim_ids: list[str]=field(default_factory=list)
    upstream_hashes: dict[str,str]=field(default_factory=dict)
    language: AssetLanguageContract|None=None
    def to_dict(self): return asdict(self)

@dataclass
class RuleAtom:
    rule_id: str
    scope: dict[str,str]
    statement: str
    source_url: str
    verified_at: str
    expires_at: str
    authority: str='OFFICIAL'
    payload: dict[str,Any]=field(default_factory=dict)
    def to_dict(self): return asdict(self)

@dataclass
class ResearchAction:
    action_id: str
    reason: str
    query: str
    required_for: list[str]
    status: str='PENDING'
    preferred_source: str='OFFICIAL_CURRENT_SOURCE'
    def to_dict(self): return asdict(self)
