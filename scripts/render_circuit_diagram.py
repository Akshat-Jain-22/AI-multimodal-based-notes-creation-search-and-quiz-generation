"""
Renders a simple two-terminal circuit as a standalone SVG file.

Topology supported: a chain of "groups" in series from terminal A to
terminal B, where each group is either a single component (resistor or
source) or a PARALLEL BANK of two or more resistors. This covers the
overwhelming majority of intro-level Thevenin/Norton problems — one source,
plus a series chain where at most one link is a parallel combination —
without needing to support arbitrary nested/bridge networks.

Legacy input shape (a flat "components" list, no "groups") is still
accepted and treated as before: every component in its own series group.
This exists so a schema-drift response from generate_quiz.py's LLM call
(which is supposed to emit "groups" but nothing enforces that at the
schema level any more than it enforces "mcq requires options") degrades to
the old pure-series rendering instead of crashing.

This exists specifically so quiz questions with invented numerical values
(e.g. "given the voltage source is 15V and resistors are 10 ohms and 20
ohms...") get a diagram that actually matches those numbers, instead of
reusing a captured lecture screenshot whose values belong to a different
example entirely.

Deliberately simple/schematic rather than artistic — this is a free, local,
CPU-only renderer with no external dependencies beyond the stdlib.
"""

import os
import uuid

RESISTOR_WIDTH = 60
RESISTOR_HEIGHT = 24
SOURCE_RADIUS = 20
COMPONENT_SPACING = 130
PARALLEL_GROUP_WIDTH = RESISTOR_WIDTH + 70   
PARALLEL_BRANCH_GAP = RESISTOR_HEIGHT + 26   
BASE_HEIGHT = 150
MARGIN_X = 50

STROKE = "#1a1a1a"


def _normalize_groups(circuit):
    """Returns circuit's "groups" if present, else wraps a legacy flat
    "components" list into one series group per component (see module
    docstring)."""
    groups = circuit.get("groups")
    if groups:
        return groups
    return [{"connection": "series", "components": [c]} for c in circuit.get("components", [])]


def _is_parallel_bank(group):
    return group.get("connection") == "parallel" and len(group.get("components", [])) > 1


def _resistor_svg(cx, cy, label, value):
    half = RESISTOR_WIDTH / 2
    x0 = cx - half
    segments = 6
    seg_w = RESISTOR_WIDTH / segments
    amplitude = RESISTOR_HEIGHT / 2

    pts = [(x0, cy)]
    for i in range(1, segments):
        x = x0 + i * seg_w
        y = cy - amplitude if i % 2 == 1 else cy + amplitude
        pts.append((x, y))
    pts.append((x0 + RESISTOR_WIDTH, cy))
    points_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)

    label_text = f"{label} = {value}" if value else label
    return (
        f'<polyline points="{points_str}" fill="none" stroke="{STROKE}" stroke-width="2"/>'
        f'<text x="{cx}" y="{cy - RESISTOR_HEIGHT - 10}" font-size="12" '
        f'text-anchor="middle" fill="{STROKE}">{label_text}</text>'
    ), half


def _source_svg(cx, cy, label, value, kind="voltage_source"):
    label_text = f"{label} = {value}" if value else label

    if kind == "current_source":
        symbol = (
            f'<circle cx="{cx}" cy="{cy}" r="{SOURCE_RADIUS}" fill="none" stroke="{STROKE}" stroke-width="2"/>'
            f'<line x1="{cx}" y1="{cy+8}" x2="{cx}" y2="{cy-8}" stroke="{STROKE}" stroke-width="2"/>'
            f'<polygon points="{cx-4},{cy-8} {cx+4},{cy-8} {cx},{cy-14}" fill="{STROKE}"/>'
        )
    else:
        symbol = (
            f'<circle cx="{cx}" cy="{cy}" r="{SOURCE_RADIUS}" fill="none" stroke="{STROKE}" stroke-width="2"/>'
            f'<text x="{cx}" y="{cy - 4}" font-size="14" text-anchor="middle" fill="{STROKE}">+</text>'
            f'<text x="{cx}" y="{cy + 13}" font-size="14" text-anchor="middle" fill="{STROKE}">-</text>'
        )

    label_svg = (
        f'<text x="{cx}" y="{cy - SOURCE_RADIUS - 12}" font-size="13" '
        f'text-anchor="middle" fill="{STROKE}">{label_text}</text>'
    )
    return symbol + label_svg, SOURCE_RADIUS


def _parallel_bank_svg(x_left, x_right, wire_y, components):
    """Draws a bank of 2+ resistors in parallel between x_left and x_right,
    as stacked horizontal branches joined by two vertical bus rails —
    the standard simple-schematic way to draw a parallel combination."""
    k = len(components)
    total_height = (k - 1) * PARALLEL_BRANCH_GAP
    top_y = wire_y - total_height / 2
    bottom_y = wire_y + total_height / 2

    bus_x_left = x_left + 14
    bus_x_right = x_right - 14
    comp_cx = (bus_x_left + bus_x_right) / 2

    parts = [
        f'<line x1="{x_left:.1f}" y1="{wire_y:.1f}" x2="{bus_x_left:.1f}" y2="{wire_y:.1f}" stroke="{STROKE}" stroke-width="2"/>',
        f'<line x1="{bus_x_right:.1f}" y1="{wire_y:.1f}" x2="{x_right:.1f}" y2="{wire_y:.1f}" stroke="{STROKE}" stroke-width="2"/>',
        f'<line x1="{bus_x_left:.1f}" y1="{top_y:.1f}" x2="{bus_x_left:.1f}" y2="{bottom_y:.1f}" stroke="{STROKE}" stroke-width="2"/>',
        f'<line x1="{bus_x_right:.1f}" y1="{top_y:.1f}" x2="{bus_x_right:.1f}" y2="{bottom_y:.1f}" stroke="{STROKE}" stroke-width="2"/>',
    ]

    for i, comp in enumerate(components):
        branch_y = top_y + i * PARALLEL_BRANCH_GAP
        label = comp.get("label", f"R{i+1}")
        value = comp.get("value", "")
        resistor_svg, half = _resistor_svg(comp_cx, branch_y, label, value)
        parts.append(
            f'<line x1="{bus_x_left:.1f}" y1="{branch_y:.1f}" x2="{comp_cx-half:.1f}" y2="{branch_y:.1f}" '
            f'stroke="{STROKE}" stroke-width="2"/>'
        )
        parts.append(resistor_svg)
        parts.append(
            f'<line x1="{comp_cx+half:.1f}" y1="{branch_y:.1f}" x2="{bus_x_right:.1f}" y2="{branch_y:.1f}" '
            f'stroke="{STROKE}" stroke-width="2"/>'
        )

    return "".join(parts)


def render_circuit_svg(circuit, output_path):
    """circuit = {
        "groups": [
            {"connection": "series", "components": [ {"type","label","value"} ]},
            {"connection": "parallel", "components": [ {...}, {...}, ... ]},
            ...
        ],
        "terminal_labels": ["A", "B"]
    }
    A group's "connection" only matters when it has 2+ components (a
    parallel bank); a single-component group is just that component in
    series with the rest of the chain regardless of its "connection" value.
    Legacy flat "components" input (no "groups") is also accepted — see
    _normalize_groups(). Writes an SVG file to output_path and returns that path.
    """
    groups = _normalize_groups(circuit)
    terminals = circuit.get("terminal_labels") or ["A", "B"]
    term_a, term_b = (list(terminals) + ["A", "B"])[:2]

    group_widths = []
    max_branches = 1
    for g in groups:
        if _is_parallel_bank(g):
            max_branches = max(max_branches, len(g["components"]))
            group_widths.append(PARALLEL_GROUP_WIDTH)
        else:
            group_widths.append(COMPONENT_SPACING)

    height = max(BASE_HEIGHT, 70 + max_branches * PARALLEL_BRANCH_GAP)
    wire_y = height / 2
    width = MARGIN_X * 2 + sum(group_widths or [COMPONENT_SPACING])

    parts = [f'<svg viewBox="0 0 {width:.0f} {height:.0f}" xmlns="http://www.w3.org/2000/svg">']
    parts.append(f'<rect width="{width:.0f}" height="{height:.0f}" fill="white"/>')

    cursor_x = MARGIN_X
    parts.append(f'<circle cx="{cursor_x}" cy="{wire_y:.1f}" r="4" fill="{STROKE}"/>')
    parts.append(
        f'<text x="{cursor_x}" y="{wire_y+28:.1f}" font-size="14" text-anchor="middle" '
        f'fill="{STROKE}">{term_a}</text>'
    )

    for g, gw in zip(groups, group_widths):
        next_x = cursor_x + gw

        if _is_parallel_bank(g):
            parts.append(_parallel_bank_svg(cursor_x, next_x, wire_y, g["components"]))
        else:
            comp = (g.get("components") or [{}])[0]
            comp_cx = (cursor_x + next_x) / 2
            ctype = comp.get("type", "resistor")
            label = comp.get("label", "C")
            value = comp.get("value", "")

            if ctype == "resistor":
                symbol_svg, half_width = _resistor_svg(comp_cx, wire_y, label, value)
            else:
                symbol_svg, half_width = _source_svg(comp_cx, wire_y, label, value, kind=ctype)

            parts.append(
                f'<line x1="{cursor_x}" y1="{wire_y:.1f}" x2="{comp_cx-half_width}" y2="{wire_y:.1f}" '
                f'stroke="{STROKE}" stroke-width="2"/>'
            )
            parts.append(symbol_svg)
            parts.append(
                f'<line x1="{comp_cx+half_width}" y1="{wire_y:.1f}" x2="{next_x}" y2="{wire_y:.1f}" '
                f'stroke="{STROKE}" stroke-width="2"/>'
            )

        cursor_x = next_x

    parts.append(f'<circle cx="{cursor_x}" cy="{wire_y:.1f}" r="4" fill="{STROKE}"/>')
    parts.append(
        f'<text x="{cursor_x}" y="{wire_y+28:.1f}" font-size="14" text-anchor="middle" '
        f'fill="{STROKE}">{term_b}</text>'
    )

    parts.append("</svg>")
    svg_content = "\n".join(parts)

    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    return output_path


def circuit_caption(circuit):
    """A short human-readable caption summarizing the circuit's components,
    used as the image alt-text/caption in the quiz output. A parallel bank
    is shown grouped with "||" so the caption itself communicates topology,
    not just values."""
    groups = _normalize_groups(circuit)
    parts = []
    for g in groups:
        comps = g.get("components", [])
        labels = [f"{c.get('label','')}={c.get('value','')}" for c in comps if c.get("label")]
        if not labels:
            continue
        if _is_parallel_bank(g):
            parts.append("(" + " || ".join(labels) + ")")
        else:
            parts.extend(labels)
    return ", ".join(parts) if parts else "Generated circuit diagram"


def unique_diagram_path(output_dir="generated_diagrams", prefix="circuit"):
    return os.path.join(output_dir, f"{prefix}_{uuid.uuid4().hex[:8]}.svg")