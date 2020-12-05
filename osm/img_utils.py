from osm.models import Image
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np


image = Image.load_from_disk(Path('gmaps/cache/satellite/18/42.414757,-71.064076.png'), bounding_box=None)


data = np.zeros(image.data.shape)

dist_thresh = 50
target = np.array([108, 116, 129])


def calc_dist(p: np.array) -> float:
    offset = np.abs(target - p)
    return np.sqrt(np.dot(offset, np.transpose(offset)))


for i in range(image.height):
    for j in range(image.width):
        d = calc_dist(image.data[i][j][:3])
        if d < dist_thresh:
            data[i][j] = (255, 0, 0, 255)

plt.imshow(image.data)
plt.imshow(data)
plt.show()
