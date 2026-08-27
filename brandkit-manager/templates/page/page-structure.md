# BrandKit page — canonical structure

The complete set of headings the page covers. This file is an OUTLINE, not code:
`init-page` fills each block from the project's real tokens/components, and
`audit` check #15 uses this list as the canonical coverage checklist.

The chrome is fixed and universal (copied from `chrome/`); this outline is the
**content** a project supplies as one `.mdx` per tab. Each block in a `.mdx` is a
prose rule beside a live `<Demo>` (the specimen rendered, and its copyable
source). Stateful specimens live in a sibling `<tab>.examples.tsx`.

Rules: every heading below either exists on the page or is annotated in
`docs/BrandKit.md` as "skipped: <reason>". Headings marked *(per project)* only
apply when the project has the thing. `[DOMAIN]`/`[PLACEHOLDER]` items are named
by the project.

## The canonical tabs, in order

> These are the **baseline**, not the whole set. A project drops the ones it has
> no subject for (note it as "skipped: <reason>" in `docs/BrandKit.md`) and adds
> its own where it has a subject these do not cover — a data-visualisation tab, a
> map/geo tab, an email-template tab, a print tab. `config.tabs` is the real list;
> everything downstream reads it rather than a fixed number, so nothing here says
> how many a project ends up with.

**Brand → Foundations → Colour → Components → Formatting → Layouts → Voice →
Accessibility.** Tokens before the things built from them; the one per-project
identity tab (Brand) first; cross-cutting Voice and Accessibility last. The order
is the `tabs` list in `config.ts`.

The split separates **universal** from **per-project** so the same structure
drops into any project: Brand is the project's identity; Foundations, Colour,
Components, Formatting, Voice and Accessibility are universal frameworks holding
the project's own tokens/specimens; Layouts is inherently per-project (its
screens).

## Header (not a tab — it is the fixed chrome)

- **Mark + "BrandKit" chip** — the mark comes from `config.logo` (the project's
  component); the chrome never imports it
- **Global controls** — theme · width · then a divider · accent · density. Theme
  and width are universal (any project); accent and density are per-project. They
  change everything at once; the point is whether a decision survives every
  combination

## Tab: Brand *(the one per-project identity tab)*

- **The mark** — component vs shipped files, variants (on card / on background /
  monochrome), sizes, exclusion zone
- **On the system backgrounds** — the mark on every surface, in both themes,
  following the active accent
- **In context** — favicon, launcher crops (iOS / Android / PWA) *(per project)*

## Tab: Foundations

- **Typefaces** — families per role (mark / interface / figures), hosting
- **Type scale** — every scale token rendered live, weights
- **Spacing** — the scale steps rendered; gaps/padding per breakpoint
- **Radii** — named tokens rendered; the roots the component library derives from
- **Iconography** — the icon set(s), sizes per context, stroke/weight rules
- **Elevation** — shadow tokens per theme; stacking order *(per project)*
- **Motion** — animation principles, duration/easing specimens with replay,
  `prefers-reduced-motion` behaviour (cross-ref Accessibility)

## Tab: Colour

- **Neutrals per theme** — full token table, values read live, use of each
- **Raw → semantic** — how the semantic layer aliases onto the raw palette, each
  row live-checked for drift
- **Contrast, measured live** — the demanding pairs (the ones a palette change
  breaks first), computed from rendered values, never transcribed
- **Functional / status colours** — success, danger, warning…; and the domain's
  semantic ink pairs argued once here (e.g. an expense colour ≠ an error colour)
- **Accents / identities grid** — every colour identity × every theme, live, with
  a measured WCAG badge per swatch
- **Where the accent goes — and where it does not** — the enumerated places, with
  real-screen evidence

## Tab: Components

One block per real UI primitive the app uses — detected from the project, not
from this list. Reference superset to check against:

buttons (variants + sizes) · fields/forms (all states, including error+focused at
once) · disabled treatment · card variants · chip/badge · dismissible filter
tags · toolbar · alert · toast (live queue) · dialog/modal · drawer/sheet · table
(with live filter/sort demo) · progress · skeleton/loading · segmented control ·
dropdown/kebab menu · date picker · period selector · search/combobox with
suggestions · avatars/identity icon · screen states (loading / error boundary /
not-found) · density comparison · domain state glyphs (shape first, tint policy)

Each block: rendered specimen + copyable code + the note stating its rule.
Specimens sit where their defects can show (a state that breaks, a background it
will actually meet). Components is the sole owner of the shared field-error and
screen-state specimens — other tabs reference them rather than re-rendering.

## Tab: Formatting

Locale- and config-driven rendering of data — universal, not a domain tab. The
project's central formatting module is the single source; everything here is live
output, not transcribed:

- **Amounts / figures** — the format config (not a browser locale), exact-string
  precision, tabular numerals
- **Signed values** — positive/negative, the sign as the signal and colour only
  reinforcing it
- **Dates** — from the API's string, without timezone drift; the formats a config
  can hold
- **Percentages** — uncapped where the data can exceed the nominal maximum

## Tab: Layouts *(inherently per-project — its screens)*

- **App shell at committed widths** — embedded mockups at their real pixel widths
  (scaled visually, never reflowed). `WireframeRow` wraps, so wide frames drop to
  the next line rather than scrolling off-screen
- **Density comparison** — the same view at each density *(per project)*
- **Key screens** — the screens/patterns that define the product, at the widths
  that change them
- **Grid / breakpoint behaviour** — columns/gaps per breakpoint

Wide specimens (wireframe rows, comparison tables) use the `Block` `stacked`
variant: prose above, preview full-width.

## Tab: Voice

- **Errors** — the pattern (what failed · what survived · way out) with real
  specimens, strings verbatim from `voice.md`
- **Empty states** — the cases (never existed / not here / no matches)
- **Loading and error** — neither an empty state; both keep the view's shell
- **Destructive confirmation** — what is lost named, the verb on the button, a
  real alert-dialog (focus behaviour shown, not drawn)
- **Reading copy from the catalogue** — components hold keys, never literal text

## Tab: Accessibility

- **Criteria table** — the WCAG criteria the project commits to, with status
- **Focus states** — the ring, on the backgrounds it actually meets;
  focused-and-invalid at once
- **Target sizes** — touch vs pointer minimums, measured
- **Colour vision** — the palette + specimens under greyscale and
  protan/deutan/tritan filters ("never colour alone" made visible)
- **A field in error, colour taken away** — the greyscale 1.4.1 test
- **Reduced motion** — what stops, tied to the Motion block
