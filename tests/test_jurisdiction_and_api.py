"""
Jurisdiction containment (backend) and API endpoint tests.
Synthetic boundaries in a temporary file plus the repository's own boundary data. No network.
main.py is imported with BANDHOO_SKIP_DOTENV=1 so .env is never read, and with Gemini keys blank.
"""

import asyncio
import json
import os

import pytest

from complaint_engine.jurisdiction import JURISDICTION_CONFIRMATION_MESSAGE, assess_point, load_boundaries


def _square(name, x0, y0, size, hole=None):
    ring = [[x0, y0], [x0 + size, y0], [x0 + size, y0 + size], [x0, y0 + size], [x0, y0]]
    coords = [ring] + ([hole] if hole else [])
    return {"type": "Feature", "properties": {"name": name}, "geometry": {"type": "Polygon", "coordinates": coords}}


@pytest.fixture
def synthetic(tmp_path):
    hole = [[72.805, 19.005], [72.807, 19.005], [72.807, 19.007], [72.805, 19.007], [72.805, 19.005]]
    data = {"type": "FeatureCollection", "features": [
        _square("Alpha", 72.80, 19.00, 0.02, hole=hole),
        _square("Beta", 72.82, 19.00, 0.02),
        _square("Overlap1", 72.90, 19.10, 0.02),
        _square("Overlap2", 72.91, 19.11, 0.02),
    ]}
    p = tmp_path / "boundaries.geojson"
    p.write_text(json.dumps(data))
    load_boundaries.cache_clear()
    return str(p)


def test_inside_one_polygon(synthetic):
    r = assess_point(19.012, 72.812, path=synthetic)
    assert (r.status, r.station) == ("inside", "Alpha")
    assert r.distance_to_boundary_m > 100
    assert "unverified" in r.boundary_data["provenance"]


def test_near_shared_boundary_requires_confirmation(synthetic):
    r = assess_point(19.012, 72.8195, path=synthetic)  # about 50 m from the Alpha/Beta edge
    assert r.status == "near_boundary" and r.station is None
    assert r.message == JURISDICTION_CONFIRMATION_MESSAGE


def test_outside_all_polygons_requires_confirmation(synthetic):
    r = assess_point(18.90, 72.70, path=synthetic)
    assert r.status == "outside_all" and r.station is None


def test_point_in_hole_is_outside(synthetic):
    r = assess_point(19.006, 72.806, path=synthetic)
    assert r.status == "outside_all"


def test_overlapping_polygons_are_ambiguous(synthetic):
    r = assess_point(19.115, 72.915, path=synthetic)
    assert r.status == "multiple" and r.station is None


def test_missing_location_and_missing_data(tmp_path):
    assert assess_point(None, None).status == "no_location"
    r = assess_point(19.0, 72.8, path=str(tmp_path / "absent.geojson"))
    assert r.status == "data_unavailable" and r.station is None


def test_real_boundaries_each_polygon_interior_point_maps_to_its_own_polygon():
    load_boundaries.cache_clear()
    features, meta = load_boundaries()
    assert meta["features"] == 91
    from complaint_engine.jurisdiction import point_in_geometry
    for name, geom in features:
        ring = geom["coordinates"][0]
        # deterministic interior point: centroid when it lies inside, otherwise skip (concave shapes)
        a = cx = cy = 0.0
        for (x0, y0), (x1, y1) in zip(ring, ring[1:]):
            c = x0 * y1 - x1 * y0
            a += c; cx += (x0 + x1) * c; cy += (y0 + y1) * c
        a /= 2
        x, y = cx / (6 * a), cy / (6 * a)
        if not point_in_geometry(x, y, geom):
            continue
        r = assess_point(y, x)
        assert r.status in ("inside", "near_boundary")
        assert r.station in (name, None)
        if r.status == "inside":
            assert r.station == name


def test_real_boundaries_point_at_sea_gets_no_station():
    load_boundaries.cache_clear()
    r = assess_point(18.95, 72.70)
    assert r.status == "outside_all" and r.station is None


# ── API (main.py) ──

@pytest.fixture(scope="module")
def main_module():
    os.environ["BANDHOO_SKIP_DOTENV"] = "1"
    os.environ["GEMINI_API_KEY"] = ""
    os.environ["GOOGLE_API_KEY"] = ""
    load_boundaries.cache_clear()
    import main
    return main


def test_get_jurisdiction_endpoint_never_returns_a_nearest_centroid_guess(main_module):
    from main import Location
    out = asyncio.run(main_module.get_jurisdiction(Location(latitude=18.95, longitude=72.70)))
    assert out["station"] is None and out["details"] is None
    assert out["status"] == "outside_all" and out["method"] == "polygon_containment"
    assert out["message"] == JURISDICTION_CONFIRMATION_MESSAGE


def test_get_jurisdiction_endpoint_inside_a_polygon(main_module):
    from main import Location
    features, _ = load_boundaries()
    name, geom = features[0]
    ring = geom["coordinates"][0]
    a = cx = cy = 0.0
    for (x0, y0), (x1, y1) in zip(ring, ring[1:]):
        c = x0 * y1 - x1 * y0
        a += c; cx += (x0 + x1) * c; cy += (y0 + y1) * c
    a /= 2
    x = cx / (6 * a)
    y = cy / (6 * a)
    out = asyncio.run(main_module.get_jurisdiction(Location(latitude=y, longitude=x)))
    assert out["method"] == "polygon_containment"
    assert out["status"] == "inside"
    assert out["station"] == name and out["details"]["name"] == name


def test_structure_endpoint_returns_unverified_draft_record(main_module):
    from complaint_engine.models import ComplaintStructureRequest
    report = asyncio.run(main_module.structure_complaint(ComplaintStructureRequest(
        statement="On 14/10/2026 at 9 pm a man took my bag at Dadar Market.",
        evidence=[{"evidence_type": "photo"}])))
    assert report["submission_status"].startswith("draft_only")
    assert report["persistence"].startswith("none")
    assert report["independently_verified"] == []
    assert report["supporting_evidence_provided"][0]["verification_status"] == "unverified"
    assert report["legal_provisions"].startswith("Not included")


def test_classify_offence_endpoint_still_available(main_module):
    from legal_engine.schemas import NarrativeInput
    out = asyncio.run(main_module.classify_offence(NarrativeInput(narrative="Someone snatched my gold chain on the road and ran away.")))
    assert out.predictions and out.inference_status.startswith("fallback")
