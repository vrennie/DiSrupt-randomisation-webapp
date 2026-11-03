"""Build a complete illustrative three-area partition of KwaZulu-Natal.

Usage (offline regeneration only)::

    pip install 'shapely>=2'
    python scripts/generate_areas.py

The geometry is drawn in the coordinates of the user-supplied annotated
918 x 1038 map. The exact study site locations/classes are in assets/sites.csv.

Green study area B expands to the western and southern outer borders.
Purple study area A expands to the northern/eastern outer borders.
The continuous blue corridor between A and B includes all non-study dots.
All shapes are precisely clipped to the province's outer boundary.

These display regions are illustrative ONLY, not official geographic or trial
randomisation boundaries. Update the manual control points here if needed.
"""

import csv
import json
import re
from pathlib import Path

from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

# The narrow intervening non-study corridor, from the northern provincial
# edge to the coastal cluster of non-study sites. Its edges are hand-positioned
# between the adjacent green and purple site dots.
BLUE_CORRIDOR = [
    (317, 120), (325, 180), (329, 235), (330, 305), (322, 370),
    (309, 434), (300, 510), (320, 540), (343, 559), (369, 575),
    (370, 600), (365, 642), (363, 684), (381, 713), (422, 732),
    (476, 737), (498, 715), (514, 689), (522, 656), (522, 628),
    (500, 604), (465, 580), (443, 570), (405, 565), (398, 552),
    (368, 505), (366, 443), (381, 375), (385, 300), (388, 230),
    (393, 180), (397, 120),
]

# This large polygon reaches beyond the province on the western and southern
# sides. Intersecting it with the province makes the green area follow the
# west, southwest, and southern external outline exactly.
WESTERN_STUDY_AREA = [
    (-100, -100), (317, -100), (317, 120), (325, 180),
    (329, 235), (330, 305), (322, 370), (309, 434),
    (300, 510), (320, 540), (343, 559), (369, 575),
    (370, 600), (365, 642), (363, 684), (381, 713),
    (422, 732), (490, 745), (710, 816), (1080, 899),
    (1080, 1250), (-100, 1250),
]


def svg_path(geometry):
    """Export SVG paths including holes; the app renders with evenodd fill."""
    polygons = [geometry] if geometry.geom_type == "Polygon" else list(geometry.geoms)
    output = []
    for polygon in polygons:
        if polygon.is_empty:
            continue
        for ring in (polygon.exterior, *polygon.interiors):
            pts = [(round(x, 2), round(y, 2)) for x, y in ring.coords]
            output.append(
                "M" + f"{pts[0][0]},{pts[0][1]}"
                + "".join(f"L{x},{y}" for x, y in pts[1:]) + "Z"
            )
    return " ".join(output)


def main():
    svg = (ASSETS / "province_outline.svg").read_text(encoding="utf-8")
    match = re.search(r'<path d="([^\"]+)"', svg)
    if not match:
        raise ValueError("Province SVG does not contain its outer boundary path")
    coords = [
        (float(x), float(y))
        for x, y in re.findall(r"([0-9.]+),([0-9.]+)", match.group(1))
    ]
    province = Polygon(coords)
    if not province.is_valid:
        raise ValueError("Invalid province boundary geometry")

    blue = province.intersection(Polygon(BLUE_CORRIDOR))
    green = province.intersection(Polygon(WESTERN_STUDY_AREA)).difference(blue)
    purple = province.difference(unary_union([green, blue]))
    areas = {"A": purple, "B": green, "non_study": blue}

    if any(area.is_empty or not area.is_valid for area in areas.values()):
        raise ValueError("Empty/invalid partition area")
    if province.difference(unary_union(list(areas.values()))).area > 0.001:
        raise ValueError("Partition leaves an uncoloured provincial gap")
    for area_name, region in areas.items():
        for other_name, other in areas.items():
            if area_name < other_name and region.intersection(other).area > 0.001:
                raise ValueError(f"Overlapping areas: {area_name} and {other_name}")

    with (ASSETS / "sites.csv").open(encoding="utf-8", newline="") as fp:
        sites = list(csv.DictReader(fp))
    if len(sites) != 57 or len({s["site_id"] for s in sites}) != len(sites):
        raise ValueError("Unexpected number of sites or duplicate site IDs")
    for site in sites:
        if site["area"] not in areas:
            raise ValueError(f"Unknown site category {site['area']}")
        dot = Point(float(site["x"]), float(site["y"]))
        if not areas[site["area"]].buffer(0.05).covers(dot):
            raise ValueError(f"Site is not inside its assigned area: {site['site_id']}")

    output = {
        "description": (
            "Illustrative complete province partition: purple A reaches the "
            "north/east border, green B reaches the west/south border, "
            "and the intervening corridor is blue non-study. "
            "Not official administrative boundaries."
        ),
        "viewBox": [0, 0, 918, 1038],
        "opacity": 0.50,
        "paths": {key: svg_path(value) for key, value in areas.items()},
    }
    (ASSETS / "area_envelopes.json").write_text(
        json.dumps(output, indent=2) + "\n", encoding="utf-8"
    )
    print("Wrote assets/area_envelopes.json")
    print("Area sizes in map pixel^2:", {k: round(v.area) for k,v in areas.items()})
    print("Validated: no white gaps, no overlaps, all 57 sites in their assigned area.")


if __name__ == "__main__":
    main()
