import numpy as np


triangle = np.array(
    [[1, 2, 3],
     [4, 5, 6],
     [7, 8, 9]]
)
triangle_b = np.array(
    [[10, 20, 30],
     [40, 50, 60],
     [70, 80, 90]]
)
polygon = np.array([triangle, triangle_b])

b = polygon + np.array([1, 2, 3])
print(b)

my_view = polygon.copy().ravel()

my_view[1] = 999

print(my_view)
print(polygon)