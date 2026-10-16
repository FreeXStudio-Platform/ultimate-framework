"""HTML partials for the doc-system (DESIGN_SYSTEM.md §4-6, RULEBOOK L21).

Every function returns a plain ``str`` of HTML. All interpolated text is escaped via
``html.escape`` — callers may pass pre-built (already-escaped/safe) HTML fragments as
``body``/``svg`` parameters where documented. Stdlib only; mypy --strict clean.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from html import escape
from pathlib import Path
from typing import Final

from tools.docgen.models import DocHeader, Tier

_ASSETS_DIR: Final[Path] = Path(__file__).resolve().parent / "assets"
_MARK_PATH: Final[Path] = _ASSETS_DIR / "engine-mark-placeholder.svg"

_TIER_BADGE_CLASS: Final[dict[Tier, str]] = {
    Tier.PUBLIC: "badge-public",
    Tier.CONFIDENTIAL: "badge-confidential",
    Tier.SECRET: "badge-secret",
}

_TIER_LABEL: Final[dict[Tier, str]] = {
    Tier.PUBLIC: "PUBLIC",
    Tier.CONFIDENTIAL: "CONFIDENTIAL",
    Tier.SECRET: "SECRET",
}

_TIER_GLYPH: Final[dict[Tier, str]] = {
    # Shield glyph for PUBLIC, gold diamond for CONFIDENTIAL, ember hazard-stripe swatch for SECRET.
    Tier.PUBLIC: '<span aria-hidden="true">&#128737;</span>',
    Tier.CONFIDENTIAL: '<span aria-hidden="true">&#9670;</span>',
    Tier.SECRET: '<span aria-hidden="true">&#9888;</span>',
}


def classification_badge(tier: Tier) -> str:
    """Render the classification badge: PUBLIC=shield, CONFIDENTIAL=gold, SECRET=ember-striped."""
    css_class = _TIER_BADGE_CLASS[tier]
    label = _TIER_LABEL[tier]
    glyph = _TIER_GLYPH[tier]
    return f'<span class="badge {css_class}">{glyph}<span>{escape(label)}</span></span>'


def logo_svg() -> str:
    """Inline the project mark (single source: assets/engine-mark-placeholder.svg — swap for a real mark before shipping)."""
    svg = _MARK_PATH.read_text(encoding="utf-8").strip()
    # Tag with a class hook for sizing via CSS (masthead vs. verified-stamp contexts differ).
    return svg.replace("<svg ", '<svg class="mark-svg" ', 1)


def theme_toggle() -> str:
    """A small inline-JS theme toggle: persists to localStorage, honors prefers-color-scheme.

    Self-contained (no external script). Safe to inline multiple times per page (uses
    ``closest`` lookups and idempotent listeners scoped to the clicked button).
    """
    return """\
<button type="button" class="theme-toggle" data-docgen-theme-toggle aria-label="Toggle light/dark theme">
  <span data-docgen-theme-label>theme</span>
</button>
<script>
(function () {
  var KEY = "docgen-theme";
  function apply(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    document.querySelectorAll("[data-docgen-theme-label]").forEach(function (el) {
      el.textContent = theme;
    });
  }
  function initial() {
    try {
      var saved = window.localStorage.getItem(KEY);
      if (saved === "dark" || saved === "light") return saved;
    } catch (e) { /* localStorage unavailable — fall through */ }
    var prefersLight = window.matchMedia && window.matchMedia("(prefers-color-scheme: light)").matches;
    return prefersLight ? "light" : "dark";
  }
  var current = initial();
  apply(current);
  document.querySelectorAll("[data-docgen-theme-toggle]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      current = current === "dark" ? "light" : "dark";
      apply(current);
      try { window.localStorage.setItem(KEY, current); } catch (e) { /* ignore */ }
    });
  });
})();
</script>"""


def masthead(header: DocHeader) -> str:
    """Render the document masthead: logo + title + mono meta line + classification badge + theme toggle."""
    title = escape(header.title)
    meta_bits = [
        escape(header.id),
        escape(header.owner),
        escape(header.status),
        escape(header.last_reviewed),
    ]
    meta_line = " &middot; ".join(meta_bits)
    badge = classification_badge(header.classification)
    logo = logo_svg()
    toggle = theme_toggle()
    return f"""\
<header class="masthead">
  <div class="masthead-brand">
    <div class="masthead-logo" aria-hidden="true">{logo}</div>
    <div class="masthead-titles">
      <h1 class="t-h2">{title}</h1>
      <div class="t-mono-label masthead-meta">{meta_line}</div>
    </div>
  </div>
  <div class="masthead-meta">
    {badge}
    {toggle}
  </div>
</header>"""


def section(
    eyebrow: str, body: str, *, eyebrow_renderer: Callable[[str], str] | None = None
) -> str:
    """Render a numbered section frame: mono eyebrow (real id) + hairline + body.

    ``eyebrow_renderer`` is the same opt-in used by :func:`data_table`: a heading authored in
    Markdown may legitimately contain a code span, and escaping it left literal backticks in the
    rendered heading. Defaults to plain escaping for callers whose eyebrow is a literal id.
    """
    render_eyebrow = eyebrow_renderer or escape
    return f"""\
<section class="doc-section">
  <h2 class="t-eyebrow">{render_eyebrow(eyebrow)}</h2>
  <div class="t-body">{body}</div>
</section>"""


def data_table(
    headers: list[str],
    rows: list[list[str]],
    *,
    cell_renderer: Callable[[str], str] | None = None,
) -> str:
    """Render a data table: dark header row, tabular-nums, wrapped in an overflow-x container.

    ``headers`` and each row cell are HTML-escaped by default (plain text only, no embedded
    markup). A caller whose cells are Markdown — the document generator — passes ``cell_renderer``
    to get inline rendering (code spans, emphasis, links) instead. It stays opt-in because the
    other callers (finance_report and friends) pass literal strings, where a stray ``*`` must
    remain a ``*`` and not silently become emphasis. The renderer is responsible for its own
    escaping; that is why the default is ``escape`` itself.
    """
    render = cell_renderer or escape
    head_cells = "".join(f"<th>{render(h)}</th>" for h in headers)
    body_rows = []
    for row in rows:
        cells = "".join(f"<td>{render(str(c))}</td>" for c in row)
        body_rows.append(f"<tr>{cells}</tr>")
    body_html = "".join(body_rows)
    return f"""\
<div class="doc-table-wrap">
  <table class="doc-table">
    <thead><tr>{head_cells}</tr></thead>
    <tbody>{body_html}</tbody>
  </table>
</div>"""


def figure(
    svg: str,
    caption: str,
    legend_html: str = "",
    *,
    reader_question: str = "",
    insight: str = "",
) -> str:
    """Render a figure block: ``.svgwrap`` blueprint canvas + numbered caption + optional legend
    + an optional "what this shows" interpretive block.

    ``svg`` is trusted pre-rendered SVG markup (from ``visual.render``); ``caption``,
    ``reader_question``, and ``insight`` are escaped. ``legend_html`` is trusted pre-built HTML
    (e.g. from a legend-building helper) and passed through unescaped by design — callers are
    responsible for escaping any dynamic text within.

    A figure is a VIEW of the same system/calculation the surrounding document already
    describes in prose and numbers — not decoration (see ``../../INTERPRETATION.md``).
    ``reader_question`` states what this specific figure answers; ``insight`` states the
    plain-language conclusion the picture makes obvious that raw numbers/text alone don't. Both
    are optional — an empty ``insight_block`` renders nothing extra, so a purely illustrative
    figure (no interpretive claim yet) is not forced to fabricate one.
    """
    legend_block = f'<div class="figure-legend">{legend_html}</div>' if legend_html else ""
    insight_parts = []
    if reader_question:
        insight_parts.append(f'<div class="figure-reader-question">{escape(reader_question)}</div>')
    if insight:
        insight_parts.append(f'<div class="figure-insight">{escape(insight)}</div>')
    insight_block = f'<div class="figure-insight-block">{"".join(insight_parts)}</div>' if insight_parts else ""
    # Emit the optional rows ONLY when they carry something. Interpolating an empty
    # ``legend_block`` into an indented template leaves a line holding two spaces and nothing else,
    # which is a whitespace error to `git diff --check` — so every figure without a legend put a
    # defect into a GENERATED file that no author could fix at the source. Measured: 15 such lines
    # in the tracked `examples/capability-gallery.html` (`OG-245`). Joining the populated blocks is
    # the repair rather than stripping the output afterwards, because a cleanup pass over generated
    # HTML is a second thing to keep correct.
    optional_rows = "".join(f"  {block}\n" for block in (legend_block, insight_block) if block)
    return f"""\
<figure class="doc-figure">
  <div class="svgwrap">{svg}</div>
  <figcaption class="figcap">{escape(caption)}</figcaption>
{optional_rows}</figure>"""


_CALLOUT_CLASS: Final[dict[str, str]] = {
    "info": "callout-info",
    "warn": "callout-warn",
    "crit": "callout-crit",
}


def callout(kind: str, body: str) -> str:
    """Render a callout block with an accent/severity left rule.

    ``kind`` is one of ``info``/``warn``/``crit`` (unknown kinds fall back to the neutral
    accent rule rather than raising, since callouts are presentational, not gating).
    """
    css_class = _CALLOUT_CLASS.get(kind, "")
    return f'<div class="callout {css_class}">{body}</div>'


def verified_stamp(audit_ref: str) -> str:
    """Render the 'Verified by ' trust footer stamp (DESIGN_SYSTEM §6).

    Static by default (reduced-motion compliant — no animation is emitted here; a future
    motion layer may progressively enhance this markup, but the base render must be legible
    and complete without any script/animation running).
    """
    logo = logo_svg()
    ref = escape(audit_ref)
    return f"""\
<div class="verified-stamp">
  <div class="verified-stamp-mark" aria-hidden="true">{logo}</div>
  <div class="verified-stamp-text">
    <span class="t-mono-label">Verified by </span>
    <span class="t-body-sm">{ref}</span>
  </div>
</div>"""


# ---- WCAG AA contrast helpers -------------------------------------------------------------


def _hex_to_rgb(color: str) -> tuple[float, float, float]:
    """Parse a ``#rrggbb`` or ``#rgb`` hex color into 0-255 float channels. Raises on bad input."""
    c = color.strip().lstrip("#")
    if len(c) == 3:
        c = "".join(ch * 2 for ch in c)
    if len(c) != 6:
        raise ValueError(f"not a hex color: {color!r}")
    r = int(c[0:2], 16)
    g = int(c[2:4], 16)
    b = int(c[4:6], 16)
    return float(r), float(g), float(b)


def _srgb_channel_to_linear(c: float) -> float:
    cs = c / 255.0
    if cs <= 0.04045:
        return cs / 12.92
    return math.pow((cs + 0.055) / 1.055, 2.4)


def _relative_luminance(color: str) -> float:
    r, g, b = _hex_to_rgb(color)
    rl = _srgb_channel_to_linear(r)
    gl = _srgb_channel_to_linear(g)
    bl = _srgb_channel_to_linear(b)
    return 0.2126 * rl + 0.7152 * gl + 0.0722 * bl


def contrast_ratio(fg: str, bg: str) -> float:
    """Return the WCAG contrast ratio between two ``#rrggbb`` hex colors (1.0 .. 21.0)."""
    l1 = _relative_luminance(fg)
    l2 = _relative_luminance(bg)
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def wcag_aa_ok(fg: str, bg: str, large: bool = False) -> bool:
    """True if ``fg`` on ``bg`` meets WCAG AA: >=4.5:1 normal text, >=3:1 large text (>=18pt/14pt-bold)."""
    ratio = contrast_ratio(fg, bg)
    threshold = 3.0 if large else 4.5
    return ratio >= threshold
