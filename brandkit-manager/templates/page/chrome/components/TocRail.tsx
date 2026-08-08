import { useEffect, useRef, useState } from "react";

interface TocItem {
  id: string;
  label: string;
}

import { IconCode } from "./icons";

/**
 * The "On this page" rail. Built from the rendered `.bk-block[id]` headings —
 * a block appears here by existing, no hand-kept list — and scroll-spied with an
 * IntersectionObserver so the item for the block in view is marked current.
 * After the blocks, a link to the tab's `.mdx` source (dev serves the module).
 *
 * Re-mounted per tab (keyed on tab id upstream), so switching tabs rebuilds it.
 */
export function TocRail({ tabId }: { tabId: string }) {
  const [items, setItems] = useState<TocItem[]>([]);
  const [active, setActive] = useState<string>("");
  const nav = useRef<HTMLElement>(null);

  useEffect(() => {
    // Reading the DOM the MDX tab just rendered: the block list can't be known
    // before render, so this synchronises React state from an external system
    // (the rendered `section[id]` nodes), which is what effects are for.
    const main = document.getElementById("bk-content");
    if (!main) return;
    const blocks = [...main.querySelectorAll<HTMLElement>(".bk-block[id]")];
    const found: TocItem[] = blocks.flatMap((b) => {
      const h = b.querySelector("h2");
      return h?.textContent ? [{ id: b.id, label: h.textContent }] : [];
    });
    // eslint-disable-next-line react-hooks/set-state-in-effect -- syncing from the rendered DOM, not derivable state
    setItems(found);
    setActive(found[0]?.id ?? "");

    if (!("IntersectionObserver" in window) || found.length === 0) return;
    const obs = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) setActive((e.target as HTMLElement).id);
        });
      },
      { rootMargin: "-45% 0px -50% 0px", threshold: 0 },
    );
    blocks.forEach((b) => obs.observe(b));
    return () => obs.disconnect();
  }, []);

  // Adjust the base path below if your tabs live somewhere other than
  // `src/brandkit/tabs/` (see chrome.md and config.ts.template).
  const mdxHref = `/src/brandkit/tabs/${tabId}.mdx`;

  return (
    <aside className="bk-toc" aria-label="On this page" ref={nav}>
      <p className="bk-toc__title">On this page</p>
      {items.map((it) => (
        <a
          key={it.id}
          href={`#${it.id}`}
          aria-current={it.id === active ? "true" : undefined}
          onClick={(e) => {
            e.preventDefault();
            const reduce = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
            document.getElementById(it.id)?.scrollIntoView({
              behavior: reduce ? "auto" : "smooth",
              block: "start",
            });
          }}
        >
          {it.label}
        </a>
      ))}
      <div className="bk-toc__sep" />
      <a className="bk-toc__mdx" href={mdxHref} target="_blank" rel="noreferrer">
        <IconCode />
        View .mdx
      </a>
    </aside>
  );
}
