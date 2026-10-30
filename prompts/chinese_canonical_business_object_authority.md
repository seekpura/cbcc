# Chinese-Canonical Human Business Object Authority — v0.6.51

## Purpose
A real v0.6.49 delivery proved that having a few `*_cn` fields is not enough: Market/Audience, Strategy, Frameworks, Visual Master, RACE, Culture, Content Matrix, Asset detail, Production Notes and other operator content can still render as English. Chinese-first is therefore an **object-authoring and rendered-surface invariant**, not a field whitelist.

## 1. Canonical operator language
For a Chinese-default project, every human-operable business object is authored with Chinese as the canonical primary value. This applies globally to Product Truth, Market, Audience, Intersectionality, Strategy, Frameworks, Pricing/Economics/Offer, Visual/Photography/CMF, Content Matrix, RACE, Culture/Localization, Compliance/Risk, Evidence, Ads, Reviews, Measurement, Asset Universe, Asset Detail, Video/Creator/LIVE, Production/Assembly Notes and Operations.

Any string that answers what / why / evidence / tradeoff / implication / guard / execution / decision / metric / risk / next action / production instruction is Chinese-primary. Do not author English operator prose first and depend on a later translator or a remote `_cn` field.

Examples:
- market fact/effect displayed to the operator are Chinese;
- audience primary/secondary/gender/income/geography/language/culture are Chinese;
- STP/JTBD/AIDA/FABE/4P/Funnel explanations are Chinese while framework names remain exact;
- visual thesis/composition/camera/light/material/fidelity are Chinese execution prose containing exact values such as 85mm/5200K/2:1;
- asset question/job/WHY/metric/composition/camera/light/production_notes are Chinese;
- Content Matrix and RACE descriptive fields are Chinese while platform names, IDs and metric abbreviations remain exact.

New modules inherit this invariant automatically. No module is exempt because its field name was absent from an older validator.

## 2. Explicit foreign-first zones
Only exact target-market Listing copy, exact visible asset copy/hook/subtitle/VO/CTA, `Model Prompt EN`, raw source quotations/titles where fidelity matters, platform raw keys, proper nouns, IDs, INCI, URLs and code may remain foreign-first.

Every foreign-first human item still needs same-object Chinese translation or meaning/use. Platform-primary non-English additionally keeps an English semantic baseline. Raw foreign research/review/competitor content keeps source-original + Chinese semantic interpretation in the same object.

## 3. Renderer contract
`index.html` renders Chinese canonical operator values on the primary surface. Foreign/source values are secondary details, exact-copy blocks or expandable sublayers. A page fails if English business prose is primary while Chinese exists elsewhere.

## 4. Asset contract
Every production-ready asset keeps:
1. Chinese business/creative rationale;
2. Model Prompt CN;
3. provider-readable Model Prompt EN;
4. exact target-market Visible Copy;
5. English semantic baseline when target copy is non-English;
6. Chinese translation/use;
7. Chinese-first Production/Assembly Notes;
8. source/reference/fidelity/QA/repair.

The English layer does not force English onto the final image/video. `Model Prompt EN` must not contain Chinese execution prose; exact non-English render strings may appear only as explicitly quoted visible copy.

## 5. Standalone media
Any media actually shown in `index.html` must have an embedded data/blob source or embedded fallback. `src="sources/foo.png"` alone fails standalone delivery even when the ZIP contains the file.

## 6. Acceptance
Completion fails when any operator business prose is foreign-only outside explicit foreign-first zones. A validator that checks only a hardcoded set such as `HUMAN_KEYS`, a few `_cn` fields, file existence, headings or booleans cannot certify completion.
