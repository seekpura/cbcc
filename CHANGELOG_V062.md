# v0.6.2 — Human Delivery Hub

This release changes delivery UX, not the underlying strategy authority.

- Added `runtime/cbcc/human_delivery.py`.
- Added mandatory `HUMAN_DELIVERY.json`, `00_PROJECT_HUB.md`, `01_LISTING_UPLOAD_READY.md` in project delivery builds.
- Platform category name / ID / path is now surfaced as a first-class upload field with explicit READY / 待查证 status.
- Rebuilt offline HTML as a responsive tabbed Project Hub rather than sequential Markdown concatenation.
- Added copy-ready listing field cards and one-click copy behavior.
- Added asset portfolio cards, risk/hold panel, deep-dive accordion and file browser.
- Original strategy, per-locale copy, per-asset packages and machine JSON remain authoritative and independently editable.
