# v0.6.30 — Agent Art Direction Authority

## Why this release exists
A real commerce case exposed a regression: visual assets could collapse into repeated product-led compositions even though earlier authority required deliberate product presence and per-asset expression. The failure was not a lack of more layout rules. It was an authority inversion: deterministic runtime heuristics were allowed to fill creative decisions that belong to the host Agent.

v0.6.30 restores the intended architecture: **Agent authors strategy, portfolio curation and per-asset Art Direction; runtime validates, serializes, compiles, executes, traces and packages.**

## Root causes corrected
- Surface architecture previously inferred `REQUIRED / OPTIONAL` product presence from intent/surface and could make that heuristic look authoritative.
- Prompt compilation could treat the mere existence of product identity/source references as permission to create a visible product subject/layer.
- A `FORBIDDEN` product-presence decision could still regain a product layer through product-identity fallback logic.
- Direction-level composition/camera/lighting/color defaults could overwrite asset-level creative decisions.
- Missing per-asset design decisions could fall into deterministic intent→composition/view fallbacks instead of returning to the Agent.
- Historical knowledge still contained fixed Creative Opportunity / Direction counts that could steer the host back toward quota-driven exploration.
- Product reference/fidelity, Product Truth authority and visible product presence were not sufficiently separated end-to-end.

## Current creative authority
The host Agent owns, dynamically and per project:
- asset existence, omission, merge and portfolio sequence;
- visual carrier / information representation;
- product presence and product role per asset;
- subject, action, environment, props and people/casting when relevant;
- composition, spatial rhythm, scale relationships, focal path and negative space;
- evidence hierarchy and decisive moment;
- photography, lens/view, lighting, CMF/material behavior only when relevant to the selected carrier/production route;
- production route and iteration/revision decisions.

Runtime owns deterministic execution concerns only: truth/boundary validation, serialization, schema/trace, prompt compilation, provider handoff, packaging, review lineage and tests.

## Product presence contract
Per-asset Agent Art Direction can resolve product presence as `HERO_REQUIRED`, `REQUIRED`, `SUPPORTING`, `DETAIL_ONLY`, `OPTIONAL→PRESENT|ABSENT`, `FORBIDDEN` or `NOT_APPLICABLE` as needed.

Source files have an independent role such as `SUBJECT_REFERENCE`, `TRUTH_REFERENCE_ONLY`, `LOCKED_SOURCE_LAYER` or `NOT_NEEDED`.

`FORBIDDEN` and truth-only reference modes do not produce a packshot, corner signature, ghost silhouette, podium product or product renderer layer.

## Missing-decision behavior
When Agent authority is active, missing Art Direction or unresolved product presence now returns explicit states such as:
- `AUTHOR_PER_ASSET_ART_DIRECTION`
- `AGENT_ART_DIRECTION_REQUIRED`
- `UNRESOLVED_AGENT_DECISION`

Runtime does not repair these gaps by inventing a product hero, left-text/right-product composition, centered card, generic lifestyle scene or photography recipe.

## Surface authority
Surface architecture still contributes useful platform/surface constraints and compatibility suggestions, but product-presence heuristics are marked advisory:
- `authority = SURFACE_COMPATIBILITY_SUGGESTION_ONLY`
- `authoritative_for_generation = false`
- final authority = `AGENT_ART_DIRECTION`

## Prompt compilation
A new Agent-authority compilation path:
- consumes per-asset Art Direction directly;
- keeps Product Truth/source references available without converting them into visible subjects;
- only creates product renderer layers for explicitly visible product states;
- blocks generation when required creative decisions remain unresolved;
- projects selected Art Direction into the Design Card/Prompt without requiring the host to duplicate the same decisions into a second `creative_brief` object.

## Direction / portfolio behavior
- Direction is a shared system, not a page template.
- Per-asset Art Direction outranks direction-level defaults.
- Creative Opportunity and Direction counts are task-dependent; fixed `6–12` / `3–5` quotas are removed from current authority.
- Portfolio review explicitly checks repeated composition grammar, unjustified product repetition and carrier monotony.

## Photography / CMF
Photography remains a full professional capability, not a universal schema. Camera/lens/light/Prelight/CMF parameters are authored when they materially affect the selected asset and production route. Once selected, those parameters must survive Design Card → Canonical Prompt → machine/provider contract → production/review.

## Verification added
v0.6.30 adds focused regression and end-to-end coverage for:
- `FORBIDDEN` product presence never creating a product layer;
- missing Agent Art Direction blocking rather than inventing design;
- per-asset composition surviving direction-level shared systems;
- Surface `REQUIRED` suggestions being overridden by Agent `FORBIDDEN` decisions;
- top-level host Agent portfolio/art-direction inputs surviving plan normalization;
- direct per-asset Art Direction projection into Canonical Prompt;
- full project flow from `agent_plan` through Surface → Creative → Asset package → Prompt contract;
- installable Plugin/Skill archives containing the new authority runtime, knowledge and Skill contract.

## Compatibility
Legacy deterministic visual signatures remain only as compatibility fallback when Agent creative authority is not active. They are not the creative authority for FULL visual projects or host-Agent-authored asset work.
