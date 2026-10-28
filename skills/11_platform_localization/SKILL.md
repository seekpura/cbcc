---
name: cbcc-platform-localization
description: Route work through platform/market adapters for listing, image, video, creator, ads, fees, logistics and claims without inventing current rules.
---
# Platform Localization

Read `references/platforms/platform_registry.yaml`.

## Reference-toolkit compatibility
- Primary specialization: Shopee BR, Mercado Livre BR.
- Secondary/reference support: Amazon, TikTok Shop and Shopify in specific content/pricing contexts.
- This system supports extension adapters (e.g. Noon) without pretending their current rules are already verified.

## Rule freshness
A rule must carry source + verified_date + market/platform scope. If absent/stale: `REVERIFY_REQUIRED`.

## Output
- selected adapter;
- capability coverage;
- verified rules used;
- rules requiring verification;
- downstream localization constraints for listing/image/video/creator/ads/fees/logistics/claims.

## Business Pack Compiler
Runtime resolution separates family planning packs from exact Site/Program packs. Category/Surface/Locale-scoped current RuleAtoms are the authority for field/submission rules; family packs remain planning knowledge.
