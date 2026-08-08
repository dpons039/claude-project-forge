import type { MDXComponents } from "mdx/types";

import { Demo } from "./components/Demo";
import { Block } from "./components/Block";

/**
 * The components every tab `.mdx` can use without importing them — injected
 * through `MDXProvider`. `Demo` and `Block` are the two load-bearing ones (the
 * dual specimen block and the editorial wrapper); the rest map plain markdown
 * elements onto the BrandKit's prose styles.
 *
 * A tab `.mdx` writes prose as markdown and drops `<Block title spec={…}><Demo …/>
 * </Block>` for each specimen. Because these come from the provider, the `.mdx`
 * stays clean — the reason the content is authorable without touching the chrome.
 */
export const mdxComponents: MDXComponents = {
  Demo,
  Block,
};
