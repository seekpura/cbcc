# v0.6.43 — Global Chinese Interpretation

## Problem fixed
Human delivery was Chinese-first in principle but not complete in execution. Some target-market foreign content—especially Listing category/classification, description, attributes, search terms, FAQ and other localized fields—could appear without a Chinese meaning/use companion. The previous audit mainly covered active Listing rows and asset Visible Copy, so preserved Listing data and other human-facing commerce surfaces could escape the contract.

## New authority
Every human-facing foreign-language commerce string that an operator needs to understand must:
1. preserve the exact original target-market text; and
2. provide Chinese interpretation / meaning / use in the same human object.

This includes Listing, category/classification, attributes, descriptions, search terms, FAQ, asset Visible Copy, video/creator copy, advertising copy, surfaced review/CS/return quotes and surfaced research/competitor evidence.

Technical identifiers/proper names such as SKU, GTIN/EAN/UPC, URL, HEX, INCI, model/part number, HS Code and official brands keep their exact values; their human labels/use explanations remain Chinese-first.

## Runtime changes
- Add `global_chinese_interpretation.py` to propagate existing Listing companions, audit preserved Listing data, and audit human-facing VIDEO / ADS / REVIEW / RESEARCH structured copy.
- Add Chinese-first localized Listing field labels while keeping raw platform keys secondary.
- `delivery_export` now uses the global audit and blocks final READY state when any required Chinese companion is missing.
- Non-Listing tasks that still display preserved Listing content render bilingual rows instead of foreign-only preserved values.
- `待补中文释义` is an incomplete state, not a valid FULL completion state.

## Agent responsibility
Runtime does not invent arbitrary machine translations. The Host Agent must author semantic Chinese interpretation before finalization. Search terms may use Chinese intent explanations rather than literal word-for-word translation; reviews/research excerpts preserve original tone while Chinese explains meaning and decision signal.

## Regression coverage
`tests/test_v0643_global_chinese_interpretation.py` covers:
- category, description, attributes, search terms and FAQ;
- preserved Listing content outside active Listing scope;
- video on-screen/VO copy;
- ad hook/headline/body/CTA;
- review/customer-voice excerpts;
- research excerpts;
- same-object Chinese companions;
- technical identifier exemptions;
- raw localized platform keys as secondary labels;
- rejection of `待补中文释义` as finished delivery.
