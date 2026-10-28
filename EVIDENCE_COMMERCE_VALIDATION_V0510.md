# v0.5.10 Evidence Commerce Validation

## Purpose
Validate one question: **when a Category Commerce prior conflicts with current scoped evidence, which authority wins and how does the strategy change?**

Authority order used in this release:

`Product Truth / verified policy & evidence → own shopper questions / feedback / behavior → current scoped market/search/review/competitor evidence → Category Commerce prior → generic fallback`

A lower layer can influence prioritization but cannot create a higher-authority fact or claim.

## Category-prior conflict stress cases

| Case | Category prior top | Current effective top | Effective top proof | Dynamic assets | Evidence-supported offer test candidates |
| --- | --- | --- | --- | ---: | ---: |
| Food & beverage | DIETARY_FIT | TASTE_PREP | real product/serving/preparation evidence | 2 | 3 |
| Electronics | COMPATIBILITY | SERVICE | warranty/service/package facts | 2 | 4 |
| Apparel fit | SIZE_SELECTION | MATERIAL_CARE | fabric/construction/color truth | 2 | 2 |
| High-ticket durable | SITE_FIT | DELIVERY_INSTALL | delivery/installation facts | 2 | 4 |

The important result is not the asset count. In all four cases the category prior remained in trace but current supplied evidence changed the effective commercial priority.

## Same-product platform-cross validation
The same electronics evidence priority (`COMPATIBILITY`, `PERFORMANCE_PROOF`, `USAGE`) was compiled across four platform systems:

| Platform | Native system | Information density | Strategy expression |
| --- | --- | --- | --- |
| TikTok Shop | TIKTOK_SHOP_NATIVE_COMMERCE | LOW_PER_BEAT | discovery-led identity then one unresolved decision per beat; offer follows value/proof |
| Shopee | SHOPEE_COMPARISON_COMMERCE | COMPACT_COMPARISON | mobile comparison, exact configuration and objection resolution |
| Amazon | AMAZON_SEARCH_PROOF_SYSTEM | HIGH_SCANNABILITY | search identity and structured decision facts first |
| DTC / Shopify | DTC_MODULAR_PDP_LIFECYCLE | MODULAR_DEEP | modular proof/risk routing with lifecycle/bundle logic tied to contribution/repeat evidence |

Platform logic changes the presentation and decision path. It does not change Product Truth or fabricate a different evidence priority for the same product.

## Offer evidence boundaries
- **Promo response**: observed price/discount/conversion/orders/contribution can support a test hypothesis; descriptive elasticity is not a causal elasticity estimate.
- **Bundle affinity**: attach rate requires an explicit denominator and shows observational affinity, not incremental demand.
- **Repeat/replacement cycle**: observed repeat timing can guide a retention hypothesis but does not create recommended usage frequency or arbitrary CRM cadence.
- **Release rule**: evidence may promote an offer to `EVIDENCE_SUPPORTED_TEST_CANDIDATE_NOT_LOCKED`; Product Truth, actual capability, contribution economics and incrementality still govern lock.

## Proof evidence conditions
Category-typical proof formats are treated as requirements, not already-proven facts. The compiled Proof Hierarchy states what evidence is needed and whether the current input supplies it before the proof can be used.

## Real defect found during validation
A high-ticket question containing “delivery and installation … what must I prepare?” was initially captured by the generic food/preparation rule because of the word `prepare`. Runtime ordering was corrected so hard delivery/installation and service intents outrank generic sensory/preparation language. A tea preparation question remains `SENSORY_PREP`.

## Boundary of this validation
These are structured pressure-test inputs designed to validate Runtime behavior. They are **not** presented as a live marketplace population study, causal experiment, or business-performance claim. Current production decisions still require real current market sources, Product Truth, policy/service facts and measured economics.
