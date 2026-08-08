import { useEffect, useRef, useState } from "react";

import { contrast, FLOORS, readToken, type Floor } from "../lib/contrast";

interface RatioProps {
  /** Token names, e.g. `--fg-2`. Use your project's own custom-property names. */
  foreground: string;
  background: string;
  floor?: Floor;
}

/**
 * A measured contrast ratio with its pass mark.
 *
 * Recomputed whenever the theme or accent changes, by observing the
 * attributes on `<html>` — the same attributes the controls write.
 */
export function Ratio({ foreground, background, floor = "text" }: RatioProps) {
  const [ratio, setRatio] = useState<number | null>(null);
  /**
   * Measured **where this sits**, not off `<html>`.
   *
   * Custom properties inherit, so a `<Ratio>` inside a nested
   * `[data-theme="…-dark"]` block would resolve to the light value if read off
   * `<html>` — the page could only ever measure the theme the control happened
   * to be on, while showing both side by side. The anchor is its own DOM node.
   */
  const anchor = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    const measure = () => {
      // A frame's grace: custom properties resolve after the attribute lands.
      requestAnimationFrame(() => {
        const scope = anchor.current ?? document.documentElement;
        setRatio(contrast(readToken(foreground, scope), readToken(background, scope)));
      });
    };

    measure();

    const observer = new MutationObserver(measure);
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["data-theme", "data-accent", "class"],
    });
    return () => observer.disconnect();
  }, [foreground, background]);

  if (ratio === null) {
    return <span ref={anchor} className="font-mono type-meta">—</span>;
  }

  const required = FLOORS[floor];
  const passes = ratio >= required;

  return (
    <span ref={anchor} className="inline-flex items-center gap-1 font-mono type-meta">
      <span>{ratio.toFixed(2)}</span>
      {/*
        The mark is a word, never a colour on its own (WCAG 1.4.1).

        Prefer your project's own semantic pass/fail classes over the raw token
        names — this component renders on every tab, so it is chrome, not a
        token specimen. Map `text-success` / `text-danger` (or your
        equivalents) onto whatever tokens your theme defines for those roles.
      */}
      <span className={passes ? "text-success" : "font-bold text-danger"}>
        {passes ? "PASS" : "FAIL"}
      </span>
      <span className="text-muted">/ {required}</span>
    </span>
  );
}
