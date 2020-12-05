from skimage import io
from pathlib import Path
import numpy as np
from typing import List


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

    def __eq__(self, other):
        return self.lat == other.lat and self.lon == other.lon


class Image:

    def __init__(self, data: np.ndarray, bounds: BoundingBox, file_path: Path):
        self.data = data
        self.bounds = bounds
        self.file_path = file_path
        self.width = len(self.data[0])
        self.height = len(self.data)

    @staticmethod
    def load_from_disk(file_path: Path, bounding_box: BoundingBox):
        data = io.imread(str(file_path))
        return Image(data, bounding_box, file_path)

    def get_pixel_coords(self) -> List[List[Coordinate]]:
        """
        Calculates a matrix of lat-lon coordinate pairs for every pixel in the image.
        :return: a matrix of Coordinates where the first index corresponds to y and
        the second index corresponds to x (origin at top left).
        """
        lat_range = self.bounds.max_lat - self.bounds.min_lat
        lng_range = self.bounds.max_lon - self.bounds.min_lon
        pixel_width = lng_range / self.width
        pixel_height = lat_range / self.height
        res = []
        for y in range(self.height):
            res.append([])
            for x in range(self.width):
                res[y].append(Coordinate(
                    lat=((self.height - y) + 0.5) * pixel_height + self.bounds.min_lat,
                    lon=(x + 0.5) * pixel_width + self.bounds.min_lon
                ))
        return res


class Line:
    def __init__(self, m: float, b: float):
        """
        Creates a new line.
        :param m: the slope
        :param b: the y-intercept
        """
        self.m = m
        self.b = b
