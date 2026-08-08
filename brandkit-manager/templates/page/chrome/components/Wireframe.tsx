/**
 * A mockup image/HTML frame, embedded at a fixed width.
 *
 * These should be the originals, copied into `src/brandkit/wireframes/` rather
 * than redrawn in JSX. Reimplementing a mockup as markup invites drift — a
 * region goes missing, a width is never built, a link exists in the JSX that
 * exists in no mockup. The exploration/mockup file is the source; a copy of it
 * in another language is a second source that quietly disagrees.
 *
 * ## The width has to be real
 *
 * The frame's width is what the media queries inside it see, so it cannot be
 * capped. Do not add `max-w-full` — that overrides the width attribute and the
 * mockup lays itself out at whatever the column allows, which reads as mobile
 * even when a desktop width was requested.
 *
 * Instead the iframe keeps its true width and is **scaled down** with a CSS
 * transform when it will not fit. A transform is applied after layout, so the
 * document inside still measures its full width and picks the right
 * breakpoint; only the pixels on screen shrink.
 *
 * ## Why they do not follow the theme controls
 *
 * A mockup usually carries its own stylesheet, so the accent, theme and
 * density at the top of the page do not reach inside it. That is correct
 * rather than a limitation: a greyscale/structural mockup is how layout gets
 * decided, with colour kept deliberately out of the way. What the palette
 * does to a real component is what the other tabs show.
 *
 * ## Why they live under src/
 *
 * `public/` is copied into the build wholesale, so a mockup there would ship
 * to every user. Files under `src/` are only bundled when something imports
 * them; Vite serves them in dev regardless.
 */
interface WireframeProps {
  /** Path under `wireframes/`, query string included. */
  src: string;
  /** Viewport width in pixels — this is what the media queries see. */
  width: number;
  /** Height in pixels; keep consistent across a row unless the view is shorter. */
  height?: number;
  /** What this width represents. */
  label: string;
  /** Optional line on what to look at. */
  note?: string;
  /**
   * Shrink to this fraction of true size. The frame still *is* `width` wide as
   * far as the document inside is concerned.
   */
  scale?: number;
}

export function Wireframe({
  src,
  width,
  height = 760,
  label,
  note,
  scale = 1,
}: WireframeProps) {
  return (
    <figure className="m-0 shrink-0">
      <figcaption className="mb-1 type-meta">
        <span className="font-semibold">{label}</span>{" "}
        <span className="text-muted">{width}px</span>
        {scale !== 1 ? <span className="text-muted"> · {Math.round(scale * 100)}%</span> : null}
        {note ? <span className="text-muted"> · {note}</span> : null}
      </figcaption>

      {/* The wrapper reserves the *scaled* footprint; the iframe keeps its
          real size and is scaled into it. Without this the shrunken frame
          would still occupy its full width and leave a gap. No background of
          its own — let the mockup paint its own body colour and rely on the
          border for separation; a wrapper background can visibly clash with
          the mockup's own in one theme or the other. */}
      <div
        className="overflow-hidden rounded-md border border-border"
        style={{ width: width * scale, height: height * scale }}
      >
        <iframe
          // Vite serves src/ in dev, which is the only place this page runs.
          src={`/src/brandkit/wireframes/${src}`}
          width={width}
          height={height}
          title={`${label} at ${width} pixels`}
          loading="lazy"
          className="block border-0"
          style={
            scale === 1
              ? undefined
              : { transform: `scale(${scale})`, transformOrigin: "top left" }
          }
        />
      </div>
    </figure>
  );
}

/**
 * A wrapping row of mockups.
 *
 * Wrap rather than scroll: inside a `stacked` block the row has the full page
 * width, so a frame that will not fit drops to the next line — visible at a
 * glance — instead of hiding off the right edge behind a scrollbar. No
 * `tabIndex`/`role`: a wrapping row is not a scroll container, so it needs no
 * keyboard-reachability affordance.
 */
export function WireframeRow({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex flex-wrap items-start gap-4" role="group" aria-label="Mockups at several widths">
      {children}
    </div>
  );
}
