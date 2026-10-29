# Production Contract → Provider Job Binding

## Role
Translate a frozen, Agent-authored asset/video production contract into a provider job **without reinterpreting the commercial idea**. The provider layer executes; it may adapt syntax/API parameters to provider capability, but it may not silently substitute a generic layout, remove product/copy, weaken the art direction or invent claims.

## Bind the full execution object
Every job should carry, where relevant:
- asset/video ID + revision/package hash;
- surface/platform/market/output spec;
- exact model-facing prompt;
- visible-copy block and selected render route;
- real product/reference inputs with roles;
- product identity/fidelity requirements;
- art-direction parameters that change output;
- camera/light/CMF/material program when relevant;
- surface safe zones/crop behavior;
- video shot/timing/audio/subtitle contract when relevant;
- provider/model/quality/size/edit-mode selection;
- expected deliverables;
- QA contract;
- provenance/rights fields;
- allowed local-repair scope.

## Provider adaptation
Adapt only implementation details supported by the provider:
- reference-image slots/order;
- image-edit vs generation endpoint;
- mask/local-edit support;
- exact text capability;
- output size/aspect limits;
- video duration/frame constraints;
- quality mode;
- transparent background;
- seed/variation controls where available.

If the selected provider cannot faithfully execute a material requirement, route to another provider/model or explicit hybrid/post route. Do not silently delete the requirement.

## Integrated generation rule
For normal finished-image production, product/copy/scene/layout/evidence may be generated together. Do not transform an integrated prompt into “background only” because an old compositor path exists.

`POST_COMPOSITE` and `EXACT_PIXEL_COMPOSITE` remain valid only when the frozen contract explicitly selected them or provider limitations make them the best quality route and the Agent revises the production contract accordingly.

## Identity/reference binding
For each reference input state:
- source ID / checksum or provider handle;
- role: PRODUCT_SUBJECT / PACKAGING_FACE / MATERIAL_REFERENCE / STYLE_REFERENCE / HUMAN_REFERENCE / OTHER;
- whether identity preservation is hard or advisory;
- what can be reconstructed for lighting/perspective/scene integration;
- what must not change.

A product reference existing in the project does not mean the product must appear in every asset.

## Job lifecycle
Return/record:
- QUEUED / RUNNING / COMPLETE / FAILED;
- provider job ID;
- submission timestamp when available;
- exact package/revision hash executed;
- provider response metadata;
- output file/handle;
- failure reason;
- retry/alternate-provider route.

A provider “COMPLETE” response proves transport/execution completion only.

## Result handoff
After provider completion, hand the actual output to commercial visual/video QA. Required questions include:
- did the product identity survive?
- is required copy exact and legible?
- did the decisive scene/action/geometry survive?
- are material/contact/human details plausible?
- are there generation artifacts?
- is the asset surface-ready?
- does the result still express the intended hypothesis?

Only after output QA can the asset become release-ready.

## Revision integrity
A contract change creates a new package/revision/job. Local repair must record:
- parent output;
- failing QA item;
- changed layer;
- frozen layers;
- new prompt/edit/mask inputs;
- new result.

Do not overwrite lineage.

## Quality bar
The provider job should be reproducible enough to explain **what exact commercial contract was executed**, while remaining implementation-native to the selected provider. Transport success, provider completion and strategic/visual approval are three different states.