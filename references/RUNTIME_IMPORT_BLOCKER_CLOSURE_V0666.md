# v0.6.66 Runtime Import Blocker Closure

## Real failure
GitHub Actions run `41071064281`, job `124114975096`, failed during pytest collection before requirement/runtime tests could execute. Python 3.11 raised:

`SyntaxError: f-string expression part cannot include a backslash`

at `runtime/cbcc/human_delivery.py` in the asset-overview Markdown row, where `.replace('|','\\|')` was embedded directly inside an f-string expression.

## Source repair
Commit `99d434b7151ea9ef7d8aa6e2f5fa74a1e9708526` changed only that source expression: role text is escaped before interpolation, then the precomputed value is inserted into the f-string. The one-shot repair workflow ran `python -m py_compile runtime/cbcc/human_delivery.py` successfully before committing.

## Release rule
A strict `REQ-001..060` Consumer Map or unit-level PASS is not runnable proof when package import fails. v0.6.66 acceptance requires CI to import the real runtime and execute the focused regression suite from clean GitHub checkout. Any next failure is treated as a real blocker and fixed before package publication.

The installed plugin must ultimately receive this exact fixed source from a CI-built GitHub artifact, not a hand-authored approximation. Fresh positive K01 FULL host/plugin E2E remains separate and pending until current Host Skill snapshot parity is proven.