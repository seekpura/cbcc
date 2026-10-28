# v0.5.13 — Real Product Strategy Quality Depth

## Why this release exists
v0.5.12 closed the executable Production → Review → Local Revision → Learning loop. v0.5.13 deliberately stops expanding frameworks and uses current real products to expose professional-quality failures after integration.

## Real-product blind validation
Products used as quality stress cases:
- COSRX Advanced Snail 96 Mucin Power Essence — beauty.
- Anker Prime 20,000mAh Power Bank (200W) — electronics.
- UNIQLO Round Mini Shoulder Bag — fashion accessory.
- Owala FreeSip 24oz — home durable.

Public facts/search/review/competitor observations are carried as sourced project inputs. Missing landed cost/platform/ad economics remain missing; the runtime is not allowed to invent them.

## Runtime fixes driven by failures
- Category-aware decision classification is shared by Dynamic Asset, Listing/PDP and Evidence Reconciliation.
- Compound buyer questions can become independent atomic jobs when they answer separate decisions.
- Auto-merge requires decision intent + sub-topic + surface + asset family; incremental information cannot disappear merely because jobs share a broad funnel stage.
- `decision_question_audit` and `decision_coverage_summary` make original → atomic → asset lineage explicit.
- Strategy Authority now materializes Consumer Decision Question Coverage and Decision-specific Listing Jobs.
- Decision-topic proof contracts distinguish clinical, formula, performance, compatibility, size/fit, care, seal/leak, weather, usage and comparison evidence.
- Missing economics can no longer emit a false “economics available” offer status.
- Generic P0/P1/P2 repetition is reduced; proof is not created by repeating the proposition.

## Host Strategy Authoring
- The existing `strategy_annotations` contract is operationalized as `artifacts/strategy_host_authoring_request.json`.
- Host/model authoring deepens value translation, Positioning/Value Proposition, message hierarchy, Listing rationale, visual WHY and content logic.
- Protected deterministic authorities are rejected if supplied through annotations: Product Truth, claim ledger, Market/Economics/Ads/Experiment calculations, source quality, exact policy, claim/source trace, Final Copy state and asset hashes.
- Human-readable Strategy Authority renders Host Value Translation and Host Strategic Rationale.

## Final Copy hard-boundary refinement
An extra numeric token in authored copy remains blocked unless the same listing field already references an approved Claim containing that number. This allows traced facts such as Anker’s approved 100W-per-USB-C Claim to enter the referenced highlights field without weakening numeric drift protection.

## Production boundary
This release does not fabricate real image/video Provider execution for the four public products. Exact product masters/provider connectors were not supplied. Asset packages and production contracts compile, but external production remains an explicit boundary.
