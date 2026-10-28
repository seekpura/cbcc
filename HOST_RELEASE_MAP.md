# CBCC Host Release Map

GitHub `main` remains the source-of-truth capability baseline.

## Current repaired source build
- Source capability baseline: `0.6.29-final-stabilization` with post-release human-delivery/FULL-contract repairs on `main`.
- Accepted release workflow run: `40785985043` (`CBCC human-delivery release acceptance`).
- Accepted source commit for that packaged artifact: `08831089c6d26e28fa2d10b87d02790876f8d46d`.
- GitHub Release asset name remains `v0.6.29` because the corrective work repairs the existing stabilization baseline rather than starting a new capability cycle.
- Plugin ZIP SHA256: `8bf4bbdb020e4c8653df501a2b1de4ac5b6479634e6dda74feab3776c4f66b08`.

## ChatGPT host release
- Plugin ID: `plugins_6ae0bf51262c8191a0065b9b73594169`.
- ChatGPT host version: `0.6.30`.
- Host release ID: `pluginrel_6ae2824ba8f481919c55f8453ca96d57`.
- Reason for host version difference: the Plugin Creator host automatically bumps an unchanged semantic version to the next patch when an existing plugin is edited. The host version therefore records the repaired deployment; it does not define a separate CBCC capability architecture.

## Authority rule
Do not infer capability from a version number alone. The accepted source contract is the current GitHub `main` plus its release acceptance tests. A complete commerce project must pass FULL hard-contract coverage and real human-delivery artifact acceptance; task-scoped work keeps dynamic scope autonomy.
