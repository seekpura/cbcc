# Seven First-Class Commerce Tool Contracts — v0.6.1

These are capability entrypoints, not shallow checkers. The deterministic/runtime depth remains in `runtime/cbcc/`; these wrappers expose the seven reference-agent responsibilities as one stable contract layer.

| # | Tool | Runtime contract |
|---|---|---|
| 01 | Market Research | `market_research_tool` |
| 02 | Product Strategy | `product_strategy_tool` |
| 03 | Listing Creative | `listing_creative_tool` |
| 04 | Product Image | `product_image_tool` |
| 05 | Product Video | `product_video_tool` |
| 06 | Advertising Optimization | `advertising_optimization_tool` |
| 07 | Review Analysis | `review_analysis_tool` |

Usage: each wrapper reads one UTF-8 JSON object from a file path argument or stdin and prints UTF-8 JSON. Inputs map directly to the named Python function keyword arguments.

```bash
python toolkits/11_seven_agent_contracts/01_market_research.py input.json
python toolkits/11_seven_agent_contracts/06_advertising_optimization.py ads.json
```

The image tool does **not** inherit the reference project's fixed nine-image quota. It uses CBCC dynamic decision/surface architecture.
