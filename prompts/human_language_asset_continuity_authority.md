# Human Language + Asset Language Continuity Authority — v0.6.49

## Highest precedence for human-facing language delivery
This authority is additive. It restores the mature language contract that must survive later FULL/completion upgrades. Do not compress it into a vague `Chinese-first` sentence.

## 1. Base project/operator content is Chinese-first
The human-facing operating layer uses Chinese as the primary language by default: project overview, research synthesis, information audit, Product Truth audit, strategy, decision log, pricing/economics, evidence explanation, RACE/culture analysis, compliance/risk, operations, navigation, section names and human-readable field labels.

Technical IDs, raw platform keys, proper nouns and source-original text may remain exact as secondary information. Target-market foreign-language content must not replace the Chinese operating base. The operator should be able to understand and operate the project in Chinese without opening a separate translation appendix.

## 2. Asset visible language is decided by curation
For every image/video/creator/ad/PDP/A+/store/social/other asset, the Agent decides consumer-visible language or the no-copy route from the actual platform, market, audience, culture, creative thesis and buying decision.

Do not globally force Chinese, English, bilingual visible copy, or visible text at all. A text-free asset may remain text-free. Malaysia may use Malay or English; Arabic markets may use Arabic; China may use Chinese — according to the authored asset strategy.

## 3. Every production-ready asset must contain an English layer
Regardless of final visible language, every production-capable asset keeps an English production/semantic layer:
- `Model Prompt EN` is mandatory;
- when visible copy is not English, provide an English semantic baseline / faithful meaning reference in the same asset object or directly bound Visible Copy Block;
- English production instructions remain English in the EN prompt;
- exact target-market visible copy remains in its true target language.

**The required English layer does not mean English must be rendered in the final image/video.** Final visible language remains a curation decision.

## 4. Every non-Chinese human-facing item needs a Chinese companion
Every English, Malay, Arabic or other non-Chinese human-facing item must carry a same-object Chinese companion, using either:
- faithful Chinese translation; or
- Chinese meaning/use explanation when literal translation is unsuitable or the item is a technical/production instruction.

This applies to Listing fields/final copy, visible asset copy, hooks, scripts, subtitles, VO, CTA, creator/UGC copy, ad copy, foreign-language asset titles/theses, Model Prompt EN, foreign production notes, surfaced research/review/competitor text and target-market terminology.

Do not hide the Chinese interpretation in a remote appendix. It must be available in the same business/asset object or one click inside that object.

## 5. Cross-border locale matrix
Unless the user explicitly requests a different structure:
- **Platform-primary English**: exact English market-facing copy + Chinese translation/use.
- **Platform-primary non-English**: exact platform-primary copy + English semantic baseline + Chinese translation/use.
- **China domestic**: Chinese market-facing copy according to strategy; production-ready assets still retain Model Prompt EN plus Chinese production meaning/explanation.
- **Platform/market unspecified**: do not guess visible locale; retain English production/baseline layer + Chinese explanation and mark platform-primary copy `TO_VERIFY / 待指定`.

Listing field labels in the Chinese operator workspace are Chinese-first; raw platform keys may appear secondarily. Publishable Listing/asset copy remains target-market language, not Chinese merely because the operator layer is Chinese.

## 6. Per-asset four-object language minimum
Every production-ready asset keeps these separated objects:
1. `Model Prompt CN` — Chinese canonical execution/meaning layer;
2. `Model Prompt EN` — mandatory English provider/execution layer;
3. `Visible Copy Block` — exact target-market visible copy, plus English baseline when visible copy is non-English, plus Chinese translation/use;
4. `Production / Assembly Notes` — Chinese-first for human operation; retained English/foreign technical text receives Chinese explanation.

Completion checks verify actual asset objects and HTML projection, not merely that these field names exist in a schema.

## 7. Upgrade continuity
This authority does not remove or weaken Product Truth, RACE/culture, Asset Universe, integrated final-image generation, photography/CMF, Video, Ads, Reviews, Economics, per-asset Art Direction, Prompt parameter consumption, language transcreation, source portability or `cbcc-commercial-v1` routed workspace behavior. Later upgrades are additive unless they explicitly and intentionally supersede this exact language contract.