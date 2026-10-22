"""
Polygon-containment jurisdiction assessment.

Replaces the earlier nearest-station-centroid lookup, which is not a jurisdiction test.
A station is named only when the point lies inside exactly one polygon and is not close
to a boundary. Every other case returns "Police jurisdiction requires confirmation."
The boundary dataset's source and date are not verified; this is recorded with each result.
"""

import hashlib
import json
import math
import os
from functools import lru_cache
from typing import List, Optional, Tuple

from complaint_engine.models import JurisdictionAssessment

JURISDICTION_CONFIRMATION_MESSAGE = "Police jurisdiction requires confirmation."
NEAR_BOUNDARY_METERS = 100.0
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_GEOJSON_CANDIDATE = os.path.join(REPO_ROOT, "datasets", "mumbai_police_jurisdictions.geojson")
DEFAULT_GEOJSON = _GEOJSON_CANDIDATE if os.path.exists(_GEOJSON_CANDIDATE) else os.path.join(REPO_ROOT, "mumbai_police_jurisdictions.geojson")


def _point_in_ring(x: float, y: float, ring: List[List[float]]) -> bool:
    inside = False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i][0], ring[i][1]
        xj, yj = ring[j][0], ring[j][1]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def _polygons(geometry: dict) -> List[list]:
    if not geometry:
        return []
    if geometry.get("type") == "Polygon":
        return [geometry["coordinates"]]
    if geometry.get("type") == "MultiPolygon":
        return list(geometry["coordinates"])
    return []


def point_in_geometry(lng: float, lat: float, geometry: dict) -> bool:
    for rings in _polygons(geometry):
        if rings and _point_in_ring(lng, lat, rings[0]) and not any(_point_in_ring(lng, lat, h) for h in rings[1:]):
            return True
    return False


def distance_to_boundary_m(lng: float, lat: float, geometry: dict) -> float:
    """Approximate distance (metres) to the nearest boundary edge, local equirectangular projection."""
    kx = 111320.0 * math.cos(math.radians(lat))
    ky = 110540.0
    best = math.inf
    for rings in _polygons(geometry):
        for ring in rings:
            for (x1, y1), (x2, y2) in zip(ring, ring[1:]):
                ax, ay = (x1 - lng) * kx, (y1 - lat) * ky
                bx, by = (x2 - lng) * kx, (y2 - lat) * ky
                dx, dy = bx - ax, by - ay
                len2 = dx * dx + dy * dy
                t = max(0.0, min(1.0, -(ax * dx + ay * dy) / len2)) if len2 else 0.0
                best = min(best, math.hypot(ax + t * dx, ay + t * dy))
    return best


@lru_cache(maxsize=4)
def load_boundaries(path: str = DEFAULT_GEOJSON) -> Tuple[tuple, dict]:
    with open(path, "rb") as f:
        raw = f.read()
    data = json.loads(raw.decode("utf-8"))
    features = tuple(
        (f.get("properties", {}).get("name"), f.get("geometry"))
        for f in data.get("features", [])
    )
    meta = {
        "file": os.path.basename(path),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "features": len(features),
        "provenance": "unverified (source and date of the boundary data are not documented)",
    }
    return features, meta


def assess_point(
    latitude: Optional[float],
    longitude: Optional[float],
    path: str = DEFAULT_GEOJSON,
    near_boundary_m: float = NEAR_BOUNDARY_METERS,
) -> JurisdictionAssessment:
    if latitude is None or longitude is None or not all(math.isfinite(v) for v in (latitude, longitude)):
        return JurisdictionAssessment(status="no_location", message=JURISDICTION_CONFIRMATION_MESSAGE)
    try:
        features, meta = load_boundaries(path)
    except (OSError, ValueError) as exc:
        return JurisdictionAssessment(
            status="data_unavailable", message=JURISDICTION_CONFIRMATION_MESSAGE,
            boundary_data={"error": type(exc).__name__},
        )
    hits = [(name, geom) for name, geom in features if point_in_geometry(longitude, latitude, geom)]
    if not hits:
        return JurisdictionAssessment(status="outside_all", message=JURISDICTION_CONFIRMATION_MESSAGE, boundary_data=meta)
    if len(hits) > 1:
        return JurisdictionAssessment(status="multiple", message=JURISDICTION_CONFIRMATION_MESSAGE, boundary_data=meta)
    name, geom = hits[0]
    dist = round(distance_to_boundary_m(longitude, latitude, geom), 1)
    if dist < near_boundary_m:
        return JurisdictionAssessment(
            status="near_boundary", distance_to_boundary_m=dist,
            message=JURISDICTION_CONFIRMATION_MESSAGE, boundary_data=meta,
        )
    return JurisdictionAssessment(
        status="inside", station=name, distance_to_boundary_m=dist,
        message="Map-based estimate from boundary data whose source is unverified; police to confirm.",
        boundary_data=meta,
    )
