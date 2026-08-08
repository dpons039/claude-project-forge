import { useEffect, useState } from "react";

/**
 * The accent currently set on `<html>`.
 *
 * Needed wherever a specimen declares its own `data-theme` — showing light and
 * dark side by side, say. If your theme CSS keys selectors on the compound
 * `[data-theme="…"][data-accent="…"]` (both attributes on one element), a
 * nested `data-theme` alone leaves `--accent` undefined inside its subtree and
 * anything reading it silently loses its colour — this hook lets a specimen
 * re-supply the current `data-accent` explicitly in that case.
 *
 * Read from the DOM rather than threaded through props: the BrandKit chrome
 * already writes the accent to `<html>`, so a second copy in React state would
 * be one more thing that can disagree. Typed as `string`, not a project-specific
 * accent union — this lib is part of the universal chrome and cannot depend on
 * one project's accent list.
 */
export function useActiveAccent(fallback = ""): string {
  const [accent, setAccent] = useState<string>(
    () => document.documentElement.getAttribute("data-accent") ?? fallback,
  );

  useEffect(() => {
    const read = () => {
      const value = document.documentElement.getAttribute("data-accent");
      if (value) setAccent(value);
    };

    const observer = new MutationObserver(read);
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["data-accent"],
    });
    read();
    return () => observer.disconnect();
  }, []);

  return accent;
}
