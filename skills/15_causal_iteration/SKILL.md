---
name: cbcc-causal-iteration
description: Turn real post-launch signals into scoped revision experiments without broad redesign.
---

# Causal Iteration

## Required before change
- baseline
- root cause
- hypothesis
- target metric
- change scope
- locked scope
- test window

## Rule
One experiment targets one primary root cause.

Multiple assets may change only if they all address that same root cause.

## Never
- change price + hero + listing + ads + coupon simultaneously and claim causality
- rewrite frozen upstream layers without explicit unfreeze
- use total sales as the only success metric for a narrow copy change

## Output
- `revision_request.json`
- `experiment_plan.json`
- `keep_locked.json`
