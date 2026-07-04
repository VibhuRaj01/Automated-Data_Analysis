from __future__ import annotations

import base64
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"
TEMPLATE_NAME = "report_template.html"

_BULLET_PREFIXES = ("-", "*", "\u2022")


# --------------------------------------------------------------------------
# Small pure helpers (kept standalone so they're easy to unit test)
# --------------------------------------------------------------------------


def _insight_to_html(insight_text: Optional[str]) -> Optional[str]:
    """
    Convert Insight Writer's bullet-point plain text into an HTML <ul>.

    Falls back to a single <p> if the text doesn't look bullet-shaped
    (e.g. legacy/manual insight text) rather than dropping it.
    """
    if not insight_text or not insight_text.strip():
        return None

    lines = [line.strip() for line in insight_text.strip().splitlines() if line.strip()]
    bullets = [
        line.lstrip("-*\u2022 ").strip()
        for line in lines
        if line.startswith(_BULLET_PREFIXES)
    ]

    if bullets and len(bullets) >= len(lines) / 2:
        items = "".join(f"<li>{_escape(b)}</li>" for b in bullets)
        return f"<ul>{items}</ul>"

    return f"<p>{_escape(insight_text.strip())}</p>"


def _escape(text: str) -> str:
    """Minimal HTML escaping for text we insert outside Jinja's autoescape
    (insight text is marked `| safe` in the template since we build real
    <ul>/<li> markup for it ourselves)."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _image_to_data_uri(path: Path) -> Optional[str]:
    """Read a PNG/JPG chart off disk and inline it as a base64 data URI,
    so the resulting HTML report is a single portable file with no
    dependency on relative image paths."""
    if not path.exists():
        return None
    ext = path.suffix.lower().lstrip(".")
    mime = "image/png" if ext == "png" else f"image/{ext}"
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def _resolve_chart_path(chart_path: str | Path, project_root: Path) -> Path:
    """chart_path may be given relative to the project root (as generator.py
    produces, e.g. 'outputs/graphs/graph_001.png') or already absolute."""
    p = Path(chart_path)
    return p if p.is_absolute() else (project_root / p)


# --------------------------------------------------------------------------
# Report assembly
# --------------------------------------------------------------------------


def _get_jinja_env(template_dir: Path = TEMPLATE_DIR) -> Environment:
    return Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(["html"]),
    )


def _build_context(
    profile: dict,
    report_items: list[dict],
    report_title: str,
    dataset_name: str,
    embed_images: bool,
    project_root: Path,
) -> dict[str, Any]:
    dataset = profile.get("dataset", {})
    columns = profile.get("columns", [])

    sorted_items = sorted(
        report_items,
        key=lambda item: item.get("analysis", {}).get("priority", 999),
    )

    rendered_items = []
    for idx, item in enumerate(sorted_items, start=1):
        analysis = item.get("analysis", {})
        chart_path_raw = item.get("chart_path")
        insight_text = item.get("insight")

        chart_data_uri = None
        chart_href = None
        if chart_path_raw:
            resolved = _resolve_chart_path(chart_path_raw, project_root)
            if embed_images:
                chart_data_uri = _image_to_data_uri(resolved)
            elif resolved.exists():
                chart_href = str(resolved)

        rendered_items.append(
            {
                "anchor": idx,
                "analysis": analysis,
                "chart_path": str(chart_path_raw) if chart_path_raw else None,
                "chart_data_uri": chart_data_uri,
                "chart_href": chart_href,
                "insight_html": _insight_to_html(insight_text),
            }
        )

    return {
        "report_title": report_title,
        "dataset_name": dataset_name,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "dataset": dataset,
        "columns": columns,
        "items": rendered_items,
    }


def build_report(
    profile: dict,
    report_items: list[dict],
    report_title: str = "Automated Data Analysis Report",
    dataset_name: str = "dataset",
    output_dir: str | Path = "outputs/reports",
    embed_images: bool = True,
    project_root: str | Path = ".",
    template_dir: str | Path = TEMPLATE_DIR,
) -> Path:
    """
    Render the final HTML report and write it to disk.

    Parameters
    ----------
    profile : dict
        Output of profiler.profile_dataset().
    report_items : list[dict]
        See module docstring for the expected shape of each item.
    report_title : str
        Title shown in the report header.
    dataset_name : str
        Human-readable dataset name, shown under the title.
    output_dir : str | Path
        Directory the HTML file is written into (created if missing).
    embed_images : bool
        If True (default), chart PNGs are base64-inlined so the report
        is a single self-contained file. If False, the report links to
        the chart files by path instead (smaller file, but not portable
        on its own).
    project_root : str | Path
        Root that relative chart_path values (e.g. "outputs/graphs/x.png")
        are resolved against. Defaults to the current working directory.
    template_dir : str | Path
        Directory containing report_template.html. Override only if you've
        moved/renamed the templates folder.

    Returns
    -------
    Path
        Path to the written HTML file.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    project_root = Path(project_root)

    env = _get_jinja_env(Path(template_dir))
    template = env.get_template(TEMPLATE_NAME)

    context = _build_context(
        profile=profile,
        report_items=report_items,
        report_title=report_title,
        dataset_name=dataset_name,
        embed_images=embed_images,
        project_root=project_root,
    )

    html = template.render(**context)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = output_dir / f"report_{timestamp}.html"
    out_path.write_text(html, encoding="utf-8")

    return out_path


def build_pdf_report(
    html_path: str | Path, output_path: Optional[str | Path] = None
) -> Path:
    """
    Convert an already-built HTML report to PDF using WeasyPrint.

    WeasyPrint is an optional dependency (per task.md, PDF export via
    WeasyPrint is explicitly listed as a "future" item) -- it isn't
    required to use build_report(). This raises a clear, actionable
    error if it isn't installed rather than failing on a cryptic
    ImportError deep in a stack trace.
    """
    html_path = Path(html_path)
    if not html_path.exists():
        raise FileNotFoundError(f"HTML report not found: {html_path}")

    try:
        from weasyprint import HTML  # noqa: WPS433 (intentionally lazy import)
    except ImportError as e:
        raise ImportError(
            "PDF export requires WeasyPrint, which is not installed. "
            "Install it with `pip install weasyprint` (it also needs system "
            "libraries -- Pango, Cairo, GDK-PixBuf -- see "
            "https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation). "
            "The HTML report at the given path is still fully usable on its own."
        ) from e

    output_path = Path(output_path) if output_path else html_path.with_suffix(".pdf")
    HTML(filename=str(html_path)).write_pdf(str(output_path))
    return output_path
