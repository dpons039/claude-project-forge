# init-page — generate the dev-only page (frontend required)

**This skill ships no page code.** The heading set comes from
`templates/page/page-structure.md`; every file is generated for THIS project
from its real tokens and components, carrying the debugged techniques listed
in Step 8. Never copy another project's values.

## Step 1 — Detect stack facts

- Build config (`vite.config.ts` or equivalent): how entries are declared.
- `package.json`: UI library (HeroUI / shadcn / MUI / none), CSS approach.
- Token files (grep `--` custom-property declarations under the styles dir):
  the page must read these live, never hardcode.
- `CLAUDE.md`: chrome language = the written-artifacts language (code + docs
  + comments + commits) and UI language (examples). If the convention only
  declares a code language (older form), read how `docs/` is actually written
  — do not assume; confirm if they differ.

## Step 2 — Ask what cannot be inferred

- **Domain tab**: name + what belongs on it — or whether the 6 fixed tabs
  cover everything.
- **Global controls**: expose whatever compound state controls exist
  (theme / accent / density multiply into dozens of combinations; a
  multi-identity project may need an identity selector instead). The token CSS reveals the
  dimensions (`[data-theme]`, `[data-accent]`, density classes) — confirm the
  exposure with the user, don't hardcode a count of three.

## Step 3 — Build exclusion, by construction

The page must be absent from production because of a **structural fact the
build tool enforces** — an entry never declared — never because of an
environment check.

Vite-family default: a sibling HTML entry next to the app's `index.html`.
With no `rollupOptions.input` (or an input list that simply does not include
it), the entry is never built; `ls dist/` confirms with no faith in a
conditional. It cannot live in `public/` — that folder is copied into the
build wholesale.

### Adapting to a different stack

Keep the principle, replace the mechanism: the page must be excluded by an
entry point never declared, a route never registered, or a bundle never
referenced — something `ls dist/` (or the platform's equivalent) can verify.
Never `import.meta.env.DEV`, a runtime guard, or a router conditional: those
require trusting a condition instead of reading the build output.

## Step 3b — Canonical deployed layout

```
frontend/
├── brandkit.html            (sibling entry, outside the build inputs)
└── src/brandkit/            (EVERYTHING encapsulated here)
    ├── main.tsx             (own root)
    ├── BrandKit.tsx         (shell: sticky header + tabs + controls)
    ├── tabs/                (one file per tab)
    │   ├── Foundations.tsx · Colour.tsx · Components.tsx
    │   ├── [Domain].tsx     (project name, e.g. DataAndMoney.tsx)
    │   └── Layouts.tsx · Voice.tsx · Accessibility.tsx
    ├── components/          (Section.tsx [Section+TabIntro+Frame],
    │                         CodeBlock.tsx, Wireframe.tsx, Ratio.tsx,
    │                         Controls.tsx)
    ├── lib/                 (controls.ts, contrast.ts, hooks)
    └── wireframes/          (HTML mockups, copied — corrections as inline comments)
```

**Import direction rule:** `src/brandkit/` may import from the app (that is
the point — exhibit the real components and tokens); the app **never** imports
from `src/brandkit/`. One such import pulls brandkit code into the production
bundle without the dist check seeing it — chunks are not named "brandkit".

## Step 4 — Entry HTML (generated)

A sibling of the app's index: gating comment stating the by-construction
exclusion (and why it cannot live in `public/`), unconditional
`<meta name="robots" content="noindex" />`, the default state attributes the
project's token system reads (`data-theme` etc.), font preloads only if
self-hosted, a `#brandkit` mount div, module script to
`src/brandkit/main.tsx`. `scroll-padding-top` as pre-mount fallback for the
sticky header (Step 6 replaces it with the measured value).

## Step 5 — Own root (generated)

Own `createRoot` in `src/brandkit/main.tsx` — sharing the app's entry would
couple the page to providers and routers it must not depend on. Conditional:
i18n init (only if the app initialises one — lets settled `t()` keys
resolve), ErrorBoundary, toast/notification provider (a queue-driven toast
can only be shown live if the queue renderer is mounted).

## Step 6 — Shell (generated)

`BrandKit.tsx`: sticky header (mark + title + "Dev only"), the global
controls, tab strip, one panel per tab; tab state controlled by the URL
fragment (linkable sections, back button walks tabs). Header height is
measured, not assumed (it moves with density and wrapping controls) and
published as a custom property that section headings and `scroll-padding-top`
consume.

## Step 7 — Generate the tabs (per project)

One file per tab, headings from **`templates/page/page-structure.md`**. For
each heading, read the project's real tokens/components and build the block.
Where the structure file leaves room, these rules apply:

- **Foundations** includes **Iconography** and **Motion** (with
  `prefers-reduced-motion`, cross-ref Accessibility).
- **Colour**'s grid axis is the project's dimensionality (N accents × 2
  themes, or N identities × 2 modes) — the tab's job is canonical, the shape
  is not. Every swatch carries a live-measured WCAG badge.
- **Components** blocks come from the project's real primitives (detect from
  imports/components dir), each rendered with the actual component + its
  copyable code.
- **Voice** strings come from `docs/voice.md`, copied literally once, not
  wired to i18n (per-block exceptions where the wiring is the point).
- **Accessibility** ratios are computed live, never transcribed.

Skipping a canonical heading requires "skipped: <reason>" in
`docs/BrandKit.md` (audit check #15 enforces it against the structure file).

## Step 8 — Shared components (generated, carrying the debugged techniques)

Implement fresh for the project: `Section`/`TabIntro`/`Frame`, `CodeBlock`,
`Wireframe` (+`WireframeRow`), `Ratio` + a contrast lib, `Controls`. These
techniques cost real debugging in the references — carry each one, as code
comments where the next maintainer will meet them:

- **Frame / "the specimen has to sit where the defect can show"**: the frame
  shares its surface colour with many components, so a same-background
  specimen proves nothing about the boundary (a boxless alert looked fine for
  weeks and arrived grey inside a same-coloured card in production). Show the
  state that breaks; put controls on the background they will meet.
- **Section**: note beside the specimen on wide screens (stacked, the page
  becomes a narrow column); prose capped ~70ch; sticky headings offset by the
  *measured* header-height custom property, never a constant.
- **CodeBlock**: the copy button is the point — code that is not right there
  comes back as the same question. Handle clipboard failure visibly.
- **Wireframe**: the iframe keeps its TRUE width and scales via CSS
  `transform` — a `max-width` cap overrides the width attribute, the document
  inside picks the phone breakpoint, and every mockup renders as mobile. The
  wrapper reserves the scaled footprint. Mockups live under `src/` (a
  static/public dir ships to every user) and scroll rows are
  keyboard-reachable with a name.
- **Ratio / contrast lib**: resolve tokens by painting a probe and reading
  `getComputedStyle` (raw strings miss `color-mix`/`oklch`); rasterise via a
  1px canvas (browsers keep the given colour space); composite translucent
  foregrounds over the background (face-value alpha always flatters — the
  direction a contrast check must never err in); measure at the component's
  own DOM node, not `<html>` (custom properties inherit — nested theme blocks
  resolve wrong otherwise). Floors = the project's own, not just AA.
- **Controls**: write state to `document.documentElement`
  attributes/classes — the same attributes the entry HTML defaults and the
  `Ratio` observer watch.

## Step 9 — Fill BrandKit.md TBDs

Dev URL, real tab list, "How to add a block" with the project's real
component names, the four rules (official classes; chrome/examples languages;
verbatim strings; never colour alone).

## Step 9b — doc-coverage wiring

If `.claude/doc-coverage.json` exists, add a warning trigger:
`{"pattern": "<page dir>", "docs": ["docs/BrandKit.md"]}` — the existing
hooks then nag when the page changes without its doc.

## Step 10 — Verify

Run the production build; confirm the entry is absent from the output
(`find dist/ -iname "*brandkit*"` → empty). This is the same check `audit`
re-runs mechanically.
