import type { ReactNode } from "react";

import { slugify } from "../lib/slug";

/**
 * One editorial block: the rule/prose on the left (`spec`), the live specimen on
 * the right (`children` — normally a `<Demo>`). The heading carries a stable id
 * (slug of `title`) so the on-this-page rail can link to it and scroll-spy it.
 */
export interface BlockProps {
  title: string;
  /** The prose fiche: rule, why, metadata. */
  spec: ReactNode;
  /** The live preview column — a `<Demo>`. */
  children: ReactNode;
  /**
   * Stack the spec ABOVE a full-width preview instead of the default two-column
   * split. For specimens too wide for the 66% preview column — several scaled
   * wireframes in a scrolling row, a wide comparison table — where the side-by-side
   * layout crushes them to unreadable. The prose reads first, the specimen gets the
   * whole width.
   */
  stacked?: boolean;
}

export function Block({ title, spec, children, stacked = false }: BlockProps) {
  const id = slugify(title);
  return (
    <section className="bk-block" id={id} aria-labelledby={`${id}-title`}>
      <div className={stacked ? "bk-block__stack" : "bk-block__grid"}>
        <div className="bk-block__spec">
          <h2 id={`${id}-title`}>{title}</h2>
          {spec}
        </div>
        <div className="bk-block__preview-wrap">{children}</div>
      </div>
    </section>
  );
}
