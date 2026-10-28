# v0.5.14 — Real Production Quality Preflight

## Why this release exists
v0.5.13 made Strategy / Listing / Dynamic Assets materially deeper, but the production handoff could still collapse distinct assets into similar visual execution and could mark a LOCKED_PIXEL asset as provider-ready without an exact bound product master. v0.5.14 fixes that production-runtime gap. It is not a new framework layer and it is not RC.

## Runtime changes
- Added exact source-product-master binding with SHA-256 lineage. Missing or hash-mismatched masters remain missing; the runtime does not invent a substitute.
- LOCKED_PIXEL / real-product production now enters `HOLD_REAL_PRODUCT_PREFLIGHT` when the required exact product master is not bound.
- Every compiled asset now receives a decision-specific `visual_production_signature`, including visual job, composition grammar, evidence plane, camera/view logic, context role, differentiation axis and surface-native modifier.
- The Asset Compiler creates that signature even for direct/legacy asset rows, preventing a bypass around the decision-led visual grammar.
- Added semantic `editable_layer_contract` / frozen layers. LOCKED_PIXEL freezes product master pixels, logo, packaging print, product geometry and product color identity.
- Provider Jobs now carry `production_quality_contract` + `execution_brief` instead of only package hashes and generic QA expectations.
- Provider results must return evidence-bearing quality observations for the relevant dimensions. Boolean checkboxes alone do not satisfy v0.5.14 quality evidence.
- Local Revision maps leaf fields such as headline, composition or prop presence to declared editable layers and blocks product-identity edits outside a newly compiled source-of-truth package.
- Production failure codes can route Learning to visual product-fidelity, surface, Photography/CMF, copy-visual alignment or asset-differentiation execution layers while freezing Product Truth / Positioning / Offer unless evidence implicates them.
- Strategy Authority / per-asset Photography WHY now expose asset visual production signatures so differentiation is upstream, not bolted onto the Provider envelope.

## Provider result quality dimensions
The production contract can require evidence for:
- product identity preservation;
- source product master lineage and product-layer operation;
- decision answer visibility;
- target-surface usability;
- copy-to-visual attribution;
- Photography/CMF alignment;
- visual differentiation versus the asset's assigned decision job.

## Compatibility
The existing nine-section Strategy Authority, dynamic asset count, complete per-asset `00–11`, Final Copy workflow, Provider → Review → Local Revision → Package Hash continuity and bounded Learning loop are preserved.

Historical tests that previously assumed `LOCKED_PIXEL` could enter Provider execution without a source product master were migrated to the new production contract rather than weakening the new behavior.

## Explicit boundary
This release does **not** claim that external image/video Provider quality has been validated on real product masters. The current handoff package did not include exact real product master files plus live external Provider outputs. v0.5.14 therefore establishes a production-quality preflight and executable result contract; the next step is to run the actual Provider → Review → Local Revision → Learning loop on real outputs and fix observed production failures before RC.
