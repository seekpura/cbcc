# v0.5.2 Strategy Integration Depth

This build is an additive strategy-depth release on the v0.5.1 Strategy Depth baseline. It does not redesign the architecture and does not replace the independent asset workflow.

## 1. Market / competitor / search interpretation
- Added conservative raw-row normalization with provenance and explicit field mapping.
- Kept category/sample capacity, CR3/CR10/HHI, price distribution/valley signals and configuration analysis, then added competitor structural clusters, seller-efficiency context, keyword/search demand and an explicit market opportunity map.
- Added Customer Voice aggregation for supplied market/competitor review labels: theme, sentiment, competitor, audience, source and examples remain traceable; Runtime deliberately does not auto-classify free text.
- Opportunity outputs distinguish observed signals from recommendations and require demand × product fit × unit economics × platform execution cross-checks.
- Market results now feed human Strategy Authority decision cards instead of remaining calculator sidecars.

## 2. Product / SKU / Offer / Economics
- Dynamic SKU roles now combine explicit role, configuration/bundle, demand signals and unit economics with confidence/rationale.
- Price ladder includes absolute/percentage gaps and is interpreted as a value architecture rather than price spacing alone.
- Coupon, affiliate and paid media are unified into a shared contribution/growth-budget pool.
- Added target-contribution headroom, break-even ROAS/CPA, coupon/affiliate ceilings and one-variable sensitivity scenarios.
- Economics results flow into formal Product/SKU/Offer Strategy.

## 3. Positioning / Value Proposition / Message Architecture
- Added explicit target customer, job/tension, frame, value promise, RTBs, secondary gains, competitive alternative, risk reducers and proof boundary.
- Added P0–P3 message hierarchy, Belief Sequence, Means–End chain, Signaling strategy, Cognitive Budget and Commerce Response Ladder.
- Strategy Authority now formally carries STP, JTBD, RACE, AIDA, FABE, 4P, Funnel, Fogg, Means–End, Signaling, FIRST Hero Gate, Cognitive Budget, Belief Sequence and Commerce Response Ladder as decision lenses rather than asset templates.

## 4. Listing / search conversion architecture
- Added keyword intent/priority roles and decision-stage mapping.
- Added field-level decision jobs, objection routing, usage/package/FAQ planning, localization/transcreation and claim/source trace summary.
- Human Strategy Authority now exposes title, hero, attributes, highlights, description, FAQ, usage, package, PDP sequence, SEO/GEO and localization logic.

## 5. Visual / photography WHY
- Added parameter-level rationale for focal length, working distance, camera height, yaw/pitch/roll, focus plane, aperture/DOF, key/fill/negative-fill/rim, CCT/WB, shadow/highlight, reflection/polarization, color management, CMF and casting/styling.
- Decisions explain consumer/business purpose rather than listing unexplained camera settings.
- Positive-first creative selection remains intact; plants, water, models, props, laboratory cues and scenes remain conditional tools rather than global bans.

## 6. Platform content and dynamic asset curation
- Platform content rows now carry content pillar, message layer, shopper entry/exit state, barrier, belief target, hook type, platform-native logic, reuse/new-production logic and business hypothesis.
- Dynamic asset derivation now uses `Consumer Decision Question × Strategic Job × Surface Need × Incremental Information × Business Hypothesis`.
- Listing objections and communication-type feedback can create missing decision jobs.
- Duplicate question/job/surface assets merge by default; cross-surface repetition requires a real native-surface difference.

## 7. Ads / feedback / learning feedback loop
- Ads diagnosis follows Eligibility/Traffic → Click Package → PDP/Traffic Quality → Economics → Incrementality.
- Added budget/bid hypotheses and explicit attribution-vs-incrementality readiness.
- Feedback now distinguishes product defect from expectation/misunderstanding/usage/package issues and carries category×source, category×severity, revision route and frozen-layer guidance.
- These results are rendered into the final Strategy Authority and route local revisions instead of existing as passive analytics.

## 8. Knowledge / ontology / prompt runtime consumption
- `strategy_reasoning_context.json` now contains project-selected Prompt and Knowledge authority excerpts, not only registry metadata/hashes.
- Each of the nine Strategy Authority sections records its reasoning-authority bindings.
- Ontology adds SearchDemand, CompetitorCluster, MarketOpportunity, SharedGrowthBudget, OfferRoom, SurfaceNeed, BusinessHypothesis, TranscreationContract and IncrementalityEvidence plus their strategy relations/constraints.
- Expanded professional prompt authorities for Market, SKU/Offer, Positioning/Message, Listing, Visual/Photography, Platform Content and Dynamic Asset Curation; runtime selection consumes them.

## 9. Asset package non-regression hardened
- Every activated asset now always materializes the complete `00_asset_manifest.yaml` through `11_strategy_authority_trace.json` package.
- `03_photography_contract.json` remains as an explicit `NOT_APPLICABLE_OR_NOT_SUPPLIED` contract when photography is not applicable/supplied.
- `11_strategy_authority_trace.json` remains even when upstream strategy context is unavailable, recording that status rather than disappearing.
- Provider Job → Provider Result → Review Item → Local Revision → Package Hash continuity remains intact.

## Validation philosophy
Focused regression validation confirms that the deeper strategy integrates through the existing runtime and that the asset/production chain remains intact. Test counts are not used as a proxy for professional completeness; further development should continue with real-product strategy quality and multi-product field validation before Release Candidate work.
