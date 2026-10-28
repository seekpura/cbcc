# Market / Competitor / Search Strategy Interpretation

## Purpose
Convert deterministic market outputs into commercial hypotheses that can change SKU, offer, positioning, listing, content and asset decisions. The tool output is evidence; it is not the recommendation by itself.

## Required reasoning contract
For every important market signal write:
- **WHAT** the supplied sample actually shows.
- **WHY** it matters commercially.
- **EVIDENCE** and the collection scope behind the signal.
- **CONSUMER LOGIC**: what buyer expectation or decision set could explain it.
- **PLATFORM LOGIC**: how search, recommendation, gallery, creator, live or paid surfaces change the implication.
- **BUSINESS LOGIC**: effect on entry mode, positioning, SKU, price, margin, acquisition or retention.
- **ALTERNATIVE EXPLANATIONS** that could create the same pattern.
- **EXECUTION**: what changes now and what must remain provisional.
- **MEASUREMENT**: what post-launch evidence confirms/refutes the hypothesis.

## Data normalization first
- Preserve raw rows and provenance before field normalization.
- Distinguish observed revenue from revenue derived from explicit `price × units`.
- State collection date, category filters, seller coverage and known sampling bias when supplied.
- Never turn an export into a total-market estimate unless representativeness is established.
- Missing rating/review/search fields are unknown, not zero.

## Capacity and concentration
Interpret sample sales/revenue/item/seller counts together with CR3, CR10 and HHI.
- High concentration can imply a mature reference set, trust advantages or distribution power; it does **not** automatically mean “do not enter”.
- Low concentration can imply fragmentation, many niches or weak brand power; it does **not** automatically mean “easy opportunity”.
- Cross-check concentration with competitor efficiency, search demand, price/configuration structure and review themes.

## Price distribution and valleys
- Dense price bands are evidence of observed payment behavior in the sample, not necessarily the optimal price.
- Sparse price bands are **hypotheses**, not whitespace opportunities.
- Validate any valley against demand, configuration, value proposition, contribution economics and platform price signaling.
- Explain whether the candidate price creates a meaningful value step or merely sits between competitors.

## Configuration opportunity
Analyze size, pack, bundle, format, variant and other purchasable configurations.
- Compare units/item, revenue/item, median price and review/return signals when available.
- Ask which usage cycle, trial need, replenishment need or gifting need the configuration serves.
- A bundle needs a buyer job and economic logic; “more items” alone is not a strategy.

## Competitor clusters
Cluster only on observable dimensions first: price tier × configuration × seller/brand efficiency × visible listing proposition when available.
- Do not invent psychographic labels such as “young”, “luxury”, “clinical” without evidence.
- For each candidate cluster identify the real decision set the shopper compares.
- Then add listing claims, visual grammar, reviews and search terms to explain how the cluster competes.

## Seller efficiency
Use revenue/item, units/item and related ratios to identify efficient assortments or sellers, but do not confuse efficiency with causality.
- A high-efficiency seller may benefit from brand demand, traffic, distribution or a narrow hero assortment.
- Use the signal to select competitors for deeper review, not to copy their creative automatically.

## Search demand
Map term → intent → decision stage → product fit.
- Core/category/specification terms establish relevance.
- Benefit/problem/use-case terms are only usable when Product Truth supports them.
- High volume + low product fit is a traffic-quality risk.
- Translate search intent into title/attribute/PDP jobs on search surfaces and into hooks/topics on recommendation surfaces.

## Customer Voice / competitor-review themes
Use supplied review/theme labels to understand repeated buyer tensions, expectation gaps, usage questions and competitor weaknesses.
- Deterministic Runtime aggregation MUST use explicit `theme/category` and `sentiment` labels only; do not silently infer semantics from raw review text.
- Preserve competitor/source/audience links and unclassified counts so evidence gaps remain visible.
- Frequency in the supplied sample is not population prevalence unless sampling representativeness is established.
- Route a relevant theme through Product Truth before using it as Positioning tension, Listing objection, Content hook or Dynamic Asset job.
- Separate a true product defect from an expectation/communication/usage/package issue before recommending creative changes.

## Opportunity map
An opportunity requires the intersection of:
1. demand evidence;
2. product/SKU fit;
3. an explainable value proposition;
4. unit-economics viability;
5. platform-native execution capability;
6. a measurable hypothesis.

Label low-evidence signals as `HYPOTHESIS_NOT_RECOMMENDATION`. Never upgrade a price valley, low-competition keyword or weak competitor cluster into a recommendation without cross-checks.
