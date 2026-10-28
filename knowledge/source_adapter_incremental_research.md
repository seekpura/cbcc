# Source Adapter / Incremental Research Authority

## Purpose
Turn larger competitor, search and review datasets into repeatable research inputs without treating ingestion convenience as evidence quality.

## Professional rules
- Every adapter names its dataset, schema map, source, refresh mode and key semantics.
- `FULL_SNAPSHOT` means the supplied rows are the current analytical snapshot.
- `INCREMENTAL_BATCH` may carry forward prior keyed rows; it must not be inferred from a partial file.
- Added / changed / removed rows are provenance changes, not automatically market changes.
- High-watermark values describe ingestion progress only; they do not prove upstream completeness or freshness.
- Exact key/fingerprint dedup and semantic-near-duplicate review are separate. Near duplicates are NEVER silently deleted.
- Cross-market/site/platform/category adapters stay separate unless the research question explicitly calls for comparison.

## Strategy consumption
Adapter refresh information should answer: what changed, which strategy conclusion depends on it, and whether only a local strategy layer needs refresh.

## WHY
Large-scale research becomes dangerous when refresh mechanics erase lineage. Incremental ingestion must reduce maintenance cost without reducing epistemic discipline.
