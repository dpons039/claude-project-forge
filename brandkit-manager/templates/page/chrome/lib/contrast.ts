/**
 * WCAG contrast, computed from what the browser actually rendered.
 *
 * The point of doing this at runtime rather than pasting figures from a docs
 * page is that it stays honest: if a token changes and someone forgets to
 * re-measure, the BrandKit says so instead of repeating a number that used to
 * be true.
 */

/**
 * Resolves a custom property to a concrete `rgb()`, in the context of `scope`.
 *
 * **Always through a probe**, never by reading the raw string. Reading the raw
 * string only works for something like `--focus: var(--fg-2)`, and nothing
 * else. A theming system built on `color-mix()` — e.g. HeroUI deriving
 * `--accent-hover`/`--accent-soft` as `color-mix(in oklab, var(--accent) …)` —
 * does not start with `var(`, falls through hex/`rgb()` patterns, and comes
 * back `null`, which `Ratio` would render as an em dash, indistinguishable
 * from "still loading". A measurement page that silently declines to measure
 * is worse than one that is wrong. Painting the value onto an element and
 * reading `getComputedStyle().color` makes the browser do the resolution,
 * whatever the syntax.
 *
 * `scope` matters for the same reason: custom properties are inherited, so a
 * token inside a nested `[data-theme="…-dark"]` subtree resolves to the dark
 * value only if it is read there. Reading everything off `<html>` means the
 * page can never measure a theme it is not currently showing.
 */
export function readToken(name: string, scope: Element = document.documentElement): string {
  const raw = getComputedStyle(scope).getPropertyValue(name).trim();
  if (!raw) return "";

  const probe = document.createElement("span");
  probe.style.color = raw;
  probe.style.display = "none";
  scope.appendChild(probe);
  const resolved = getComputedStyle(probe).color;
  probe.remove();
  return resolved;
}

/**
 * Rasterises any CSS colour to sRGB bytes.
 *
 * Resolving through a probe is not enough on its own: a browser keeps the
 * colour space it was given, so `color-mix(in oklab, …)` comes back as
 * `oklab(0.48 -0.089 0.004 / 0.15)` — still unparseable by a pattern that
 * knows hex and `rgb()`. Painting one pixel and reading it back makes the
 * browser do the conversion, which is both exact and syntax-proof: `oklch()`,
 * `lab()`, `color(display-p3 …)` and whatever CSS adds next all arrive here as
 * four numbers. Clamping to sRGB is correct rather than lossy — WCAG contrast
 * is defined on sRGB.
 */
function rasterise(colour: string): [number, number, number, number] | null {
  const canvas = document.createElement("canvas");
  canvas.width = 1;
  canvas.height = 1;
  const ctx = canvas.getContext("2d", { willReadFrequently: true });
  if (!ctx) return null;

  // An unparseable value leaves `fillStyle` at whatever it already held, so
  // assigning it after two different sentinels tells the cases apart: a valid
  // colour lands on the same result both times, an invalid one keeps the two
  // sentinels. Cheaper and safer than pattern-matching the string, which is
  // what this function exists to avoid doing.
  ctx.fillStyle = "#000000";
  ctx.fillStyle = colour;
  const first = ctx.fillStyle;
  ctx.fillStyle = "#ffffff";
  ctx.fillStyle = colour;
  if (first !== ctx.fillStyle) return null;

  ctx.clearRect(0, 0, 1, 1);
  ctx.fillRect(0, 0, 1, 1);
  const [r, g, b, a] = ctx.getImageData(0, 0, 1, 1).data;
  if (r === undefined || g === undefined || b === undefined || a === undefined) return null;
  return [r, g, b, a / 255];
}

/** `[r, g, b, a]`, with `a` in 0–1. Accepts hex, `rgb()` and `rgba()`. */
function toRgbaLiteral(colour: string): [number, number, number, number] | null {
  const value = colour.trim();

  // Covers both `rgb(1, 2, 3)` and the modern `rgb(1 2 3 / 40%)`.
  const rgbMatch = /^rgba?\(([^)]+)\)$/.exec(value);
  if (rgbMatch?.[1]) {
    const parts = rgbMatch[1].split(/[,\s/]+/).filter(Boolean);
    const [r, g, b] = parts.slice(0, 3).map(Number);
    if (r === undefined || g === undefined || b === undefined) return null;
    const rawAlpha = parts[3];
    const alpha =
      rawAlpha === undefined
        ? 1
        : rawAlpha.endsWith("%")
          ? Number(rawAlpha.slice(0, -1)) / 100
          : Number(rawAlpha);
    return [r, g, b, Number.isFinite(alpha) ? alpha : 1];
  }

  const hex = value.replace(/^#/, "");
  if (hex.length === 3) {
    const [r, g, b] = [...hex].map((c) => parseInt(c + c, 16));
    return r === undefined || g === undefined || b === undefined ? null : [r, g, b, 1];
  }
  if (hex.length === 6) {
    const [r, g, b] = [0, 2, 4].map((i) => parseInt(hex.substring(i, i + 2), 16)) as [
      number,
      number,
      number,
    ];
    return [r, g, b, 1];
  }
  return null;
}

function luminance([r, g, b]: [number, number, number]): number {
  const [lr, lg, lb] = [r, g, b].map((c) => {
    const s = c / 255;
    return s <= 0.03928 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4;
  }) as [number, number, number];
  return 0.2126 * lr + 0.7152 * lg + 0.0722 * lb;
}

/**
 * Contrast ratio, or `null` if either colour could not be read.
 *
 * A translucent foreground is **composited over the background** rather than
 * measured as if it were opaque. WCAG contrast is defined between the colours
 * a person actually sees, and e.g. `text-foreground/70` at face value reports
 * the ratio of the ink rather than of the result — a number that is always too
 * favourable, which is the direction a contrast check must never err in.
 */
export function contrast(a: string, b: string): number | null {
  // Canvas first, literal parsing only where there is no canvas to draw on.
  const read = (c: string) => rasterise(c) ?? toRgbaLiteral(c);
  const [fg, bg] = [read(a), read(b)];
  if (!fg || !bg) return null;

  const alpha = fg[3];
  const composited: [number, number, number] = [
    fg[0] * alpha + bg[0] * (1 - alpha),
    fg[1] * alpha + bg[1] * (1 - alpha),
    fg[2] * alpha + bg[2] * (1 - alpha),
  ];

  const [la, lb] = [luminance(composited), luminance([bg[0], bg[1], bg[2]])];
  const [hi, lo] = la > lb ? [la, lb] : [lb, la];
  return (hi + 0.05) / (lo + 0.05);
}

/**
 * Whether a ratio clears its floor.
 *
 * `text` is WCAG AA's 4.5:1 for body text (raise it if your project holds
 * itself to a stricter internal floor). `graphic` is 3:1 — criterion 1.4.11,
 * which governs controls and meaningful shapes. `danger` is provided as a
 * documented-exception slot (e.g. a brand-red that cannot clear 4.5:1) —
 * delete it if your project has no such exception.
 */
export const FLOORS = { text: 4.5, graphic: 3, danger: 4.5 } as const;
export type Floor = keyof typeof FLOORS;
