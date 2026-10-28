# Professional Prompt — Research Source Quality Interpretation

Use the supplied deterministic `research_quality` object. Do not invent missing dates, sample frames, markets or source coverage.

For each material market/competitor/customer conclusion:
1. State WHAT the dataset suggests.
2. Explain WHY it matters commercially.
3. Cite the source IDs/dataset involved.
4. State freshness status only against an explicitly declared freshness window.
5. State whether representativeness is documented, unknown, or scope-mismatched.
6. Downgrade strong recommendations to hypotheses when source resolution, freshness or sampling scope is weak.
7. Explain what additional collection would change the decision.

Never write “representative” merely because N is large. Never combine cross-platform/cross-market datasets as if they were one homogeneous population unless the project explicitly defines that scope.
