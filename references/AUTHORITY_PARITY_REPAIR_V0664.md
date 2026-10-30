# v0.6.64 Installed Authority Parity Repair

## Why this release exists
Post-install readback of actual plugin release `0.6.63` proved that Runtime changes landed, but current packaged authority was still inconsistent:
1. `resources/references/CONVERSATION_REQUIREMENT_AUDIT.md` was a heading-only ~3.6KB projection instead of the detailed cumulative REQ-001..050 ledger;
2. `resources/references/SOURCE_REQUIREMENT_NON_REGRESSION_LOCK.md` still identified v0.6.62 and pointed to the old implementation matrix;
3. `resources/references/REQUIREMENT_IMPLEMENTATION_MATRIX_V0663.md` was missing from the installed plugin.

This is a release-parity defect even though the real-K01 Runtime audit itself is present.

## v0.6.64 repair requirements
The actual installed plugin must contain, simultaneously:
- detailed `CONVERSATION_REQUIREMENT_AUDIT.md` with substantive REQ-001..050 definitions, not headings only;
- `CONVERSATION_REQUIREMENT_LEDGER_EXTENSION_01.md` for REQ-051..060;
- verbatim `USER_LONG_REQUIREMENTS_STRATEGY_CULTURE_EXECUTION_CN.md`;
- current `REQUIREMENT_IMPLEMENTATION_MATRIX_V0664.md`;
- current `SOURCE_REQUIREMENT_NON_REGRESSION_LOCK.md` pointing to v0.6.64 authorities;
- `REAL_K01_HOST_SHORTCUT_AUDIT_CLOSURE_V0663.md` and the v0.6.63 Runtime audit behavior;
- top Skill and `resources/SKILL.md` byte-identical and current;
- `plugin.json`, `.codex-plugin/plugin.json`, both Skills and `resources/VERSION` on the same 0.6.64 family.

## Completion proof
After installation, re-read the actual plugin. Source ZIP/build intent is not proof. At minimum verify manifest version, top/deep Skill version+size/content parity, VERSION, detailed ledger size/content, current matrix presence, current source lock, and the changed Runtime audit. Fresh positive K01 FULL E2E still remains separate and pending until executed through the host/plugin authoring path.