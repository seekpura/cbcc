# v0.6.40 — Project-Authored HTML Runtime Wiring

v0.6.39 established the project-authored HTML authority, but the final `delivery_workspace` path still stopped after asset compatibility transformation and did not invoke the project-authored presentation transform.

## Fixed
- wire `project_authored_html()` into `delivery_workspace.build_delivery_html()`;
- remove the persistent capability sidebar from final DOM presentation;
- keep permanent navigation to project identity + return to Project Map only;
- replace next-step command cards with a project-object map using current product / market / platform / locale / asset context;
- keep current priority separate from information architecture;
- change generic module phase rails into contextual horizontal lenses;
- suppress strategy/content/evidence numbering by default when it only implies a fake workflow;
- preserve all underlying v0.6.37 commercial content, Listing, Visual/Video, asset and production depth.

## Verification target
The focused regression test proves both the transform itself and the actual `delivery_workspace.build_delivery_html()` wiring.
