# Changelog — v0.5.7 Adapter Cursor + Advanced Causal + Terminology + Provider Binding + Prelight Depth

## Development principle
Cumulative enhancement from v0.5.6. No architecture restart, no fixed asset count, no Gate expansion as progress, and no reduction of the existing nine-section Strategy Authority or `00–11` asset package / Provider / Review / Local Revision / Package Hash chain.

## 1. Marketplace / Search / Review adapter families + cursor/checkpoint
`research_source_adapters` now supports explicit adapter families:
- `MARKET_SNAPSHOT` → `market_rows`
- `MARKETPLACE_LISTINGS` → `competitor_listing_rows`
- `SEARCH_DEMAND` → `market_keyword_rows`
- `REVIEW_VOICE` → `market_review_rows`

Each adapter may preserve `cursor_field`, previous/next cursor, batch/page metadata, high-watermark, `has_more`, primary-key change set, and resumable refresh state. Cursor/checkpoint metadata is explicitly not treated as proof of exhaustive coverage.

## 2. Advanced causal-design interpretation
Experiment analysis now adds design-specific diagnostics for:
- cluster randomization: ICC, average cluster size, design effect, approximate sample inflation,
- geo experiments: pre-period pair comparability signals,
- CUPED: supplied pre/outcome correlation and approximate variance-reduction planning context,
- sequential monitoring: conservative Bonferroni-style boundary diagnostics.

These are planning/review aids. The runtime does not replace cluster-aware inference, geo-spillover analysis, unit-level CUPED implementation, or formal alpha-spending procedures.

## 3. Terminology memory + cross-field Final Copy consistency
Listing input may provide explicit locale terminology memory with canonical terms, allowed/forbidden variants, required fields and consistency mode.

Runtime now:
- audits title/highlight/description/etc. against supplied terminology memory,
- blocks explicit forbidden-term or required-term violations,
- flags cross-field variant drift for review or blocking when `CANONICAL_ONLY`,
- sends the same terminology memory with Host Authoring Requests,
- keeps Final Copy approval version-bound and professional-review-bound.

The runtime never invents local-language terminology.

## 4. Surface / platform pack → Provider Job binding
Surface Production Contracts now carry compiled platform-pack provenance into Strategy Authority and each asset package. Production run compilation adds immutable contract binding metadata:
- surface production contracts,
- platform pack binding,
- layout contract hash,
- photography contract hash,
- shot-level lighting reasoning.

Provider `job.json` carries these bindings. Contract changes require a new frozen package/job. Provider result validation can detect unacknowledged or mismatched supplied contract hashes without implying strategic approval.

## 5. Prelight / test-shot / exposure / polarization / color consistency
CMF/material lighting now compiles a repeatable pre-production capture plan:
- neutral/product-color reference frame,
- label-readability test frame,
- edge/material-response frame,
- reflection-control comparison when applicable,
- conceptual lighting diagram using supplied geometry,
- measured exposure-ratio plan instead of invented ratios,
- conditional polarization comparison,
- shot-family color consistency rules.

These plans are copied into each IMAGE asset's shot-level photography reasoning and therefore into `03_photography_contract.json`.

## 6. Knowledge / Ontology / Prompt Runtime
Added and dynamically selected:
- `PROMPT-ADAPTER-CURSOR` / `KNOW-ADAPTER-CURSOR`
- `PROMPT-ADVANCED-CAUSAL` / `KNOW-ADVANCED-CAUSAL`
- `PROMPT-TERMINOLOGY-MEMORY` / `KNOW-TERMINOLOGY-MEMORY`
- `PROMPT-PRODUCTION-BINDING` / `KNOW-PRODUCTION-BINDING`
- `PROMPT-PRELIGHT-COLOR` / `KNOW-PRELIGHT-COLOR`

Ontology adds AdapterCheckpoint/CursorWindow, ClusterDesign/GeoExperiment/CUPEDPlan/SequentialMonitoringPlan, TerminologyMemory/TerminologyAudit, ProductionContractBinding, PrelightPlan/LightingDiagram/ExposureRatioPlan/PolarizationPlan/ColorConsistencyPlan.

## 7. Compatibility / real fixture validation
- Full compatibility regression: `68 passed` (compatibility signal only, not product-completeness score).
- KIYUU Malaysia TikTok fixture: 9 Strategy Authority sections, 3 dynamic assets, all 3 complete `00–11`, `PRODUCTION=PENDING`, Final Copy remains 2 `DRAFT_REVIEW_REQUIRED` + 2 `TO_AUTHOR`, 0 false `APPROVED_FINAL`.
- All 3 IMAGE packages now contain prelight / lighting diagram / color consistency reasoning and platform-pack-bound Surface Production Contracts.
