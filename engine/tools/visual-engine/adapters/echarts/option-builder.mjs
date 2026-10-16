/**
 * Normalized visual job → ECharts option.
 *
 * The AI agent supplies a compact job packet (schemas/visual-job.schema.json);
 * this module owns ALL renderer syntax. Agents never hand-write ECharts
 * options for routine work (token-efficiency rule §32).
 *
 * Determinism: no Date.now, no Math.random, no force layouts. Graph presets
 * use circular/preset layouts so output is byte-stable for the regression
 * suite.
 */
import { VisualJobError } from "./validate.mjs";

const GRID = { left: 56, right: 24, top: 48, bottom: 40, containLabel: true };

function titleBlock(job) {
  const t = { left: 8, top: 6 };
  if (job.title) t.text = job.title;
  if (job.subtitle) t.subtext = job.subtitle;
  return job.title || job.subtitle ? { title: t } : {};
}

function datasetOf(job) {
  const { dimensions, source } = job.data;
  if (!Array.isArray(dimensions) || !Array.isArray(source)) {
    throw new VisualJobError("G-STRUCT", `visual "${job.selected_visual}" needs data.dimensions + data.source (table shape)`);
  }

  // ECharts treats a first row of all-strings as a HEADER and silently drops it. A row like
  // ["critical", "12"] — a perfectly ordinary result of a CSV read or a JSON API that quotes its
  // numbers — therefore vanished from the chart, which then rendered normally and wrongly. Refuse
  // rather than guess: the engine cannot know whether the author meant a header or a data row, and
  // a chart that silently omits a category is worse than one that fails to build (T-R9).
  if (source.length > 0 && Array.isArray(source[0]) && source[0].length > 1
      && source[0].every((cell) => typeof cell === "string")) {
    throw new VisualJobError(
      "G-STRUCT",
      `data.source[0] is all strings (${JSON.stringify(source[0])}). ECharts would treat it as a ` +
      `header row and DELETE it from the chart. If it is data, coerce the measure columns to ` +
      `numbers; if it is a header, remove it — data.dimensions already names the columns.`,
    );
  }

  // Duplicate CATEGORY labels collapse onto one axis position and the bars are drawn on top of one
  // another, so three runs scoring 10, 30 and 5 render as a single bar reading 30. Data disappearing
  // behind other data is the worst failure a chart can have, because it looks entirely normal.
  //
  // Scoped to a CATEGORICAL first column on purpose. The first version applied this to every family
  // and broke the scatter golden immediately: on a scatter plot the first column is an X VALUE, and
  // repeated x-values are ordinary data, not a collision. A guard that is right for one chart family
  // and wrong for another is not a guard — it is a false red, and a false red trains people to
  // bypass the gate. The engine's own regression suite caught it in the same run.
  const firstColumnIsCategorical =
    source.length > 1 && Array.isArray(source[0]) &&
    source.every((row) => !Array.isArray(row) || row.length === 0 ||
                          (typeof row[0] === "string" && !Number.isFinite(Number(row[0]))));
  if (firstColumnIsCategorical) {
    const seen = new Map();
    const dupes = [];
    for (const row of source) {
      if (!Array.isArray(row) || row.length === 0) continue;
      const key = String(row[0]);
      if (seen.has(key)) { if (!dupes.includes(key)) dupes.push(key); }
      else seen.set(key, true);
    }
    if (dupes.length > 0) {
      throw new VisualJobError(
        "G-STRUCT",
        `data.source has duplicate category labels in the first column: ` +
        `${JSON.stringify(dupes.slice(0, 5))}. They would collapse onto one axis position and the ` +
        `values would be drawn on top of each other, silently. Aggregate them, or make the labels ` +
        `distinct.`,
      );
    }
  }
  return { dataset: { dimensions, source } };
}

/**
 * Build one series per measure column, each with an EXPLICIT encode.
 *
 * Never rely on ECharts' implicit dataset dimension-to-axis inference — with
 * multiple series sharing one dataset it is order/name-sensitive, silently
 * mis-binds category/time axes (a `time` axis with no encode was seen
 * defaulting to nonsense tick values instead of the actual date column), and
 * its fallback resolution path is a measurable source of cross-platform
 * floating-point drift (macOS arm64 vs Linux x64 CI produced different bytes
 * for the identical job — caught by the golden-regression gate, 2026-08-10).
 * `orientation: "horizontal"` swaps the encode for bar_horizontal's category
 * y-axis; each series gets its OWN x per its OWN measure, never one shared
 * encode across every series (the bar_horizontal bug this replaces).
 */
function seriesForTable(job, type, { orientation = "vertical", ...extra } = {}) {
  const dims = job.data.dimensions;
  const measures = dims.slice(1);
  return measures.map((name) => ({
    type,
    name,
    encode: orientation === "horizontal" ? { y: dims[0], x: name } : { x: dims[0], y: name },
    ...extra,
  }));
}

const BUILDERS = {
  bar(job) {
    return { ...datasetOf(job), ...titleBlock(job), grid: GRID, legend: legend(job),
      xAxis: { type: "category" }, yAxis: valueAxis(job),
      series: seriesForTable(job, "bar", job.stack ? { stack: "total" } : {}) };
  },
  bar_grouped(job) { return BUILDERS.bar(job); },
  bar_stacked(job) { return BUILDERS.bar({ ...job, stack: true }); },
  bar_horizontal(job) {
    return { ...datasetOf(job), ...titleBlock(job), grid: GRID, legend: legend(job),
      yAxis: { type: "category", inverse: true }, xAxis: valueAxis(job),
      series: seriesForTable(job, "bar", { orientation: "horizontal", ...(job.stack ? { stack: "total" } : {}) }) };
  },
  line(job) {
    return { ...datasetOf(job), ...titleBlock(job), grid: GRID, legend: legend(job),
      xAxis: { type: job.time_axis ? "time" : "category", boundaryGap: false }, yAxis: valueAxis(job),
      series: seriesForTable(job, "line") };
  },
  line_step(job) {
    const o = BUILDERS.line(job); o.series.forEach((s) => (s.step = "end")); return o;
  },
  area(job) {
    const o = BUILDERS.line(job); o.series.forEach((s) => (s.areaStyle = { opacity: 0.25 })); return o;
  },
  area_stacked(job) {
    const o = BUILDERS.area(job); o.series.forEach((s) => (s.stack = "total")); return o;
  },
  scatter(job) {
    return { ...datasetOf(job), ...titleBlock(job), grid: GRID, legend: legend(job),
      xAxis: { type: "value", name: job.data.dimensions[0], nameLocation: "middle", nameGap: 28 },
      yAxis: { type: "value", name: job.data.dimensions[1] },
      series: [{ type: "scatter", symbolSize: 9, encode: { x: 0, y: 1, tooltip: [0, 1] } }] };
  },
  bubble(job) {
    const o = BUILDERS.scatter(job);
    const sizes = job.data.source.map((r) => Number(r[2]) || 0);
    const max = Math.max(1, ...sizes);
    o.series[0].symbolSize = (val) => 6 + 30 * Math.sqrt((Number(val[2]) || 0) / max);
    return o;
  },
  pie(job, { donut = false } = {}) {
    return { ...titleBlock(job), legend: legend(job),
      series: [{ type: "pie", radius: donut ? ["45%", "72%"] : "72%", center: ["50%", "56%"],
        data: job.data.items, label: { show: true, formatter: "{b}: {c}" },
        emphasis: { scale: false } }] };
  },
  donut(job) { return BUILDERS.pie(job, { donut: true }); },
  heatmap(job, theme) {
    const { rows, cols, matrix } = job.data;
    // The matrix must match the axes it is drawn against. ECharts plots [col, row, value] points
    // and simply does not draw a point whose index falls outside the category axis, so a matrix
    // with an extra row or a short row lost those cells with no error and no visible gap — and a
    // matrix with FEWER rows than `rows` shifted every value onto the wrong label, which is worse
    // than losing it: the chart is confidently wrong and looks complete. Both are silent
    // wrong-output, the class this engine refuses.
    if (Array.isArray(rows) && Array.isArray(matrix) && matrix.length !== rows.length) {
      throw new VisualJobError("G-CHART",
        `heatmap matrix has ${matrix.length} row(s) but data.rows declares ${rows.length} ` +
        `(${rows.join(", ")}). Every value would be drawn against the wrong row label.`);
    }
    if (Array.isArray(cols) && Array.isArray(matrix)) {
      const bad = matrix.findIndex((row) => Array.isArray(row) && row.length !== cols.length);
      if (bad !== -1) {
        throw new VisualJobError("G-CHART",
          `heatmap matrix row ${bad} has ${matrix[bad].length} cell(s) but data.cols declares ` +
          `${cols.length}. Cells past the axis are dropped from the render without warning.`);
      }
    }
    const points = [];
    matrix.forEach((row, r) => row.forEach((v, c) => points.push([c, r, v ?? "-"])));
    const flat = matrix.flat().filter((v) => typeof v === "number");
    return { ...titleBlock(job),
      grid: { ...GRID, right: 96 },
      xAxis: { type: "category", data: cols, splitArea: { show: true } },
      yAxis: { type: "category", data: rows, inverse: true, splitArea: { show: true } },
      // docgen law: a heatmap never ships without its scale legend.
      visualMap: { min: job.scale_min ?? Math.min(0, ...flat), max: job.scale_max ?? Math.max(1, ...flat),
        calculable: false, orient: "vertical", right: 8, top: "center",
        inRange: { color: theme?.semantic?.heatRamp ?? ["#0F2040", "#4A7FC1", "#EDB84A"] } },
      series: [{ type: "heatmap", data: points, label: { show: job.show_values ?? true, fontSize: 10 } }] };
  },
  matrix(job, theme) { return BUILDERS.heatmap(job, theme); },
  sankey(job) {
    return { ...titleBlock(job),
      series: [{ type: "sankey", data: job.data.nodes, links: job.data.links,
        emphasis: { focus: "adjacency" }, nodeAlign: "left",
        lineStyle: { color: "gradient", curveness: 0.5 }, label: { fontSize: 11 } }] };
  },
  funnel(job) {
    return { ...titleBlock(job), legend: legend(job),
      series: [{ type: "funnel", data: job.data.items, sort: "descending", gap: 2,
        label: { show: true, formatter: "{b}: {c}" } }] };
  },
  graph(job) {
    return { ...titleBlock(job),
      series: [{ type: "graph", layout: job.layout ?? "circular", // deterministic; never "force"
        data: job.data.nodes.map((n) => ({ ...n, symbolSize: n.symbolSize ?? 24 })),
        links: job.data.links, roam: false, label: { show: true, position: "right", fontSize: 11 },
        edgeSymbol: ["none", "arrow"], edgeSymbolSize: 7,
        lineStyle: { curveness: job.layout === "none" ? 0 : 0.18 } }] };
  },
  tree(job) {
    return { ...titleBlock(job),
      series: [{ type: "tree", data: [job.data.root], orient: "LR", symbolSize: 8,
        label: { position: "left", fontSize: 11 }, leaves: { label: { position: "right" } },
        expandAndCollapse: false, initialTreeDepth: -1 }] };
  },
  treemap(job) {
    return { ...titleBlock(job),
      // `root?.children` (not `root.children`): the `?? items` fallback is the documented
      // second input shape for this family, but without the optional chain an items-only job
      // throws TypeError on the missing `root` before the `??` is ever reached — so the
      // fallback was unreachable. No test/preset/fixture covered either hierarchy family.
      series: [{ type: "treemap", data: job.data.root?.children ?? job.data.items,
        roam: false, nodeClick: false, breadcrumb: { show: false },
        label: { show: true, fontSize: 11 } }] };
  },
  sunburst(job) {
    return { ...titleBlock(job),
      series: [{ type: "sunburst", data: job.data.root?.children ?? job.data.items, // see treemap above
        radius: ["12%", "82%"], label: { fontSize: 10 } }] };
  },
  boxplot(job) {
    return { ...titleBlock(job), grid: GRID,
      xAxis: { type: "category", data: job.data.categories },
      yAxis: valueAxis(job),
      series: [{ type: "boxplot", data: job.data.values }] }; // pre-computed [min,q1,med,q3,max]
  },
  radar(job) {
    return { ...titleBlock(job), legend: legend(job),
      radar: { indicator: job.data.axes, radius: "62%" },
      series: [{ type: "radar", data: job.data.series.map((s) => ({ name: s.name, value: s.values })) }] };
  },
  timeline(job) {
    const events = job.data.events;
    return { ...titleBlock(job), grid: { ...GRID, top: 64, bottom: 56 },
      xAxis: { type: "time" },
      yAxis: { type: "value", show: false, min: -1, max: 1 },
      series: [{ type: "scatter", symbolSize: 12,
        data: events.map((e, i) => ({ name: e.name, value: [e.date, i % 2 === 0 ? 0.35 : -0.35] })),
        label: { show: true, formatter: (p) => p.name, position: "top", fontSize: 10, rotate: 0 },
        markLine: { silent: true, symbol: "none", label: { show: false },
          data: events.map((e) => ({ xAxis: e.date })), lineStyle: { type: "dashed", opacity: 0.3 } } }] };
  },
  scorecard(job) {
    // Status scorecard = horizontal bar with semantic status colors, value labels.
    return BUILDERS.bar_horizontal(job);
  },
};

function legend(job) {
  const show = job.legend ?? (job.data?.dimensions?.length > 2 || job.data?.items?.length > 1);
  return { show: Boolean(show), top: job.title ? 28 : 8, right: 8 };
}

function valueAxis(job) {
  const axis = { type: job.log_scale ? "log" : "value" };
  // `nameLocation: "middle"` (+ a gap clearing the tick labels) is required, not cosmetic:
  // ECharts' default for an axis name is nameLocation "end", which lands it in the top-left
  // corner for a vertical value axis and at the right edge for a horizontal one — the exact
  // spots titleBlock() puts the title ({left: 8, top: 6}) and where the plot area ends. A job
  // declaring BOTH `title` and `units` therefore rendered the unit on top of the title, or
  // outside the SVG box entirely on bar_horizontal. Measured in a browser, three separate
  // figures. The bubble builder above already sets this pair correctly; valueAxis did not,
  // and no shipped preset happened to combine title+units on a valueAxis chart, so nothing
  // caught it. nameGap 46/32: vertical axes need more room for rotated tick labels.
  if (job.units?.[0]) {
    axis.name = job.units[0];
    axis.nameLocation = "middle";
    axis.nameGap = job.selected_visual === "bar_horizontal" || job.selected_visual === "scorecard" ? 32 : 46;
  }
  if (job.scale_min !== undefined) axis.min = job.scale_min;
  if (job.scale_max !== undefined) axis.max = job.scale_max;
  return axis;
}

/** Apply semantic severity/status colors when the preset declares them. */
function applySemantics(option, job, preset, theme) {
  const sem = preset?.semantics;
  if (!sem || !theme) return option;
  if (sem.severity_items && Array.isArray(option.series)) {
    for (const s of option.series) {
      if (Array.isArray(s.data)) {
        s.data = s.data.map((d) => {
          const key = (d.severity ?? d.name ?? "").toString().toLowerCase();
          const color = theme.severity?.[key === "critical" ? "crit" : key === "medium" ? "med" : key];
          return color ? { ...d, itemStyle: { ...(d.itemStyle ?? {}), color } } : d;
        });
      }
    }
  }
  return option;
}

export function buildOption(job, theme, preset) {
  const builder = BUILDERS[job.selected_visual];
  if (!builder) {
    throw new VisualJobError("G-ROUTE",
      `no ECharts builder for "${job.selected_visual}" — check ENGINE_ROUTING_POLICY.json for the owning engine`);
  }
  let option = builder(job, theme);
  // Preset defaults merge under the job (job-derived structure wins).
  if (preset?.defaults) option = deepMerge(structuredClone(preset.defaults), option);
  option = applySemantics(option, job, preset, theme);
  option.animation = false; // SSR determinism; interactive HTML re-enables
  option.aria = { enabled: true, decal: { show: Boolean(job.accessibility?.decal) } };
  if (job.tooltip !== false) option.tooltip = option.tooltip ?? { trigger: "item" };
  return option;
}

function deepMerge(base, over) {
  if (Array.isArray(base) || Array.isArray(over) || typeof base !== "object" || typeof over !== "object" || !base || !over) {
    return over ?? base;
  }
  const out = { ...base };
  for (const [k, v] of Object.entries(over)) out[k] = k in base ? deepMerge(base[k], v) : v;
  return out;
}
