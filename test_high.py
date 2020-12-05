from osm.gmaps.gmaps import Coordinate, GoogleMapsImageCache
from osm.map import Map, BoundingBox
from osm.api.osm import QueryBuilder, bounding_box_to_query_str
from osm.visualizer import visualize_map
from line_utils import highlight_path

bbox = {
    'minLat': 42.403,
    'minLon': -71.079,
    'maxLat': 42.428,
    'maxLon': -71.045,
}

center = Coordinate(42.414757, -71.064076)
img_cache = GoogleMapsImageCache('osm/gmaps/cache')
image = img_cache.get_img(center, zoom=18)

query = QueryBuilder()
query.add_component('nwr[name="Main Street"]({{bbox}});')
query.add_component('out geom;')
res = query.execute(bbox=bounding_box_to_query_str(image.bounds))

# Highlight the road paths
for way in res:
    # Updates `image`
    highlight_path(image, way.nodes, 0.0001)

# m = Map(bbox=BoundingBox(bbox['minLat'], bbox['minLon'], bbox['maxLat'], bbox['maxLon']))
m = Map(bbox=image.bounds)
m.add_object(image)
# for r in res:
#     m.add_object(r)
visualize_map(m)
