from dotenv import load_dotenv
from osm.models import Coordinate, Image, BoundingBox
from pathlib import Path
import requests
import shutil
import os
import math

load_dotenv()


class GoogleMapsImageCache:
    _API_KEY_ENVIRON_VAR_NAME = 'GOOGLE_API_KEY'
    _API_URL = 'https://maps.googleapis.com/maps/api/staticmap?key='

    def __init__(self, cache_dir='cache'):
        # Get the Google Maps API key from the environment variables
        api_key = os.environ.get(self._API_KEY_ENVIRON_VAR_NAME)
        if api_key is None:
            raise EnvironmentError(f'Could not get the environment variable {self._API_KEY_ENVIRON_VAR_NAME}')
        self._API_URL += api_key

        # Ensure the cache directory is set up properly
        self.cache_dir = Path(cache_dir)
        if self.cache_dir.exists() and not self.cache_dir.is_dir():
            raise IOError(f'{cache_dir} exists but is not a directory')
        if not self.cache_dir.exists():
            # This will raise an error if it fails. We'll just let that bubble up.
            self.cache_dir.mkdir(parents=True)
        # Cache dir should exist now, but let's make sure we have write access
        if not os.access(cache_dir, os.W_OK):
            raise IOError(f'It does not appear that {cache_dir} is writable')
        # We should be good to go

    def get_img(self, center: Coordinate, zoom: int = 21, width: int = 640, height: int = 640, map_type: str = 'satellite') -> Image:
        """
        Downloads an image to the cache (if necessary) and returns a path to the downloaded image.

        :param center: the center of the image
        :param zoom: the zoom level
        :param width: the width of the image to fetch
        :param height: the height of the image to fetch
        :param map_type: 'satellite' | 'roadmap' | 'hybrid' | 'terrain'
        :return: file path to the image on disk
        """
        data_dir = self.cache_dir / map_type / str(zoom)
        if not data_dir.exists():
            data_dir.mkdir(parents=True)

        file_path = data_dir / f'{center}.png'
        if not file_path.exists():
            img_url = f'{self._API_URL}&center={center}&zoom={zoom}&size={width}x{height}&maptype={map_type}'
            self._download_img(file_path, img_url)

        bounding_box = calculateBbox(center, zoom, width, height)
        return Image.load_from_disk(file_path, bounding_box)

    @staticmethod
    def _download_img(file_path: Path, img_url: str) -> None:
        """
        Download an image to the given folder.

        :param file_path: the file path to save the image to
        :param img_url: the full URL of the image
        """
        # Open the url image, set stream to True, this will return the stream content.
        response = requests.get(img_url, stream=True)

        # Check if the image was retrieved successfully
        if response.status_code != 200:
            raise IOError(f'Could not download image {img_url} to {file_path}')

        # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
        response.raw.decode_content = True

        # Open a local file with wb ( write binary ) permission.
        with open(str(file_path), 'wb') as f:
            shutil.copyfileobj(response.raw, f)


# The code below calculates the bounding box for a given Google Maps image.
# Code from https://stackoverflow.com/questions/44784839/calculate-bounding-box-of-static-google-maps-image
_C = { 'x': 128, 'y': 128 }
_J = 256 / 360
_L = 256 / (2 * math.pi)

def tb(a):
    return 180 * a / math.pi

def sb(a):
    return a * math.pi / 180

def bounds(a, b, c):
    if b is not None:
        a = max(a, b)
    if c is not None:
        a = min(a, c)
    return a

def latlonToPt(lat: float, lon: float):
    a = bounds(math.sin(sb(lat)), -(1 - 1E-15), 1 - 1E-15)
    return {
        'x': _C['x'] + lon * _J,
        'y': _C['y'] + 0.5 * math.log((1 + a) / (1 - a)) * - _L
    }

def ptToLatlon(pt):
    return [tb(2 * math.atan(math.exp((pt['y'] - _C['y']) / -_L)) - math.pi / 2), (pt['x'] - _C['x']) / _J]


def calculateBbox(center: Coordinate, zoom, sizeX, sizeY) -> BoundingBox:
    cp = latlonToPt(center.lat, center.lon)
    pixelSize = math.pow(2, -(zoom+1))
    pwX = sizeX*pixelSize
    pwY = sizeY*pixelSize

    ne = ptToLatlon({'x': cp['x'] + pwX, 'y': cp['y'] - pwY})
    sw = ptToLatlon({'x': cp['x'] - pwX, 'y': cp['y'] + pwY})

    return BoundingBox(sw[0], sw[1], ne[0], ne[1])


if __name__ == '__main__':
    cache = GoogleMapsImageCache()
    center = Coordinate(42.414757, -71.064076)
    print(cache.get_img(center, zoom=18))
