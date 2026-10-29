# v0.6.44 — Default Prompt Authority Consolidation

## Problem fixed
CBCC accumulated multiple long `defaultPrompt` entries as successive regression fixes were added. Those prompts were not merely invocation hints; they duplicated business authority already owned by Host Skill / Canonical Skill and created a second policy surface that could drift, conflict or keep growing with every release.

## New boundary
From v0.6.44 onward, `defaultPrompt` is not a business-policy layer. Fixed CBCC behavior lives in Host Skill / Canonical Skill and detailed canonical contracts. The installable manifest omits `defaultPrompt` entirely.

The integrated Skill authority retains the fixed principles that previously appeared in manifest prompts:
- Chinese-first human delivery and same-object Chinese interpretation for foreign human-facing content;
- mature routed FULL interaction floor;
- FULL commercial depth and seven first-class commerce capabilities;
- dynamic Asset Universe separate from Live/Activation Set capacity;
- Agent creative/curation authority;
- complete per-asset Human Design Card + four production objects;
- additive upgrade rule.

## Release guard
The v0.6.44 package guard fails if `plugin.json` or `.codex-plugin/plugin.json` contains `defaultPrompt`, or if Host/Canonical no longer contain the integrated authority boundary.

## Compatibility
This is an authority-source refactor, not a capability reduction. v0.6.43 Chinese interpretation behavior and v0.6.42 interaction/Asset Universe recovery remain in force.
