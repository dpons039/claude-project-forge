# init-page — install the dev-only page (frontend required)

**This skill ships the chrome as real files.** The page is not regenerated per
project: the universal chrome lives in `templates/page/chrome/` and is **copied
in unchanged**. A project supplies only three things — `config.ts` (filled from
the template), one `.mdx` per tab, and its mark component (named in config). The
tab set is `templates/page/page-structure.md`.

So init-page is: **copy the chrome → wire the build → fill `config.ts` → write
the tabs**. No chrome code is authored per project.

## Step 1 — Detect stack facts

- Build config (`vite.config.ts` or equivalent): how entries are declared, and
  whether MDX is already wired.
- `package.json`: UI library (HeroUI / shadcn / MUI / none), CSS approach, React
  version. The chrome assumes a Vite-family build + a React-family model.
- Token files (grep `--` custom-property declarations under the styles dir): the
  page reads these live; `config.ts` names the theme/accent/density values that
  the CSS defines.
- `CLAUDE.md`: chrome language = the written-artifacts language (code + docs +
  comments). The chrome text is English by default; a project's specimens are in
  its own UI language.

## Step 2 — Ask what cannot be inferred

- **Tabs**: the eight in `page-structure.md` are the default. Confirm which apply
  (a project with no money-like data still has Formatting for dates/numbers; a
  project with no wireframes may thin Layouts). Removing a canonical tab needs a
  "skipped: <reason>" note in `docs/BrandKit.md`.
- **Global controls / appearance dimensions**: the chrome exposes theme · width ·
  accent · density. The token CSS reveals the real dimensions (`[data-theme]`,
  `[data-accent]`, density classes) — `config.ts` lists the values; confirm them
  with the user, do not hardcode a count.
- **The mark**: which component the top-left brand chip renders. It becomes
  `config.logo`.

## Step 3 — Build exclusion, by construction

The page must be absent from production because of a **structural fact the build
tool enforces** — an entry never declared — never a runtime check.

Vite-family default: a sibling HTML entry beside the app's `index.html`. With no
`rollupOptions.input` (or an input list that omits it), the entry is never built;
`ls dist/` confirms with no faith in a conditional. It cannot live in `public/` —
that folder is copied wholesale.

### Adapting to a different stack

Keep the principle, replace the mechanism: excluded by an entry never declared, a
route never registered, or a bundle never referenced — something `ls dist/` can
verify. Never `import.meta.env.DEV`, a runtime guard, or a router conditional.

## Step 4 — Copy the chrome

Copy `templates/page/chrome/` into the project's page dir (canonically
`frontend/src/brandkit/`), unchanged:

```
frontend/
├── brandkit.html            (from entry.html.template — sibling, outside build inputs)
└── src/brandkit/
    ├── main.tsx             (own root)
    ├── BrandKit.tsx         (the chrome: sticky header + tabs + controls + on-this-page rail)
    ├── brandkit.css         (own --bk-* palette; project tokens appear only inside demos)
    ├── mdx-components.tsx    (injects Demo/Block into every .mdx)
    ├── mdx.d.ts
    ├── config.ts            (from config.ts.template — THE per-project file)
    ├── components/          (Block, Demo, TocRail, icons, Ratio, Wireframe — universal)
    ├── lib/                 (slug, useHashTab, useActiveAccent, contrast — universal)
    ├── tabs/               (one .mdx per tab + <tab>.examples.tsx + index.ts — per project)
    └── wireframes/          (HTML mockups if the project has them — per project)
```

The `chrome/` files are copy-paste-identical across projects — do not edit them.
Everything a project varies is `config.ts`, the `tabs/`, and the mark component
config points at.

**Import direction rule:** `src/brandkit/` may import from the app (the point —
exhibit the real components and tokens); the app **never** imports from
`src/brandkit/`. One such import pulls brandkit code into the production bundle
without the dist check seeing it — chunks are not named "brandkit".

## Step 5 — Wire the build (MDX + entry)

- Add the entry: copy `entry.html.template` to `frontend/brandkit.html`, fill
  `[PROJECT_NAME]`. It carries `<meta name="robots" content="noindex">`, the
  default state attributes the token system reads, a `#brandkit` mount div, a
  module script to `src/brandkit/main.tsx`, and `scroll-padding-top` for the
  sticky header.
- Add the MDX toolchain: `@mdx-js/rollup` + `@mdx-js/react`, and the plugin lines
  from `vite-config-snippet.md` (`enforce:"pre"` before the react plugin, and the
  react `include` regex covering `.mdx`). Without these, `.mdx` imports do not
  compile.

## Step 6 — Fill config.ts

`config.ts.template` is the one file the project writes by hand. Fill:

- `name` — the product name (the brand chip label).
- `logo` — import the project's mark component and pass it (the chrome takes the
  component through config; it never imports a project component itself).
- `themes` — the `data-theme` values + a readable label each.
- `accents` / `densities` — the values the token CSS defines. If the app already
  declares these centrally (a single source the boot/appearance code reads),
  DERIVE them from there rather than re-listing (the template shows both forms) —
  the BrandKit is a viewer and should follow the app, not keep a second copy.
- `defaults` — the appearance on first load.
- `tabs` — the ordered id+label list; each id maps to `tabs/<id>.mdx`.

## Step 7 — Write the tabs

One `.mdx` per tab, headings from **`page-structure.md`**. `tabs-example/` is the
worked shape. For each block:

```mdx
<Block title="…" spec={<p>the rule, why, metadata</p>}>
  <Demo title="foo.tsx" code={`…usage snippet…`}>
    …the live specimen…
  </Demo>
</Block>
```

Rules that cost real debugging — carry them:

- **`.mdx` inline expressions are plain JS, not TypeScript.** No `as const`, no
  type annotations (MDX parses with acorn and rejects them). Anything needing
  types goes in the sibling `<tab>.examples.tsx`, imported into the `.mdx`.
- **Stateful / complex specimens** (anything with hooks, i18n `t()`,
  `getComputedStyle`, a real dialog) live in `<tab>.examples.tsx` as exported
  components. Simple inline specimens (a row of buttons) can stay in the `.mdx`.
- **`stacked` for wide specimens.** Wireframe rows and wide comparison tables use
  `<Block stacked>` (prose above, preview full-width); the default two-column
  block would crush them.
- **`min-width` under grids/flex.** A specimen whose control does not shrink
  (a full-width input, say) needs a fixed-width wrapping box, not a `1fr` track
  that it stretches past the row — box it and let the row wrap.
- **Register each tab** in `tabs/index.ts` and add its id+label to `config.tabs`.
- **Voice** strings come from `docs/voice.md`, copied literally; **Accessibility**
  ratios are computed live via the `Ratio` component, never transcribed.

## Step 8 — Fill BrandKit.md TBDs

Dev URL, the real tab list, "How to add a block" (create `<id>.mdx`, register in
`index.ts`, add the config line), and the rules (official token classes;
chrome-English / specimen-UI-language; verbatim voice strings; never colour
alone).

## Step 8b — doc-coverage wiring

If `.claude/doc-coverage.json` exists, add a trigger:
`{"pattern": "<page dir>", "docs": ["docs/BrandKit.md"]}` — the hooks then nag
when the page changes without its doc.

## Step 9 — Verify

Run the production build; confirm the entry is absent (`find dist/ -iname
"*brandkit*"` → empty). `tsc` and lint clean; every `.mdx` compiles (the dev
server renders them). This is the same check `audit` re-runs mechanically.
