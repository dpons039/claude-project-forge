# update — change anything, keep everything coherent

The BrandKit is one system with five artefacts (page, BrandKit.md, design.md,
voice.md, PRODUCT.md). Every change walks the cross-update table below —
never stop at "the page is updated".

## Step 1 — Classify the change

New component block · new wireframe · token value · copy/tone/vocabulary ·
new accent/theme/identity · new UI language · removal.

## Step 2 — The cross-update table

| If the change is... | Also touch... |
|---|---|
| A colour/type/spacing token value | `design.md` FIRST — docs are upstream; the page reads tokens, it does not define them |
| A new component block | The block count/list in `BrandKit.md` — written prose, not derived, so it goes stale silently |
| Copy in a specimen | `voice.md`, wording copied back verbatim — the two never diverge in either direction |
| A string that also exists in the locale catalog | Copy verbatim, punctuation included. Wording licence exists; a *different rule* does not (canonical case: "un correo válido" vs shipped "un correo completo") |
| A wireframe/mockup source | Re-copy into the page's embedded copy (never symlink). **Diff before overwriting** — the embedded copies carry corrections as inline comments a blind re-copy would drop |
| A new accent/theme/identity | `PRODUCT.md § Brand Commitments` if it enumerates them; `design.md` token table; the Colour tab description in `BrandKit.md` if it states a count |
| A new UI language | `voice.md` (per-language register/vocabulary if it differs); decide whether the Voice tab keeps one canonical language for specimens |
| A contrast-affecting token | The theme test file that pins the ratios — a token change nobody re-pins is a stale number waiting to mislead |
| Removal of any of the above | The inverse of its addition row — doc + code + count in the same change |

## Step 3 — Apply the code change

Follow `docs/BrandKit.md` § How to add a block: official classes not raw
tokens; chrome in the docs language, examples in the UI language; strings
verbatim from the settled source; never colour alone. Put the specimen where
the defect can show (a specimen sharing its background with its frame proves
nothing about the boundary; show the state that breaks, not the tidiest one).

## Step 4 — Walk the whole table

Check every row's applicability, not just the obvious one. Most drift
incidents come from the second-order row (the count, the test pin, the
PRODUCT.md enumeration), not the first.

## Step 5 — Offer an audit

After any update, offer to run `audit` as a self-check that no row was
missed.
