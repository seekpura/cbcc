# R06-01 Requirement Authority Reconstruction — Closure Evidence

## Scope
This closure is attribution/governance only. It does not replace the detailed requirement ledgers, does not author commerce strategy, and does not weaken any Product Truth / market / Listing / creative / Provider / Review / Revision / Measurement / Learning capability.

## Source baseline
- repository: `seekpura/cbcc`
- baseline main: `3d8e1822bc3f7a2d653fff8c5cc5f6b333efb259`
- R06-00 immutable tree: `0ea80b3a861658526e4ed65ae2da6ee7941d6a98`

## RED
Characterization test: `tests/test_v0682_r0601_requirement_authority.py`

Initial RED commit: `1bdf0fe692bba295b144f79b7347a8f68f8e40a0`

Initial CURRENT release verifier: run `41481254672`.
Existing stages before the new authority test passed; the run failed when the new R06-01 characterization entered the Phase-8 wildcard. This proves the RED was introduced by the missing authority contract rather than inherited from an already-red baseline.

Additional RED findings found during GREEN work:
1. REQ-028/REQ-029 were classified as later user clarifications but initially had no later-user origin.
2. `file.py::symbol` consumer paths were incorrectly treated as literal filesystem paths.
3. REQ-050 had `tests/test_v0663_real_k01_host_shortcut_audit.py` listed as a business consumer instead of proof-only evidence.
4. the old freshness checker hard-coded the CURRENT override set to exactly REQ-046..048, making the test oracle define future authority.
5. the first loader draft silently defaulted missing derived lineage to `PG-CBCC-01` and used machine `strategy/listing` modules as implicit Human Projection evidence. Both shortcuts were removed before closure.

## GREEN authority contract
`references/REQUIREMENT_AUTHORITY_CURRENT.json` now classifies the active REQ-001..090 set as exactly:
- `USER_CANONICAL`
- `USER_LATER_CLARIFICATION`
- `DERIVED_PRODUCT_PRINCIPLE`
- `ENGINEERING_GUARD`

and records inactive rules under:
- `REJECTED_DEPRECATED`

The overlay is attribution-only:
- detailed cumulative requirement ledgers remain semantic authority;
- consumer maps remain execution-wiring authority;
- tests/workflows/validators/self-PASS are proof/guard surfaces only;
- derived and engineering rows have explicit source-side `derived_from` lineage;
- rejected/deprecated rows have no active business consumer and identify their superseding current rules.

## Direct-vs-derived correction
REQ-013 is explicitly `DERIVED_PRODUCT_PRINCIPLE`, derived from `UC-H-03` (the user requirement that price/sales/claim facts must not be fabricated). The current engineering interpretation may use competitor-price observations as research/scenario evidence but may not present them as verified own-SKU price facts. That interpretation is not represented as verbatim user wording.

## Later clarification lineage
The following project-wide corrections are explicit later-user authority, not generic engineering preference:
- Chinese-first human delivery and Chinese companion meanings;
- non-flowing SaaS-like Human Workspace;
- JSON/MD/HTML/asset/Prompt same-source projection;
- open/dynamic Asset Universe with no fixed 6/9/12 system quota;
- per-asset bilingual Canonical Prompt with actual photography/execution parameters and no governance noise;
- reference-guided real-product fidelity as normal route; exact pixel/composite only when explicitly required;
- construction debris/static deny mechanisms/test scaffolding may not reduce Agent capability.

## Rejected / deprecated rules
The authority file explicitly rejects and supersedes:
- global pixel lock;
- fixed asset count;
- fixed asset order;
- permanent capability-menu workspace;
- fixed camera preset;
- global no-visible-copy;
- validator-as-strategy;
- K01-as-system-template;
- five-file asset shortcut replacing mature packages;
- test oracle / self-PASS as business authority.

## Runtime audit behavior
`runtime/cbcc/requirement_authority.py`:
- loads REQ-001..090 attribution without rewriting their business semantics;
- aggregates CURRENT consumer wiring;
- validates direct-user and later-user origin classes;
- requires explicit `derived_from` for every derived/engineering row;
- rejects test/workflow paths as business consumers;
- checks consumer path existence while correctly handling `file.py::symbol` references;
- rejects deprecated rules with active business consumers;
- checks P0 direct-user anchors for real runtime and Human projection coverage;
- does not treat generic strategy/listing machine modules as Human projection proof;
- does not fabricate missing lineage.

## CURRENT override correction
REQ-050 is overridden so its historical K01 regression test is proof-only. Its business consumers remain reference/runtime authorities.

`scripts/check_v0664_requirement_consumer_map.py` now reads the CURRENT override set declared by `REQUIREMENT_CONSUMER_MAP_CURRENT_OVERRIDES.json`; REQ-046..048 remain mandatory release-process rows, but the checker no longer hard-codes the entire future override set.

## Permanent release protection
- `current-requirement-freshness.yml` runs the R06-01 authority test and freshness tests when authority inputs change.
- `current-release-verification.yml` runs the authority regression with the cumulative release suite.
- the exact built plugin must contain one `resources/references/REQUIREMENT_AUTHORITY_CURRENT.json` whose bytes are exactly identical to the source authority file.
- `SOURCE_REQUIREMENT_NON_REGRESSION_LOCK.md` and the CURRENT loading map require attribution loading before semantic execution and preserve the proof-only boundary.

## Verification already observed before task-close
At commit `3b43c94ba2573e048577a02f9f137f5c4390d3fd`, CURRENT release run `41485369645`, job `125414173761` completed all substantive build/test/package steps successfully, including:
- Phase 5, 6, 7 and 8 maturity regression suites;
- R06-01 authority regression;
- current requirement accounting;
- stable CURRENT build;
- exact ZIP authority byte-parity proof;
- CURRENT package checker;
- v0.6.70–v0.6.75 cumulative release checks;
- verified artifact metadata and artifact upload.

The final task-close commit must rerun these guards. This document alone is not completion evidence.

## Capability conservation
No Product Truth, Market, Economics, Listing, Culture, Visual, Dynamic Asset, Prompt, Provider, Review/Revision, Measurement/Learning or Human Workspace business compiler was replaced by the authority overlay. The task changes attribution, consumer accounting, release guards and proof classification only.
