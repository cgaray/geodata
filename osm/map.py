from typing import List
from .models import BoundingBox, Image

from .api.response_parser import Way


ImageList = List[Image]
WayList = List[Way]

class Map:

    def __init__(self, bbox: BoundingBox = None):
        self.bounding_box = bbox
        self.ways = self.__new_way_list()
        self.images = self.__new_image_list()

    @staticmethod
    def __new_way_list() -> WayList:
        return []

    @staticmethod
    def __new_image_list() -> ImageList:
        return []

    def add_object(self, obj):
        if type(obj) is Way:
            self.ways.append(obj)
        elif type(obj) is Image:
            self.images.append(obj)
        else:
            raise NotImplementedError(f'Adding the type {type(obj)} is not yet supported.')
