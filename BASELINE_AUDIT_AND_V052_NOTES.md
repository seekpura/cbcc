# Baseline Audit + v0.5.2 Development Notes

## Baseline authority
Source baseline used for this development batch:
`cross-border-commerce-creative-v0.5.1-strategy-depth(1).zip`

Validation sample only:
`CBCC_v0.5.1_KIYUU_strategy_depth_demo(1).zip`

No older v0.3 / v0.4 alpha / v0.5.0 tree was used as a source baseline.

## v0.5.1 continuity confirmed before development

### Strategy Authority
The KIYUU delivery contains:
- `strategy/MASTER_STRATEGY_CN.md`
- `strategy/strategy_authority.json`
- `strategy/EXECUTIVE_SUMMARY.json`
- `strategy/STRATEGY_DECISION_INDEX.json`
- all nine required Strategy Authority section JSONs.

### Independent per-asset package
Every KIYUU sample asset contains the complete existing `00`–`11` sequence, including `03_photography_contract.json` and `11_strategy_authority_trace.json`.

### Review / production / local revision continuity
The KIYUU sample contains the Review Workspace and per-asset review items. Its captured production state is `PENDING`, so it does not pretend that provider jobs/results were executed in that delivery sample.

The v0.5.1 source baseline contains the production/review/revision implementation for:
- package-hash generation and verification;
- Provider Job envelopes;
- Provider Result ingest/validation;
- Review Items / Review Decisions;
- Local Revision requests with `allowed_fields` scope.

These components remain in v0.5.2.

### Knowledge / ontology / prompt runtime
The v0.5.1 sample contains `supporting_analysis/strategy_reasoning_context.json`; source runtime already compiles project-specific reasoning context. v0.5.2 deepens this from registry/hash selection to content-level authority excerpts and explicit nine-section bindings.

## v0.5.2 additive development

### Market / competitor / customer-entry understanding
- conservative raw-field normalization + raw provenance;
- sample capacity / CR3 / CR10 / HHI;
- price distribution / valley hypotheses;
- configuration efficiency/opportunity;
- competitor structural clusters;
- seller efficiency;
- keyword/search demand and intent;
- supplied-label Customer Voice aggregation across theme × sentiment × competitor × audience, with unclassified counts and no free-text semantic invention;
- opportunity map with cross-check requirements and confidence;
- Strategy Authority interpretation cards with WHY/execution/measurement.

### Product / SKU / Offer / Economics
- dynamic SKU roles and confidence;
- price-ladder strategy;
- shared contribution/growth budget across coupon + affiliate + paid media;
- target-contribution headroom;
- break-even ROAS/CPA and coupon/affiliate ceilings;
- scenario/sensitivity analysis;
- results flow into formal Product/SKU/Offer Strategy.

### Positioning / Value Proposition / Message
- explicit target / tension / frame / promise / RTB / alternative / risk reducers / proof boundary;
- P0–P3 message hierarchy;
- Belief Sequence;
- Means–End;
- Signaling;
- Cognitive Budget;
- Commerce Response Ladder;
- formal framework set expanded without turning frameworks into fixed asset templates.

### Listing / Search
- search intent architecture;
- field decision jobs;
- objection routing;
- FAQ / usage / package planning;
- claim/source trace;
- SEO/GEO;
- localization/transcreation;
- human-facing Strategy Authority renders the full listing plan.

### Visual / Photography WHY
- parameter-level WHY for lens, distance, camera geometry, focus/DOF, light geometry, fill/negative fill/rim, CCT/WB, shadow/highlight, reflection/polarization, color management, CMF and casting/styling;
- positive-first creative selection retained.

### Platform Content Matrix
Rows now carry content pillar, message layer, shopper entry/exit state, barrier, belief target, hook type, native-surface logic, reuse/new-production logic, culture adaptation, business hypothesis and job-aligned metrics.

### Dynamic Asset Curation
Default derivation now uses:
`Consumer Decision Question × Strategic Job × Surface Need × Incremental Information × Business Hypothesis`.

Listing objections and communication-type feedback can add missing decision jobs. Duplicate question/job/surface combinations merge by default.

### Ads / Feedback / Iteration
- Ads: eligibility/traffic → click package → PDP/traffic quality → economics → incrementality;
- budget/bid hypotheses and attribution-vs-incrementality distinction;
- Feedback: defect vs communication, category×source, category×severity, frozen-layer local revision routing;
- results are rendered into Strategy Authority.

### Runtime-consumed professional authorities
`strategy_reasoning_context.json` now contains selected professional Prompt/Knowledge content excerpts and section bindings. Ontology was extended with strategy objects that are used by the runtime selection layer rather than added only for count.

### Asset package hardening
Every activated asset now requires all of:
`00_asset_manifest.yaml` through `11_strategy_authority_trace.json`.

`03` and `11` remain explicit status-bearing contracts when not applicable/supplied. Provider Job → Provider Result → Review Item → Local Revision → Package Hash is preserved.

## Compatibility note
The v0.5.2 tree contains every original non-cache file from the uploaded v0.5.1 baseline. This development batch changes existing files in place and adds only v0.5.2 documentation/tests; it does not delete baseline source files.

## Next development priorities
1. Multi-real-product field validation across materially different categories/markets/platforms.
2. Extend the new supplied-label Customer Voice layer with more real-market collection adapters and representative sampling evidence before recommendation synthesis.
3. More product-specific offer/cannibalization/lifecycle reasoning for multi-SKU portfolios.
4. Stronger transcreation and platform-native listing/content authoring for real locales.
5. Only after those, Release Candidate-level validation/packaging.
