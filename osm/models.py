from skimage import io
from pathlib import Path
import numpy as np


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

    def __str__(self):
        return f'{self.min_lat},{self.min_lon},{self.max_lat},{self.max_lon}'


class Coordinate:

    def __init__(self, lat, lon):
        """
        Creates a new Coordinate representing a latitude-longitude pair.
        :type lat: float
        :type lon: float
        """
        self.lat = lat
        self.lon = lon

    def __str__(self):
        return f'{self.lat},{self.lon}'


class Image:

    def __init__(self, data: np.ndarray, bounds: BoundingBox, file_path: Path):
        self.data = data
        self.bounds = bounds
        self.file_path = file_path

    @staticmethod
    def load_from_disk(file_path: Path, bounding_box: BoundingBox):
        data = io.imread(str(file_path))
        return Image(data, bounding_box, file_path)
