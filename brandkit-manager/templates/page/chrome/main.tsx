import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
// import { Toast } from "@heroui/react"; // if your project uses HeroUI's toast queue

// import "@/locales/i18n"; // if your project has i18n, load it so specimens render real strings
import "@/styles/index.css"; // your project's real stylesheet — adjust the path
import "./brandkit.css";

import { BrandKit } from "./BrandKit";

/**
 * The BrandKit entry (dev-only). Mounts the chrome; the app's stylesheet (and
 * i18n, if any) are loaded so specimens render exactly as they do in the
 * product. Never built for production — keep this entry out of
 * `build.rollupOptions.input` so only the app's own `index.html` is built.
 */
const root = document.getElementById("brandkit");
if (root) {
  createRoot(root).render(
    <StrictMode>
      <BrandKit />
      {/* If your project uses a queue-driven toast/notification provider,
          mount it here too, in the same place the app's own main.tsx does —
          otherwise a demo that fires a toast has nowhere for it to render. */}
      {/* <Toast.Provider placement="bottom" /> */}
    </StrictMode>,
  );
}
