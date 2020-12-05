from .map import Map
import matplotlib.pyplot as plt


def visualize_map(map_obj, title: str = None):
    for img in map_obj.images:
        extent = (
            img.bounds.min_lon,
            img.bounds.max_lon,
            img.bounds.min_lat,
            img.bounds.max_lat,
        )
        plt.imshow(img.data, extent=extent)

    for way in map_obj.ways:
        xs = []
        ys = []
        for n in way.nodes:
            xs.append(n.lon)
            ys.append(n.lat)
        plt.plot(xs, ys, '-')

    if title:
        plt.title(title)
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')

    if map_obj.bounding_box is not None:
        plt.xlim(map_obj.bounding_box.min_lon, map_obj.bounding_box.max_lon)
        plt.ylim(map_obj.bounding_box.min_lat, map_obj.bounding_box.max_lat)
    plt.show()
