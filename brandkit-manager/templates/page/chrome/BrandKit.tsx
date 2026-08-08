import { useEffect, useMemo, useState } from "react";
import { MDXProvider } from "@mdx-js/react";

import { config } from "./config";
import { mdxComponents } from "./mdx-components";
import { TocRail } from "./components/TocRail";
import { Moon, Sun, ArrowsWide, ArrowsNarrow } from "./components/icons";
import { useHashTab } from "./lib/useHashTab";
import { tabModules } from "./tabs";

// The tab ids, derived once from config — the valid URL fragments.
const TAB_IDS = config.tabs.map((t) => t.id);

/**
 * The BrandKit chrome — dir-4. Header + tab nav are sticky; the content is the
 * active tab's `.mdx`, rendered with `mdxComponents` (so `<Demo>`, headings and
 * blocks all resolve). Theme / accent / density / width write straight to
 * `<html>`, exactly as the real app does, so a decision is tested under the real
 * mechanism rather than a BrandKit-only context.
 */
export function BrandKit() {
  const { tab: tabId, selectTab } = useHashTab(TAB_IDS, config.tabs[0]?.id ?? "");
  const [theme, setTheme] = useState(config.defaults.theme);
  const [accent, setAccent] = useState(config.defaults.accent);
  const [density, setDensity] = useState(config.defaults.density);
  const [full, setFull] = useState(false);

  // Appearance → <html>, the way the app's own bootstrap does it.
  useEffect(() => {
    const root = document.documentElement;
    root.setAttribute("data-theme", theme);
    root.setAttribute("data-accent", accent);
    root.setAttribute("data-width", full ? "full" : "contained");
    config.densities.forEach((d) => root.classList.remove(d.value));
    root.classList.add(density);
  }, [theme, accent, density, full]);

  const Logo = config.logo;
  const ActiveTab = useMemo(() => tabModules[tabId], [tabId]);
  // First theme = light, last = dark, by convention. Read once with fallbacks so
  // the toggle is safe under noUncheckedIndexedAccess and if the list is short.
  const lightTheme = config.themes[0]?.value ?? config.defaults.theme;
  const darkTheme = config.themes[config.themes.length - 1]?.value ?? lightTheme;
  const dark = theme === darkTheme;

  return (
    // .bk-root scopes the chrome's OWN palette; `data-bk-dark` follows the theme
    // toggle so the chrome flips too. Project tokens live only inside previews.
    <div className="bk-root" {...(dark ? { "data-bk-dark": "" } : {})}>
      {/* Two rows: L1 brand + all controls (theme/width/accent/density) · L2 tabs. */}
      <header className="bk-bar">
        <div className="bk-bar__inner">
          {/* L1 — brand and every control. */}
          <div className="bk-row bk-row--l1">
            <span className="bk-brand" aria-label={`${config.name} BrandKit`}>
              <Logo />
              <span className="bk-devtag">BrandKit</span>
            </span>

            <div className="bk-controls">
              <button
                type="button"
                className="bk-btn"
                aria-pressed={dark}
                onClick={() => setTheme(dark ? lightTheme : darkTheme)}
              >
                {dark ? <Sun /> : <Moon />}
                {dark ? "Light" : "Dark"}
              </button>

              <button
                type="button"
                className="bk-btn"
                aria-pressed={full}
                onClick={() => setFull((v) => !v)}
              >
                {full ? <ArrowsNarrow /> : <ArrowsWide />}
                {full ? "Contained" : "Full width"}
              </button>

              {/* Divider: universal chrome controls (left) vs per-project (right). */}
              <span className="bk-divider" aria-hidden />

              <div className="bk-ctl">
                <span className="bk-ctl__label">Accent</span>
                <div className="bk-swatches" role="group" aria-label="Accent">
                  {config.accents.map((a) => (
                    <button
                      key={a.value}
                      type="button"
                      className="bk-swatch"
                      // The chip carries its OWN theme + accent, so theme.css
                      // resolves `--accent` through the same compound
                      // `[data-theme][data-accent]` selector the app keys on —
                      // the colour shown IS the colour applied, and it flips
                      // with light/dark for free. No hex is copied here.
                      data-theme={theme}
                      data-accent={a.value}
                      aria-pressed={a.value === accent}
                      aria-label={a.label}
                      title={a.label}
                      onClick={() => setAccent(a.value)}
                    />
                  ))}
                </div>
              </div>

              <div className="bk-ctl">
                <span className="bk-ctl__label">Density</span>
                <div className="bk-seg" role="group" aria-label="Density">
                  {config.densities.map((d) => (
                    <button
                      key={d.value}
                      type="button"
                      aria-pressed={d.value === density}
                      onClick={() => setDensity(d.value)}
                    >
                      {d.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* L2 — tabs. */}
          <div className="bk-row bk-row--l2">
            <nav className="bk-tabs" aria-label="BrandKit sections">
              {config.tabs.map((t) => (
                <button
                  key={t.id}
                  type="button"
                  className="bk-tab"
                  aria-current={t.id === tabId ? "page" : undefined}
                  onClick={() => selectTab(t.id)}
                >
                  {t.label}
                </button>
              ))}
            </nav>
          </div>
        </div>
      </header>

      <div className="bk-shell">
        <main className="bk-main" id="bk-content">
          <MDXProvider components={mdxComponents}>
            {ActiveTab ? <ActiveTab /> : <p>Tab not found.</p>}
          </MDXProvider>
        </main>
        <TocRail key={tabId} tabId={tabId} />
      </div>
    </div>
  );
}
