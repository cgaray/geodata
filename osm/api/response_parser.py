from xml.etree import ElementTree


def parse_api_response(xml):
    """
    :type xml: str
    """
    root = ElementTree.fromstring(xml)
    results = []
    for child in root:
        if child.tag == 'way':
            results.append(Way.from_xml(child))
    return results


class Node:
    def __init__(self, ref, lat, lon):
        self.ref = ref
        self.lat = lat
        self.lon = lon

    @staticmethod
    def from_xml(node_node):
        attrs = node_node.attrib
        return Node(attrs['ref'], attrs['lat'], attrs['lon'])

    def __str__(self):
        return f'Node {self.ref}: ({self.lat},{self.lon}'


class BoundingBox:
    def __init__(self, min_lat, min_lon, max_lat, max_lon):
        """
        Represents a bounding box based on min and max latitude and longitude values.
        :type min_lat: float
        :type min_lon: float
        :type max_lat: float
        :type max_lon: float
        """
        self.min_lat = min_lat
        self.min_lon = min_lon
        self.max_lat = max_lat
        self.max_lon = max_lon

    @staticmethod
    def from_xml(xml_node):
        """
        :type xml_node: ElementTree.Element
        """
        attrs = xml_node.attrib
        return BoundingBox(attrs['minlat'], attrs['minlon'], attrs['maxlat'], attrs['maxlon'])


class Tag:
    def __init__(self, key, value):
        """
        :type key: str
        :type value: str
        """
        self.key = key
        self.value = value

    @staticmethod
    def from_xml(xml_node):
        """
        :type xml_node: ElementTree.Element
        """
        attrs = xml_node.attrib
        return Tag(attrs['k'], attrs['v'])


class Way:
    def __init__(self, way_id, bounds, nodes, tags):
        """
        An OSM Way
        :type way_id: int
        :type bounds: BoundingBox
        :type nodes: list of Node
        :type tags: list of Tag
        """
        self.id = way_id
        self.bounds = bounds
        self.nodes = nodes
        self.tags = tags

    @staticmethod
    def from_xml(way_node):
        """
        :type way_node: ElementTree.Element
        """
        way_id = way_node.attrib.get('id')
        bounds = None
        nodes = []
        tags = []
        for child in way_node:
            if child.tag == 'bounds':
                bounds = BoundingBox.from_xml(child)
            elif child.tag == 'nd':
                nodes.append(Node.from_xml(child))
            elif child.tag == 'tag':
                tags.append(Tag.from_xml(child))
        return Way(way_id, bounds, nodes, tags)

    def __str__(self):
        return f"Way {self.id}:\n" \
               f"\t{len(self.nodes)} nodes\n" \
               f"\t{len(self.tags)} tags"

