# v0.5.8 Multi-Category Strategy Validation

## Validation question
Can the same CBCC runtime preserve one commerce decision architecture while producing materially different strategy, asset portfolio, surface allocation and photography reasoning for different product categories?

## Method
Three materially different product fixtures were compiled through the same Strategy → Listing → Visual → Dynamic Asset → Asset Compiler → Provider Job chain under intentionally comparable platform conditions.

Validation inputs:
1. **Beauty / personal care:** KIYUU K01 project facts.
2. **Fashion / accessory:** UNIQLO Round Mini Shoulder Bag public official-product facts captured 2026-10-27. Source: `https://www.uniqlo.com/us/en/products/E481610-000/00`.
3. **Home durable / food storage:** IKEA 365+ rectangular glass/plastic food-storage public official-product facts captured 2026-10-27. Source: `https://www.ikea.com/us/en/cat/ikea-365-food-storage-49524/`.

The non-KIYUU fixtures are validation inputs only. They are not assertions that those brands currently sell those exact products through TikTok Shop Malaysia.

## Defects found before correction
### 1. Governance was censoring strategy
An exact platform pack with a limited verified-surface list could remove GALLERY/VIDEO objects entirely. This violated the product principle that evidence/governance is a guardrail, not the strategy engine.

### 2. Cross-category visual homogenization
Without an explicit user photography contract, beauty, fashion and home products could inherit the same generic commercial-visual fallback and nearly empty camera planning.

### 3. Beauty-biased decision taxonomy
Fit/wear, capacity, leak/seal, stacking and care questions were not represented strongly enough as distinct purchase decisions.

### 4. Duplicate consumer questions
Different wording for the same purchase decision could create redundant assets because dedupe was based on question text rather than purchase-decision intent.

### 5. Textile material reasoning gap
Transparent/glossy/matte materials had stronger CMF treatment than woven textile products.

## Corrections
- Added category-family execution profiles.
- Added purchase-decision intent classification.
- Added semantic merge by decision intent for auto-curated jobs.
- Preserved explicit user-authored asset jobs exactly.
- Separated platform verification/submission status from strategy-planning eligibility.
- Added category-specific visual territory and photography recommendation ranges.
- Added strategy-derived photography contracts when no explicit contract is supplied; all remain prelight-required and non-factual.
- Added textile/woven CMF lighting logic.

## Observed outputs
### Beauty / personal care — 4 assets
- `IDENTIFY → GALLERY`
- `RELEVANCE → CREATOR`
- `PROOF → GALLERY`
- `USAGE → PDP_VIDEO`

Visual direction: formula/package evidence + realistic routine context with restrained beauty treatment.

### Fashion / accessory — 5 assets
- `IDENTIFY → GALLERY`
- `RELEVANCE → CREATOR`
- `FIT_WEAR → CREATOR`
- `WEATHER_BOUNDARY → GALLERY`
- `CARE_MAINTENANCE → FAQ`

Two wear/adjustment questions were merged into one `FIT_WEAR` asset. Textile lighting now protects weave/soft volume rather than applying a beauty/glass recipe.

### Home durable — 6 assets
- `PACKAGE_CONTENTS → GALLERY`
- `SIZE_CAPACITY → GALLERY`
- `SEAL_LEAK → PDP_VIDEO`
- `STORAGE_STACKING → PDP_VIDEO`
- `MATERIAL_SENSORY → GALLERY`
- `USAGE → PDP_VIDEO`

Two capacity questions were merged into one `SIZE_CAPACITY` asset. Transparent/refraction behavior drives its material-lighting reasoning.

## Platform authority separation test
A deliberately limited exact TikTok Shop US pack still reports unsupported/unverified GALLERY/PDP_VIDEO surfaces, but the strategy graph retains relevant VISUAL/VIDEO objects with `STRATEGY_PLANNING_RESEARCH_REQUIRED`. This preserves strategic exploration while keeping submission certainty honest.

## Non-regression boundary
The release preserves:
- nine Strategy Authority sections,
- question-driven asset count,
- every asset's complete `00–11` package,
- Provider Job / Result / Review / Local Revision / Package Hash workflow,
- v0.5.7 source paths.

## Interpretation
v0.5.8 does **not** prove that every category is solved. It establishes a stronger anti-template runtime: different categories are now expected to produce different decision priorities, surface mixes, visual territory and photography reasoning unless evidence genuinely supports convergence.
