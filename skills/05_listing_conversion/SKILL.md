---
name: cbcc-listing-conversion
description: Build multi-platform, market-localized listing conversion architecture from verified product truth, STP/JTBD, positioning, claims and current platform adapters.
---
# Listing Conversion

Listing is a conversion system: SEARCH → CLICK → IDENTIFY → UNDERSTAND → DESIRE → PROOF → FIT → OBJECTION → TRUST → ACTION.

## Inputs
product_facts, claim_ledger, STP/JTBD, culture_constraints, positioning, information_hierarchy, target platform/market, verified platform adapter, keyword data when available.

## Outputs
- keyword architecture: category/core/attribute/feature/benefit/problem/audience/scenario/ingredient/compatibility/long-tail/risk;
- title strategy and variants where meaningful;
- highlights/bullets;
- description / PDP sections appropriate to the platform;
- attributes/specifications/usage/package contents;
- FAQ + objection handling;
- claim mapping + forbidden words;
- listing traceability mapping each field → source_id / claim_id / consumer job / asset link;
- platform-localized copy in target language(s), with back-translation QA where needed.

## Rules
- No fixed description structure across platforms.
- Every number has a source/spec reference.
- Every buyer-visible claim has a valid claim_id.
- Platform numeric/policy limits come from current verified adapter or are `REVERIFY_REQUIRED`.
- Local language is composed for the market, not blindly translated.

## Compiler 2.0
Platform-scoped field contracts, classified keyword evidence, numeric trace and per-field source/claim references compile into `listing_analysis.json`. Semantic copywriting remains an evidence-led strategy task rather than a deterministic Python guess.
