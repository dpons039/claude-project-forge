import { useEffect, useState } from "react";

/**
 * Keeps the selected tab and the address bar in step, so a section can be linked
 * to — `brandkit.html#components` points someone at a tab rather than telling
 * them which one to click, and a refresh lands back on it.
 *
 * The valid ids are passed in (from `config.tabs`), not hard-coded: the chrome is
 * universal, so it cannot know one project's tab list. An unknown fragment falls
 * back to `fallback` rather than leaving the page with no panel.
 *
 * Selecting a tab moves the state **and** writes the fragment, in that order. The
 * tidier design — write the fragment only and let `hashchange` move the state —
 * is wrong: `hashchange` is queued, not dispatched synchronously, so a controlled
 * selection would be handed back the id it already had and treat it as refused.
 *
 * A fragment, not a path: the BrandKit entry is a standalone Vite entry with no
 * router and no server rewrite, so `/components` would 404 on reload.
 *
 * Nothing is written on first load: a visit with no fragment shows the fallback
 * and leaves the address bar alone rather than pushing a history entry nobody
 * asked for.
 */
export function useHashTab(
  ids: readonly string[],
  fallback: string,
): { tab: string; selectTab: (id: string) => void } {
  const fromHash = (): string => {
    const fragment = window.location.hash.replace(/^#/, "");
    return ids.includes(fragment) ? fragment : fallback;
  };

  const [tab, setTab] = useState<string>(fromHash);

  useEffect(() => {
    const sync = (): void => {
      // Only a KNOWN tab id moves the selection. In-page anchors fire hashchange
      // too — a focus target inside a tab, the block ids the on-this-page rail
      // links — and treating those as tab ids would bounce the page to another
      // tab mid-read.
      const fragment = window.location.hash.replace(/^#/, "");
      if (ids.includes(fragment)) setTab(fragment);
    };
    window.addEventListener("hashchange", sync);
    return () => window.removeEventListener("hashchange", sync);
  }, [ids]);

  return {
    tab,
    selectTab: (id: string): void => {
      setTab(id);
      window.location.hash = id;
    },
  };
}
