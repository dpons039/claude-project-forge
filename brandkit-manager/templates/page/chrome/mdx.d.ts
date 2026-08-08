/**
 * `.mdx` files compile to a React component (the default export). TypeScript
 * needs this ambient declaration to import them; `@mdx-js/rollup` provides the
 * runtime. Scoped to the BrandKit — it is the only place MDX is used.
 */
declare module "*.mdx" {
  import type { ComponentType } from "react";
  const MDXComponent: ComponentType<Record<string, unknown>>;
  export default MDXComponent;
}
