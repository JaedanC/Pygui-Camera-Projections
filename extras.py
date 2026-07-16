import numpy as np


def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))

def clamp_np(n: np.ndarray, smallest: np.ndarray, largest: np.ndarray):
    return np.array([clamp(n[i], smallest[i], largest[i]) for i in range(len(n))])

def convert_screen_position_2_to_pixel_position_2(screen_position_2: np.ndarray, sandbox_size_2: np.ndarray):
    # (-1,  1) = top-left
    # ( 1,  1) = top-right
    # (-1, -1) = bottom-left
    # ( 1, -1) = bottom-right
    # ( 0,  0) = center
    # return (1 - screen_position_2) * sandbox_size_2 / 2
    x, y = screen_position_2
    return np.array([
        (1 - x) * sandbox_size_2[0] / 2,
        (1 - y) * sandbox_size_2[1] / 2
    ])

def squared_dist(a_3: np.ndarray, b_3: np.ndarray):
    return sum((ac - bc) ** 2.0 for ac, bc in zip(a_3, b_3))


def average_points_3_3(points_3_3: np.ndarray):
    a_3, b_3, c_3 = points_3_3
    return np.array([
        (a_3[0] + b_3[0] + c_3[0]) / 3,
        (a_3[1] + b_3[1] + c_3[1]) / 3,
        (a_3[2] + b_3[2] + c_3[2]) / 3,
    ])


def distance_between_triangle_world_position_3_3_to_world_position_3(
        triangle_world_position_3_3: np.ndarray,
        world_position_3: np.ndarray
    ):
    triangle_average_world_position_3 = average_points_3_3(triangle_world_position_3_3)
    squared_distance = squared_dist(triangle_average_world_position_3, world_position_3)
    return squared_distance

def sort_triangles_by_distance_to_camera(
        triangle_screen_coords_3_3_n: np.ndarray,
        triangle_world_coords_3_3_n: np.ndarray,
        camera_world_coords_3: np.ndarray
    ):
    combined = [(sc_3, wc_3) for sc_3, wc_3 in zip(triangle_screen_coords_3_3_n, triangle_world_coords_3_3_n)]
    combined.sort(key=lambda x: -distance_between_triangle_world_position_3_3_to_world_position_3(x[1], camera_world_coords_3))
    return combined
