# Research Source Quality / Freshness / Representativeness

## Purpose
Market, competitor, keyword and customer-voice rows are not equally authoritative merely because they exist. Strategy must record **where the observation came from, when it was observed, what population/sample it covers, and what scope it can support**.

## Authority model
`Dataset → Source ID → Source record → Observation date → Declared freshness window → Market/platform/category scope → Sample frame/method → Strategic interpretation`.

## MUST
- Preserve source IDs at row/dataset level where possible.
- Separate unresolved source IDs from resolved source records.
- Calculate source age only from supplied dates and the project `as_of` date.
- Apply freshness PASS/STALE only when an explicit `max_age_days` window is supplied. Otherwise record age without inventing a threshold.
- Never infer representativeness from row count, sales volume, review count, brand prestige or source authority.
- Treat population scope, sample frame, sampling method and inclusion criteria as representativeness documentation, not proof.
- Flag platform/site/market/category scope mismatch before using data to make a local decision.

## WHY
A beautifully calculated CR3, keyword table or review-theme frequency can still be strategically wrong if the sample is stale, cross-market, convenience sampled, or source-untraceable. Source quality determines the strength of the **decision**, not merely the cleanliness of the spreadsheet.

## Decision contract
WHAT → WHY → EVIDENCE → SOURCE QUALITY → CONSUMER LOGIC → PLATFORM LOGIC → BUSINESS LOGIC → EXECUTION → MEASUREMENT.
