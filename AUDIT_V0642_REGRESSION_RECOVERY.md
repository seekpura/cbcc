# CBCC v0.6.42 Comprehensive Regression-Recovery Audit

## Audit question
Did v0.6.39–v0.6.41 actually upgrade v0.6.36/v0.6.37, or did the delivery layer distort/remove capabilities? Does v0.6.42 recover the agreed behavior without rolling back later commercial/creative improvements?

## Executive conclusion
The major commerce/creative capabilities were mostly still present in source, but v0.6.39–v0.6.41 changed the Host/delivery authority in a way that allowed the actual human artifact to compress, hide or mis-execute them. The main regressions were therefore **execution and human-delivery regressions**, not wholesale source deletion.

v0.6.42 restores the v0.6.36 interaction floor and keeps v0.6.37+ commercial/operator/integrated-render depth as additive capability. It also makes the existing Asset Universe activation-only rule explicit in Host authority and regression tests so a platform gallery limit cannot be reinterpreted as total asset count.

## Baselines
### v0.6.36 interaction baseline
`runtime/cbcc/delivery_html.py` already provides:
- routed primary pages with one active primary work surface at a time;
- dynamic projection of only current project objects;
- module subviews;
- Asset Library → independent `asset/<id>` detail routes;
- asset detail local views;
- Prompt Workbench;
- global/current-page search;
- copy actions;
- responsive desktop/mobile navigation;
- print/PDF projection.

This interaction model is the minimum human-product floor for FULL/high-density projects.

### v0.6.37 additive capability baseline
v0.6.37 added/strengthened:
- integrated commercial image generation authority;
- dynamic video generation authority;
- operator execution density;
- commercial prompt density;
- actual-output QA and smallest repair routing;
- pricing/economics/offer continuity;
- advertising diagnosis;
- review analysis and bounded revision routing;
- stronger Host activation for seven first-class commerce tools.

These are additive. None authorizes removal of v0.6.36 interaction or complete business objects.

## Root-cause audit
### P0-1 — “不要流水线” was misread as “remove stable interaction”
**Regression:** v0.6.39–v0.6.41 authority removed the stable route/subview/detail expectation and allowed entirely project-authored global shells, including one-page narrative or thin object-switcher forms.

**Why wrong:** the rejected “流水线” was the weak sequential/report-like delivery and template thinking, not normal interactive page switching. v0.6.36 already had acceptable interaction.

**v0.6.42:** `delivery_workspace` no longer calls the v0.6.39–v0.6.41 global `project_authored_html()` postprocessor. `delivery_html.py` remains final navigation/content authority.

### P0-2 — Platform gallery capacity was executed as total asset quota
**Regression:** Host execution produced only the platform gallery count (for example 9) instead of planning a larger Asset Universe with live/test/rotation/paid/PDP candidates.

**Why wrong:** existing `asset_universe_authority.py` already states:
- `fixed_total_asset_limit=False`;
- `platform_capacity_is_activation_constraint_only=True`;
- platform capacity limits only simultaneous live activation;
- explicit H01/H02/H03 and other variants survive when they represent independent hypotheses.

**v0.6.42:** Host/contract/defaultPrompt/regression tests now explicitly state Asset Universe ≠ Live Set.

### P0-3 — Operator upgrade changed from additive to replacement/then disappeared
**Regression:** one version injected a giant operator block in front of the project; another removed the operator/commercial addition to avoid the giant block.

**v0.6.42:** Operator Execution + Commercial Brain become a normal routed `运营执行` work surface only when real operator/commercial artifacts exist. It does not replace Strategy, Listing, Visual/Video, Assets, Economics, Ads, Review or Evidence.

### P0-4 — Installed Host/Canonical authority drift
**Regression:** plugin manifest version, Host Skill version and `resources/SKILL.md` version diverged; installed Host/Canonical Skills were materially shorter than the root canonical authority.

**v0.6.42:** current hotfix installation aligns both Host and resource Skill on v0.6.42 critical authority. Formal release builder additionally rebuilds canonical `resources/SKILL.md` from root `SKILL.md` and applies a package-size/authority guard.

## Capability acceptance matrix

| Capability / requirement | v0.6.36 | v0.6.37+ | Regression in 39–41 | v0.6.42 acceptance |
|---|---|---|---|---|
| Product Truth / claim / evidence | KEEP | deepened | could be compressed in human UI | KEEP + directly inspectable |
| Market / audience / culture research | KEEP | deepened | could become summary only | KEEP |
| Product Strategy / SKU / Positioning | KEEP | deepened | could be hidden behind thin workspace | KEEP |
| Pricing / Economics / Offer | v36 seven-tool continuity | strengthened | operator/HTML visibility inconsistent | KEEP; explicit inputs only; `MISSING_INPUT` preserved |
| Listing final publishable copy | KEEP | strengthened | could be summary/hidden | KEEP; directly readable/copyable |
| Localization / transcreation | KEEP | strengthened | no intended deletion | KEEP; target original + Chinese meaning/use |
| Visual master / Art Direction | KEEP | strongly strengthened | human artifact could show thin cards | KEEP full depth |
| Photography / Lighting / CMF | KEEP | Production Parameter Closure strengthened | prompt/UI could collapse selected parameters | KEEP; selected generation-changing parameters must survive |
| Product fidelity / source reference | KEEP | reference-guided native generation strengthened | no intended rollback | KEEP |
| Integrated final image generation | partial/earlier | explicit default in v37 | Host restrictions previously distorted route | KEEP; no global no-text/no-product/post-compose rule |
| Dynamic Asset Universe | KEEP | strengthened | Host wrongly capped at platform slots | RECOVERED + regression test |
| Multi-Hero H01/H02/H03 | KEEP | explicit variant identity | Host output could collapse | RECOVERED + guarded |
| Multi Benefit / Proof variants | KEEP | explicit variants | Host output could collapse | RECOVERED + guarded |
| Paid Ad variants | capability exists | advertising diagnosis deepened | gallery count could suppress paid universe | RECOVERED + guarded |
| PDP / A+ / Detail / Longform | capability exists | asset universe strengthened | could be excluded by gallery quota | RECOVERED + guarded |
| Store / Banner / Campaign / Seasonal | capability exists | dynamic universe | could be excluded by gallery quota | RECOVERED + guarded |
| Social / Creator / UGC | capability exists | dynamic universe | could be excluded by gallery quota | RECOVERED + guarded |
| Video variants / narrative | KEEP | dynamic narrative authority | risk of one fixed timeline | KEEP + anti-template authority |
| Advertising Optimization | seven-tool | deepened | could disappear from human artifact | KEEP; Commercial Brain/operations visibility |
| Review Analysis | seven-tool | deepened | could disappear from human artifact | KEEP |
| Actual-output QA | earlier review | strongly deepened | could be hidden | KEEP per asset |
| Smallest repair route | earlier repair | deepened | could be hidden | KEEP per asset |
| Model Prompt CN | KEEP | production density deepened | could be hidden in files | KEEP directly inspectable |
| Model Prompt EN | KEEP | production density deepened | could be hidden in files | KEEP directly inspectable |
| Visible Copy Block | KEEP | clarified | could be hidden | KEEP directly inspectable |
| Production / Assembly Notes | KEEP | clarified | could be hidden | KEEP directly inspectable |
| Chinese-first human delivery | KEEP | strengthened | no intended rollback | KEEP |
| Route-level interaction | KEEP | should remain | REGRESSED | RECOVERED |
| Module subviews / lenses | KEEP | should remain | REGRESSED/uncertain | RECOVERED |
| Asset detail routes | KEEP | should remain | REGRESSED | RECOVERED |
| Search / copy | KEEP | should remain | REGRESSED by shell replacement risk | RECOVERED |
| Responsive / print/PDF | KEEP | should remain | shell replacement risk | RECOVERED |
| Operator-ready execution | partial | v37 strengthened | first over-injected, then removed | RECOVERED as additive route |
| Runtime/Gate/hash as secondary | KEEP principle | v37 clarified | risk of state-first UI | KEEP as Inspector, not main content |
| No fabricated economics | KEEP | explicit v37 authority | one bad host artifact fabricated sample prices | RECOVERED + Host rule |

## Required asset behavior example
If the platform gallery capacity is 9 and the useful candidates are:
- H01/H02/H03 = 3 Heroes;
- B01–B06 = 6 benefit/proof candidates;
- AD01–AD04 = 4 Paid Ads;
- PDP01 = 1 PDP/A+ object;
- VID01 = 1 video;
then Asset Universe = 15, not 9. The platform may select at most 9 relevant gallery candidates for the current Live Set; Paid/PDP/Video/Test/Rotation objects remain in their own pools and are not deleted.

## v0.6.42 verification completed
- Local delivery-workspace smoke: routed page model, sidebar, asset detail route, local view, copy and search preserved; operations/commercial brain added as a routed page; v0.6.39–v0.6.41 global shell absent.
- Local Asset Universe smoke: 15 candidates + platform capacity 9 retained 15 candidates, 3 Hero variants, 4 Paid Ads, PDP content and video; capacity remained activation-only.
- Installed plugin readback: manifest v0.6.42; Host Skill v0.6.42; resource Skill v0.6.42; final `delivery_workspace.py` no longer imports/calls `project_authored_html`; `data-route="operations"` present.
- Formal CI workflow now builds the actual v0.6.42 ZIP, unpacks that ZIP and runs package guards against the unpacked installable plugin.

## Still not allowed to claim yet
- GitHub Actions has not executed any test step because the GitHub-hosted job repeatedly returns `runner_id=0` and `steps=[]`. A red workflow icon is therefore infrastructure allocation failure, not test evidence.
- The currently installed v0.6.42 is an in-place recovery overlay containing the critical v0.6.42 Host/Canonical authority and runtime changes. The **formal** builder is designed to package the full root canonical Skill and enforce the larger canonical-size guard, but that full formal archive has not been produced by GitHub Actions while the runner is unavailable.
- A new real FULL KIYUU project invocation/output still needs to be inspected as a user-level acceptance test. Runtime/unit smoke proves the responsibility layers, not the final visual/UX quality of a fresh full artifact.

## Release rule going forward
No future “upgrade” may merge if it does any of the following:
1. removes v0.6.36 routed interaction without a demonstrably superior replacement that preserves all functions;
2. turns platform live capacity into total Asset Universe count;
3. removes or hides multi-Hero / Paid / PDP / Social / Video / Test / Rotation variants;
4. substitutes Operator/Runtime state for complete business content;
5. shrinks Host/Canonical authority enough to lose seven-tool, Asset Universe, integrated-render, per-asset production or interaction-floor rules;
6. claims completion without a real human-artifact acceptance test when the release changes human delivery behavior.
