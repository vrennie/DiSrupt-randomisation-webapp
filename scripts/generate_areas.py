"""Regenerate the illustrative area envelopes from assets/sites.csv.

Requires Shapely >=2.0, only for this offline regeneration script:
    pip install shapely
    python scripts/generate_areas.py

The shapes are image-derived visual envelopes, NOT administrative boundaries.
They are clipped to the external KZN province outline and partitioned by
nearest marked site so semi-transparent regions never overlap.
"""

import csv
import json
import re
from pathlib import Path

from shapely import MultiPoint, Point, Polygon, concave_hull
from shapely.ops import unary_union, voronoi_diagram

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
GROUPS = ("A", "B", "non_study")
RATIO = 0.32
MARGINS = {"A": 35, "B": 35, "non_study": 30}  # source-map pixels


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
            commands.append(f"M{pts[0][0]},{pts[0][1]}" + "".join(
                f"L{x},{y}" for x, y in pts[1:]
            ) + "Z")
    return " ".join(commands)


def main():
    with (ASSETS / "sites.csv").open(encoding="utf-8", newline="") as f:
        sites = list(csv.DictReader(f))
    if not sites or any(s["area"] not in GROUPS for s in sites):
        raise ValueError("Site CSV is empty or contains invalid area categories")
    if len({s["site_id"] for s in sites}) != len(sites):
        raise ValueError("Duplicate site_id in sites.csv")

    svg = (ASSETS / "province_outline.svg").read_text(encoding="utf-8")
    match = re.search(r'<path d="([^"]+)"', svg)
    if match is None:
        raise ValueError("Province SVG lacks its external outline path")
    coords = [(float(x), float(y)) for x, y in re.findall(r'([0-9.]+),([0-9.]+)', match.group(1))]
    province = Polygon(coords)
    if not province.is_valid:
        raise ValueError("Province outline polygon is invalid")

    points = [Point(float(s["x"]), float(s["y"])) for s in sites]
    if len({(p.x, p.y) for p in points}) != len(points):
        raise ValueError("Duplicate dot positions")
    nearest_cells = {key: [] for key in GROUPS}
    for cell in voronoi_diagram(MultiPoint(points), envelope=province.envelope.buffer(250)).geoms:
        probe = cell.representative_point()
        site_index = min(range(len(points)), key=lambda i: points[i].distance(probe))
        nearest_cells[sites[site_index]["area"]].append(cell)

    areas = {}
    for key in GROUPS:
        group_points = [p for p, s in zip(points, sites) if s["area"] == key]
        if len(group_points) < 3:
            raise ValueError(f"Need >=3 sites in group {key} for shaded envelope")
        contour = concave_hull(MultiPoint(group_points), ratio=RATIO, allow_holes=False)
        expanded = contour.buffer(MARGINS[key], join_style=1)
        clipped = expanded.intersection(unary_union(nearest_cells[key])).intersection(province)
        if clipped.is_empty:
            raise ValueError(f"Empty area shape for {key}")
        for site in group_points:
            if not clipped.buffer(0.25).covers(site):
                raise ValueError(f"Site outside own area envelope for {key}: {site}")
        areas[key] = clipped

    for i, left in enumerate(GROUPS):
        for right in GROUPS[i + 1:]:
            if areas[left].intersection(areas[right]).area > 0.001:
                raise ValueError(f"Area envelopes overlap: {left}, {right}")

    data = {
        "description": "Image-derived illustrative buffered site envelopes (not official administrative boundaries)",
        "viewBox": [0, 0, 918, 1038],
        "opacity": 0.50,
        "paths": {k: svg_path(areas[k].simplify(1.2, preserve_topology=True)) for k in GROUPS},
    }
    (ASSETS / "area_envelopes.json").write_text(
        json.dumps(data, indent=2) + "\n", encoding="utf-8"
    )
    print("Updated assets/area_envelopes.json")
    print("Site counts:", {key: sum(s["area"] == key for s in sites) for key in GROUPS})


if __name__ == "__main__":
    main()
