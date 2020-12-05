import math
import numpy as np
from osm.models import Coordinate, Image, Line
from typing import List, Tuple

PointPair = Tuple[Coordinate, Coordinate]


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


def highlight_path(img: Image, path: List[Coordinate], width: float) -> Image:
    pixel_coords = img.get_pixel_coords()
    highlight_mask = Image(
        data=np.zeros((img.height, img.width, img.channels)),
        bounds=img.bounds,
    )

    # For each path segment
    for point_pair in _gen_path_pairs(path):
        highlight_line_segment(
            mask=highlight_mask,
            point_pair=point_pair,
            width=width,
            pixel_coords=pixel_coords
        )

    return highlight_mask


def highlight_line_segment(mask: Image, point_pair: PointPair, width: float, pixel_coords: List[List[Coordinate]]) -> None:
    p1, p2 = point_pair
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
                mask.data[y][x] = (255, 0, 0, 255)


dist_thresh = 50
target = np.array([108, 116, 129])


def _calc_pixel_dist(p: np.array) -> float:
    offset = np.abs(target - p)
    return float(np.sqrt(np.dot(offset, np.transpose(offset))))


from osm.visualizer import visualize_map
from osm.map import Map

def calculate_road_width(img: Image, point_pair: PointPair, threshold: float, max_width: float, pixel_coords: List[List[Coordinate]]) -> float:
    prev_width = 0
    for frac in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]:
        width = max_width * frac
        mask = Image(
            data=np.zeros((img.height, img.width, img.channels)),
            bounds=img.bounds,
        )
        highlight_line_segment(mask, point_pair, width, pixel_coords)
        road_pixel_count = 0
        mask_pixel_count = 0
        for i, mask_row in enumerate(mask.data):
            for j, mask_pixel in enumerate(mask_row):
                # Check red channel (TODO: Something better than this)
                if mask_pixel[0] > 0:
                    mask_pixel_count += 1
                    # This pixel is part of the mask. See if it's "road colored"
                    d = _calc_pixel_dist(img.data[i][j][:3])
                    # print(d)
                    if d < threshold:
                        road_pixel_count += 1
        m = Map(img.bounds)
        m.add_object(img)
        m.add_object(mask)
        visualize_map(m, f'Width: {width}')
        if mask_pixel_count == 0:
            continue
        if road_pixel_count / mask_pixel_count > 0.8:
            prev_width = width
        else:
            # This width was too much, so return the last width within the color threshold
            return prev_width
