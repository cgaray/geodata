import requests

from .response_parser import parse_api_response

_API_BASE = 'https://overpass-api.de/api/interpreter'

# nwr[name="Main+Street"](42.34738030389109,-71.09038352966309,42.44524802967223,-71.01253509521483);out+geom;

bounding_box = {
    'minLat': 42.34738030389109,
    'minLon': -71.09038352966309,
    'maxLat': 42.44524802967223,
    'maxLon': -71.01253509521483,
}


def bounding_box_to_query_str(bb):
    return f"{bb['minLat']},{bb['minLon']},{bb['maxLat']},{bb['maxLon']}"


def InvalidHTTPResponse(Exception):
    pass


class QueryBuilder:
    def __init__(self):
        self._components = []

    def add_component(self, component):
        self._components.append(component)

    @staticmethod
    def __replace_placeholders(text, placeholder_lookup_table):
        """
        Replaces all instances of "{{placeholder_key}}" with the corresponding value in the table.
        :param text: the text to find and replace on
        :type text: str
        :param placeholder_lookup_table: a lookup table to use when replacing placeholders
        :type placeholder_lookup_table: dict of str: str
        :return: the text with all the "{{placeholder_key}}" replaced with "placeholder_value"
        """
        resulting_text = text
        for placeholder_name, value_to_use in placeholder_lookup_table.items():
            resulting_text = resulting_text.replace(f'{{{{{placeholder_name}}}}}', value_to_use)
        return resulting_text

    def execute(self, **kwargs):
        placeholder_lookup_table = {k: str(v) for k, v in kwargs.items()}
        query_str = '\n'.join(map(lambda c: self.__replace_placeholders(c, placeholder_lookup_table), self._components))
        response = requests.post(_API_BASE, data=query_str)
        if response.status_code != 200:
            raise InvalidHTTPResponse(response.text)
        return parse_api_response(response.text)


if __name__ == '__main__':
    query = QueryBuilder()
    query.add_component('nwr[name="Main Street"]({{bbox}});')
    query.add_component('out geom;')
    res = query.execute(bbox=bounding_box)
    for r in res:
        print(r)
