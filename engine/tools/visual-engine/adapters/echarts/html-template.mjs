/**
 * Self-contained interactive HTML export.
 *
 * Docgen law carried over: zero external references — ECharts is inlined from
 * the pinned node_modules copy, the theme is inlined, no CDN, no @import.
 * Reduced-motion users and print get the static SVG fallback via
 * `prefers-reduced-motion` / `print` media queries (same pattern as docgen's
 * layered_workflow dual-variant SVG).
 */
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const HERE = dirname(fileURLToPath(import.meta.url));

let _echartsDist;
function echartsDist() {
  if (!_echartsDist) {
    _echartsDist = readFileSync(join(HERE, "..", "..", "node_modules", "echarts", "dist", "echarts.min.js"), "utf8");
  }
  return _echartsDist;
}

const esc = (s) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

export function interactiveHTML({ job, option, theme, themeName, width, height, staticSVG, versions, ground }) {
  // OG-50: the page chrome follows the theme instead of being baked dark.
  //
  // The chart SVG has always been theme-correct — it is generated FROM `theme`. What was hardcoded
  // was everything around it: a `#060608` body, `#EAEEF5` ink and a `#8A96AE` caption, on every
  // export. A light-theme interactive HTML therefore framed light-theme ink in near-black, and the
  // defect was invisible in the SVG path and invisible in source.
  //
  // Ink comes from the SAME theme object the chart is rendered with, so the two cannot disagree;
  // the ground is passed in because `theme.backgroundColor` is deliberately "transparent" for
  // every non-print theme (a chart inherits its host's ground) and a standalone page has no host.
  const bg = ground ?? "#060608";
  const ink = theme?.textStyle?.color ?? "#EAEEF5";
  const inkMuted = theme?.title?.subtextStyle?.color ?? "#8A96AE";
  const scheme = themeName === "project-theme-light" || themeName === "print-theme" ? "light" : "dark";
  const interactiveOption = { ...option, animation: true, animationDuration: 400 };
  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(job.title ?? "visual")}</title>
<style>
  :root { color-scheme: ${scheme}; }
  body { margin: 0; background: ${bg}; color: ${ink};
         font-family: "Inter", system-ui, -apple-system, sans-serif; }
  main { max-width: ${width + 48}px; margin: 24px auto; padding: 0 16px; }
  h1 { font-family: "Space Grotesk", system-ui, sans-serif; font-size: 18px; font-weight: 600; margin: 0 0 4px; }
  p.q { color: ${inkMuted}; font-size: 13px; margin: 0 0 16px; }
  #chart { width: ${width}px; height: ${height}px; max-width: 100%; }
  .static-fallback { display: none; }
  figcaption { color: ${inkMuted}; font-size: 12px; margin-top: 12px; }
  @media (prefers-reduced-motion: reduce), print {
    #chart { display: none; }
    .static-fallback { display: block; }
  }
</style>
</head>
<body>
<main>
  <h1>${esc(job.title ?? "")}</h1>
  <p class="q">${esc(job.reader_question ?? "")}</p>
  <figure>
    <div id="chart" role="img" aria-label="${esc(job.title ?? job.reader_question ?? "chart")}"></div>
    <div class="static-fallback">${staticSVG}</div>
    <figcaption>${esc(job.text_summary ?? "")}</figcaption>
  </figure>
</main>
<script>${echartsDist()}</script>
<script>
  (function () {
    var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduced) return; // static fallback is already visible via CSS
    echarts.registerTheme(${JSON.stringify(themeName)}, ${JSON.stringify(theme)});
    var chart = echarts.init(document.getElementById("chart"), ${JSON.stringify(themeName)}, { renderer: "canvas" });
    chart.setOption(${JSON.stringify(interactiveOption)});
    window.addEventListener("resize", function () { chart.resize(); });
  })();
</script>
<!-- generated-by visual-engine · echarts@${versions.echarts} inlined (self-contained, no CDN) -->
</body>
</html>
`;
}
