# CBCC Current Canonical Skill Build Authority

## Current rule
The canonical packaged Skill is built additively from the last verified mature Skill floor plus current authorities. `CURRENT` never means “whatever the latest source file happens to say”; VERSION, current builder, packaged override family, top/deep Skill and final ZIP proof must converge on one release family.

For current **v0.6.71**, `scripts/build_plugin_dist_v0671.py` first calls the v0.6.70 canonical builder, which itself reconstructs and hard-checks the exact verified v0.6.69 Skill floor:
- v0.6.69 UTF-8 bytes: `48517`;
- v0.6.69 SHA256: `f3ed58aafc24947e85fc268144ea787d4db5eaed66b31008f6a5cf87500cbd54`.

The v0.6.71 builder additionally requires the v0.6.70 canonical Skill floor to remain `54752` UTF-8 bytes and to retain the `0.19 Canonical Materialization + Human Projection Parity` marker before adding v0.6.71 authority. Thus v0.6.69 remains the immutable maturity floor, v0.6.70 remains the semantic/prompt/Human-parity floor, and v0.6.71 is additive rather than a rebase.

## Stable construction contract
1. `VERSION` identifies the current semantic release family and full authority version.
2. `scripts/build_plugin_dist_current.py.CURRENT_BUILDER_TARGET` must equal that family.
3. `references/REQUIREMENT_CONSUMER_MAP_CURRENT_OVERRIDES.json.current_release_version` must equal that family in repository and final ZIP.
4. The release builder must preserve the previous verified Skill floor before adding current authority.
5. Current GitHub resources are copied from the current branch/main; historical versioned builders are provenance/regression evidence, not a replacement release authority.
6. Canonical Skill is written byte-identically to packaged top `SKILL.md` and `resources/SKILL.md`.
7. Manifest, both Skills, `resources/VERSION`, CURRENT override and CURRENT builder target belong to one family.
8. `scripts/check_current_release_package.py` validates the exact built ZIP before installation.
9. CI records exact ZIP SHA256 + bytes and uploads that exact artifact; installation may use only that verified artifact.
10. Installed plugin parity and active Host Skill snapshot parity are separate evidence.

## v0.6.71 Full Canonical Human + Package Lineage contract
v0.6.70 remains fully active underneath this release: semantic field-domain guard, Visible Copy language-slot guard, named Art Direction→Design Card/CN/EN Prompt projection, single canonical lineage, selected photography-parameter consumption, Human field projection, Copy/Search behavior, RACE Platform/culture execution completion and pre-ZIP parity blocking.

v0.6.71 closes the remaining real-package gaps from the v0.6.69 K01 audit:

- `canonical_full_parity_v0671.py` reconstructs the Human payload from the **real final package** (`HUMAN_DELIVERY`, strategy authority, supporting analysis, Asset Universe, asset packages) and writes `CANONICAL_HUMAN_DATA.json`. Real static routed HTML no longer depends on a synthetic `const DATA` fixture.
- every meaningful preserved Canonical Business Object leaf is statically reachable via `data-canonical-path`; generic field coverage blocks silent Human omission.
- `listing_markdown_parity_v0671.py` positively materializes `localized_copy` into `01_LISTING_UPLOAD_READY.md` and audits both `copy_center` and multilingual canonical rows.
- `asset_package_full_lineage_v0671.py` binds every present mature numbered asset file (00–15 family) byte-for-byte to the same canonical Art Direction lineage in `CANONICAL_LINEAGE.json`.
- Human asset projection independently exposes Visual Spec, Photography Contract, Layout Contract, Prompt CN/EN, Source Trace, Strategy Trace, Visible Copy, Production Object and Prompt Contract/lineage rather than collapsing them into one summary card.
- `strategy_execution_completion_v0671.py` requires major authored decisions to consume platform / region / audience / race-ethnicity-culture Context WHY separately. Missing causal evidence remains `TO_VERIFY`.
- intersectionality must materialize interaction-analysis rows with multi-dimension mechanism, evidence/assumption, stereotype guard, execution and verification action; listing five identity labels alone is insufficient.
- `asset_execution_relevance_v0671.py` closes people and Typography dimensions as `SELECTED / TO_VERIFY / NOT_NEEDED + WHY`; unknown identity attributes may never be silently invented as selected facts.
- `canonical_full_package_audit_v0671.py` and `delivery_export_continuity.py` run positive materialization and these parity checks before final re-ZIP.

Current Prompt boundary order is:
`Agent asset → explicit human/typography relevance completion → normalize full named Art Direction → semantic domain guard → mature Prompt compiler → integrated/native route → semantic membrane → canonical lineage stamp`.

## Strict requirement accounting
The effective REQ-001..060 map remains:
- base: `REQUIREMENT_CONSUMER_MAP_V0664.json`;
- CURRENT release-process overrides: `REQUIREMENT_CONSUMER_MAP_CURRENT_OVERRIDES.json`.

The strict checker must report exactly 60 requirements, concrete Consumer paths, concrete proof objects, no generic/TBD/TODO placeholders, and current release-process evidence for REQ-046/047/048.

## Current release workflow
`.github/workflows/current-release-verification.yml` is the stable release path:
`v0.6.71 acceptance aggregate → prior-current regression/requirement freshness → build_plugin_dist_current → exact ZIP → current + v0.6.70 floor checks → SHA256/bytes metadata → upload exact verified artifact`.

Diagnostic workflows/steps are temporary engineering evidence and are not release authority.

## Evidence boundary
Passing source/unit/package tests proves implementation and package integrity, not fresh positive Host behavior. After installation, a fresh Host context that actually resolves v0.6.71 must run the K01 FULL project against the source Excel. Actual Provider Result / generated media / Review / Local Revision / provenance remains independently `E2E_PENDING` until genuinely produced.
