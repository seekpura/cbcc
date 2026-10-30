# v0.6.66 Runtime Import Blocker Closure

## Real failure
GitHub Actions run `41071064281`, job `124114975096`, failed during pytest collection before requirement/runtime tests could execute. Python 3.11 raised:

`SyntaxError: f-string expression part cannot include a backslash`

at `runtime/cbcc/human_delivery.py` in the asset-overview Markdown row, where `.replace('|','\\|')` was embedded directly inside an f-string expression.

## Source repair
Commit `99d434b7151ea9ef7d8aa6e2f5fa74a1e9708526` changed only that source expression: role text is escaped before interpolation, then the precomputed value is inserted into the f-string. The one-shot repair workflow ran `python -m py_compile runtime/cbcc/human_delivery.py` successfully before committing.

## Next CI failures and resolution
After the SyntaxError was removed, clean-source CI reached the historical focused suite and reported four failures. Two were real source-contract drift and two were formatting-bound tests:
- CURRENT Source Lock had lost exact historical semantic anchors `read before every release change` and `actual FULL project materialization path`; these were restored explicitly, together with the protected Chinese capability anchors 人物、场景、道具、摄影、灯光、CMF、材质、构图、文案、文化、视频.
- The Art Direction final-boundary test was tied to one historical assignment spelling even though Runtime still normalized before compile and finalized the semantic membrane afterward. The test now checks the semantic call order with a whitespace/assignment-form tolerant expression.
- The workspace shell test treated spaces around `WORKSPACE_SHELL_VERSION = 'cbcc-commercial-v1'` as a regression. It now verifies the assignment semantically while retaining the same exact shell-version requirement.

No commercial behavior was weakened to satisfy these tests.

## Release rule
A strict `REQ-001..060` Consumer Map or unit-level PASS is not runnable proof when package import fails. v0.6.66 acceptance requires CI to import the real runtime and execute the focused regression suite from clean GitHub checkout. Any next failure is treated as a real blocker and fixed before package publication.

The release workflow must also run the strict 60-row Consumer Map checker, the real-K01 host-shortcut regression test, and current source/Host-snapshot parity checks before artifact publication.

The installed plugin must ultimately receive this exact fixed source from a CI-built GitHub artifact, not a hand-authored approximation. Fresh positive K01 FULL host/plugin E2E remains separate and pending until current Host Skill snapshot parity is proven.