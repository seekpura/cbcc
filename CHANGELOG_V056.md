# Changelog — v0.5.6 Adapter + Causal + Copy + Production + CMF Depth

## Development principle
Cumulative enhancement from v0.5.5. No architecture restart, no fixed asset count, no Gate expansion as a progress metric, and no reduction of the established `00–11` asset package / Provider / Review / Local Revision / Package Hash chain.

## 1. Source Adapter + incremental research refresh
Added `runtime/cbcc/tools/source_adapters.py` and Runtime integration for host-supplied competitor/search/review datasets.

New capabilities:
- explicit adapter ID and target research dataset,
- schema/field maps,
- `FULL_SNAPSHOT` vs `INCREMENTAL_BATCH`,
- explicit primary keys,
- added / changed / removed row change-set,
- updated-at high-watermark,
- optional prior refresh state,
- source-record injection,
- semantic near-duplicate candidate review.

Important boundary: semantic near-duplicates are `REPORT_ONLY_NEVER_AUTO_DELETE`. A high-watermark is ingestion provenance, not proof of freshness or completeness.

Materialized artifacts:
- `artifacts/research_source_adapter_refresh.json`
- `artifacts/research_source_adapter_state.json`

Adapter rows feed the same Market Strategy Authority instead of remaining a sidecar ingestion report.

## 2. Experiment / causal-design depth
Extended `runtime/cbcc/tools/experiment.py` with:
- assignment/randomization review,
- pre-period standardized-difference diagnostics,
- baseline + absolute/relative MDE planning,
- approximate two-proportion required N per arm,
- contamination / spillover / interference review,
- segmented outcome summaries with explicit exploratory boundary.

Existing binary experiment output remains backward-compatible at the top level. Design quality now enters Strategy Authority / risk interpretation before scale decisions.

## 3. Portfolio marginal contribution by segment/cohort
Holdout marginal-contribution rows now preserve `segment`, `cohort`, and `period` and compile an arithmetic segment/cohort rollup.

Boundary remains explicit: segment/cohort arithmetic is not proof of heterogeneous treatment effect.

## 4. Host/model-assisted Final Copy loop
Added host response orchestration:
- Runtime emits author / revise / review tasks,
- host/model can return locale × field authored copy,
- every response creates a NEW version event,
- parent version / task metadata are preserved,
- host generation cannot approve its own output,
- old review is stale when a newer version exists,
- current version must pass deterministic hard checks + explicit native/claim/platform/culture review.

New artifacts:
- `artifacts/listing_copy_host_authoring_requests.json`
- `artifacts/listing_copy_host_authoring_apply.json` when responses are supplied.

## 5. Surface Production Contracts
Platform Content Matrix now carries a `surface_production_contract` in addition to authoring logic.

Contracts cover:
- entry state / decision job,
- working media intent,
- first-frame/first-line requirement,
- safe-zone/copy-density logic,
- motion/demo logic,
- audio/caption logic,
- product-fidelity / proof visibility,
- master-asset reuse vs recompose,
- measurement,
- explicit platform-policy authority boundary.

Exact pixel/duration/file limits remain sourced from platform packs/current policy rather than being invented by generic runtime guidance.

Surface Production Contracts now flow into each activated asset's:
- `04_layout_contract.json`
- `09_production_notes.md`

## 6. CMF / material-specific shot-level lighting
Visual/Photography Strategy now compiles a `material_lighting_profile` from supplied CMF only.

It distinguishes practical optical concerns for explicitly supplied material/finish signals such as:
- clear/glass/translucent,
- glossy plastic/lacquer,
- metal/foil,
- matte/paper/soft-touch.

Each IMAGE asset receives `shot_lighting_reasoning` explaining:
`Consumer Question → decision visibility → supplied CMF/material response → key geometry → fill/negative fill → highlight/reflection control → color management → purchase barrier → metric`.

If material behavior is under-specified, Runtime marks the setup provisional and requires a material test rather than inventing a finish.

## 7. Knowledge / Ontology / Prompt Runtime
Added and dynamically selected:
- `PROMPT-SOURCE-ADAPTERS` / `KNOW-SOURCE-ADAPTERS`
- `PROMPT-CAUSAL-EXPERIMENT` / `KNOW-CAUSAL-EXPERIMENT`
- `PROMPT-HOST-COPY` / `KNOW-HOST-COPY`
- `PROMPT-SURFACE-PRODUCTION` / `KNOW-SURFACE-PRODUCTION`
- `PROMPT-CMF-LIGHTING` / `KNOW-CMF-LIGHTING`

Ontology now includes SourceAdapter / RefreshState / ResearchChangeSet / SemanticDuplicateCandidate / ExperimentDesign / PowerPlan / BalanceDiagnostic / InterferenceRisk / HostAuthoringResponse / SurfaceProductionContract / MaterialLightingProfile / ShotLightingReasoning and their relations.

## 8. Non-regression / validation
- v0.5.5 baseline paths preserved: `369 / 369`
- missing baseline paths: `0`
- added professional-depth/test files before version documentation: `12`
- full compatibility regression: `67 passed`

The test count is a compatibility signal only, not a product-completeness score.

KIYUU fixture recompile:
- nine formal Strategy Authority sections preserved,
- dynamic asset count remains `3`, not forced to 6/9/12,
- all 3 assets retain complete `00–11`,
- all 3 IMAGE packages carry asset-specific photography reasoning,
- Surface Production Contract is materialized in asset production/layout files,
- Final Copy remains 2 `DRAFT_REVIEW_REQUIRED` + 2 `TO_AUTHOR`, 0 false `APPROVED_FINAL`,
- `PRODUCTION = PENDING`; no fabricated Provider Result.
