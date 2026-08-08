# Vite config wiring for the BrandKit

Add to your project's `vite.config.ts`. Two things are required: the MDX
plugin (so `.mdx` tab files compile to React components) and telling the React
plugin to also transform `.mdx` files.

```ts
import mdx from "@mdx-js/rollup";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [
    // MDX must run in the `pre` phase, before the React plugin, so React's
    // transform sees already-compiled JSX. `providerImportSource` wires the
    // `.mdx` files to `@mdx-js/react`'s MDXProvider, so the BrandKit can
    // inject shared components (Block, Demo) into every tab without each
    // `.mdx` importing them. MDX is only used by the dev-only BrandKit; it
    // never reaches the production build as long as your build only lists
    // your app's own entry HTML.
    { enforce: "pre", ...mdx({ providerImportSource: "@mdx-js/react" }) },

    // Extend the default include so the React transform also runs over
    // `.mdx` (and `.md`, if you use plain markdown blocks) — by default the
    // React plugin only looks at `.jsx`/`.tsx`.
    react({ include: /\.(jsx|js|mdx|md|tsx|ts)$/ }),

    // ...your other plugins (Tailwind, router, etc.)
  ],
});
```

## Keeping the BrandKit out of production

Do not add `brandkit.html` to `build.rollupOptions.input`. If your config
declares no explicit `rollupOptions.input` at all, Vite defaults to building
only `index.html` at the project root, and `brandkit.html` is never bundled or
shipped — it only exists as a dev-server entry point. If your config DOES
declare `rollupOptions.input` for some other reason (e.g. a multi-page app),
make sure `brandkit.html` is deliberately left out of that list.

## MDX ambient types

TypeScript needs to know what importing a `.mdx` file resolves to. This is
provided by `chrome/mdx.d.ts` (copied in with the rest of the chrome) — no
extra config needed, but make sure your `tsconfig.json`'s `include` covers the
`src/brandkit/` directory so the ambient declaration is picked up.
