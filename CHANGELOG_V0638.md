# v0.6.38 — Host FULL Delivery Regression Fix

## Trigger
A real v0.6.37 KIYUU FULL test exposed a packaging/host-execution regression: the installed plugin's dense host/canonical Skill authority had been replaced by a short manual overlay. In Skills-only execution the host then produced a shallow fixed dashboard instead of the complete project workspace.

Observed regression symptoms included a fixed eight-route navigation shell, three-card strategy summaries, unsupported RM price options, visual asset cards that hid the real Design Card/Prompt depth in folders, and one fixed video first-frame/choreography presented as the video plan.

## Fix
- Treat Host-native / Skills-only execution as a first-class FULL production path with parity to canonical Runtime delivery depth.
- Add `prompts/host_full_delivery_anti_regression.md` as explicit authority.
- `运营执行台` is the front door only; it cannot replace complete Strategy, Listing, Visual, Video, Economics, Ads, Review or Evidence objects.
- FULL workspace routes are authored from actual project objects and active operator jobs; fixed capability menus/page counts are forbidden.
- Every active asset must expose its complete human Design Card plus Model Prompt CN / Model Prompt EN / Visible Copy Block / Production or Assembly Notes in the primary human artifact.
- Forbid invented prices, budgets, ROAS, fees, CVR or other numeric values used merely to make a UI look complete. Missing economics inputs remain `MISSING_INPUT`.
- Preserve v0.6.37 integrated final visual generation, per-asset product/text decisions, commercial prompt density, decision-derived video and actual-output QA.

## Packaging repair
`scripts/build_plugin_dist_v0638.py` starts from the established dense plugin builder, keeps the full canonical root `SKILL.md` in packaged resources, injects v0.6.37 integrated-render authority plus the v0.6.38 host anti-regression authority, and never substitutes a short compatibility shell.

## Release guard
`scripts/check_plugin_host_authority_density.py` rejects releases when:
- packaged host Skill is under 12 KB;
- packaged canonical Skill is under 70 KB;
- core FULL / creative / prompt / per-asset visibility authorities disappear;
- manifest/default prompt fails to activate v0.6.38 host authority.

This guard is intentionally narrow: byte floors catch catastrophic authority replacement; semantic phrase checks catch capability loss. They are not a general “longer is better” rule.
