---
name: cbcc-market-intelligence
description: Analyze market capacity, competition concentration, price bands, configuration opportunity, and competitor structure from supplied data.
---
# Market Intelligence
## Inputs
- verified market/category data
- platform + market + category
- optional competitor/keyword data
- optional cost constraints

## Rules
- Calculable metrics must come from calculators/scripts.
- Single-period data cannot establish growth trends.
- Missing market data is `DATA_REQUIRED`, not a guessed market size.
- Price opportunity is not simply the highest-sales price band.

## Outputs
- `market_analysis.json`
- `competitor_analysis.json`
- `price_opportunity.json`
- `configuration_opportunity.json`
- `data_confidence.md`
