"""Regenerate the illustrative province-clipped partition areas.

Requires Shapely >=2.0 only for this offline regeneration step:
    pip install shapely
    python scripts/generate_areas.py

The resulting shapes are visual design aids, NOT official administrative
boundaries. They are clipped to the KZN province outline and reflect the
current concept:
- Area A (purple) extends to the west and northwest border.
- Area B (green) extends to the east and south border.
- The intervening space is the non-study area (blue).

Because four northern sites were manually reassigned into area B, area B also
contains a separate northwestern pocket around those markers.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from shapely.geometry import Polygon
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

# Manual design polygons in image coordinates. These are clipped to the
# province outline so only the in-province parts remain visible.
A_TOP = [
    (-100, -100),
    (1000, -100),
    (1000, 350),
    (880, 395),
    (740, 470),
    (620, 505),
    (520, 585),
    (455, 575),
    (410, 570),
    (360, 530),
    (300, 430),
    (140, 380),
    (-100, 380),
]

B_POCKET = [
    (210, 205),
    (335, 205),
    (345, 370),
    (215, 370),
]

NON_STUDY = [
    (420, 555),
    (470, 565),
    (520, 585),
    (560, 640),
    (520, 710),
    (410, 720),
    (360, 680),
    (360, 620),
]


def svg_path(geometry):
    """Convert Shapely polygon(s) to SVG paths; holes use evenodd filling."""
    shapes = [geometry] if geometry.geom_type == "Polygon" else list(geometry.geoms)
    commands = []
    for polygon in shapes:
        if polygon.is_empty:
            continue
        for ring in [polygon.exterior, *polygon.interiors]:
            pts = [(round(x, 1), round(y, 1)) for x, y in ring.coords]
            if len(pts) < 4:
                continue
            commands.append(
                f"M{pts[0][0]},{pts[0][1]}" + "".join(f"L{x},{y}" for x, y in pts[1:]) + "Z"
            )
    return " ".join(commands)


def main():
    svg = (ASSETS / "province_outline.svg").read_text(encoding="utf-8")
    match = re.search(r'<path d="([^"]+)"', svg)
    if match is None:
        raise ValueError("Province SVG lacks its external outline path")
    coords = [(float(x), float(y)) for x, y in re.findall(r"([0-9.]+),([0-9.]+)", match.group(1))]
    province = Polygon(coords)
    if not province.is_valid:
        raise ValueError("Province outline polygon is invalid")

    area_a = province.intersection(Polygon(A_TOP)).difference(Polygon(B_POCKET))
    non_study = province.intersection(Polygon(NON_STUDY)).difference(area_a)
    area_b = province.difference(unary_union([area_a, non_study]))

    if area_a.is_empty or area_b.is_empty or non_study.is_empty:
        raise ValueError("One or more illustrative regions is empty")

    data = {
        "description": (
            "Illustrative province-clipped partition areas: Area A reaches the "
            "west/northwest border, Area B reaches the eastern border, and the "
            "remaining central band is non-study. Not official administrative "
            "boundaries."
        ),
        "viewBox": [0, 0, 918, 1038],
        "opacity": 0.50,
        "paths": {
            "A": svg_path(area_a.simplify(1.2, preserve_topology=True)),
            "B": svg_path(area_b.simplify(1.2, preserve_topology=True)),
            "non_study": svg_path(non_study.simplify(1.2, preserve_topology=True)),
        },
    }
    (ASSETS / "area_envelopes.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print("Updated assets/area_envelopes.json")


if __name__ == "__main__":
    main()
