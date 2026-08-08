/**
 * Tab registry — how `BrandKit.tsx` resolves a tab id to its `.mdx` module.
 *
 * Copy this file to `src/brandkit/tabs/index.ts` and keep it in sync with
 * `config.tabs`: every `id` listed in `config.ts` must have a matching key
 * here, importing `./${id}.mdx`. A tab in `config.tabs` with no entry here
 * renders "Tab not found." (see `BrandKit.tsx`); an entry here with no line
 * in `config.tabs` never appears in the nav and is dead code.
 *
 * Static imports (not a dynamic `import()` glob) so a typo in an id is a
 * TypeScript error at the `tabModules` literal, not a silent runtime 404.
 */
import type { ComponentType } from "react";

import Example from "./example.mdx";

export const tabModules: Record<string, ComponentType> = {
  example: Example,
  // brand: Brand,
  // foundations: Foundations,
  // colour: Colour,
  // components: Components,
};
