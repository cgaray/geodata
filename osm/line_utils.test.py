import unittest
from line_utils import _calc_slope, _pixel_within_lines

from osm.models import Coordinate, Line


class TestLineUtils(unittest.TestCase):

    def test__calc_slope(self):
        p1 = Coordinate(
            lon=0,
            lat=0,
        )
        p2 = Coordinate(
            lon=6,
            lat=3,
        )
        self.assertEqual(_calc_slope(p1, p2), 0.5)

    # TODO: Handle lines with slope of zero and infinity
    def test__pixel_within_lines(self):
        # Point at (1,1)
        p = Coordinate(
            lat=1,
            lon=1,
        )
        # Simple rotated square with vertices at (1,1), (0,1), (2,1), (1, 2)
        lines = [
            Line(m=1, b=1),
            Line(m=1, b=-1),
            Line(m=-1, b=1),
            Line(m=-1, b=3),
        ]
        self.assertEqual(_pixel_within_lines(p, lines), True)


if __name__ == '__main__':
    unittest.main()
