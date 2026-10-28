---
name: cbcc-asset-compiler
description: Compile frozen strategy and asset maps into independent production packages with positive-first generation contracts and prompt-state isolation.
---
# Asset Compiler

## Authority
Source of Truth → frozen strategy → surface/asset map → asset specification → generation/layout contract.

## Boundaries
Preserve approved product facts, claims, strategy, product identity, status and frozen scope. When upstream material conflicts, emit `UPSTREAM_CONFLICT` rather than silently redesigning it.

## Per-asset package
- `00_asset_manifest.yaml`
- `01_strategy.md`
- `02_visual_spec.md`
- `03_photography_contract.json` when relevant
- `04_layout_contract.json` when relevant
- `05_prompt_CN.txt`
- `06_prompt_EN.txt`
- `07_generation_guidance.txt` (desired behavior first; concise precision boundaries second)
- `08_copy.md`
- `09_production_notes.md`
- `10_source_trace.md`

Final prompts follow `references/PROMPT_STATE_ISOLATION.md`; do not serialize workflow/QA/version databases into the model prompt.

## Runtime
`runtime/cbcc/asset_compiler.py` materializes the per-asset package and validates required files plus prompt-state isolation before the package is review-ready.
