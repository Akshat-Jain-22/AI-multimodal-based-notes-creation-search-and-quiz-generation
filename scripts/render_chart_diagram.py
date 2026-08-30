"""
Renders bar/line/pie/scatter charts from structured data (produced by the
LLM alongside a quiz question) as a standalone PNG file.

Same rationale as render_circuit_diagram.py: the LLM writes exact numbers as
structured data rather than trying to draw an image itself, so the rendered
chart is guaranteed to match the numbers stated in the question — no
hallucinated data points, no mismatched labels. Free, local, CPU-only
(matplotlib's Agg backend, no GPU/network needed).
"""

import os
import uuid

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def render_chart(spec, output_path):
    """spec = {
        "kind": "chart",
        "chart_type": "bar" | "line" | "pie" | "scatter",
        "title": str,
        "x_label": str,          # bar/line/scatter only
        "y_label": str,          # bar/line/scatter only
        "categories": [str, ...],        # bar/line
        "values": [number, ...],         # bar/line — same length as categories
        "labels": [str, ...],            # pie — slice labels
        # (pie also uses "values" — slice sizes, same length as labels)
        "points": [{"x": number, "y": number}, ...]   # scatter
    }
    Writes a PNG file to output_path and returns that path.
    """
    chart_type = spec.get("chart_type", "bar")
    title = spec.get("title", "")

    fig, ax = plt.subplots(figsize=(6, 4))

    if chart_type == "pie":
        labels = spec.get("labels", [])
        values = spec.get("values", [])
        ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
        ax.axis("equal")

    elif chart_type == "scatter":
        points = spec.get("points", [])
        xs = [p["x"] for p in points]
        ys = [p["y"] for p in points]
        ax.scatter(xs, ys)
        ax.set_xlabel(spec.get("x_label", ""))
        ax.set_ylabel(spec.get("y_label", ""))
        ax.grid(True, alpha=0.3)

    elif chart_type == "line":
        categories = spec.get("categories", [])
        values = spec.get("values", [])
        ax.plot(categories, values, marker="o")
        ax.set_xlabel(spec.get("x_label", ""))
        ax.set_ylabel(spec.get("y_label", ""))
        ax.grid(True, alpha=0.3)

    else:  # bar (default fallback)
        categories = spec.get("categories", [])
        values = spec.get("values", [])
        ax.bar(categories, values)
        ax.set_xlabel(spec.get("x_label", ""))
        ax.set_ylabel(spec.get("y_label", ""))
        ax.grid(True, axis="y", alpha=0.3)

    if title:
        ax.set_title(title)

    fig.tight_layout()

    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)

    return output_path


def chart_caption(spec):
    return spec.get("title") or f"Generated {spec.get('chart_type', 'chart')}"


def unique_chart_path(output_dir="generated_diagrams", prefix="chart"):
    return os.path.join(output_dir, f"{prefix}_{uuid.uuid4().hex[:8]}.png")