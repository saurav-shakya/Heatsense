// Only the subsets and weights the CSS uses. Latin text renders in Plex Sans / Condensed; the
// Devanagari family only supplies Hindi glyphs. MapLibre's CSS loads with the map chunk.
import "@fontsource/ibm-plex-sans/latin-400.css";
import "@fontsource/ibm-plex-sans/latin-500.css";
import "@fontsource/ibm-plex-sans/latin-600.css";
import "@fontsource/ibm-plex-sans-condensed/latin-600.css";
import "@fontsource/ibm-plex-sans-condensed/latin-700.css";
import "@fontsource/ibm-plex-sans-devanagari/devanagari-400.css";
import "@fontsource/ibm-plex-sans-devanagari/devanagari-500.css";
import "@fontsource/ibm-plex-sans-devanagari/devanagari-600.css";
import "./styles/tokens.css";
import "./styles/app.css";

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
