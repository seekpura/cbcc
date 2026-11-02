# R06-01 Requirement Authority Reconstruction — Closure Evidence

## Task state

`R06-01 = SEMANTICALLY CLOSED / FINAL EXACT-HEAD READBACK REQUIRED`

This document is the repository-side closure record for R06-01. The task is signed **COMPLETE only after the repository head containing this file** passes the CURRENT freshness workflow, the complete CURRENT release workflow, and independent exact-ZIP readback. This document alone is never completion evidence.

R06-02 is not started by this closure.

## Scope

This task reconstructs requirement attribution only. It does **not** replace the detailed requirement ledgers, author commerce strategy, or weaken Product Truth / Market / Economics / Listing / Culture / Visual / Dynamic Asset / Prompt / Provider / Review / Revision / Measurement / Learning / Human Workspace capabilities.

The authority model is intentionally five-plane:

1. `USER_CANONICAL` — only direct original user requirements.
2. `USER_LATER_CLARIFICATION` — only direct later user corrections/additions.
3. `DERIVED_PRODUCT_PRINCIPLE` — normalized professional/product inference with explicit lineage.
4. `ENGINEERING_GUARD` — implementation/release protection that cannot author business strategy.
5. `REJECTED_DEPRECATED` — superseded or prohibited historical mechanisms with zero active business consumers.

## Source baseline

- repository: `seekpura/cbcc`
- R06-01 source baseline: `3d8e1822bc3f7a2d653fff8c5cc5f6b333efb259`
- R06-00 immutable tree reference: `0ea80b3a861658526e4ed65ae2da6ee7941d6a98`

## RED #1 — authority contract did not exist

Characterization test: `tests/test_v0682_r0601_requirement_authority.py`

- RED commit: `1bdf0fe692bba295b144f79b7347a8f68f8e40a0`
- CURRENT release run: `41481254672`
- result: existing cumulative stages passed before the new R06-01 test failed with `ModuleNotFoundError: runtime.cbcc.requirement_authority`.

This isolated the first defect: CURRENT had cumulative requirement ledgers/consumer maps but no first-class attribution contract separating user authority from derived/engineering/deprecated rules.

## RED #2 — circular self-proof and normalized REQ over-attribution

The first GREEN candidate exposed a deeper problem: the loader reconstructed `direct_user_requirement_ids` and `later_user_requirement_ids` from the same `authority_assignments` being audited. That meant a row could first be labelled `USER_*` and then use the same label set as proof that it was genuinely user-authored.

A stricter source-independent test was committed at:

- RED commit: `f8605625f6579a2358bd891bf63470e5a1162dee`
- freshness run: `41493186806`
- job: `125441226943`
- result: **3 failed / 8 passed**.

The three failures were exactly the intended pollution cases:

1. direct-user set contained normalized/expanded REQs not directly authored by the user;
2. `REQ-003` was represented as `USER_CANONICAL` instead of a derived implementation of `UC-E-01`;
3. `REQ-026` / `REQ-084` represented internal fidelity architecture as later-user wording instead of derived architecture from `UL-06`.

No historical business regression was needed to produce this RED.

## Strict source-authored USER sets

`references/REQUIREMENT_AUTHORITY_CURRENT.json` now independently declares the exact direct USER handles instead of deriving them from the assignment table.

### USER_CANONICAL

Exactly:

`REQ-052 .. REQ-060` — 9 rows.

These are the direct handles for the user's original execution/output lock: information audit→max-10→assumptions→continue, Product Truth four-way+A/B/C, WHY, compliance, intersectionality, inclusive visual execution, platform/localization, P0/P1/P2 tradeoff and the nine semantic output objects.

### USER_LATER_CLARIFICATION

Exactly 5 rows:

- `REQ-004` — tests/gates/PASS are evidence, not the product/strategy author;
- `REQ-016` — Chinese-first human/operator delivery;
- `REQ-018` — complete usable Human Workspace, not a流水席/thin summary;
- `REQ-019` — dynamic/open-world Asset Universe; platform slots constrain Activation only;
- `REQ-027` — ordinary real-product references default reference-guided; exact-pixel/composite is explicit-only.

### Normalized/architectural expansions are DERIVED

Representative corrections:

- `REQ-003 ← UC-E-01`
- `REQ-008 ← UC-H-01`
- `REQ-013 ← UC-H-03`
- `REQ-026 ← UL-06`
- `REQ-032 ← UC-H-05`
- `REQ-061 ← UL-03`
- `REQ-084 ← UL-06`
- `REQ-086 ← UC-E-02`
- `REQ-089 ← UL-02`

Thus internal enum names, canonical graph architecture, Presence/Fidelity independent-axis implementation, scene-derived production closure, full projection architecture, etc. remain professional implementation/product principles and do not impersonate user wording.

## REQ-013 price/economics correction

`REQ-013` is `DERIVED_PRODUCT_PRINCIPLE`, derived from `UC-H-03` — the user's direct P0 requirement that price/sales/claim facts must not be fabricated.

Current derived meaning:

- missing own economics inputs may block a locked own final price/discount conclusion;
- competitor price-band observation, scenarios, assumptions, sensitivity and threshold analysis remain allowed research;
- competitor evidence cannot be represented as verified own-SKU price truth.

This interpretation is explicitly not promoted to verbatim user authority.

## Reference-guided correction

The direct later-user core is `REQ-027 / UL-06`.

Derived implementations include:

- `REQ-026` — per-asset production-route options are not global defaults;
- `REQ-084` — Product Presence and Product Fidelity are separate implementation axes.

The authority layer therefore preserves the user's actual correction while keeping internal architecture in the derived plane.

## Rejected / deprecated rules

The authority file explicitly rejects and supersedes 10 mechanism families, all with `active_business_consumers: []`:

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

A temporary duplicate `REQUIREMENT_AUTHORITY_MODEL_CURRENT.json` that appeared during construction was removed; the release contains only the single CURRENT attribution authority.

## Consumer-plane separation

`runtime/cbcc/requirement_authority.py` separates:

- `runtime/*` → business execution consumers;
- `scripts/*`, `references/*` and other non-runtime support → engineering/support wiring;
- `tests/*`, `.github/workflows/*` → proof-only.

Tests/workflows can never satisfy business-consumer authority. P0 user anchors require real runtime consumption plus real Human projection coverage where applicable.

The loader now preserves `direct_user_requirement_ids` and `later_user_requirement_ids` as independent source declarations; it never reconstructs them from `authority_assignments`. The audit separately compares the declared USER sets with the rows actually assigned to USER classes.

## Permanent release protection

- `current-requirement-freshness.yml` runs all `tests/test_v0682_r0601_*.py` plus cumulative freshness/canonical tests.
- `current-release-verification.yml` runs R06-01 authority regression inside the cumulative Phase 5–8 / package / v0.6.70→0.6.75 release suite.
- the exact built plugin must carry `resources/references/REQUIREMENT_AUTHORITY_CURRENT.json` byte-identically to repository source.
- `SOURCE_REQUIREMENT_NON_REGRESSION_LOCK.md` and CURRENT loading map require authority loading without allowing it to become a second business-decision engine.

## Latest implementation-head verification before this closure document

Implementation head: `c47695f8532b2c35ed64733ddcd691f1df98abc3`  
Tree: `e8d6ec035ca2c0ae751be63aafa5cb089222507b`

Freshness:

- run `41494487065`
- job `125445726031`
- result: SUCCESS, including strict R06-01 tests and cumulative CURRENT freshness/canonical regressions.

Complete CURRENT release:

- run `41494487006`
- job `125445725741`
- result: SUCCESS through Phase 5, 6, 7, 8, prior maturity accounting, stable CURRENT build, exact authority byte parity, CURRENT checker, v0.6.70→v0.6.75 cumulative release checks and artifact upload.

Verified Actions artifact:

- artifact id `13166620257`
- Actions artifact archive SHA256 `00163db52647ec37c59344a13ebbe965367a8a788acbb7b08276d9ac41fcc046`
- inner plugin ZIP SHA256 `3a10e3d8d603fa3cf6fc88251955c2717a272ba3f199cbfdba9d1de76bb18b60`

Independent post-build readback (outside the target self-PASS) verified:

- packaged authority Git blob SHA1 = source Git blob SHA1 `f190fcda072f8f349f383f51689da75442df9888`;
- packaged authority SHA256 = `4cfa2b3f53b291158855c70a2887d6e09f5999837ecc8478bca610481ae6401c`;
- `90` active REQs audited, `0` issues;
- authority counts = USER_CANONICAL 9 / USER_LATER 5 / DERIVED 64 / ENGINEERING_GUARD 12;
- rejected/deprecated count = 10, all zero active business consumers;
- strict lineage checks for REQ-003/008/013/026/027/032/061/084/086/089 passed;
- duplicate authority model file absent.

## Capability conservation audit

Comparison from `3d8e1822...` to implementation head `c47695f...` shows R06-01 touched only authority/loading/consumer accounting/release verification/tests and documentation surfaces. It did **not delete any file** and did not replace Product Truth, Market, Economics, Listing, Culture, Visual, Dynamic Asset, Prompt, Provider, Review/Revision, Measurement/Learning or Human Workspace business compilers.

The only new Runtime module is the attribution/audit overlay itself: `runtime/cbcc/requirement_authority.py`.

Therefore R06-01 changes attribution and proof classification without reducing the Commerce OS capability floor.

## Residual full-system boundary

R06-01 does not claim that every broader Commerce OS E2E objective is complete. In particular, provider actual-media truth must still be judged by the later full-system acceptance criteria rather than by a fixture, test label or self-reported PASS. Any contradictory historical manifest/status remains a later full-system audit target, not something this authority task may silently rewrite.

## Final sign-off rule

After this closure file is committed, **the new exact repository head containing it must again pass**:

1. `current-requirement-freshness`;
2. `current-release-verification`;
3. exact verified artifact download/readback.

Only that post-closure evidence may sign `R06-01 = COMPLETE` in the external handoff and user report.
