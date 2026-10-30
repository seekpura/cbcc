# CBCC Requirement Implementation Matrix — v0.6.62

## Reading rule
This matrix is the implementation ledger for `REQ-001..REQ-060`. It does **not** replace the verbatim requirement sources. A row is only `IMPLEMENTED` when the requirement has a real consumer at the layer it governs. `E2E_PENDING` means source/runtime/package logic exists but a fresh real FULL K01 run is still required before behavior can be called closed.

Status vocabulary:
- `IMPLEMENTED` — concrete source + runtime/human/package consumer exists.
- `PACKAGE_ENFORCED` — FULL package audit blocks the known regression.
- `E2E_PENDING` — implementation exists but fresh real FULL output/provider evidence has not yet been re-run.
- `SOURCE_LOCKED` — source continuity is protected, but this row is mainly release-governance rather than a runtime business object.

| REQ | Requirement | Authority / source | Real consumer | Human / package evidence | Status |
|---|---|---|---|---|---|
| REQ-001 | Additive-only evolution | `MASTER_CONSTRUCTION_CONTRACT.md`; cumulative ledger | release builders + source non-regression lock + installed-parity checks | release matrix / plugin source parity | SOURCE_LOCKED + E2E_PENDING |
| REQ-002 | Agent owns decisions | Skill; `dynamic_asset_curation.md`; Art Direction contract | asset architecture / Agent-authored `asset_art_direction`; compiler consumes, does not invent | Design Card + asset detail | IMPLEMENTED + E2E_PENDING |
| REQ-003 | Auto-complete, not gate workflow | verbatim long requirement; ledger | `long_requirement_runtime.py` max-10 + continue-under-assumptions | Information Audit / assumptions / continuation rule | IMPLEMENTED |
| REQ-004 | Validation is evidence, not product | source lock; K01 negative fixture | package audits explicitly separate actual output from planned QA | FAIL when Provider/Review/media absent | PACKAGE_ENFORCED + E2E_PENDING |
| REQ-005 | Host-native / Skills-only first-class | `full_delivery_materialization_authority.md` | `audit_host_full_package`; mature package-path checks | FULL materialization audit | PACKAGE_ENFORCED + E2E_PENDING |
| REQ-006 | Seven first-class commerce tools | Skill; Business Density contract | seven-tool runtime / commercial continuity | Human business objects / operations | IMPLEMENTED + E2E_PENDING |
| REQ-007 | FULL nine-domain depth | verbatim source; Business Density contract | `full_delivery_depth_v3.py` | nine semantic business objects in strategy/HTML | IMPLEMENTED + E2E_PENDING |
| REQ-008 | Product Truth four-way + A/B/C | verbatim source | `strategy_depth_projection_v3.py`; `full_delivery_depth_v3.py` | Product Truth / value ladder | IMPLEMENTED |
| REQ-009 | Claim → Evidence → Asset trace | Product Truth / Listing / asset contracts | claim/source trace + asset manifests/source trace | Listing trace + per-asset `10_source_trace.md` | IMPLEMENTED + E2E_PENDING |
| REQ-010 | Platform/region/audience/culture WHY | verbatim source | `long_requirement_runtime.py` `context_why`; full audit | `1.x 平台 × 区域 × 人群 × 族裔文化 WHY` | IMPLEMENTED |
| REQ-011 | Intersectionality | verbatim source | `strategy_depth_projection_v3.py`; V3 full audit | intersectionality table / culture context | IMPLEMENTED |
| REQ-012 | RACE/STP/JTBD/AIDA/FABE/4P applied | verbatim source | strategy depth / framework relationships / RACE rows | framework decision section + RACE execution table | IMPLEMENTED |
| REQ-013 | Economics input integrity | Business Density; verbatim source | economics runtime + `long_requirement_full_audit.py` price-ahead-of-economics blocker | Economics status / UNKNOWN/MISSING_INPUT | IMPLEMENTED + E2E_PENDING |
| REQ-014 | Complete Listing object | Listing authority / Business Density | listing compiler / final-copy workflow | publishable Listing fields + Chinese companion | IMPLEMENTED + E2E_PENDING |
| REQ-015 | Review/CS/returns feedback loop | Review Analysis authority | performance-learning / revision routing | Review/CS/Return → Local Revision | IMPLEMENTED + E2E_PENDING |
| REQ-016 | Chinese-first no density loss | Human language authority | human rendering / language audit | Chinese canonical HTML | IMPLEMENTED + E2E_PENDING |
| REQ-017 | Target language + EN baseline + CN meaning | language contract | listing/visible-copy projection | same-object target/EN/CN companions | IMPLEMENTED + E2E_PENDING |
| REQ-018 | HTML complete human workspace | Workspace continuity contract | delivery renderer + package audit | standalone `index.html` | IMPLEMENTED + E2E_PENDING |
| REQ-019 | Open-world Asset Universe | Asset Universe contract | `asset_universe_authority.py` + `asset_universe_family_audit.py` | `ASSET_UNIVERSE.json` | IMPLEMENTED + E2E_PENDING |
| REQ-020 | No silent family omissions | Asset Universe contract | `asset_universe_family_audit.py` 12-family audit | COVERED / NOT_NEEDED / TO_VERIFY / MISSING_INPUT + WHY | IMPLEMENTED |
| REQ-021 | Preserve real A/B variants | Asset Universe contract | `asset_universe_authority.wrap_build_asset_architecture` | variant IDs / hypothesis / pool | IMPLEMENTED + E2E_PENDING |
| REQ-022 | Presence independent from Fidelity | Art Direction + Asset Universe | per-asset presence object; integrated route authority | Product Presence audit / Design Card | IMPLEMENTED + E2E_PENDING |
| REQ-023 | No product-everywhere default | Asset Universe contract | `product_presence_portfolio_audit` | visible/absent counts + all-visible review flag | IMPLEMENTED + E2E_PENDING |
| REQ-024 | Anti-template / portfolio rhythm | Prompt Art Direction contract | portfolio duplicate/rhythm audits; Art Direction fields | per-asset delta + portfolio review | IMPLEMENTED + E2E_PENDING |
| REQ-025 | Integrated final render default | current Skill; K01 negative fixture | `integrated_render_route_authority.py` | Model Prompt + renderer recipe | IMPLEMENTED + E2E_PENDING |
| REQ-026 | Composite/no-copy/absent are per-asset | current Skill | integrated route authority + package prompt contradiction audit | per-asset copy/product route | IMPLEMENTED |
| REQ-027 | Reference-guided native product default | current Skill | `integrated_render_route_authority.py` | `REFERENCE_GUIDED_NATIVE_LOCK` + provider binding | IMPLEMENTED + E2E_PENDING |
| REQ-028 | Compiler cannot invent product/text/layout | Art Direction contract | compiler consumes structured asset; package contradiction audit | Design Card / prompt route | IMPLEMENTED + E2E_PENDING |
| REQ-029 | Visible Copy may be integrated | current Skill | integrated route authority inserts exact copy into Prompt when selected | Prompt CN/EN + Visible Copy Block | IMPLEMENTED + E2E_PENDING |
| REQ-030 | Structured Art Direction before Prompt | Prompt Art Direction contract | `full_art_direction_preservation.py`; asset compiler | `asset_art_direction` + `02_visual_spec.md` + Design Card | IMPLEMENTED + PACKAGE_ENFORCED |
| REQ-031 | Photography derived per scene | Prompt Art Direction contract | photographic route / parameter preservation | per-asset camera/light/WHY | IMPLEMENTED + E2E_PENDING |
| REQ-032 | People/inclusion full execution object | verbatim source | `long_requirement_runtime.py`; photography compiler | deep-skin/exposure/hair/body/disability/age/bias | IMPLEMENTED |
| REQ-033 | Prompt = lossless model projection | Semantic Membrane contract | normalize → compile → integrated route → final membrane | Model Prompt CN/EN + trace | IMPLEMENTED |
| REQ-034 | Prompt cannot collapse to camera/style only | Prompt Art Direction contract | prompt consumption/depth audits | dense Prompt / Design Card | IMPLEMENTED + E2E_PENDING |
| REQ-035 | Concrete parameter consumption audit | source lock / Prompt contract | prompt consumption audit + v0.6.58 concrete-value tests | missing decision report / Prompt readiness | IMPLEMENTED + E2E_PENDING |
| REQ-036 | Four production objects | Prompt contract | asset compiler | Prompt CN/EN + Visible Copy + Production Notes | IMPLEMENTED + PACKAGE_ENFORCED |
| REQ-037 | Full asset package, no five-file shortcut | FULL materialization authority | `long_requirement_full_audit.py` + asset compiler validator | `asset_packages/<id>/00...15` | PACKAGE_ENFORCED |
| REQ-038 | Provider→Result→Review→Revision→hash | production continuity contract | FULL package audit requires downstream artifacts | Provider/Review/Revision lineage | E2E_PENDING; PACKAGE_ENFORCED |
| REQ-039 | Actual-output QA | Art Direction master contract | package audit rejects prompts-only production completion | actual media + Review Item | E2E_PENDING; PACKAGE_ENFORCED |
| REQ-040 | Smallest defect repair | Review/Revision contracts | revision routing / actual-output review path | Local Revision object | IMPLEMENTED + E2E_PENDING |
| REQ-041 | Measurement/learning loop | Business Density / Review authority | performance learning / strategy revision routing | Learning Ledger / Keep-Kill-Iterate | IMPLEMENTED + E2E_PENDING |
| REQ-042 | Mature routed interaction | Workspace continuity contract | delivery workspace/runtime | one primary route + asset detail/search/back/hash | IMPLEMENTED + E2E_PENDING |
| REQ-043 | No permanent capability-menu shell | Workspace continuity + K01 fixture | FULL package audit `FIXED_CAPABILITY_MENU_SHELL` | project-authored IA required | PACKAGE_ENFORCED + E2E_PENDING |
| REQ-044 | Operations view additive | Workspace contract | delivery workspace | operations as route, not replacement | IMPLEMENTED + E2E_PENDING |
| REQ-045 | Deep FULL business objects | Business Density contract | V3 full audit + delivery object manifests | Economics/Ads/Review/Listing/Visual/etc | IMPLEMENTED + E2E_PENDING |
| REQ-046 | Re-read cumulative requirements each release | cumulative ledger / source lock | canonical loading map / builders | release provenance | SOURCE_LOCKED |
| REQ-047 | GitHub main source of truth | project authority | release development workflow | commits / VERSION / builders | IMPLEMENTED |
| REQ-048 | Installed-plugin parity proof | Authority Source Parity Lock | plugin parity validator + post-install readback | two Skills + VERSION + manifest | E2E_PENDING for v0.6.62 |
| REQ-049 | Fresh real FULL fixture required | source lock | release acceptance process | real K01 FULL package inspection | E2E_PENDING |
| REQ-050 | K01 2026-10-30 negative fixture | `K01_2026-10-30_REAL_OUTPUT_REGRESSION.md` | package audits + regression tests | old K01 must FAIL | IMPLEMENTED |
| REQ-051 | Verbatim long requirements mandatory | verbatim source + extension | canonical loading map | packaged reference source | SOURCE_LOCKED |
| REQ-052 | Audit→≤10 questions→assumptions→continue | verbatim source | `long_requirement_runtime.py` + full audit | Info Audit / decision log | IMPLEMENTED |
| REQ-053 | Four-way Product Truth + A/B/C required | verbatim source | V3 strategy/full audit | Product Truth grading table | IMPLEMENTED |
| REQ-054 | Every major strategy has four-context WHY | verbatim source | `long_requirement_runtime.py` + audit | context-WHY table | IMPLEMENTED |
| REQ-055 | P0 claims/regulatory checks | verbatim source | six-area P0 checklist + full audit | P0 compliance table | IMPLEMENTED |
| REQ-056 | Intersectionality + operational culture checks | verbatim source | V3 intersectionality + five culture execution columns | culture table + Content Matrix RACE/culture | IMPLEMENTED |
| REQ-057 | Inclusive photography concrete execution | verbatim source | long requirement runtime / photo contract | deep-skin compensation + reflector plan etc | IMPLEMENTED |
| REQ-058 | Platform execution + localization complete | verbatim source | V3 content matrix / localization rows / human projection | dimensions/duration/cover/subtitles/music/traffic/CTA/landing/UTM + localization | IMPLEMENTED |
| REQ-059 | Resource tradeoff P0/P1/P2 | verbatim source | V3 resource tradeoff / risk priority | keep/cut/why/restore + priority plan | IMPLEMENTED |
| REQ-060 | Nine semantic output objects without fixed UI shell | verbatim source | V3 strategy + workspace/package audits | all nine objects; fixed-shell audit | IMPLEMENTED + E2E_PENDING |

## Current release boundary
The matrix intentionally leaves `REQ-038`, `REQ-039`, `REQ-048`, `REQ-049` and many Human/portfolio rows as `E2E_PENDING`. They require the actual updated plugin and a fresh real K01 FULL run. A source/test-only result must not promote these rows to COMPLETE.

## Release acceptance
A release is not closed by counting `IMPLEMENTED` rows. For every row touched by a change, inspect the downstream object named in the table. For every `E2E_PENDING` row, only a fresh actual FULL project can close it.
