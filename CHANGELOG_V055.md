# v0.5.5 — Evidence + Incrementality + Authoring + Surface Depth

## Intent
Deepen professional decision quality without changing the canonical product architecture. This release strengthens the evidence entering Market/SKU/Listing/Visual strategy and makes execution contracts more surface- and asset-specific. Governance remains a background guardrail.

## 1. Research evidence ingestion and lineage
- New `runtime/cbcc/tools/evidence.py`.
- Exact same-source row fingerprints are detected deterministically.
- Default `dedup_mode=REPORT_ONLY`; analysis changes only when the project explicitly uses `EXACT_SOURCE_ROW`.
- Cross-source content matches are review candidates and are never silently deleted.
- Same explicit entity key with different content becomes a version/conflict review item rather than an automatic overwrite.
- Source records support `logical_source_id`, `version_id`, `supersedes`, observation time and lineage edges.
- `EXPLICIT_SUPERSEDES` is distinguished from a merely observed version sequence.

## 2. SKU switch / cohort / marginal contribution
- Directional switch observations now support `from_sku`, `to_sku`, switch count and explicit eligible-from denominator.
- Switch rate is calculated only when that denominator exists. Shared visitors are not treated as a switch rate.
- Cohort comparability now checks supplied construction/window/channel/market/platform/eligibility metadata before cross-cohort interpretation.
- Holdout arithmetic estimates expected control orders/contribution at treatment size, gross incremental contribution, intervention cost and net marginal contribution.
- The runtime labels causal design readiness but explicitly does **not** claim statistical significance.

## 3. Final Copy author → review → revise → re-review loop
- `_localized_copy_history` selects the current locale × field version.
- Reviews can bind to `version_id` / `revision_id`.
- If copy changes after approval, the current version becomes `REVIEW_STALE_AFTER_REVISION`; the older approval cannot release it.
- Runtime materializes separate authoring, revision and review tasks.
- Delivery includes these task artifacts so host/model/native reviewers can complete the loop without losing version context.

## 4. Platform surface-native authoring
Platform-family strategy remains shared, but actual authoring now changes by surface. Examples include:
- TikTok Shop Search Card / Gallery-PDP / Product Video / Creator / LIVE / Paid-Spark.
- Shopee Search Card / Listing-PDP / Product Video / Chat-FAQ.
- Amazon Search Result / Gallery-PDP / A+ / PDP Video.
- DTC Collection-Search / PDP Modules / Landing-Paid / UGC-Video / CRM.

Each row carries entry state, first line/frame job, message density, proof rule, CTA logic, measurement and avoid rules.

## 5. Asset-level photography causal WHY
Every IMAGE asset now receives a causal chain:
`Consumer Question → required decision visibility → perspective/composition → material/light treatment → purchase barrier → surface/business metric`.

The reasoning is written into Strategy Authority and copied into each applicable asset package `02_visual_spec.md` and `03_photography_contract.json`, so a master camera recipe is no longer treated as the explanation for every image.

## 6. Runtime-consumed professional authorities
Added Knowledge / Prompt / Ontology objects for:
- evidence ingestion + source lineage,
- marginal contribution / holdout interpretation,
- copy iteration/version review,
- asset-level photography causal reasoning.

They are dynamically selected by `strategy_reasoning_context.json` and bound into the relevant Strategy Authority sections.

## Non-regression contract
- Nine formal Strategy Authority sections remain.
- Dynamic asset count remains question/job/surface/increment driven.
- Every activated asset retains `00` through `11`.
- Provider Job → Provider Result → Review Item → Local Revision → Package Hash remains intact.
- No new Gate system was introduced.
