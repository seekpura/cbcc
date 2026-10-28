# Baseline Audit + v0.5.3 Development Notes

## Baseline
Source baseline: `cross-border-commerce-creative-v0.5.2-strategy-integration-depth.zip`.

This v0.5.3 tree was copied from that baseline and enhanced in place. No v0.5.2 source path was intentionally removed or replaced with a smaller architecture.

## Confirmed continuity
- Nine formal Strategy Authority sections remain.
- `MASTER_STRATEGY_CN.md`, `EXECUTIVE_SUMMARY.json`, `STRATEGY_DECISION_INDEX.json` remain.
- Per-asset `00–11` package remains mandatory.
- Provider / Review / Local Revision / Package Hash implementation remains.
- Dynamic asset count remains driven by consumer decision questions and surface needs.
- Strategy Reasoning Context continues to consume selected Knowledge/Ontology/Prompt authorities.

## v0.5.3 code paths changed
- `runtime/cbcc/tools/market.py`: competitor Listing/message/offer/proof observations + review joins; supplemental market evidence path.
- `runtime/cbcc/tools/economics.py`: portfolio overlap/cannibalization hypotheses, trade-up architecture, lifecycle offer map.
- `runtime/cbcc/tools/listing.py`: locale × field transcreation tasks and localized numeric-equivalence audit.
- `runtime/cbcc/strategy_depth.py`: formal Strategy Authority integration for competitor intelligence, portfolio architecture, transcreation and platform-native authoring contracts.
- `runtime/cbcc/asset_architecture.py`: explicit Product-Truth-fit market theme → Dynamic Asset route.
- `runtime/cbcc/strategy_sources.py`: runtime selection/binding of new professional authorities.
- `ontology/commerce_ontology.json`: new portfolio/competitor/localization entities and constraints.

## Validation notes
The repository regression suite plus v0.5.3 integration test is used only to detect compatibility breakage. Passing tests are **not** treated as evidence that strategy quality is complete.

Repository KIYUU Malaysia TikTok Shop fixture was recompiled under v0.5.3. Result:
- 9 Strategy Authority sections,
- 3 dynamic assets (not padded to a fixed target count),
- all 3 assets contain complete `00–11`,
- Platform Content Matrix retains en-MY and ms-MY visible locale tasks,
- Review Workspace remains materialized,
- fixture remains planning/review path, so no Provider Result is fabricated.
