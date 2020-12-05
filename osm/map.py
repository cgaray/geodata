from typing import List
from .models import BoundingBox, Image

from .api.response_parser import Way


class Map:

    def __init__(self, bbox: BoundingBox = None):
        self.bounding_box = bbox
        self.ways: List[Way] =[]
        self.images: List[Image] = []

    def add_object(self, obj):
        if type(obj) is Way:
            self.ways.append(obj)
        elif type(obj) is Image:
            self.images.append(obj)
        else:
            raise NotImplementedError(f'Adding the type {type(obj)} is not yet supported.')
