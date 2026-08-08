import { useState, type ReactNode } from "react";

import { IconCode, IconCopy, IconCheck, Reset } from "./icons";

/**
 * The dual block: one example shown two ways — rendered live, and as copyable
 * source. This is the BrandKit's signature (a block is a specimen of itself).
 *
 * Phase 1 shape (inline mode): the `.mdx` writes the example as JSX children
 * (rendered live) and passes its source as the `code` string (shown + copied).
 * The two are the same example, but typed twice — a remark plugin could later
 * capture the source from the rendered children so a block has a single source.
 * Until then this is honest: the block still renders the real component, and
 * the code is the real snippet, they just live side by side in the `.mdx`.
 *
 * A later `src` mode could import an external `.tsx` example (component + its
 * `?raw` source) for specimens too stateful to write inline (a date picker, an
 * alert dialog…). Both modes feed the same UI below.
 */
export interface DemoProps {
  /** The live specimen — real components, with state, hooks, i18n, `lang`. */
  children: ReactNode;
  /** The source shown under the preview and copied by the button. */
  code: string;
  /** Language label on the code header (default tsx). */
  lang?: string;
  /** Optional filename/label shown on the code header. */
  title?: string;
}

let demoSeq = 0;

export function Demo({ children, code, lang = "tsx", title }: DemoProps) {
  const [codeId] = useState(() => `bk-demo-code-${(demoSeq += 1)}`);
  const [open, setOpen] = useState(false);
  const [copied, setCopied] = useState(false);
  // Bumping the key remounts the preview, returning any interactive specimen
  // (removed tags, an open menu, a picked date) to its initial state. Cheap and
  // universal — every Demo gets it, so a manipulated specimen is one click from
  // fresh.
  const [runId, setRunId] = useState(0);

  const copy = () => {
    const done = () => {
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1600);
    };
    if (navigator.clipboard?.writeText) {
      navigator.clipboard.writeText(code).then(done, done);
    } else {
      done();
    }
  };

  return (
    <div className="bk-demo">
      <div className="bk-demo__preview" key={runId}>
        {children}
      </div>

      <div className="bk-demo__bar">
        <div className="bk-demo__bar-left">
          <button
            type="button"
            className="bk-demo__toggle"
            aria-expanded={open}
            aria-controls={codeId}
            onClick={() => setOpen((v) => !v)}
          >
            <IconCode />
            {open ? "Hide code" : "Show code"}
            {title ? <span className="bk-demo__file">{title}</span> : null}
          </button>
        </div>
        <div className="bk-demo__bar-right">
          <button
            type="button"
            className="bk-demo__reset"
            onClick={() => setRunId((n) => n + 1)}
            aria-label="Reset the preview to its initial state"
          >
            <Reset />
            Reset
          </button>
          <button type="button" className="bk-demo__copy" onClick={copy} data-copied={copied}>
            {copied ? <IconCheck /> : <IconCopy />}
            {copied ? "Copied" : "Copy"}
          </button>
        </div>
      </div>

      {open ? (
        <pre className="bk-demo__code" data-lang={lang} id={codeId}>
          <code>{code}</code>
        </pre>
      ) : null}
    </div>
  );
}
