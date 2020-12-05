import unittest
import numpy as np

from osm.models import BoundingBox, Coordinate, Image


class TestImageMethods(unittest.TestCase):

    def test_get_pixel_coords(self):
        data = np.zeros((10, 10))

        # Simple 0,0 to 100,100
        img = Image(
            data=data,
            bounds=BoundingBox(0, 0, 100, 100),
        )
        self.assertEqual(img.get_pixel_coords()[0][0], Coordinate(5, 5))

        # 0,500 to 100,600
        img = Image(
            data=data,
            bounds=BoundingBox(0, 500, 100, 600),
        )
        self.assertEqual(img.get_pixel_coords()[8][4], Coordinate(85.0, 545.0))


## TODO: Check multiple points


if __name__ == '__main__':
    unittest.main()
