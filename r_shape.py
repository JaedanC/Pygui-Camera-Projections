import numpy as np


def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))

def clamp_np(n: np.ndarray, smallest: np.ndarray, largest: np.ndarray):
    return np.array([clamp(n[i], smallest[i], largest[i]) for i in range(len(n))])


class Shape2D:
    """
    All a shape requires to be defined are a position, and the points (relative
    to that position that make up the shape. This should be in game coordinates).
    You can do some maths to translate this into the respective shape.
    """
    def __init__(self, position_2: np.ndarray, shape_points_2: np.ndarray):
        self._position_2 = np.array([position_2[0], position_2[1], 1])
        self._shape_points_2 = shape_points_2
    
    def get_position(self):
        """Returns a shallow copy of the position"""
        return np.array([self._position_2[0], self._position_2[1]])

    def set_position(self, position_2: np.ndarray):
        self._position_2 = np.array([position_2[0], position_2[1], 1])

    def convert_to_screen_coordinates(self, camera_matrix_3_3: np.ndarray):
        """
        This applies the correct order of matrix multiplications to return the
        points projected to the camera/screen. i.e. The camera is fake. The
        world moves!
        """
        new_points = []

        shape_t_matrix = np.array([
            [1, 0, self._position_2[0]],
            [0, 1, self._position_2[1]],
            [0, 0, 1]
        ])

        for x, y in self._shape_points_2:
            # Homogenous point
            point = np.array([x, y, 1])
            # Matrix multiplication order matters
            transformed = camera_matrix_3_3 @ shape_t_matrix @ point
            new_points.append(transformed[:2])

        return np.array(new_points)


class Rect2D(Shape2D):
    def __init__(self, position_2: np.ndarray, size_2: np.ndarray):
        super().__init__(position_2, np.array([
            [0,         0        ],
            [0,         size_2[1]],
            [size_2[0], size_2[1]],
            [size_2[0], 0        ],
        ]))


class Circle2D(Shape2D):
    def __init__(self, position_2: np.ndarray, radius: float):
        super().__init__(position_2, np.array([
            [0, 0],
        ]))
        self._radius = radius
    
    def get_radius(self):
        return self._radius

    def get_screen_radius(self, camera_scale: float):
        return self._radius * camera_scale

    def set_radius(self, radius: float):
        self._radius = radius
    

class Camera2D:
    def __init__(self, position_2: np.ndarray, scale: float):
        self._position_2 = position_2
        self._scale = scale
    
    def get_scale(self):
        """Returns a shallow copy of the position"""
        return self._scale

    def set_scale(self, scale: float):
        self._scale = scale

    def get_position(self):
        """Returns a shallow copy of the position"""
        return self._position_2.copy()

    def set_position(self, position_2: np.ndarray):
        self._position_2 = position_2

    def update_matrices(self, screen_size_2: np.ndarray):
        self._scale = clamp(self._scale, 0.05, 200)
        self._scale_matrix_3_3 = np.array([
            [self._scale, 0,          0],
            [0,          self._scale, 0],
            [0,          0,          1]
        ])
        # Moving the camera left, is effectively moving everything right. Hence
        # this matrix is inverted.
        self._camera_translation_3_3 = np.array([
            [1, 0, -self._position_2[0]],
            [0, 1, -self._position_2[1]],
            [0, 0, 1]
        ])
        # The center matrix ensures zooming is applied from the center of the
        # camera, rather than from (0, 0). It also centres the Camera on (0, 0)
        self._center_matrix_3_3 = np.array([
            [1, 0, screen_size_2[0] / 2],
            [0, 1, screen_size_2[1] / 2],
            [0, 0, 1]
        ])

    def get_camera_matrix_3_3(self):
        """
        Returns the matrix to convert a coordinate from game coords to
        camera/draw coords.
        """
        return self._center_matrix_3_3 @ self._scale_matrix_3_3 @ self._camera_translation_3_3
    
    def convert_screen_to_world_coord(self, screen_2: np.ndarray):
        return (np.linalg.inv(
            self._center_matrix_3_3 @ self._scale_matrix_3_3 @ self._camera_translation_3_3
        ) @ np.array([screen_2[0], screen_2[1], 1]))[:2]


class Shape3D:
    """
    A shape is a 3D object that contains a position
    """
    def __init__(self, world_position_3: np.ndarray):
        self._world_position_3 = world_position_3


class Polygon3D:
    """
    A polygon is a set of triangles that make up a shape.
    """
    def __init__(self, position_3: np.ndarray, shape_local_coords_3_n: np.ndarray):
        self._position_4 = np.array([position_3[0], position_3[1], position_3[2], 1])
        self._shape_local_coords_3_n = shape_local_coords_3_n

    @staticmethod
    def group_into_triangles(points_3_n: np.ndarray):
        """Returns the list of points as a 3 x n list of triangles"""
        return np.array([np.array(
            [points_3_n[i], points_3_n[i+1], points_3_n[i+2]]) for i in range(0, len(points_3_n), 3)]
        )
    
    @staticmethod
    def convert_world_coord_to_screen_coord(world_coord_3: np.ndarray, camera_matrix_4_4: np.ndarray):
        """Returns the list of points as a 3 x n list of triangles"""
        point = np.array([world_coord_3[0], world_coord_3[1], world_coord_3[2], 1])
        # Perspective shifting
        transformed = camera_matrix_4_4 @ point

        w = transformed[3]
        if abs(w) > 1e-8:
            transformed = transformed[:3] / w
        else:
            transformed = transformed[:3]

        # Homogenous point
        return transformed[:2]

    def get_position(self) -> np.ndarray:
        return np.array(self._position_4[:3])
    
    def get_vtx_world_coords(self) -> np.ndarray:
        return np.array(self._shape_local_coords_3_n) + self.get_position()

    def get_vtx_screen_coords(self, camera_matrix_4_4: np.ndarray, camera_near_plane: float) -> np.ndarray:
        """
        This applies the correct order of matrix multiplications to return the
        points projected to the camera/screen. i.e. The camera is fake. The
        world moves!
        """
        new_points = []

        shape_t_matrix = np.array([
            [1, 0, 0, self._position_4[0]],
            [0, 1, 0, self._position_4[1]],
            [0, 0, 1, self._position_4[2]],
            [0, 0, 0, 1]
        ])

        for x, y, z in self._shape_local_coords_3_n:
            # Homogenous point
            point = np.array([x, y, z, 1])
            # Matrix multiplication order matters
            transformed = camera_matrix_4_4 @ shape_t_matrix @ point

            # Perspective shifting
            w = transformed[3]
            if abs(w) > 1e-8:
                transformed = transformed[:3] / w
            else:
                transformed = transformed[:3]
            
            vertexes_visible = transformed > camera_near_plane
            if all(vertexes_visible):
                new_points.append(transformed)

        return np.array(new_points)


class Triangle3D(Polygon3D):
    def __init__(self, position_3: np.ndarray):
        super().__init__(position_3, np.array([
            [0, 0, 0],
            [0, 50, 0],
            [50, 0, 0]
        ]))


class Line3D(Polygon3D):
    def __init__(self, position_3: np.ndarray, shape_points: np.ndarray):
        super().__init__(position_3, shape_points)


class Cube3D(Polygon3D):
    def __init__(self, position_3: np.ndarray, size: float):
        super().__init__(position_3, np.array([
            [0,    0,    0],
            [0,    size, 0],
            [size, 0,    0],
            [size, 0,    0],
            [0,    size, 0],
            [size, size, 0],

            [0,    0,    size],
            [0,    size, size],
            [size, 0,    size],
            [size, 0,    size],
            [0,    size, size],
            [size, size, size],

            [0,    0,    0],
            [0,    0,    size],
            [size, 0,    0],
            [size, 0,    0],
            [0,    0,    size],
            [size, 0,    size],

            [0,    size, 0],
            [0,    size, size],
            [size, size, 0],
            [size, size, 0],
            [0,    size, size],
            [size, size, size],

            [0,    0,    0],
            [0,    0,    size],
            [0,    size, 0],
            [0,    size, 0],
            [0,    0,    size],
            [0,    size, size],

            [size, 0,    0],
            [size, 0,    size],
            [size, size, 0],
            [size, size, 0],
            [size, 0,    size],
            [size, size, size],
        ]))


class Camera3D:
    @staticmethod
    def perspective_projection(fov_deg: float, aspect: float, near: float, far: float):
        f = 1.0 / np.tan(np.radians(fov_deg) / 2)

        return np.array([
            [f/aspect, 0, 0,                         0],
            [0,        f, 0,                         0],
            [0,        0, (far + near)/(near - far), (2 * far * near)/(near - far)],
            [0,        0, -1,                        0]
        ])

    @staticmethod
    def orthogonal_projection(fov_deg: float, aspect: float, near: float, far: float):
        # TODO
        pass

    def __init__(self, position_3: np.ndarray, fov: float=90, near_plane: float=0.1):
        self._position_3 = position_3
        self._fov_degrees = fov
        self._yaw = np.rad2deg(0)
        self._pitch = np.rad2deg(0)
        self._near_plane = near_plane
    
    def get_position(self):
        """Returns a shallow copy of the position"""
        return self._position_3.copy()
    
    def set_position(self, position_3: np.ndarray):
        self._position_3 = position_3
    
    def get_fov(self):
        return self._fov_degrees

    def set_fov(self, fov_degrees: float):
        self._fov_degrees = fov_degrees

    def get_rotation_degrees(self):
        return np.rad2deg(self._yaw), np.rad2deg(self._pitch)

    def set_rotation_degrees(self, yaw_degrees, pitch_degrees):
        self._yaw = np.deg2rad(yaw_degrees)
        self._pitch = np.deg2rad(pitch_degrees)

    def get_near_plane(self):
        return self._near_plane

    def update_matrices(self, canvas_size_2: np.ndarray):
        self._projection_matrix_4_4 = Camera3D.perspective_projection(
            fov_deg=self._fov_degrees,
            aspect=canvas_size_2[0] / canvas_size_2[1],
            near=self._near_plane,
            far=1000
        )
        # Moving the camera left, is effectively moving everything right. Hence
        # this matrix is inverted.
        translation_matrix = np.array([
            [1, 0, 0, -self._position_3[0]],
            [0, 1, 0, -self._position_3[1]],
            [0, 0, 1, -self._position_3[2]],
            [0, 0, 0, 1],
        ])

        # Add rotation here in the future
        c = np.cos(-self._yaw)
        s = np.sin(-self._yaw)
        yaw = np.array([
            [ c, 0, s, 0],
            [ 0, 1, 0, 0],
            [-s, 0, c, 0],
            [ 0, 0, 0, 1]
        ])
        
        c = np.cos(-self._pitch)
        s = np.sin(-self._pitch)
        pitch = np.array([
            [1, 0, 0, 0],
            [0, c,-s, 0],
            [0, s, c, 0],
            [0, 0, 0, 1]
        ])
        rotation = pitch @ yaw

        self._view_matrix_4_4 = rotation @ translation_matrix

    def get_camera_matrix_4_4(self):
        """
        Returns the matrix to convert a coordinate from game coords to
        camera/draw coords.
        """
        return self._projection_matrix_4_4 @ self._view_matrix_4_4


def main():
    camera = Camera2D(0, 6, 2)
    shape = Shape2D(np.array([10, 5]))
    shape.draw(camera.get_camera_matrix_3_3())


if __name__ == "__main__":
    main()
