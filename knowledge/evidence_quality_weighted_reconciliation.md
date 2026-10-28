# Evidence Quality Weighted Reconciliation

## Purpose

Current market evidence should change strategy only in proportion to what the evidence can actually support. A large row count or a dramatic review theme is not automatically strong evidence. Product Truth and current verified policy remain the highest authorities for facts and claims. Current market/search/review/competitor evidence can reorder priority, sequence and research attention, but only after research quality is considered.

## Quality dimensions

Use the following dimensions together, not independently:

- **Freshness**: compare observation age only against a project/source-declared freshness window. Never invent a universal 30/60/90-day threshold.
- **Traceability / coverage**: measure how much of the dataset has source IDs and how many source IDs resolve to source records. Evidence that cannot be traced should have less power to reorder strategy.
- **Representativeness metadata**: sample frame, population scope, sampling method and inclusion criteria describe what can be generalized. Metadata is not proof of representativeness, but missing metadata lowers confidence.
- **Scope match**: market, site, platform family and category must match the target decision. Cross-scope observations may be useful context but should not dominate local priority.
- **Explicit source quality**: use a caller-declared source-quality score/tier when supplied. Never infer quality from brand prestige or publisher name alone.
- **Agreement / conflict**: independent evidence families that point to the same unresolved decision increase confidence; explicitly declared conflicts reduce it. Agreement does not create Product Truth.

## Reconciliation logic

Category Commerce Profile is a prior, not a winner by default. Combine a category-prior score with quality-weighted current evidence. Strong, current, traceable, scope-matched evidence can move an objection/proof ahead of the category default. Weak, stale, scope-mismatched or unresolved evidence should normally remain a research signal rather than overwrite a strong prior.

Explicit own shopper questions, own classified feedback and own behavioral evidence sit above external market observations because they are project-specific. They still cannot create a product fact or claim.

## Product Truth fit before asset routing

Search demand, competitor proof norms and review themes should automatically create **fit-review tasks**, not assets. A host/reviewer must explicitly confirm that verified Product Truth genuinely addresses the observed concern. Only a confirmed fit can become a Consumer Decision Question for Dynamic Asset Curation. This prevents the common failure mode: "competitor customers complain about X, therefore our product solves X."

## Output contract

Every evidence-priority row should expose:

- raw evidence weight;
- quality multiplier/components;
- quality-weighted evidence;
- agreement/conflict factor;
- category-prior score;
- final effective priority score;
- source evidence trace and boundary.

A strategy decision should be explainable as:

`Category Prior + Quality-weighted Current Evidence -> Effective Priority -> Execution -> Measurement`.
