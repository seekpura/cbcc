from __future__ import annotations

CANONICAL_GATES=[
'EVIDENCE','PRODUCT_TRUTH','COMMERCE_ENTITY','TARGET_CONTEXT','CULTURE_CONTEXT','OFFER_ECONOMICS',
'DECISION','PLATFORM_COMPILE','CONTENT_GRAPH','ASSET_ARCHITECTURE','CREATIVE','STRATEGY_AUTHORITY','ASSET_COMPILE','EXECUTION','PRODUCTION',
'MEASUREMENT','LEARNING','AUDIT']

DEFAULT_EDGES={
'EVIDENCE':['PRODUCT_TRUTH'],
'PRODUCT_TRUTH':['COMMERCE_ENTITY','OFFER_ECONOMICS'],
'COMMERCE_ENTITY':['TARGET_CONTEXT'],
'TARGET_CONTEXT':['CULTURE_CONTEXT','PLATFORM_COMPILE'],
'CULTURE_CONTEXT':['DECISION','CONTENT_GRAPH','ASSET_ARCHITECTURE'],
'OFFER_ECONOMICS':['DECISION'],
'DECISION':['CONTENT_GRAPH'],
'PLATFORM_COMPILE':['CONTENT_GRAPH','ASSET_ARCHITECTURE','EXECUTION'],
'CONTENT_GRAPH':['ASSET_ARCHITECTURE','CREATIVE'],
'ASSET_ARCHITECTURE':['CREATIVE','STRATEGY_AUTHORITY'],
'CREATIVE':['STRATEGY_AUTHORITY'],
'STRATEGY_AUTHORITY':['ASSET_COMPILE'],
'ASSET_COMPILE':['EXECUTION'],
'EXECUTION':['PRODUCTION'],
'PRODUCTION':['MEASUREMENT'],
'MEASUREMENT':['LEARNING'],
'LEARNING':['AUDIT']}

class DependencyGraph:
    def __init__(self, edges=None): self.edges=edges or DEFAULT_EDGES
    def downstream(self, gate:str)->list[str]:
        seen=set(); stack=list(self.edges.get(gate,[]))
        while stack:
            n=stack.pop()
            if n in seen: continue
            seen.add(n); stack.extend(self.edges.get(n,[]))
        return [g for g in CANONICAL_GATES if g in seen]
    def invalidate_set(self, changed:list[str])->list[str]:
        out=set(changed)
        for g in changed: out.update(self.downstream(g))
        return [g for g in CANONICAL_GATES if g in out]
