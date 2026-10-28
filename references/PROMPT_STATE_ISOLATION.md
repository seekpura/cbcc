# Prompt / Internal-State Isolation

The final image/video generation prompt is an execution artifact, not a serialized project database.

Include only what the generation model needs:
- current product and approved visible copy;
- canvas/aspect/size;
- product/source fidelity instruction;
- composition/geometry/scale;
- camera/lens/lighting/CMF/image behavior;
- casting/culture behavior when relevant;
- approved semantic elements;
- typography-safe area or text-rendering instruction;
- concise precision boundaries needed for truth/compliance.

Keep outside the final prompt:
- workflow state names;
- version history;
- asset IDs unless useful for operator identification;
- QA checklists;
- internal evidence grades and source IDs;
- large serialized strategy objects;
- repeated policy prose.

Complex technical typography/layout instructions belong in a deterministic `layout_contract`, not a bloated generative prompt.
