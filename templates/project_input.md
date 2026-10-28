# CBCC Project Input — v0.5.4 Research + Behavior + Final Copy Depth

> 不要求一次填满。缺失项会标记其影响范围，但不会把所有策略工作一起阻断。当前规则/市场数据/单位经济等时效信息只在真正影响对应决策时补齐。

## 1. Product Truth / SKU
- Project ID:
- Product name / Brand / Category:
- SKU / Variants / Bundle / Multipack:
- Product format / Net content / Dimensions:
- Formula / ingredients / materials / process:
- Usage / routine / compatibility:
- Package contents / packaging copy / warnings:
- Verified product photos / packaging photos / texture references:
- Product fidelity: `LOCKED_PIXEL | REFERENCE_CONSTRAINED | GENERATIVE`
- Source IDs / source type / verification date:

## 2. Claims / Evidence
For each claim:
- claim_id:
- exact claim:
- classification: `REAL_SELLING_POINT | PERCEIVED_BENEFIT | EMOTIONAL_VALUE | PENDING`
- evidence level / status:
- source_ids:
- perceived benefit:
- emotional value (only if genuinely supported):
- claim boundary / publication limitation:

## 3. Target Context
- Platform family / Exact site / Program:
- Market / Country / Region / City (when relevant):
- Category / Subcategory:
- Primary locale / support locales / visible-copy locales:
- Currency / sales model / logistics model:
- Required Surfaces:

## 4. Audience / Culture / Intersectionality
- Primary audience / secondary audience:
- JTBD / trigger / pain / barrier / decision factors:
- Age / gender / income / geography / lifestyle (only when relevant):
- Race / ethnicity evidence and source status:
- Intersectionality dimensions:
- Languages / religion / festivals:
- Skin tone / hair / body / disability / family structure considerations:
- Clothing / body exposure / gestures / body contact:
- Color symbolism / humor / CTA implications:
- Casting implications / visual implications / copy implications:
- Cultural statements + source_ids + `VERIFIED | LIKELY | ASSUMPTION | PENDING`:

## 5. Market / Competitor Data
Provide one of:
- `market_rows` directly, or
- `market_file`: CSV / XLSX / JSON
- `market_field_map` when source columns differ
- `market_keyword_rows`: term / volume / competition / rank / intent / source
- `market_review_rows`: explicit theme/category / sentiment / competitor/brand/seller / audience_segment / text / source_id / count (Runtime aggregates supplied labels only; no free-text auto-classification)
- `competitor_listing_rows`: competitor / title / observed claim / explicit message_theme / offer_type / proof_type / configuration / surface / locale / visual_pattern / source_id
- `market_theme_fit`: only when a market/review theme is explicitly validated against own Product Truth; may include theme / fit_status / consumer_question / source refs and can create a Dynamic Asset decision job
- `market_source_records`: source_id / kind / title / URL / observed_at or collected_at / max_age_days / market / site / platform_family / category / population_scope / sample_frame / sampling_method / inclusion_criteria / exclusion_criteria / coverage_note
- `market_research_as_of`: project comparison date for source age
- `market_research_scope`: expected market / site / platform_family / category and optional default `max_age_days`
- collection scope / date / category filters / seller coverage / known sampling bias

Useful fields:
- product / seller / brand
- units / revenue / price
- configuration / size / bundle
- rating / review count
- keywords / ranking / traffic when available
- competitor listing / visual / review references

## 6. Offer / Unit Economics / SKU Strategy
- Price / currency:
- landed product cost:
- fulfillment / logistics:
- platform fixed and rate fees:
- payment / tax / refund allowance:
- affiliate commission / creator cost:
- ad spend or target CPA/ROAS:
- coupon / promotion scenarios:
- minimum target contribution per order / target contribution margin:
- affiliate room / paid-media room assumptions (if any):
- scenario sensitivity variables: discount / affiliate / ad cost / refund allowance:
- multiple SKU scenarios / candidate roles:
- per-scenario buyer_job / target_segment / channel / product_family / lifecycle_stage / offer_type / unit_count:
- candidate price ladder / bundle / trial / premium configurations:
- behavioral validation when available under `offer_economics`:
  - `behavior_rows | portfolio_behavior_rows`: sku / visitors / clicks / orders / new_customers / repeat_customers / revenue / contribution / source_id
  - `pair_behavior_rows | portfolio_pair_rows`: sku_a / sku_b / shared_visitors / visitors_a / visitors_b / switch_a_to_b / switch_b_to_a / paired_orders / exclusive orders / source_id
  - `cohort_rows | portfolio_cohort_rows`: cohort / sku / acquired_customers / repeat_customers / orders / revenue / contribution / source_id
  - `incrementality_rows | portfolio_incrementality_rows`: test_id / sku / treatment_n / treatment_orders / control_n / control_orders / treatment/control contribution / randomized / source_id

## 7. Listing / Search
- Current or planned title / fields / attributes:
- Keyword rows: term / cluster / intent / source / volume / priority inputs:
- Existing PDP/listing copy:
- Common questions / objections / return reasons:
- FAQ facts / usage steps / package contents / compatibility / size expectations:
- local-language search terms / transcreation notes / prohibited literal translations:
- optional `_localized_copy`: `{locale: {field: localized_value}}` for authored localized drafts/source copy; runtime checks literal numerical equivalence and creates locale × field authoring tasks
- optional `_localized_copy_reviews`: list/dict with locale / field / decision / native_fluency / claim_equivalence / platform_fit / culture_fit / reviewer / notes; only explicit approval + hard-check pass can release `APPROVED_FINAL`
- field-level `_source_refs` / `_claim_refs` where available:
- Platform field constraints if already verified:

## 8. Advertising / Feedback / Experiments
- `ad_rows`: impressions / clicks / orders / spend / revenue + campaign/ad-group identifiers
- ad eligibility / inventory / budget pacing / bid / audience / placement fields when available
- incrementality evidence: holdout / geo split / lift test / causal experiment / baseline notes
- `feedback_rows`: source / category / severity / text / product-vs-communication classification
- experiment: control / variant / sample sizes / conversions / causal variable / minimum lift

## 9. Brand / Visual / Photography / CMF
- Positioning inputs (optional; strategy engine can derive candidates):
- Brand tone / palette HEX / typography:
- Creative references with role: Truth / Visual / Category / Cultural / Anti-pattern
- Style / composition / information-design preference:
- Camera body / focal length / full-frame equivalent / macro requirement:
- Camera height / working distance / yaw / pitch / roll:
- Shot size / crop / perspective intent:
- Product occupancy % / negative space / type-safe area:
- Focus plane / aperture / DOF:
- Key azimuth/elevation / modifier / size / distance:
- Fill / negative fill / rim / background light / contrast ratio:
- CCT / white balance / shadow direction/length/softness/density:
- Exposure / highlight roll-off / clipping policy:
- flags / diffusion / polarization / reflection control:
- transparent / metal / glossy material handling:
- skin-tone metering / highlight protection / separation:
- output color space / neutral reference / exact product color fidelity:
- CMF: Color / Material / Finish:
- wardrobe / hair / makeup / hand grooming / props:
- shutter / ISO when a real-shoot context needs them:

## 10. Platform Content Targets
Repeat per target platform/site when multi-platform:
- platform / site / market / audience:
- desired content families / surfaces:
- creator/live/paid/CRM/FAQ/return-prevention needs:
- reuse preference vs platform-native production:

## 11. Dynamic Asset Jobs (optional)
Do **not** specify a fixed number just to fill slots. For each known job:
- consumer_question:
- strategic_job:
- surface / family / asset type:
- surface_need: why this surface requires a distinct treatment instead of reuse
- reason_to_exist:
- incremental_information:
- business_hypothesis: what behavior should improve if this question is resolved
- product_fidelity:
- production_mode:
- visible_copy:
- source_ids / claim_ids:
- success_metric:

If omitted, the system derives assets from Consumer Decision Questions × Strategic Jobs × Surface Need × Incremental Information × Business Hypothesis. Repeated questions are merged unless the surface context creates a genuinely different decision job.

## 12. Strategy Annotations (professional model / human interpretation)
Optional domain-level enrichment that must not overwrite deterministic truth/calculations:
- executive_summary
- information
- value_ladder
- market_insights
- culture_insights
- product_strategy
- positioning
- message_hierarchy
- listing_strategy
- frameworks
- visual_strategy
- asset_portfolio
- content_matrix
- race_execution
- culture_checklist
- performance_learning
- ab_hypotheses
- priority_plan

Every major recommendation should use the decision contract:
`WHAT → WHY → EVIDENCE → CONSUMER → PLATFORM → CULTURE → BUSINESS → EXECUTION → MEASUREMENT`.

## 13. Production / Revision
- `compile_assets: true|false`
- Provider preferences / available photographer / designer / AI / 3D / video provider:
- Production asset IDs (when selectively producing):
- Local revision scope (`allowed_fields`) — e.g. only `spoon_presence`:
- Existing output paths / result envelopes for provider ingest:
