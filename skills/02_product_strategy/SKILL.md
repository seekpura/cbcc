---
name: cbcc-product-strategy
description: Convert verified market/product truth into product role, SKU roles, configuration strategy, commercial risks, and unit economics.
---
# Product Strategy
## Inputs
- product_facts
- market_analysis
- company_capabilities
- after_sales_capacity
- real cost structure

## Rules
- SKU roles are dynamic, not a mandatory four-SKU template.
- No cost data → no price recommendation.
- Configuration follows demand + differentiation + capability + margin + after-sales.
- One primary conversion proposition is chosen later; this module supplies the commercial evidence.

## Outputs
- `product_strategy.json`
- `sku_roles.json`
- `unit_economics.json`
- `commercial_risks.md`
