# v0.6.41 — Project-Authored SaaS Workspace

The first v0.6.40 renderer wiring removed the old capability sidebar but used a mandatory project-map card grid. Review identified that this would simply replace one fixed dashboard with another.

## Corrected
- persistent navigation remains project identity + Project Home + neutral Project Objects access only;
- current project objects live in a searchable SaaS object switcher/drawer rather than a permanent capability menu;
- the project home no longer renders a mandatory card wall;
- current priority remains independent of information architecture;
- object labels still consume current product / market / platform / locale / asset context;
- generic module rails remain contextual horizontal lenses;
- asset subviews remain lenses on one object rather than production phases;
- underlying v0.6.37 commercial depth and all full pages remain intact.

The object switcher is a deterministic Runtime fallback, not a universal Host-native design template. Host-native Agent authoring may use another interface when the project warrants it.
