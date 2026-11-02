# R06-03 — Canonical Truth → Projection Unification Closure

## Scope

R06-03 closes canonical business truth projection drift only. It does not execute R06-04 Agent Autonomy Restoration, R06-07 external-vendor E2E, or R06-10 final repository debris/release audit.

## Source anchor

- R06-02 locked baseline: `ca28481da8737a04bce000ae0afb5d5dc2167fad`
- Implementation head before this closure trigger: `91dda4d9ccac37eda24642e1149976021a4a35bd`

## RED evidence

Formal RED #1 on `r06-03-red-staging`:

- workflow run `41512182383`
- result: `4 failed / 29 passed`
- exact gaps:
  1. `build_project()` did not materialize `canonical_commerce_graph.json` even though the canonical graph module existed;
  2. `08_copy.md` and `14_visible_copy_block.json` could diverge under freshly rebuilt lineage;
  3. `12_design_card.json` and `13_prompt_contract.json.design_card` could diverge under fresh lineage;
  4. `05/06_prompt_*.txt` and `13_prompt_contract.json` could diverge under fresh lineage.

Formal RED #2 for the final-delivery boundary:

- valid isolated RED commit: `acfb1cc05adc7de425226c16cc171d119315997e`
- result: `1 failed / 35 passed`
- exact failure: final delivery omitted `supporting_analysis/canonical_commerce_graph.json` although project Runtime had materialized the graph.

An earlier RED fixture at `f1b99706bf2550686af51444889e64d2364aa405` failed for unrelated FULL-materialization fixture incompleteness and is explicitly not used as defect proof.

## Root causes

1. Canonical commerce graph was an isolated authority module/test, not wired into the real `build_project()` path.
2. Byte lineage could be freshly rebuilt while semantically conflicting projections remained internally inconsistent.
3. Canonical Human payload could collect conflicting asset projections and self-sign them without a semantic parity guard.
4. Final-delivery support allowlist omitted the newly real canonical commerce graph, severing projection lineage at export.

## GREEN implementation

- `runtime/cbcc/compiler.py`
  - materializes the canonical commerce graph after current project business objects/execution contracts exist.
- `runtime/cbcc/canonical_materialization_integrity.py`
  - adds cross-projection semantic parity checks for Design Card, Visible Copy, production notes, CN/EN prompt text and Prompt Contract.
- `runtime/cbcc/canonical_full_parity_v0671.py`
  - refuses to create/sign Canonical Human payload from internally conflicting asset projections;
  - consumes canonical graph lineage when exported into supporting analysis.
- `runtime/cbcc/delivery_export.py`
  - preserves `artifacts/canonical_commerce_graph.json` in final `supporting_analysis/`.
- `tests/test_v0682_r0603_canonical_projection_unification.py`
  - locks project graph wiring and semantic projection parity.
- `tests/test_v0682_r0603_delivery_graph_projection.py`
  - locks final-delivery graph preservation as observable export behavior.

## Invariants locked by this task

- JSON business authorities remain canonical; Markdown, HTML, model prompts and asset packages are projections, not independent business-truth authors.
- Fresh hash/byte lineage cannot override semantic conflicts between projections.
- Canonical Human payload fails closed on conflicting asset projections instead of signing both versions.
- Project canonical graph lineage survives into final delivery.
- Existing reference-guided default and explicit-only exact-pixel semantics are not changed.
- Existing Provider → Review → Local Revision, measurement/learning, Human Workspace and capability-conservation chains are not removed or replaced.

## Verification authority

This document does not self-certify release success. The exact commit containing this closure must independently pass CURRENT release verification, CURRENT requirement freshness, focused/cross-scope regression, exact artifact download/unpack, and external handoff hash recording before R06-03 may be marked COMPLETE.

Historical `release-v0633` remains a stale version-pinned workflow (`VERSION == 0.6.33...`) and is not CURRENT release authority; repository release-workflow debris is deferred to R06-10 rather than weakening CURRENT to satisfy a historical release script.
