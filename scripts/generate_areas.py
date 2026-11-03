"""Rebuild visual study-area envelopes and their exact blue complement.

Install `shapely>=2` then run `python scripts/generate_areas.py` from the
repository root. All shapes are *illustrative*, not official GIS boundaries.

The study areas A/B follow image-digitised site clusters, buffered outward
and clipped to the province. Everything in the province outside the two
study envelopes is assigned to the blue non-study visual region, without
leaving white gaps. The Streamlit UI also draws the entire province blue
first to provide a robust no-gap fallback in the browser.
"""

from __future__ import annotations

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
MARGINS = {"A": 35, "B": 35}


def svg_path(geometry):
    """Serialize polygon exteriors/interiors as SVG evenodd subpaths."""
    shapes = [geometry] if geometry.geom_type == "Polygon" else list(geometry.geoms)
    commands = []
    for polygon in shapes:
        if polygon.is_empty:
            continue
        for ring in (polygon.exterior, *polygon.interiors):
            pts = [(round(x, 2), round(y, 2)) for x, y in ring.coords]
            commands.append("M" + f"{pts[0][0]},{pts[0][1]}" + "".join(
                f"L{x},{y}" for x, y in pts[1:]
            ) + "Z")
    return " ".join(commands)


def main():
    with (ASSETS / "sites.csv").open(encoding="utf-8", newline="") as fp:
        sites = list(csv.DictReader(fp))
    if not sites or any(s["area"] not in GROUPS for s in sites):
        raise ValueError("Invalid or missing sites")
    if len({s["site_id"] for s in sites}) != len(sites):
        raise ValueError("Duplicate site_id")
    svg = (ASSETS / "province_outline.svg").read_text(encoding="utf-8")
    match = re.search(r'<path d="([^"]+)"', svg)
    if not match:
        raise ValueError("Missing province boundary SVG path")
    coords = [(float(x), float(y)) for x, y in re.findall(
        r"([0-9.]+),([0-9.]+)", match.group(1)
    )]
    province = Polygon(coords)
    if not province.is_valid:
        raise ValueError("Invalid province geometry")

    sites_points = [Point(float(site["x"]), float(site["y"])) for site in sites]
    cells_by_area = {group: [] for group in GROUPS}
    for cell in voronoi_diagram(MultiPoint(sites_points), envelope=province.envelope.buffer(250)).geoms:
        probe = cell.representative_point()
        nearest = min(range(len(sites_points)), key=lambda i: sites_points[i].distance(probe))
        cells_by_area[sites[nearest]["area"]].append(cell)

    areas = {}
    for group in ("A", "B"):
        group_points = [point for point, site in zip(sites_points, sites) if site["area"] == group]
        hull = concave_hull(MultiPoint(group_points), ratio=RATIO, allow_holes=False)
        envelope = hull.buffer(MARGINS[group], join_style=1)
        areas[group] = envelope.intersection(unary_union(cells_by_area[group])).intersection(province)
        if areas[group].is_empty:
            raise ValueError(f"Empty study area {group}")
        for point in group_points:
            if not areas[group].buffer(0.25).covers(point):
                raise ValueError(f"Study site outside area {group}: {point}")

    # The blue region is the entire remainder of the province, not just a
    # buffered hull around blue dots. This eliminates all white holes.
    areas["non_study"] = province.difference(unary_union([areas["A"], areas["B"]]))
    for point, site in zip(sites_points, sites):
        if site["area"] == "non_study" and not areas["non_study"].buffer(0.25).covers(point):
            raise ValueError(f"Non-study site under A/B shading: {site['site_id']}")
    if province.difference(unary_union(list(areas.values()))).area > 0.001:
        raise ValueError("Area partition leaves white gaps")
    if areas["A"].intersection(areas["B"]).area > 0.001:
        raise ValueError("Study areas overlap")

    data = {
        "description": "Buffered study-area site envelopes and full blue non-study complement, all clipped to the province. Illustrative, not official boundaries.",
        "viewBox": [0, 0, 918, 1038],
        "opacity": 0.5,
        "paths": {
            key: svg_path(areas[key].simplify(1.2, preserve_topology=True))
            for key in GROUPS
        },
    }
    (ASSETS / "area_envelopes.json").write_text(
        json.dumps(data, indent=2) + "\n", encoding="utf-8"
    )
    print("Created areas:", {k: round(v.area, 1) for k, v in areas.items()})
    print("Every pixel of the provincial outline is assigned to an area.")


if __name__ == "__main__":
    main()
