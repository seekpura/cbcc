# Dynamic Asset Curation

## Purpose
Create the smallest sufficient portfolio that answers the unresolved purchase decisions across the required surfaces. There is no global target such as 6, 7, 9 or 12 assets and no fixed Packshot → Hero → Evidence → Human → Macro → Texture → Skin → Action → Documentation sequence.

## Asset existence test
An asset may exist only when it has all meaningful answers to:
1. **Consumer Decision Question** — what unresolved question or objection exists?
2. **Strategic Job** — what belief/action transition should the asset cause?
3. **Surface Need** — why does this surface require a distinct treatment rather than simple reuse?
4. **Incremental Information** — what does the shopper learn that existing assets do not already communicate?
5. **Business Hypothesis** — what observable behavior should improve if the asset works?
6. **Success Metric** — what signal matches that job?

## Merge / reuse rule
- Same question + same strategic job + same surface: merge by default.
- Same question across different surfaces: retain separate assets only when native format, shopper state, information depth or CTA materially changes the job.
- Same visual master can be reused across crops/layouts when no new information is required.
- Decorative variation is not incremental information.

## Asset contract
For each selected asset record:
- asset ID/name/type/family/surface;
- consumer question;
- purchase barrier and belief target when relevant;
- entry state / exit state;
- strategic job;
- surface need;
- reason to exist;
- incremental information;
- business hypothesis;
- handoff to the next useful state/surface;
- production mode;
- product fidelity;
- source/claim IDs;
- visible copy;
- success metric.

## Production mode selection
Choose photography, design/composite, AI generation, 3D, creator/video or hybrid based on product fidelity, required evidence, available truth assets and the communication job. Do not choose AI merely because an asset is visual.

## Portfolio review
Before finalizing:
- identify duplicate consumer questions;
- check missing objections/beliefs;
- check surfaces with no useful decision job;
- check whether a proposed asset creates a new claim without evidence;
- check whether the portfolio overuses product packshots when context/proof would be more informative;
- check whether people/props/scenes have a positive strategic role;
- check that every asset has a measurable hypothesis.

## Package continuity
Every activated asset retains the complete `00_asset_manifest.yaml` through `11_strategy_authority_trace.json` package and continues through Provider Job → Provider Result → Review Item → Local Revision → Package Hash. Strategy depth is additive; it never collapses assets into one master document.

## v0.5.13 Decision-question preservation
Dynamic curation must preserve incremental buyer information before optimizing asset count.
- Split a compound shopper question only when it contains two independently answerable decision intents.
- Merge only when the jobs share the same decision intent, decision topic, surface need and asset family, or when one clause is merely a boundary qualifier of the other.
- Never merge merely because two questions belong to the same broad funnel stage.
- Every atomic decision job must remain traceable to its source shopper question and either an activated asset or an explicit, auditable merge target.
- The portfolio goal is the fewest assets that preserve all incremental purchase information, not the fewest assets possible.
- Use `decision_question_audit` / `decision_coverage_summary` when available; uncovered atomic jobs are a strategy-quality defect, not an invitation to add a fixed template slot.

