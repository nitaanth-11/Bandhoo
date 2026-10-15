from fastkml import kml
from shapely.geometry import Polygon, MultiPolygon

def load_police_jurisdictions(kml_path):
    with open(kml_path, "rb") as f:
        doc = f.read()

    k = kml.KML()
    k.from_string(doc)

    stations = []

    for document in k.features():
        for folder in document.features():
            for placemark in folder.features():
                name = placemark.name
                geom = placemark.geometry

                polygons = []

                if isinstance(geom, Polygon):
                    polygons.append(geom)

                elif isinstance(geom, MultiPolygon):
                    polygons.extend(list(geom.geoms))

                for poly in polygons:
                    coords = list(poly.exterior.coords)
                    stations.append({
                        "station_name": name,
                        "polygon": Polygon(coords)
                    })

    return stations
