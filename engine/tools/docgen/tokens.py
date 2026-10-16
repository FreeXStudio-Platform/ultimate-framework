"""Atlas design tokens -> CSS (RULEBOOK L15/L21, DESIGN_SYSTEM.md sections 1-3).

Loads ``assets/tokens.json`` (vendored from the Atlas — never fork values here, re-vendor
instead) and emits a single self-contained stylesheet: vendored ``@font-face`` faces
(``fonts.build_font_face_css()``), dark (native) + light (report/print) themes, brand +
severity variables, the Atlas ``.t-*`` type-role classes, spacing/radii, the blueprint
diagram canvas (``.svgwrap``), and the doc-system component CSS (masthead, classification
badge, data table, figure, callout, verified stamp, theme toggle).

Stdlib only; mypy --strict clean; no network references (no ``@import``, no CDN links) —
fonts are embedded as base64 data-URIs, not fetched.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Final

from tools.docgen.fonts import build_font_face_css

_ASSETS_DIR: Final[Path] = Path(__file__).resolve().parent / "assets"
_TOKENS_PATH: Final[Path] = _ASSETS_DIR / "tokens.json"


class TokensUnavailable(RuntimeError):
    """The design-token source could not be read.

    Raised instead of letting a bare ``JSONDecodeError``/``OSError`` escape at IMPORT time. Every
    entry point imports this module, so a corrupt ``tokens.json`` killed ``docgen manifest`` — and
    anything else — with a raw traceback that named a JSON column and not the problem. Fail-closed
    is right (a document rendered without its design tokens is not the document); an unreadable
    stack trace is not.
    """


def _load_tokens(path: Path = _TOKENS_PATH) -> dict[str, object]:
    """Load the vendored Atlas token JSON. Fail-CLOSED, with a diagnosis rather than a traceback."""
    try:
        with path.open("r", encoding="utf-8") as f:
            data: dict[str, object] = json.load(f)
    except (OSError, ValueError) as exc:
        raise TokensUnavailable(
            f"{path} could not be read as JSON ({exc}). Every rendered document depends on it, so "
            "the engine refuses rather than rendering an unstyled artifact. Restore the file from "
            "git: `git checkout -- tools/docgen/assets/tokens.json`."
        ) from exc
    if not isinstance(data, dict) or not data:
        raise TokensUnavailable(
            f"{path} parsed but is {type(data).__name__} and/or empty — the token set cannot be "
            "empty; every colour, size and spacing value in a rendered document comes from it."
        )
    return data


_TOKENS_CACHE: dict[str, object] | None = None


def tokens_data() -> dict[str, object]:
    """The token set, loaded on FIRST USE rather than at import.

    Module-level `TOKENS = _load_tokens()` raised during import, so no caller could ever catch it:
    every entry point imports this module, and a corrupt tokens.json killed `docgen manifest` and
    everything else with a raw traceback before `main()` existed to handle it. Deferring the load
    keeps the fail-closed behaviour and moves the failure somewhere a caller can turn into a
    diagnosis.
    """
    global _TOKENS_CACHE
    if _TOKENS_CACHE is None:
        _TOKENS_CACHE = _load_tokens()
    return _TOKENS_CACHE


def __getattr__(name: str) -> object:
    """Keep `tokens.TOKENS` working for existing callers, now lazily."""
    if name == "TOKENS":
        return tokens_data()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def _css_vars(prefix_map: dict[str, str]) -> str:
    """Render a flat name->value mapping as ``--name:value;`` lines (2-space indented)."""
    lines = [f"  --{name}:{value};" for name, value in prefix_map.items()]
    return "\n".join(lines)


def _sub(name: str) -> dict[str, str]:
    """Fetch a nested string-keyed, string-valued sub-object from ``TOKENS`` (e.g. ``"brand"``)."""
    value = tokens_data()[name]
    if not isinstance(value, dict):
        raise TypeError(f"tokens.json[{name!r}] is not an object: {type(value).__name__}")
    return {str(k): str(v) for k, v in value.items()}


def build_css() -> str:
    """Emit the full self-contained doc-system stylesheet from ``TOKENS``.

    Includes the vendored ``@font-face`` rules (real Space Grotesk/Inter/JetBrains Mono faces,
    embedded as base64 data-URIs — see ``fonts.py``), both ``:root``/``[data-theme=dark]`` and
    ``[data-theme=light]`` grounds/inks, brand + severity variables, the Atlas ``.t-*``
    type-role classes (system-stack fallbacks after the real face, never a serif), spacing/
    radii, the ``.svgwrap`` blueprint grid, table/badge/callout/masthead component rules, a
    ``prefers-reduced-motion`` guard, and a visible ``:focus-visible`` ring. No ``@import``,
    no CDN reference — every font byte is embedded, so a self-contained render always shows
    the real Atlas faces rather than silently substituting a system font.
    """
    grounds_dark = _sub("grounds_dark")
    inks_dark = _sub("inks_dark")
    grounds_light = _sub("grounds_light")
    inks_light = _sub("inks_light")
    brand = _sub("brand")
    severity = _sub("severity")
    fonts = _sub("fonts")
    weights = _sub("weights")
    font_size = _sub("font_size")
    line_height = _sub("line_height")
    spacing = _sub("spacing")
    radii = _sub("radii")
    layout = _sub("layout")
    diagram = _sub("diagram")

    dark_vars = _css_vars(
        {
            "ink": grounds_dark["ink"],
            "night": grounds_dark["night"],
            "steel": grounds_dark["steel"],
            "steel-2": grounds_dark["steel-2"],
            "bone": inks_dark["bone"],
            "ash": inks_dark["ash"],
            "mute": inks_dark["mute"],
            "faint": inks_dark["faint"],
            "bg": "var(--night)",
            "paper": "var(--night)",
            "paper-2": "var(--steel)",
            "fg": "var(--bone)",
            # Distinct-named aliases for embedded third-party SVG (tools/docgen/mermaid_bridge.py):
            # those SVGs set their OWN local --bg/--fg on their own root element, which would
            # make a literal var(--bg) self-referencing (CSS treats that as a cycle -> the
            # guaranteed-invalid value, not "inherit from the page" — confirmed by rendering,
            # not assumed). Aliasing under different names one level up avoids the cycle: the
            # embedded SVG references var(--mermaid-bg), which is NOT redefined locally on the
            # SVG itself, so it correctly inherits this page-level value.
            "mermaid-bg": "var(--bg)",
            "mermaid-fg": "var(--fg)",
        }
    )
    light_vars = _css_vars(
        {
            "ink": grounds_light["ink"],
            "night": grounds_light["night"],
            "steel": grounds_light["steel"],
            "steel-2": grounds_light["steel-2"],
            "bone": inks_light["bone"],
            "ash": inks_light["ash"],
            "mute": inks_light["mute"],
            "faint": inks_light["faint"],
            "bg": grounds_light["night"],
            "paper": grounds_light["night"],
            "paper-2": grounds_light["steel"],
            "fg": inks_light["bone"],
            "mermaid-bg": "var(--bg)",
            "mermaid-fg": "var(--fg)",
        }
    )
    brand_vars = _css_vars(
        {
            "shield": brand["shield"],
            "shield-hi": brand["shield-hi"],
            "shield-dim": brand["shield-dim"],
            "bronze": brand["bronze"],
            "bronze-hi": brand["bronze-hi"],
            "ember": brand["ember"],
            "ember-hi": brand["ember-hi"],
            "gold": brand["gold"],
            "gold-hi": brand["gold-hi"],
            "gold-mark": brand["gold-mark"],
            "verify": brand["verify"],
            "sev-crit": severity["crit"],
            "sev-high": severity["high"],
            "sev-med": severity["med"],
            "sev-med-hi": severity["med-hi"],
            "sev-low": severity["low"],
            "sev-info": severity["info"],
            "accent": "var(--shield-hi)",
            "shield-glow": "#4A7FC126",
            "f-display": fonts["display"],
            "f-body": fonts["body"],
            "f-mono": fonts["mono"],
            "fw-label": str(weights["label"]),
            "fw-eyebrow": str(weights["eyebrow"]),
            "fw-body": str(weights["body"]),
            "fw-emphasis": str(weights["emphasis"]),
            "fw-button": str(weights["button"]),
            "fw-display": str(weights["display"]),
            "maxw": layout["maxw"],
            "pad": layout["pad"],
            "r-xs": radii["xs"],
            "r-sm": radii["sm"],
            "r-md": radii["md"],
            "r-lg": radii["lg"],
            "r-pill": radii["pill"],
            "diagram-grid": diagram["grid"],
        }
    )
    fs_vars = _css_vars({f"fs-{k}": v for k, v in font_size.items()})
    lh_vars = _css_vars({f"lh-{k}": v for k, v in line_height.items()})
    sp_vars = _css_vars({f"g{k}": v for k, v in spacing.items()})
    font_faces = build_font_face_css()

    return f"""\
/* doc-system stylesheet — generated by tools/docgen/tokens.py from assets/tokens.json.
   Self-contained: no @import, no CDN — fonts embedded as base64 data-URIs below. Do not
   hand-edit; edit the token source and rebuild (RULEBOOK L7). */

{font_faces}

:root, [data-theme="dark"] {{
{dark_vars}
}}

[data-theme="light"] {{
{light_vars}
}}

:root {{
{brand_vars}
{fs_vars}
{lh_vars}
{sp_vars}
}}

* {{ box-sizing: border-box; }}

html {{ color-scheme: dark light; }}

body {{
  margin: 0;
  background: var(--bg);
  color: var(--fg);
  font-family: var(--f-body);
  font-weight: var(--fw-body);
  font-size: var(--fs-base);
  line-height: var(--lh-base);
  -webkit-font-smoothing: antialiased;
}}

.doc-root {{
  max-width: var(--maxw);
  margin: 0 auto;
  padding: var(--pad);
}}

/* ---- Atlas type-role classes (DESIGN_SYSTEM.md §2) ---- */
.t-h1, .t-h2, .t-h3, .t-h4 {{
  font-family: var(--f-display);
  font-weight: var(--fw-display);
  line-height: var(--lh-tight);
  letter-spacing: -0.01em;
  text-wrap: balance;
  margin: 0;
}}
.t-h1 {{ font-size: var(--fs-4xl); }}
.t-h2 {{ font-size: var(--fs-3xl); }}
.t-h3 {{ font-size: var(--fs-2xl); }}
.t-h4 {{ font-size: var(--fs-xl); }}

.t-lede {{
  font-family: var(--f-body);
  font-weight: var(--fw-body);
  font-size: var(--fs-lg);
  line-height: var(--lh-loose);
  max-width: 68ch;
}}
.t-body {{
  font-family: var(--f-body);
  font-weight: var(--fw-body);
  font-size: var(--fs-base);
  line-height: var(--lh-base);
  max-width: 68ch;
}}
.t-body-sm {{
  font-family: var(--f-body);
  font-weight: var(--fw-body);
  font-size: var(--fs-sm);
  line-height: var(--lh-base);
}}
.t-mono-label {{
  font-family: var(--f-mono);
  font-weight: var(--fw-label);
  font-size: var(--fs-xs);
  letter-spacing: 0.18em;
  text-transform: uppercase;
}}
.t-mono-data {{
  font-family: var(--f-mono);
  font-weight: var(--fw-body);
  font-variant-numeric: tabular-nums;
  font-size: var(--fs-sm);
}}
.t-caption, .t-eyebrow {{
  font-family: var(--f-mono);
  font-weight: var(--fw-eyebrow);
  font-size: var(--fs-xs);
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: var(--ash);
}}

/* ---- Masthead ---- */
.masthead {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--g4);
  padding-bottom: var(--g5);
  border-bottom: 1px solid var(--faint);
  margin-bottom: var(--g6);
}}
.masthead-brand {{ display: flex; align-items: center; gap: var(--g3); }}
.masthead-logo {{ width: 28px; height: 28px; color: var(--fg); flex: none; }}
.masthead-titles {{ display: flex; flex-direction: column; gap: var(--g1); }}
.masthead-meta {{ display: flex; align-items: center; gap: var(--g3); flex-wrap: wrap; }}

/* ---- Classification badge ---- */
.badge {{
  display: inline-flex;
  align-items: center;
  gap: var(--g1);
  padding: 3px var(--g3);
  border-radius: var(--r-pill);
  font-family: var(--f-mono);
  font-weight: var(--fw-label);
  font-size: var(--fs-2xs);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  white-space: nowrap;
}}
.badge-public {{ background: var(--shield-dim); color: var(--shield-hi); border: 1px solid var(--shield); }}
.badge-confidential {{ background: #3A2E10; color: var(--gold-hi); border: 1px solid var(--gold); }}
.badge-secret {{
  color: var(--bone);
  border: 1px solid var(--sev-crit);
  background: repeating-linear-gradient(45deg, #3A0E0F, #3A0E0F 6px, #2A0A0B 6px, #2A0A0B 12px);
}}

/* ---- Section frame ---- */
.doc-section {{ margin: var(--g8) 0; }}
.doc-section > .t-eyebrow {{ display: block; margin: 0 0 var(--g2); padding-bottom: var(--g1); border-bottom: 1px solid var(--faint); }}
/* The section eyebrow is an <h2> (a document needs a real heading outline, not one <h1> and
   24 styled spans), so its browser-default top margin has to be zeroed explicitly — the
   `.t-h*` reset above does not cover `.t-eyebrow`. */

/* ---- Tables ---- */
.doc-table-wrap {{ overflow-x: auto; margin: var(--g5) 0; }}

/* Every native figure draws its caption INSIDE the SVG (visual.py `_caption_block`) so that a
   standalone .svg export is self-describing. Inside a document the same caption is also emitted as
   a real <figcaption> — selectable, themed, at body size, and read by assistive technology — so the
   in-SVG copy is a duplicate rendered at ~4-9px after the viewBox scales down. Hide it here rather
   than removing it from the renderers, because the standalone export genuinely needs it: the
   duplication is a property of the EMBEDDING, so the embedding is where it should be resolved. */
.svgwrap svg text.figure-caption {{ display: none; }}

/* The .svgwrap blueprint grid is decorative and belongs behind docgen's own line-art figures. A
   chart-engine SVG paints no ground of its own (backgroundColor is "transparent", so it inherits
   the document), so the grid showed THROUGH the plot area — graph paper behind every bar and
   radar. Give an embedded chart its own ground. */
.svgwrap svg[data-engine="echarts"], .svgwrap svg[data-engine="mermaid"] {{ background: var(--bg); }}

/* A hash, a URL or a long path has no break opportunity, so it runs past the 68ch text column and
   out of its container. */
.t-body, .figcap, .t-list li, .doc-table td, .doc-table th {{ overflow-wrap: anywhere; }}

/* Block elements emitted by the Markdown renderer. `p` needs an explicit margin reset: the
   browser default is 1em top AND bottom, which stacked a full blank line between paragraphs and,
   before the renderer joined hard-wrapped lines, between every source line of one sentence. */
p {{ margin: 0; }}
.t-body + .t-body {{ margin-top: var(--g3); }}
.t-list {{ margin: var(--g3) 0; padding-left: var(--g5); line-height: var(--lh-base); }}
.t-list li {{ margin: var(--g1) 0; }}
.t-list li::marker {{ color: var(--mute); }}
.t-code {{
  font-family: var(--f-mono);
  font-size: 0.9em;
  padding: 0.1em 0.35em;
  border-radius: 3px;
  background: var(--faint);
  border: 1px solid var(--faint);
}}
.t-pre {{
  font-family: var(--f-mono);
  font-size: var(--fs-sm);
  line-height: 1.55;
  margin: var(--g4) 0;
  padding: var(--g3);
  border-radius: 6px;
  background: var(--faint);
  border: 1px solid var(--faint);
  overflow-x: auto;
  white-space: pre;
}}
.t-pre code {{ background: none; border: 0; padding: 0; font-size: inherit; }}
.t-quote {{
  margin: var(--g4) 0;
  padding: var(--g2) var(--g4);
  border-left: 3px solid var(--accent);
  color: var(--mute);
}}
.t-quote p {{ margin: 0; }}
.t-rule {{ border: 0; border-top: 1px solid var(--faint); margin: var(--g6) 0; }}
.t-link {{ color: var(--accent); text-decoration: underline; text-underline-offset: 2px; }}

/* Print. A table inside `overflow-x: auto` is CLIPPED on paper — the columns past the fold are
   simply gone from the PDF, with no scrollbar and no indication anything is missing. On print,
   let the wrapper overflow visibly and allow the table to shrink to the page instead. */
@media print {{
  .doc-table-wrap {{ overflow-x: visible; }}
  .doc-table-wrap table {{ width: 100%; table-layout: auto; font-size: 9pt; }}
  .doc-table-wrap td, .doc-table-wrap th {{ word-break: break-word; overflow-wrap: anywhere; }}
  .t-pre {{ white-space: pre-wrap; overflow-x: visible; }}
  figure, table, .t-pre, blockquote {{ break-inside: avoid; }}
  .t-h2, .t-h3 {{ break-after: avoid; }}
}}
table.doc-table {{ width: 100%; border-collapse: collapse; font-size: var(--fs-sm); }}
table.doc-table thead th {{
  background: var(--paper-2);
  color: var(--fg);
  text-align: left;
  font-family: var(--f-mono);
  font-weight: var(--fw-label);
  font-size: var(--fs-2xs);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  padding: var(--g2) var(--g3);
  border-bottom: 1px solid var(--faint);
  white-space: nowrap;
}}
table.doc-table td {{
  padding: var(--g2) var(--g3);
  border-bottom: 1px solid var(--faint);
  font-variant-numeric: tabular-nums;
  vertical-align: top;
}}
table.doc-table tbody tr:nth-child(even) {{ background: color-mix(in srgb, var(--paper-2) 40%, transparent); }}

/* ---- Figure / blueprint canvas ---- */
figure.doc-figure {{ margin: var(--g6) 0; }}
.svgwrap {{
  background-image:
    linear-gradient(var(--faint) 1px, transparent 1px),
    linear-gradient(90deg, var(--faint) 1px, transparent 1px);
  background-size: var(--diagram-grid) var(--diagram-grid);
  background-color: var(--paper);
  border: 1px solid var(--faint);
  border-radius: var(--r-md);
  padding: var(--g4);
  overflow-x: auto;
}}
.svgwrap svg {{ display: block; max-width: 100%; height: auto; }}
figcaption.figcap {{ margin-top: var(--g3); font-size: var(--fs-sm); color: var(--ash); }}
.figure-legend {{ display: flex; flex-wrap: wrap; gap: var(--g3); margin-top: var(--g2); }}
.figure-legend-item {{ display: flex; align-items: center; gap: var(--g1); font-size: var(--fs-xs); color: var(--ash); }}
/* Interpretive layer (see INTERPRETATION.md): what question the figure answers + the plain-
   language conclusion it makes obvious. Distinct from the caption (what it IS) on purpose. */
.figure-insight-block {{ margin-top: var(--g3); padding: var(--g2) var(--g3); border-left: 2px solid var(--shield-hi, var(--fg)); background: color-mix(in srgb, var(--fg) 4%, var(--bg)); }}
.figure-reader-question {{ font-size: var(--fs-xs); text-transform: uppercase; letter-spacing: .04em; color: var(--mute); margin-bottom: var(--g1); }}
.figure-insight {{ font-size: var(--fs-sm); color: var(--fg); }}

/* ---- Callouts ---- */
.callout {{
  border-left: 3px solid var(--accent);
  background: var(--paper-2);
  border-radius: 0 var(--r-sm) var(--r-sm) 0;
  padding: var(--g4);
  margin: var(--g5) 0;
}}
.callout-info {{ border-left-color: var(--sev-info); }}
.callout-warn {{ border-left-color: var(--sev-med); }}
.callout-crit {{ border-left-color: var(--sev-crit); }}

/* ---- Verified stamp (trust footer) ---- */
.verified-stamp {{
  display: flex;
  align-items: center;
  gap: var(--g3);
  padding: var(--g5);
  margin-top: var(--g8);
  border-top: 1px solid var(--faint);
}}
.verified-stamp-mark {{ width: 32px; height: 32px; color: var(--verify); flex: none; }}
.verified-stamp-text {{ display: flex; flex-direction: column; gap: 2px; }}

/* ---- Theme toggle ---- */
.theme-toggle {{
  appearance: none;
  border: 1px solid var(--faint);
  background: var(--paper-2);
  color: var(--fg);
  border-radius: var(--r-pill);
  padding: 4px var(--g3);
  font-family: var(--f-mono);
  font-size: var(--fs-2xs);
  cursor: pointer;
}}

/* ---- Focus + motion guards (DESIGN_SYSTEM §7) ---- */
:focus-visible {{
  outline: 2px solid var(--shield-hi);
  outline-offset: 2px;
}}

@media (prefers-reduced-motion: reduce) {{
  *, *::before, *::after {{
    animation-duration: 0.001ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.001ms !important;
    scroll-behavior: auto !important;
  }}
}}

@media (max-width: 768px) {{
  .masthead {{ flex-direction: column; align-items: flex-start; }}
}}
"""
