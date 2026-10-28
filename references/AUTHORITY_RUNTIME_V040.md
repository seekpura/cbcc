# v0.4 Authority Runtime Contract

This runtime borrows **architectural lessons** from the mature EPV line without copying its product scope. CBCC remains the commerce intelligence/strategy authority; visual/media engines may be providers downstream.

Core objects: Product Truth, CommerceEntity, TargetContext, OfferEconomics, DecisionTrace, ContentObject, AssetLanguageContract, RuleAtom, ResearchAction and ProjectState.

Authority state is explicit. `READY_REVIEW` means the runtime produced a reviewable artifact. `LOCKED` is only created by an explicit review action. `HOLD` preserves unresolved evidence/rule dependencies. `INVALIDATED` means an upstream change requires recomputation.

A capability ledger entry is not considered deep runtime coverage merely because a file exists. The ledger records explicit maturity and machine evidence.
