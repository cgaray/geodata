from map import Map
import matplotlib.pyplot as plt


def visualize_map(map_obj):
    """
    :type map_obj: Map
    """
    for way in map_obj.ways:
        xs = []
        ys = []
        for n in way.nodes:
            xs.append(n.lon)
            ys.append(n.lat)
        plt.plot(xs, ys, '-')

    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.show()
