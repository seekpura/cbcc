# P1 Domain Engines — Alpha2

This checkpoint deepens deterministic commerce engines without turning semantic strategy into hard-coded heuristics.

## 1. Market Engine
Consumes supplied market rows only and computes:
- supplied-row market capacity (units / revenue);
- seller concentration CR3 / CR10 / HHI;
- stable price bands and low-density valley signals;
- units/revenue per item by seller;
- configuration efficiency and median price;
- explicit missing-field data-quality report.

A price valley is an opportunity signal, not an automatic recommendation. Margin, category meaning and source representativeness remain strategy/evidence work.

## 2. Economics Engine
Supports fixed and percentage fee components and produces:
- contribution waterfall;
- contribution margin;
- contribution before ads;
- break-even ROAS;
- allowable CPA / CPC;
- coupon headroom;
- affiliate-rate ceiling;
- multi-SKU / multi-scenario matrix.

No platform fee or tax is assumed when missing.

## 3. Listing Engine
Separates semantic and deterministic tasks:
- semantic keyword classification remains upstream;
- toolkit aggregates classified keywords;
- title length/byte/required-term rules are deterministic;
- numeric tokens in customer-facing copy are traced against supplied facts/approved claims;
- field-level source and claim references are preserved.

## 4. Advertising Engine
Computes CTR, CVR, CPC, CPA, ROAS and ACoS from supplied data. Diagnostic routing uses caller-supplied thresholds or the supplied unit-economics break-even point; it does not invent a universal benchmark.

## 5. Feedback Engine
Semantic classification remains upstream. Given classified reviews/CS/return rows, the engine aggregates frequency/severity and routes categories to likely responsible modules (Listing, Product, CX, Fulfillment, etc.).

## 6. Experiment Engine
Adds uncertainty to A/B interpretation:
- conversion rates;
- absolute / relative lift;
- two-proportion z-test;
- two-sided p-value;
- Wilson 95% intervals;
- decision only when statistical evidence and optional minimum lift both pass.

The result explicitly does not prove causality when allocation, instrumentation, exposure windows or concurrent changes are uncontrolled.

## Runtime Consumption
When the corresponding request sections are present, `runtime/cbcc/compiler.py` writes:
- `artifacts/market_analysis.json`
- `artifacts/offer_economics.json`
- `artifacts/listing_analysis.json`
- `artifacts/ad_analysis.json`
- `artifacts/feedback_analysis.json`
- `artifacts/experiment_analysis.json`
- `artifacts/domain_analysis.json`

Decision Trace records which deterministic domain inputs were actually available.
