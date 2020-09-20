from map import Map
from api.osm import QueryBuilder, bounding_box_to_query_str
from api.response_parser import parse_api_response
from visualizer import visualize_map


bounding_box = bounding_box_to_query_str({
    'minLat': 42.34738030389109,
    'minLon': -71.09038352966309,
    'maxLat': 42.44524802967223,
    'maxLon': -71.01253509521483,
})


query = QueryBuilder()
query.add_component('nwr[name="Main Street"]({{bbox}});')
query.add_component('out geom;')
res = query.execute(bbox=bounding_box)

m = Map()
for r in res:
    m.add_object(r)
visualize_map(m)
