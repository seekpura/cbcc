# Global Chinese Interpretation Authority — v0.6.43

## Highest-precedence human-delivery language rule
Human delivery is Chinese-first. **Every human-facing foreign-language commerce string that an operator is expected to understand must keep its exact original text AND carry a Chinese interpretation / meaning / use in the same human object.** Chinese interpretation is part of the finished business object, not optional metadata.

This applies regardless of whether the object is currently publishable, preserved for reference, in a test pool, paid media, PDP content, or an operational/analysis surface.

## Mandatory scopes
### Listing / Seller Center
Provide Chinese interpretation for every foreign human-facing value, including when present:
- category / classification / category path;
- title / product name when localized;
- highlights / bullets / selling points;
- description / short description / long description;
- attributes and variation names/values;
- package contents / usage / warnings / FAQ;
- search terms / backend terms / keyword clusters (Chinese may explain search intent rather than mechanically translate word-for-word);
- platform field values and other publishable localized fields.

Human field titles are Chinese-first. Raw platform keys such as `description`, `category`, `attributes` are secondary technical identifiers, never the primary operator label.

### Visual assets
Every target-market Visible Copy line, CTA, evidence line, headline, caption or shopper-facing text needs Chinese meaning/use in the same asset object. Model Prompt EN is paired with Model Prompt CN; Production/Assembly Notes remain Chinese-first for human operation.

### Video / creator
Every foreign hook, first-frame line, on-screen text, subtitle, caption, dialogue, VO/script, cover text and CTA needs Chinese interpretation in the same video object/shot object.

### Advertising
Every foreign hook, headline, primary text, body/caption, creator script, offer copy, CTA and landing-message line needs Chinese interpretation in the same ad/variant object.

### Review / CS / returns
When raw foreign review, comment, complaint, return reason or customer-voice excerpt is surfaced to a human operator, preserve the verbatim original and add Chinese semantic interpretation in the same review/theme object. Do not silently replace the original quote.

### Research / strategy / competitor evidence
When a foreign shopper quote, competitor copy, category/segment label, positioning/value-proposition string or evidence excerpt is directly surfaced in the primary human artifact, preserve the original and add Chinese interpretation/use alongside it.

## Technical identifiers and proper names
Do not force literal translation of immutable identifiers or technical values such as SKU, GTIN/EAN/UPC, URL, URI, HEX, INCI, exact model/part number, HS code or official brand/proper names. Their **human field label and role/use explanation must still be Chinese** when needed. Official names remain exact.

## Semantic requirement
Chinese interpretation is for operator understanding, not mechanical bilingual decoration:
- Category/classification → semantic Chinese category equivalent;
- Search terms → Chinese search intent/use explanation is acceptable and often preferred;
- Review/consumer quote → Chinese meaning while preserving tone/decision signal;
- CTA → Chinese meaning plus CTA/use if ambiguity exists;
- Platform-specific terminology → Chinese explanation can retain the official foreign term in parentheses.

## Completion rule
`待补中文释义`, `TBD translation`, blank Chinese companion, or foreign-only human content is **not a valid FULL completion state**.

The Agent must author missing Chinese interpretation before finalization. Runtime must audit and BLOCK a false finished state; Runtime must not invent arbitrary machine translations to make a gate pass.

A FULL artifact may contain foreign-only text only when it is a technical identifier/proper name exempted above, or inside an English Model Prompt that has its paired Chinese Canonical Prompt and is clearly labeled as model execution input.

## UI rule
Whenever original foreign content is shown to the operator, its Chinese interpretation/use must be directly visible in the same object/card/row/lens. Do not require opening another file or a global translation appendix. Raw platform keys are secondary labels beneath Chinese human titles.
