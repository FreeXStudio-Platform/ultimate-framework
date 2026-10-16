"""Bridge from docgen to tools/mermaid-engine.

Mirrors echarts_bridge.py's shape exactly (one engine per family — ENGINE_ROUTING_POLICY.json's
convention — docgen never grows a second implementation of a diagram type another engine already
owns): a frozen figure-spec dataclass, an ``engine_available()`` preflight, and a fail-closed
``render()`` that shells out to the sibling engine's CLI and returns inline SVG for embedding.

Invariants preserved (same as echarts_bridge.py):
- **Fail-closed** — a missing Node runtime, missing engine deps, or invalid Mermaid syntax
  raises ``MermaidRenderError``; the build fails honestly rather than emitting a document with
  a silently absent figure (T-R9).
- **Leak-gate coverage** — the returned SVG is embedded into the document body BEFORE the
  export sanitizer runs, so rendered diagram bytes pass the same 7-gate scan as every other
  output channel.
- **No CDN** — tools/mermaid-engine/render.mjs strips the underlying library's live Google
  Fonts import before returning SVG; this bridge only ever sees the sanitized output.

stdlib only (subprocess/tempfile/pathlib). mypy --strict clean.
"""

from __future__ import annotations

import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from tools.docgen import engine_config

_REPO_ROOT = Path(__file__).resolve().parents[2]
_ENGINE_ROOT = _REPO_ROOT / "tools" / "mermaid-engine"
_ENGINE_CLI = _ENGINE_ROOT / "render.mjs"
_RENDER_TIMEOUT_S = 30

# See tools/mermaid-engine/README.md for the verified, real scope — anything outside this list
# fails closed here rather than silently attempting an unsupported diagram type.
SUPPORTED_MERMAID_TYPES = frozenset(
    {"graph", "flowchart", "sequenceDiagram", "classDiagram", "stateDiagram-v2", "erDiagram", "xychart-beta"}
)


class MermaidRenderError(RuntimeError):
    """Raised when the mermaid-engine render fails or cannot run (fail-closed)."""


@dataclass(frozen=True)
class MermaidFigureSpec:
    """A docgen figure whose SVG comes from tools/mermaid-engine.

    ``code`` is raw Mermaid diagram text (the caller is responsible for it being one of
    ``SUPPORTED_MERMAID_TYPES`` — see ``check_mermaid_type`` to validate before rendering).

    ``bg``/``fg`` default to ``--mermaid-bg``/``--mermaid-fg`` — docgen-page-level aliases
    (``tokens.py``) for its own ``--bg``/``--fg`` theme variables — rather than a fixed color.
    docgen documents ship BOTH a dark and light theme with a runtime toggle (no separate
    render per theme), so a figure with hardcoded colors would look wrong in whichever theme
    it wasn't rendered for.

    Do NOT default these to literal ``var(--bg)``/``var(--fg)``: the underlying renderer sets
    its OWN local ``--bg``/``--fg`` custom properties on the SVG's own root element, so a
    same-named reference is a genuine CSS cycle (the property becomes the guaranteed-invalid
    value at computed-value time — verified by rendering, not assumed — which then makes every
    ``var(--_node-fill)``/``var(--_text)`` etc. that depends on it invalid too, and SVG
    presentation attributes fall back to their initial value: ``fill="black"``, producing solid
    black boxes with invisible black-on-black text). The differently-named ``--mermaid-*``
    aliases are defined one level up (docgen's page CSS), so the embedded SVG's unshadowed
    ``var(--mermaid-bg)`` reference correctly inherits from there instead.

    Pass real hex values explicitly only if you genuinely want a fixed-appearance diagram
    (e.g. embedding in a context outside docgen's own theme system).
    """

    id: str
    caption: str
    code: str
    reader_question: str = ""
    insight: str = ""
    bg: str | None = "var(--mermaid-bg)"
    fg: str | None = "var(--mermaid-fg)"


def check_mermaid_type(code: str) -> str | None:
    """Return an error message if ``code``'s diagram type isn't one of the supported 6, else None."""
    first_line = code.strip().splitlines()[0].strip() if code.strip() else ""
    if not any(first_line.startswith(t) for t in SUPPORTED_MERMAID_TYPES):
        supported = ", ".join(sorted(SUPPORTED_MERMAID_TYPES))
        return (
            f"unrecognized or unsupported Mermaid diagram type in first line {first_line!r} — "
            f"tools/mermaid-engine supports exactly: {supported}. "
            "See tools/mermaid-engine/README.md for what to use instead (gantt/mindmap/etc)."
        )
    return None


def engine_available() -> tuple[bool, str]:
    """Report whether the engine can run here (Node discoverable + installed deps)."""
    if not _ENGINE_CLI.is_file():
        return False, f"engine CLI missing: {_ENGINE_CLI}"
    if not (_ENGINE_ROOT / "node_modules" / "beautiful-mermaid").is_dir():
        return False, f"engine deps not installed — run `npm install` in {_ENGINE_ROOT}"
    node_bin = engine_config.tool_path("node")
    if not node_bin:
        return False, "node not found (checked ENGINE_NODE_BIN, engine.config.json, PATH)"
    try:
        subprocess.run([node_bin, "--version"], capture_output=True, check=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return False, f"node found at {node_bin} but failed to run"
    return True, "ok"


def render(spec: MermaidFigureSpec) -> str:
    """Render ``spec.code`` through tools/mermaid-engine's CLI → sanitized (no-CDN) SVG string."""
    type_error = check_mermaid_type(spec.code)
    if type_error:
        raise MermaidRenderError(f'figure "{spec.id}": {type_error}')

    available, why = engine_available()
    if not available:
        raise MermaidRenderError(f'figure "{spec.id}" cannot render: {why}')

    with tempfile.TemporaryDirectory(prefix="docgen-mermaid-") as tmp:
        tmp_path = Path(tmp)
        input_path = tmp_path / "diagram.mmd"
        input_path.write_text(spec.code, encoding="utf-8")
        out_path = tmp_path / "diagram.svg"
        cmd = [engine_config.tool_path("node") or "node", str(_ENGINE_CLI), str(input_path), "-o", str(out_path)]
        if spec.bg:
            cmd += ["--bg", spec.bg]
        if spec.fg:
            cmd += ["--fg", spec.fg]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            # Explicit: returncode is inspected below and converted to a MermaidRenderError that
            # carries the engine's stderr. `check=False` states that on purpose (PLW1510).
            check=False,
            timeout=_RENDER_TIMEOUT_S,
            cwd=str(_ENGINE_ROOT),
        )
        if result.returncode != 0:
            detail = (result.stderr or result.stdout or "").strip()[:500]
            raise MermaidRenderError(f'figure "{spec.id}": mermaid-engine render failed — {detail}')
        if not out_path.is_file():
            raise MermaidRenderError(f'figure "{spec.id}": engine reported success but wrote no SVG')
        return out_path.read_text(encoding="utf-8")
