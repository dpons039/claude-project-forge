/**
 * The BrandKit chrome's own icons — inline SVG, no dependency.
 *
 * The chrome must not force a project to install a particular icon library:
 * it is universal, and a project might use Tabler, Lucide, its own set, or
 * none. So these few chrome glyphs (theme, width, code actions, toc) are
 * hand-inlined here. A project's OWN icon library appears only inside demos,
 * where showing the real system is the point — never in the chrome.
 *
 * Geometry is Tabler-style (outline, 24 viewBox, round caps) for visual
 * consistency with common sets, but nothing is imported.
 */
import type { SVGProps } from "react";

function Svg({ children, ...props }: SVGProps<SVGSVGElement>) {
  return (
    <svg
      width={18}
      height={18}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.75}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
      focusable={false}
      {...props}
    >
      {children}
    </svg>
  );
}

export function Moon(props: SVGProps<SVGSVGElement>) {
  return (
    <Svg {...props}>
      <path d="M12 3c.132 0 .263 0 .393 0a7.5 7.5 0 0 0 7.92 12.446a9 9 0 1 1 -8.313 -12.454z" />
    </Svg>
  );
}
export function Sun(props: SVGProps<SVGSVGElement>) {
  return (
    <Svg {...props}>
      <path d="M12 12m-4 0a4 4 0 1 0 8 0a4 4 0 1 0 -8 0" />
      <path d="M3 12h1m8 -9v1m8 8h1m-9 8v1m-6.4 -15.4l.7 .7m12.1 -.7l-.7 .7m0 11.4l.7 .7m-12.1 -.7l-.7 .7" />
    </Svg>
  );
}
/** Full width: horizontal double arrow `<-->`. */
export function ArrowsWide(props: SVGProps<SVGSVGElement>) {
  return (
    <Svg {...props}>
      <path d="M21 12h-18" />
      <path d="M6 9l-3 3l3 3" />
      <path d="M18 9l3 3l-3 3" />
    </Svg>
  );
}
/** Contained: two horizontal arrows pointing inward to a centre bar `->|<-`. */
export function ArrowsNarrow(props: SVGProps<SVGSVGElement>) {
  return (
    <Svg {...props}>
      {/* centre bar */}
      <path d="M12 5v14" />
      {/* left arrow → to centre */}
      <path d="M3 12h6" />
      <path d="M6 9l3 3l-3 3" />
      {/* right arrow ← to centre */}
      <path d="M21 12h-6" />
      <path d="M18 9l-3 3l3 3" />
    </Svg>
  );
}
export function Code(props: SVGProps<SVGSVGElement>) {
  return (
    <Svg {...props}>
      <path d="M7 8l-4 4l4 4" />
      <path d="M17 8l4 4l-4 4" />
      <path d="M14 4l-4 16" />
    </Svg>
  );
}
export function Copy(props: SVGProps<SVGSVGElement>) {
  return (
    <Svg {...props}>
      <path d="M8 8m0 2a2 2 0 0 1 2 -2h8a2 2 0 0 1 2 2v8a2 2 0 0 1 -2 2h-8a2 2 0 0 1 -2 -2z" />
      <path d="M16 8v-2a2 2 0 0 0 -2 -2h-8a2 2 0 0 0 -2 2v8a2 2 0 0 0 2 2h2" />
    </Svg>
  );
}
export function Check(props: SVGProps<SVGSVGElement>) {
  return (
    <Svg {...props}>
      <path d="M5 12l5 5l10 -10" />
    </Svg>
  );
}
export function Reset(props: SVGProps<SVGSVGElement>) {
  return (
    <Svg {...props}>
      <path d="M20 11a8.1 8.1 0 0 0 -15.5 -2m-.5 -4v4h4" />
      <path d="M4 13a8.1 8.1 0 0 0 15.5 2m.5 4v-4h-4" />
    </Svg>
  );
}

// Aliases matching the names Demo.tsx / TocRail.tsx import.
export { Code as IconCode, Copy as IconCopy, Check as IconCheck };
