---
name: cbcc-asset-architecture
description: Build dynamic multi-surface assets from consumer decision questions, belief sequence, evidence and surface handoffs; never defaults to a fixed gallery count.
---
# Dynamic Asset + Surface Architecture

Read `references/DECISION_SYSTEM_SPEC.md` and `references/SURFACE_ARCHITECTURE.md`.

## Algorithm
Purchase question → priority → belief required → evidence available → best surface → information gain → handoff → CREATE / MERGE / DEFER.

Each asset records:
- consumer question / purchase barrier / belief target / strategic job;
- journey stage, entry state and exit state;
- RACE / JTBD / optional AIDA-FABE role;
- surface/platform/market/locale;
- curation source and evidence/source/claim IDs;
- reason-to-exist and incremental information beyond adjacent assets;
- handoff to the next asset/belief/action;
- production mode / product fidelity / approved semantic elements;
- product/human/photography/CMF needs;
- priority/status/dependencies/success metric.

Use Foundation/Creative Anchor logic where useful, but do not copy one layout across the set.

Outputs: `consumer_decision_questions.json`, `belief_sequence.json`, `surface_plan.json`, `master_asset_map.json`, `asset_traceability.json`.

## Runtime
`runtime/cbcc/asset_architecture.py` creates and merges assets from explicit consumer decision jobs. Asset count is always reported as a derived result with `fixed_count_authority=false`.
