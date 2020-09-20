from typing import List

from api.response_parser import Tag, Way


WayList = List[Way]

class Map:

    def __init__(self):
        self.ways = self.__new_way_list()

    @staticmethod
    def __new_way_list() -> WayList:
        return []

    def add_object(self, obj):
        if type(obj) is Way:
            self.ways.append(obj)
        else:
            raise NotImplementedError(f'Adding the type {type(obj)} is not yet supported.')
