# BrandKit page — canonical structure

The complete set of headings the page covers. This
file is an OUTLINE, not code: `init-page` generates each block fresh from the
project's real tokens/components, and `audit` check #15 uses this list as the
canonical coverage checklist.

Rules: every heading below either exists on the page or is annotated in
`docs/BrandKit.md` as "skipped: <reason>". Headings marked *(per project)*
only apply when the project has the thing. `[DOMAIN]` items are named by the
project.

## Header (not a tab)

- **Mark + page title + "Dev only"** — the mark at header size, real component
- **Global controls** — one selector per compound state dimension the token
  system has (theme/mode, accent or identity, density, fonts…). They change
  everything at once; the point is whether a decision survives every
  combination

## Tab: Foundations

- **The mark** — component vs shipped files, variants (on card / on
  background / monochrome), sizes, exclusion zone
- **The mark in context** — favicon, iOS/Android/PWA launchers *(per project)*
- **Typefaces** — families per role (mark / interface / figures), hosting
- **Type scale** — every scale token rendered live, weights
- **Spacing** — the scale steps rendered; gaps/padding per breakpoint
- **Radii** — named tokens rendered; the roots the component library derives
  from
- **Density** — the modes, and what each actually moves *(per project)*
- **Iconography** — the icon set, sizes per context, stroke/weight rules
- **Motion** — animation principles, duration/easing specimens with replay,
  `prefers-reduced-motion` behaviour (cross-ref Accessibility)
- **Content width** — modes and their limits *(per project)*

## Tab: Colour

- **Neutrals per theme** — full token table, values read live, use of each
- **Surface hierarchy** — background/card/surface/raise layering, hovers,
  active states
- **Accents / identities grid** — every colour identity × every theme/mode,
  live, with a measured WCAG badge per swatch (N accents × 2 themes, or N
  identities × 2 modes — the grid axis is the project's dimensionality)
- **Contrast, measured live** — the demanding pairs (the ones a palette
  change breaks first), computed from the rendered values, never transcribed
- **Functional / status colours** — success, danger, warning…, and the
  domain's semantic pairs
- **Where the accent goes — and where it does not** — the enumerated places,
  with the real-screen evidence

## Tab: Components

One block per real UI primitive the app uses — detected from the project, not
from this list. Reference superset (union of both projects) to check against:

buttons (variants + sizes) · fields/forms (all states, including error+focused
at once) · disabled treatment · card variants · chip/badge · toolbar · alert ·
toast (live queue) · tabs · dialog/modal · drawer/sheet · table (with live
filter/sort demo) · progress · skeleton/loading · segmented control ·
dropdown/select · date picker · month/period selector · search/combobox with
suggestions · avatars · empty-state component

Each block: rendered specimen + copyable code + the note stating its rule.
Specimens sit where their defects can show (state that breaks, background it
will actually meet).

## Tab: [DOMAIN] *(named by the project; skip if the 6 fixed tabs cover it)*

The project's domain-specific rendering rules. Examples from the references:
amounts/figures formatting (locale, tabular numerals) · positive/negative
semantics · domain state glyphs (shape first, tint policy) · domain data
tables · multi-entity patterns ("all accounts", "all characters")

## Tab: Layouts

- **App shell at committed widths** — embedded mockups at their real pixel
  widths (scaled visually, never reflowed)
- **Density comparison** — the same view at each density *(per project)*
- **Key screens** — the screens/patterns that define the product, at the
  widths that change them
- **Grid behaviour** — columns/gaps per breakpoint

## Tab: Voice

- **Errors** — the pattern (what failed · what survived · way out) with real
  specimens, strings verbatim from `voice.md`
- **Empty states** — the cases (never existed / not here / no matches)
- **Destructive confirmation** — what is lost named, the verb on the button
- **Formats** — numbers, dates, units as copy rules *(if not already in
  [DOMAIN])*

## Tab: Accessibility

- **Criteria table** — the WCAG criteria the project commits to, with status
- **Focus states** — the ring, on the backgrounds it actually meets;
  focused-and-invalid at once
- **Target sizes** — touch vs pointer minimums, measured
- **Colour vision** — the palette under greyscale + protan/deutan/tritan
  filters ("never colour alone" made visible)
- **Reduced motion** — what stops, tied to the Motion block
