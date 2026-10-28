# Listing / Search Conversion Architecture

## Purpose
Compile a listing as a purchase-decision system: search relevance brings the right shopper in; field architecture helps that shopper identify, evaluate, trust, choose and use the product. It is not a keyword container and not a duplicated ad script.

## Search intent architecture
For each term capture:
- term / cluster / intent;
- product relevance;
- decision stage;
- volume/competition/rank when supplied;
- priority signal;
- target field/surface;
- source/provenance.

Prioritize exact relevance before volume. A high-volume irrelevant term can increase impressions while reducing CTR/CVR and increasing misunderstanding.

## Field jobs
Every field must have an incremental decision job.
- **Title**: identity + core category/search intent + critical variant/spec + at most one value cue when space/platform allow.
- **Primary image / product card**: exact product recognition and first reason to click; do not replicate the PDP.
- **Attributes**: structured fit/specification/compatibility/variant facts.
- **Highlights / bullets**: relevance and reasons-to-believe; one buyer question per block.
- **Description**: deeper context, mechanism, usage logic or proof that needs explanation.
- **FAQ**: real objections, misunderstandings and return drivers.
- **Usage**: steps, frequency, compatibility and caution only when factually supported.
- **Package**: what the buyer receives, size/count/variant and expectation boundaries.
- **Offer / CTA**: platform-native action after sufficient value and risk clarity.

## PDP sequence
Use belief order rather than a fixed visual template:
`Identify → Relate → Believe → Reduce Risk → Act → Use/Retain`.
Reorder only when product/category evidence shows a different dominant barrier.

## Objection handling
For every objection:
- classify source: product concern, fit/spec, package, usage, expectation, trust, price/offer;
- choose the single best resolution field;
- identify required evidence;
- state answer boundary;
- route repeated post-launch feedback back to that field.

Do not answer uncertainty with stronger marketing language.

## Claim/source trace
- Factual and claim-heavy fields retain source IDs / claim IDs where feasible.
- Numeric copy is traced to product truth or approved claim evidence.
- Missing evidence stays visible as a gap.
- Translation must not increase claim strength.

## Localization / transcreation
Localize the purchase logic, not just words.
- Preserve truth, numbers, specifications, claim strength and warnings.
- Reorder phrasing for natural target-language syntax and local search behavior.
- Adjust information density and CTA to the platform surface.
- Do not add cultural motifs or stereotypes merely to look local.

## SEO / GEO
SEO and generative retrieval benefit from clear entities, attributes, relationships and FAQs. Do not create unverifiable facts for “AI visibility”.

## Measurement
Map listing layers to signals:
- search relevance → eligible impressions / query quality;
- click package → CTR;
- decision architecture → PDP progression / CVR;
- expectation clarity → CS questions / return reasons;
- offer → contribution, not just GMV.

## v0.5.13 Live decision-question coverage
Category priors are scaffolding; the current product's live buyer questions are the operative PDP authority.
- Consume `decision_question_coverage` and `decision_specific_listing_jobs` when available.
- Every atomic shopper question must resolve to a listing field/surface, an asset, or an explicit reason why it does not belong on the listing.
- Do not let a generic category PDP sequence silently replace product-specific questions such as weight, cupholder fit, cleaning, exact compatibility, routine placement or weather boundary.
- A listing field should carry incremental information. If two modules answer the same question with the same evidence, combine them rather than create decorative repetition.
- Category/evidence priority may reorder the sequence, but cannot erase a live product decision job merely because it is lower-priority.

