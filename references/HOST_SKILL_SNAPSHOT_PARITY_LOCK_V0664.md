# Host Skill Snapshot Parity Lock — v0.6.64

## Why this lock exists
During the v0.6.63 release, the actual plugin store was updated and read back as version `0.6.63`, while the already-open conversation's `skills://plugins/cross-border-commerce-creative/...` resource still returned the previous `0.6.62` Skill snapshot.

Therefore an installed-plugin update and a Host conversation Skill snapshot are two different pieces of evidence. A same-conversation Skill resource can be stale after a plugin update.

## Hard rule
A fresh positive FULL E2E claim for release `R` is invalid unless the Host execution context itself resolves the CBCC Skill authority to release `R` (same semantic release family as the actual installed plugin).

If:
- actual plugin manifest/current release = `R`, but
- Host Skill snapshot in the active conversation = `R-1` or another release,

then:
- installed parity for `R` may still be proven by Plugin Creator readback;
- package/runtime negative-fixture tests for `R` may still be proven independently;
- **positive Host-native FULL E2E for `R` remains `E2E_PENDING`;**
- do not reinterpret execution under the stale snapshot as evidence for `R`.

Use a fresh Host context / fresh conversation snapshot that loads the current plugin Skill before the final positive E2E acceptance run.

## Required release proof
Before claiming a release behavior complete:
1. read actual installed `plugin.json`, top Skill, `resources/SKILL.md`, `resources/VERSION` and touched Runtime;
2. read the Host Skill resource used by the execution context;
3. compare semantic release family;
4. only if they match may that Host context provide positive FULL E2E evidence for the release;
5. record mismatches explicitly as `HOST_SKILL_SNAPSHOT_STALE`, never as a product/runtime PASS or FAIL.

## Scope
This lock does not require a new conversation for every normal use. It applies when the plugin was updated after the current Host context loaded its Skill and the result is being used as release-acceptance evidence.
