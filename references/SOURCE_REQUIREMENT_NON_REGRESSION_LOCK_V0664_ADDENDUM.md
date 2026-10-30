# Source Requirement Non-Regression Lock — v0.6.64 Addendum

Load after the current source lock and the v0.6.63 addendum.

Additional mandatory authorities:
- `REQUIREMENT_CONSUMER_MAP_V0664.json` — REQ-001..060 concrete Consumer + proof-object map;
- `HOST_SKILL_SNAPSHOT_PARITY_LOCK_V0664.md` — installed plugin versus active Host Skill snapshot release-proof boundary.

Additional release rules:
1. every REQ-001..060 row must name one or more concrete existing Consumer paths and one or more concrete proof objects;
2. generic placeholders such as “relevant Runtime consumer”, `TBD`, or `TODO` are release failures;
3. `scripts/check_v0664_requirement_consumer_map.py` must pass `60/60` with zero issues before publishing the release;
4. a row may remain `E2E_PENDING`; source/test existence may not promote it;
5. actual installed plugin parity and active Host Skill snapshot parity are separate checks;
6. when the Host Skill snapshot is stale relative to the installed release, positive Host-native FULL E2E remains pending until a fresh Host context loads the current Skill.
