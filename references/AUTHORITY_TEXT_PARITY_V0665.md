# v0.6.65 Current-Release Text Parity

## Purpose
Post-install v0.6.64 readback proved functional/source parity, but one forward-carried Skill sentence still said `Before claiming v0.6.62 behavior complete:`. This did not change Runtime behavior, but it violated the rule that current authority text must not carry stale release identity.

## Repair
- Completion gates use version-agnostic wording: `Before claiming current installed release behavior complete:`.
- The stable implementation-accounting authority is `REQUIREMENT_IMPLEMENTATION_MATRIX_CURRENT.md` rather than a version-numbered filename.
- `SOURCE_REQUIREMENT_NON_REGRESSION_LOCK.md` is a stable `CURRENT` authority. Historical versioned addenda remain for provenance only.
- Business Runtime remains unchanged from the v0.6.64 installed and verified behavior.

## Acceptance
Actual installed plugin must be re-read after update. Both Skills must be byte-identical; manifest/Skills/VERSION must share one 0.6.65 family; the Skill must contain the generic release-proof wording and must not contain `Before claiming v0.6.62 behavior complete:` or another hard-coded historical release in that gate. Detailed cumulative ledger, verbatim source, CURRENT matrix/source lock, v0.6.63 real-K01 audit and Runtime consumers must all remain present.

Fresh positive K01 FULL host/plugin E2E remains pending; this source-text parity repair cannot close it.