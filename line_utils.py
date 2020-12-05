import math
from osm.models import Coordinate, Image, Line
from typing import List


def _gen_path_pairs(path: List[Coordinate]) -> (Coordinate, Coordinate):
    for i in range(0, len(path)-1):
        yield path[i], path[i+1]


def _calc_slope(p1: Coordinate, p2: Coordinate) -> float:
    return (p2.lat - p1.lat) / (p2.lon - p1.lon)


def _pixel_within_lines(p: Coordinate, lines: List[Line]) -> bool:
    lines_ordered = _order_lines(lines)
    # Check the first line
    if p.lat > lines_ordered[0].m * p.lon + lines_ordered[0].b:
        return False
    if p.lat < lines_ordered[1].m * p.lon + lines_ordered[1].b:
        return False
    # Inverse
    if p.lat > lines_ordered[2].m * p.lon + lines_ordered[2].b:
        return False
    if p.lat < lines_ordered[3].m * p.lon + lines_ordered[3].b:
        return False
    return True


def _order_lines(lines: List[Line]) -> List[Line]:
    """ Orders lines by their slope and intercept """
    # TODO: Handle lines with 0 and infinite slopes
    pos_m = []
    neg_m = []
    # Group lines by slope
    for line in lines:
        if line.m > 0:
            pos_m.append(line)
        else:
            neg_m.append(line)
    # Order lines by intercept
    pos_m.sort(key=lambda line: line.b, reverse=True)
    neg_m.sort(key=lambda line: line.b, reverse=True)
    # [Pos slope top, pos slope bottom, neg slope top, neg slope bottom]
    return pos_m + neg_m


def highlight_path(img: Image, path: List[Coordinate], width: float) -> None:
    pixel_coords = img.get_pixel_coords()

    # For each path segment
    for p1, p2 in _gen_path_pairs(path):
        # Calculate the slope
        m = _calc_slope(p1, p2)
        # Calculate the intercept
        b = p1.lat - m * p1.lon
        # Calculate the intercepts for the bounding lines
        inv_slope = -1 / m
        # delta_b = width * math.cos(inv_slope)
        delta_b = width / math.cos(math.atan(-m))
        b_top = b + delta_b
        b_bottom = b - delta_b

        b_perpendicular_p1 = p1.lat - inv_slope * p1.lon
        b_perpendicular_p2 = p2.lat - inv_slope * p2.lon
        lines = [
            Line(m, b_top),
            Line(m, b_bottom),
            Line(inv_slope, b_perpendicular_p1),
            Line(inv_slope, b_perpendicular_p2),
        ]

        # Highlight the pixels
        for y, row in enumerate(pixel_coords):
            for x, pixel in enumerate(row):
                if _pixel_within_lines(pixel, lines):
                    img.data[y][x] = (255, 0, 0, 255)
