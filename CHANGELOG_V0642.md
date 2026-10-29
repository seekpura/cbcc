# v0.6.42 — Regression Recovery: v0.6.36 Interaction + v0.6.37 Commercial Depth

## Why this release exists
v0.6.39–v0.6.41 misinterpreted “不要流水线” as permission to replace the mature v0.6.36 workspace interaction model. In real FULL delivery this caused content to collapse into weaker shells / long-page behavior, hid commercial depth and made the operator experience worse. A separate Host execution regression also treated TikTok Shop Malaysia `max_images=9` as if it were an Asset Universe limit, despite the existing authority explicitly saying it is only an activation-set constraint.

## Recovery
- restore `delivery_html.py` / v0.6.36 routed workspace as final interaction authority;
- one active primary work surface at a time; keep module subviews, per-asset detail routes, search, copy, responsive navigation and print/PDF projection;
- stop calling the v0.6.39–0.6.41 global `project_authored_html()` post-processor from final delivery;
- add v0.6.37+ Operator Execution + Commercial Brain as an additive `运营执行` route only when real operator/commercial artifacts exist;
- preserve full Strategy / Listing / Visual / Video / Assets / Prompts / Economics / Ads / Review / Evidence content;
- reassert that platform gallery/video capacity constrains only the simultaneous Live/Activation Set, never total Asset Universe;
- preserve multi-Hero, multi-Benefit/Proof, Paid Ads, PDP/A+, Detail, Store/Banner, Social/Creator/UGC, Video, Test Pool and Rotation Pool variants when they carry distinct hypotheses;
- restore a Host-native interaction floor so “project-authored” cannot be used to flatten FULL delivery into one long page or another thin shell;
- strengthen release packaging so Host Skill and canonical authority cannot silently shrink or drift in version/critical rules.

## Regression tests
- final delivery keeps routed pages, asset detail route, subviews, search and copy actions;
- `运营执行` is additive and does not replace the project;
- `gallery_capacity=9` can coexist with Asset Universe > 9 and multiple Hero/Paid/PDP/Video variants;
- final renderer no longer imports/calls `project_authored_html()`;
- release guard checks interaction-floor, Asset Universe, multi-Hero, seven-tool, per-asset production-depth and version-parity authority in packaged Host/Canonical skills.
