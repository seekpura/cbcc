# CBCC Current Canonical Skill Build Authority

## Current rule
The canonical packaged Skill is built additively from the last verified mature Skill floor plus current authorities. `CURRENT` never means “whatever the latest source file happens to say”; VERSION, current builder, packaged override family, top/deep Skill and final ZIP proof must converge on one release family.

For current **v0.6.70**, the builder first reconstructs the exact verified v0.6.69 packaged Skill floor and hard-checks:
- UTF-8 bytes: `48517`;
- SHA256: `f3ed58aafc24947e85fc268144ea787d4db5eaed66b31008f6a5cf87500cbd54`.

Any mismatch blocks the build before v0.6.70 authority is added. v0.6.69 therefore remains the immutable maturity floor for this additive release; v0.6.68 remains the user-approved earlier mature floor underneath it.

## Stable construction contract
1. `VERSION` identifies the current semantic release family and full authority version.
2. `scripts/build_plugin_dist_current.py.CURRENT_BUILDER_TARGET` must equal that family.
3. `references/REQUIREMENT_CONSUMER_MAP_CURRENT_OVERRIDES.json.current_release_version` must equal that family in both repository and final ZIP.
4. The release builder must preserve the exact previous verified Skill floor before adding current authority.
5. Current GitHub resources are copied from current main; historical versioned builders/workflows are provenance/regression evidence, not release-health authority.
6. The canonical Skill is written byte-identically to packaged top `SKILL.md` and `resources/SKILL.md`.
7. Manifest, two Skills, `resources/VERSION`, CURRENT override and CURRENT builder target belong to one family.
8. `scripts/check_current_release_package.py` validates the exact built ZIP before installation.
9. CI records exact ZIP SHA256 + bytes and uploads that exact artifact; installation may use only that verified artifact.
10. Installed plugin parity and active Host Skill snapshot parity are separate evidence.

## v0.6.70 Canonical Materialization + Human Projection contract
Load `V0670_CANONICAL_MATERIALIZATION_PARITY.md` as the real regression authority. This release closes failures observed in the actual v0.6.69 K01 FULL output without redesigning the mature workspace.

Required runtime chain:
- `strategy_culture_materialization.py` — first-class Product Truth / strategy / culture / visual / self-check objects;
- `strategy_culture_completion_v0670.py` — RACE platform, culture script/casting/wardrobe-color-CTA/result/modification, framework measurement, four-context WHY, relevance-aware inclusion dimensions;
- `full_art_direction_preservation.py` — relevance-aware full structured Art Direction;
- `canonical_materialization_integrity.py` — semantic field-domain guard, Visible Copy slot guard, canonical Art Direction hash;
- `canonical_prompt_guard.py` — fail closed before Prompt compilation and stamp one lineage on CN/EN Prompt bundle;
- `integrated_render_route_authority.py` — per-asset integrated/native product-copy route;
- `model_prompt_semantic_membrane.py` — final model-facing orchestration membrane;
- `human_projection_integrity.py` — visible HTML field-consumption + copy/search behavior proof;
- `canonical_materialization_package_audit.py` — final FULL package parity boundary;
- `delivery_export_continuity.py` — canonical parity audit before final re-ZIP.

Canonical Prompt order is:
`named Agent Art Direction → normalize → semantic domain guard → mature compiler → integrated route → final semantic membrane → canonical Art Direction lineage stamp`.

The known v0.6.69 K01 field-shift family (`A01, A02, G08, L01, R01, S01, S02, T01, T02, V01`) must fail semantic package audit rather than being accepted merely because fields are non-empty. Runtime must not auto-shift the values back.

Human delivery rule: embedded DATA is not delivery. When authored, Listing English description/key points/attributes/package contents/FAQ; strategy/value/message/tradeoff; market rules/context WHY; visual HEX/contrast/type/platform/inclusion/Shot List; full platform execution matrix; RACE platform; culture execution checks; risks; Ads; Review status; Sources; and complete per-asset Art Direction must be visibly reachable in the project-authored workspace. Copy and search are behavioral features, not self-reported booleans.

Photography remains relevance-aware. Values selected by the Agent—lens/focal length, working distance, camera geometry, focus/aperture/DOF/shutter/ISO, light roles/modifier geometry/CCT/WB/ratio/reflection/polarization/Prelight, CMF/material response, finishing—must survive into Prompt when relevant. Non-photographic assets may mark them `NOT_NEEDED + WHY`; no fake values are invented to satisfy a checklist.

## Strict requirement accounting
The effective REQ-001..060 map remains:
- base: `REQUIREMENT_CONSUMER_MAP_V0664.json`;
- CURRENT release-process overrides: `REQUIREMENT_CONSUMER_MAP_CURRENT_OVERRIDES.json`.

The strict checker must report exactly 60 requirements, concrete Consumer paths, concrete proof objects, no generic/TBD/TODO placeholders, and current release-process evidence for REQ-046/047/048.

## Current release workflow
`.github/workflows/current-release-verification.yml` remains the stable release path:
`CURRENT requirement freshness → build_plugin_dist_current → exact ZIP → check_current_release_package → SHA256/bytes metadata → upload exact verified artifact`.

`current-requirement-freshness.yml` additionally runs v0.6.69 regression/floor tests and v0.6.70 semantic asset, Human projection, strategy/culture completion, final package and release-floor tests.

## Evidence boundary
Passing source/unit/package tests proves implementation and package integrity, not fresh positive Host behavior. After installation, a fresh Host context that actually resolves v0.6.70 must run the K01 FULL project. Actual Provider Result / media / Review / Local Revision / provenance remains independently `E2E_PENDING` until produced.
