# Platform Business Pack Specification

A platform adapter describes what can be planned; current operational truth lives in scoped RuleAtoms.

## Resolution order
1. Exact `platform_family + site + program` pack.
2. Family planning pack.
3. Structured ResearchAction.

## Exact-pack scope
RuleAtoms may narrow by category, surface and locale. Expired atoms are excluded and trigger research when relevant.

## Outputs
- resolution type: EXACT / FAMILY / NONE;
- content capabilities and surfaces;
- business capability map;
- scoped current RuleAtoms;
- unsupported requested surfaces;
- research actions;
- submission readiness.

`FAMILY_PLANNING_ONLY` is useful for architecture and research planning. It does not establish fees, category eligibility, claim eligibility, shipping terms, ad program eligibility or submission compliance.
