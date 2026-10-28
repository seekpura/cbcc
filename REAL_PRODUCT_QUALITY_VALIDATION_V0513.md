# CBCC v0.5.13 — Real Product Strategy Quality Validation

## 1. Purpose
v0.5.13 is a strategy-quality release, not a framework-count or test-count release. The objective was to run the already-integrated CBCC runtime against current, source-bound real products and identify where a structurally complete Strategy Authority still produced shallow, over-merged, generic or incorrectly evidenced commerce decisions.

The validation deliberately began from the v0.5.12 runtime before adding new logic. Runtime changes were made only after blind compilation exposed real business-quality failures.

## 2. Real-product validation set
Four materially different products were used:

| Product | Category | Source-bounded product facts used | Economics posture |
|---|---|---|---|
| COSRX Advanced Snail 96 Mucin Power Essence | Beauty | 100 mL; 96.3% snail secretion filtrate; 1,000 ppm sodium hyaluronate; official hydration-study context carried through source/claim IDs | Landed cost / fees / ad economics not supplied; do not lock Offer |
| Anker Prime 20,000mAh Power Bank (200W) | Electronics | 20,000mAh; 2 USB-C + 1 USB-A; up to 200W total; up to 100W per USB-C under supported conditions; 545 g | Landed cost / fees / ad economics not supplied; do not lock Offer |
| UNIQLO Round Mini Shoulder Bag | Fashion accessory | approx. 4L; dimensions/strap; nylon/polyester; adjustable strap; pockets; light-rain water-repellent boundary | Landed cost / fees / ad economics not supplied; do not lock Offer |
| Owala FreeSip Stainless Steel Water Bottle 24oz | Home durable | 24 fl oz; FreeSip straw + swig mechanism; leak-proof claim; triple-layer insulation; care; dimensions; warranty; official 24-hour-cold claim | Landed cost / fees / ad economics not supplied; do not lock Offer |

Source IDs, market/search/review observations and competitor observations are preserved in each validation request and project trace. Public facts are not converted into unsupported causal, health, durability or economic claims.

## 3. Blind-test failures found before v0.5.13 fixes
The first v0.5.12 compilation exposed real quality failures:

1. **Decision classification was not consistently category-aware.** COSRX identity/routine language could be classified as package content; UNIQLO capacity could fall into generic usage; weather-boundary language could be stolen by broad identity matching.
2. **Dynamic-asset merging was too aggressive.** Anker portability/weight and display-value questions, and Owala thermal-proof questions, could disappear because jobs shared a broad funnel/surface bucket.
3. **Fixing asset curation alone did not fix Listing.** Product-specific shopper questions could exist in assets while the PDP sequence still displayed generic category objections.
4. **Proof contracts were too broad.** A clinical-evidence question could inherit a generic formula-proof condition; cleaning/seal/comparison questions could inherit unrelated evidence templates.
5. **Missing economics could emit an overly optimistic Offer-readiness label.** An economics object existed even when the actual required unit-economics inputs did not.
6. **Deterministic Positioning was factually correct but commercially shallow.** Primary propositions often repeated the leading specification rather than translating facts into shopper value, trade-offs, boundaries and purchase logic.
7. **Final Copy numeric audit did not understand field-level approved Claim authority.** Anker highlights adding the approved `100W` fact were correctly blocked as an untraced extra number at first, even though that field explicitly referenced the approved Claim containing `100W`.

These failures, rather than a desire to add more architecture, drove the v0.5.13 changes.

## 4. Runtime fixes

### 4.1 Atomic consumer-decision lineage
Decision interpretation is now category-aware across Dynamic Asset, Listing/PDP and Evidence Reconciliation. Compound questions split only when they contain independent purchase decisions. Every atomic decision remains traceable through:

`source shopper question → atomic decision → decision intent/topic → asset or explicit merge`

Auto-merge now requires matching **decision intent + decision topic + surface + asset family**. The system still seeks the fewest useful assets, but it may not remove incremental purchase information merely to reduce asset count.

### 4.2 Listing coverage now follows live decisions
Strategy Authority now includes **Consumer Decision Question Coverage** and **Decision-specific Listing Jobs**. Category PDP priors can reorder information but cannot silently erase a current product question.

The effective chain is:

`Consumer Decision Question → Atomic Decision → Asset Job → Listing Job → Proof Condition`

### 4.3 Topic-specific proof contracts
Evidence conditions are now selected using decision intent **and topic**, including:

- Clinical evidence → `CLAIM_SPECIFIC_SOURCE`
- Formula / ingredient composition → `LABEL_OR_AUTHORIZED_SPEC`
- Compatibility → `COMPATIBILITY_MATRIX_OR_EXACT_SPEC`
- Conditioned performance → `CONDITIONED_PERFORMANCE_EVIDENCE`
- Size / fit / portability → `PRODUCT_MEASUREMENTS_OR_SCALE_EVIDENCE`
- Care → `CURRENT_CARE_INSTRUCTIONS`
- Seal / leak → `CLOSURE_SEAL_EVIDENCE`
- Weather boundary → `CURRENT_PRODUCT_WEATHER_CARE_SOURCE`
- Comparison / differentiation → `CURRENT_COMPARISON_SOURCE_SET`
- Package contents → `CURRENT_PACKAGE_SPEC`
- Usage → `CURRENT_USAGE_INSTRUCTIONS`

A product may need a type of proof without currently possessing that proof. The contract never converts “should prove” into “already proven.”

### 4.4 Economics boundary corrected
If landed cost, fees and other required economics are not supplied, the formal state remains:

`economics_status = INSUFFICIENT_DATA`

and Category Offer remains:

`ECONOMICS_NOT_SUPPLIED_DO_NOT_LOCK_OFFER`

Real-product strategy depth is therefore not achieved by inventing contribution margin, coupon room, affiliate room or ad room.

### 4.5 Host Strategy Authoring operationalized
The existing `strategy_annotations` contract is now a formal runtime artifact:

`artifacts/strategy_host_authoring_request.json`

The Host/model is asked to deepen:
- value translation;
- Positioning / Value Proposition;
- non-redundant Message Hierarchy;
- Listing rationale;
- Visual / Photography WHY;
- platform/content execution logic.

It must follow the same strategy decision chain:

`WHAT → WHY → EVIDENCE → CONSUMER LOGIC → PLATFORM LOGIC → CULTURE LOGIC → BUSINESS LOGIC → EXECUTION → MEASUREMENT`

Protected deterministic authorities cannot be overwritten through Host annotations, including Product Truth, claim ledger, Market/Economics/Experiment calculations, research quality, exact policy authority, claim/source trace, Final Copy release state and asset hashes.

### 4.6 Final Copy field-level Claim authority
Extra numeric content in authored copy remains blocked by default. It is permitted only when the **same listing field** already references an **approved Claim** that contains the extra number.

This fixed the Anker `100W` case without weakening numeric drift protection. A `100W` fact with no field-level Claim authority still fails hard audit.

## 5. Real-product result after fixes

### 5.1 COSRX — Beauty
Five source shopper questions compile into **six atomic decision assets** because the first compound question contains independent identity and routine decisions:

- `IDENTIFY`
- `USAGE / ROUTINE_USE`
- `PROOF / FORMULA_FACTS`
- `MATERIAL_SENSORY`
- `PROOF / CLINICAL_EVIDENCE`
- `INGREDIENT_COMPOSITION`

Coverage: **6 / 6 atomic decisions; 0 uncovered**.

Deterministic baseline proposition:
> Contains 96.3% snail secretion filtrate.

Host Strategy proposition:
> A 96.3% snail-filtrate essence with explicit hydration-study context and clear routine, texture and source boundaries.

The change is not a new product claim. It translates the already-authorized facts and shopper questions into a bounded purchase logic. Clinical evidence and formula facts now use different proof contracts.

### 5.2 Anker — Electronics
Five source questions remain **five assets**:

- `IDENTIFY`
- `COMPATIBILITY`
- `PERFORMANCE_PROOF / MULTI_DEVICE_PERFORMANCE`
- `PORTABILITY`
- `DECISION_SUPPORT / DISPLAY_VALUE`

Coverage: **5 / 5; 0 uncovered**.

Deterministic baseline proposition:
> 20,000mAh capacity with up to 200W total output.

Host Strategy proposition:
> 20,000mAh portable power with up to 200W total output—valuable only when exact compatibility, power sharing and the 545g carry trade-off fit the shopper’s use case.

The strategy therefore includes the real carry trade-off and compatibility/power-sharing decision instead of presenting maximum wattage as sufficient purchase logic.

### 5.3 UNIQLO — Fashion accessory
Five source questions remain **five assets**:

- `SIZE_CAPACITY`
- `FIT_WEAR`
- `DECISION_SUPPORT / ORGANIZATION`
- `WEATHER_BOUNDARY`
- `DIFFERENTIATION`

Coverage: **5 / 5; 0 uncovered**.

Deterministic baseline proposition:
> Approximate 4L capacity with adjustable strap and interior pockets.

Host Strategy proposition:
> Small crescent silhouette without giving up everyday carry clarity: 4L capacity, adjustable wear and interior organization, with the light-rain limit stated plainly.

The water-repellent question remains one bounded weather job rather than being over-split into repetitive assets.

### 5.4 Owala — Home durable
Five source questions remain **five assets**:

- `DIFFERENTIATION`
- `SEAL_LEAK`
- `CARE_MAINTENANCE`
- `SIZE_CAPACITY`
- `PERFORMANCE_PROOF / THERMAL_PERFORMANCE`

Coverage: **5 / 5; 0 uncovered**.

Deterministic baseline proposition:
> Patented FreeSip spout lets the user sip through the built-in straw or swig through the wide-mouth opening.

Host Strategy proposition:
> A 24oz insulated bottle built around two drinking modes, with leak, cleaning, carry-fit and 24-hour cold expectations made explicit before purchase.

The result makes the purchase decision legible without creating a new thermal, leak or durability claim.

## 6. Final Copy validation
Final Copy was exercised for Anker and Owala after the Strategy Authority fixes.

### Anker
- title: `APPROVED_FINAL`
- highlights: `APPROVED_FINAL`
- attributes: `APPROVED_FINAL`

Result: **3 / 3 approved final fields**.

The highlights field initially failed because the Host added `100W`, an extra numeric token relative to that source field. The runtime fix did **not** remove the fact and did **not** disable the hard check. It accepted the number only after verifying that the same field explicitly referenced the approved `C-ANKER-02` Claim containing `100W`.

### Owala
- title: `APPROVED_FINAL`
- highlights: `APPROVED_FINAL`
- usage: `APPROVED_FINAL`
- package: `APPROVED_FINAL`

Result: **4 / 4 approved final fields**.

### Review boundary
These approvals use `reviewer_type = HOST_VALIDATION_REVIEW` with the explicit note:

> Host validation review; not represented as independent human certification.

They demonstrate the runtime release workflow and hard-boundary behavior. They are **not** represented as independent native-language human certification.

## 7. Production boundary
No real image/video Provider execution is fabricated for COSRX, Anker, UNIQLO or Owala in this release.

Reason:
- exact locked product-master/reference-image files were not supplied for these public-product cases;
- no live external image/video Provider connector was executed.

The runtime can compile assets and production contracts, but a real Provider Result must originate from an explicit external production action and then enter the existing Provider Result → Review → Local Revision → Learning loop.

## 8. What this release proves — and what it does not
v0.5.13 provides evidence that:
- real-product buyer questions no longer have to fit a beauty-centric template;
- dynamic asset count remains decision-driven;
- source questions are auditable through atomic decisions into assets and Listing jobs;
- proof requirements are more specific to the actual decision;
- Host Strategy synthesis can deepen commercial meaning while deterministic authorities remain protected;
- Final Copy can use traced approved facts without weakening numeric hard checks;
- missing economics stays missing.

It does **not** prove that external production quality is ready for RC. Real product masters, live Provider outputs, independent/human review where required, and repeated multi-product production-learning cycles remain the next quality frontier.

## 9. Validation posture
The compatibility test suite is used only as non-regression evidence. v0.5.13 progress is defined by the real-product failures found, the runtime changes made to correct them, and the resulting Strategy/Listing/Final Copy behavior—not by a PASS count.
