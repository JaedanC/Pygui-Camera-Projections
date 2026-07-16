import numpy as np
from extras import clamp


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
        self._yaw = np.deg2rad(0)
        self._pitch = np.deg2rad(0)
        self._near_plane = near_plane
    
    def get_position_3(self):
        """Returns a shallow copy of the position"""
        return self._position_3.copy()
    
    def set_position_3(self, position_3: np.ndarray):
        self._position_3 = position_3
    
    def walk(self, amount_3):
        """Moves the camera using standard WASD controls.
            amount_2[0] = forward movement 
            amount_2[1] = right strafe movement 
            amount_3[2] = up movement 
        """
        x, y, z = self.get_position_3()
        x += amount_3[0] * np.sin(self._yaw) + amount_3[1] * np.sin(self._yaw + np.pi / 2)
        y += amount_3[2]
        z += amount_3[0] * np.cos(self._yaw) + amount_3[1] * np.cos(self._yaw + np.pi / 2)
        self.set_position_3(np.array([x, y, z]))

    def get_fov(self):
        return self._fov_degrees

    def set_fov(self, fov_degrees: float):
        self._fov_degrees = clamp(fov_degrees, 1, 360)

    def get_rotation_degrees(self):
        return np.rad2deg(self._yaw), np.rad2deg(self._pitch)

    def set_rotation_degrees(self, yaw_degrees, pitch_degrees):
        pitch_degrees = clamp(pitch_degrees, -90, 90)
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
        self._camera_matrix_4_4 = self._projection_matrix_4_4 @ self._view_matrix_4_4

    def get_camera_matrix_4_4(self):
        """
        Returns the matrix to convert a coordinate from game coords to
        camera/draw coords.
        """
        return self._camera_matrix_4_4


class Shape3D:
    """
    A shape is a 3D object that contains a position and some vertices. How the
    vertices are arranged and used is up to the implementation of a subclass.

    Vertices should be assumed to be around (0, 0). i.e. the Mesh needs to have
    a pivot point.
    """
    def __init__(self, world_position_3: np.ndarray, vertexes_n_n: np.ndarray):
        assert world_position_3.shape[0] == 3
        self._world_position_3 = world_position_3
        self._vertexes_n_n = vertexes_n_n
    
    @staticmethod
    def convert_world_position_to_screen_position(world_position_3: np.ndarray, camera: Camera3D):
        """Returns the list of points as a 3 x n list of triangles"""
        assert isinstance(camera, Camera3D)

        homogenous_world_position = np.array(
            [world_position_3[0], world_position_3[1], world_position_3[2], 1]
        )
        
        homogenous_screen_position_no_projection = camera.get_camera_matrix_4_4() @ homogenous_world_position

        # w is the projection depth.
        # All components should be divided by w
        w = homogenous_screen_position_no_projection[3]
        if abs(w) > 1e-8:
            homogenous_screen_position = homogenous_screen_position_no_projection[:3] / w
        else:
            homogenous_screen_position = homogenous_screen_position_no_projection[:3]

        return homogenous_screen_position[:2]
    
    def get_position_3(self) -> np.ndarray:
        return self._world_position_3
    
    def get_vertex_local_position_n_n(self) -> np.ndarray:
        """Returns the of the shape relative to the shape origin"""
        return self._vertexes_n_n

    def get_vertex_world_position_n_n(self) -> np.ndarray:
        """Returns the world position of the vertexes"""
        return self._vertexes_n_n + self._world_position_3

    def get_vertex_screen_positions_n_n(self, camera: Camera3D) -> np.ndarray:
        """
        This applies the correct order of matrix multiplications to return the
        points projected to the screen. i.e. The camera is fake. The world
        moves.

        The returned array is the same shape as the vertexes array for this
        subclass.
        """
        assert isinstance(camera, Camera3D)
        shape_t_matrix = np.array([
            [1, 0, 0, self._world_position_3[0]],
            [0, 1, 0, self._world_position_3[1]],
            [0, 0, 1, self._world_position_3[2]],
            [0, 0, 0, 1]
        ])

        old_shape = self._vertexes_n_n.shape

        vertexes = []
        for local_vertex_3 in self._vertexes_n_n.reshape(-1, 3):
            local_vertex_3: np.ndarray
            x, y, z = local_vertex_3
            point = np.array([x, y, z, 1])

            # Matrix multiplication order matters
            vertex_screen_position_no_projection = camera.get_camera_matrix_4_4() @ shape_t_matrix @ point

            # Perspective shifting
            w = vertex_screen_position_no_projection[3]
            if abs(w) > 1e-8:
                vertex_screen_position = vertex_screen_position_no_projection[:3] / w
            else:
                vertex_screen_position = vertex_screen_position_no_projection[:3]
            
            vertexes.append(vertex_screen_position)
        
        return np.array(vertexes).reshape(old_shape)


class Mesh3D(Shape3D):
    """
    A polygon is a set of triangles that make up a shape.
    """
    def __init__(self, position_3: np.ndarray, triangles_3_3_n: np.ndarray):
        assert triangles_3_3_n.shape[1] == 3
        assert triangles_3_3_n.shape[2] == 3
        super().__init__(position_3, triangles_3_3_n)
    
    def get_visible_triangle_screen_positions_n_n(self, camera: Camera3D):
        assert isinstance(camera, Camera3D)
        shape_t_matrix = np.array([
            [1, 0, 0, self._world_position_3[0]],
            [0, 1, 0, self._world_position_3[1]],
            [0, 0, 1, self._world_position_3[2]],
            [0, 0, 0, 1]
        ])

        triangles = []
        for triangle in self._vertexes_n_n:
            visible = True
            views = []
            for point in triangle:
                point = np.append(point, 1)

                # Matrix multiplication order matters
                view = camera.get_camera_matrix_4_4() @ shape_t_matrix @ point
                views.append(view)

                # Cull vertices (and subsequently triangles) that are behind the screen
                if view[2] > -camera.get_near_plane():
                    visible = False
                    continue
            
            ndcs = []
            if visible:
                for view in views:
                    # Perspective shifting
                    w = view[3]
                    if abs(w) > 1e-8:
                        ndc = view[:3] / w
                    else:
                        ndc = view[:3]
                    
                    ndcs.append(ndc)

                triangles.append(np.array(ndcs))
        return np.array(triangles)

class Line3D(Shape3D):
    """
    A line should be defined by a start position and an end position
    """
    def __init__(self, start_world_position_3: np.ndarray, end_world_position_3: np.ndarray):
        position = end_world_position_3 - start_world_position_3
        super().__init__(position, np.array([start_world_position_3 - position, end_world_position_3 - position]))


class Circle3D(Shape3D):
    """
    A circle is defined by a point and a radius
    """
    def __init__(self, position_3: np.ndarray, radius: float):
        super().__init__(position_3, np.array([]))
        self._radius = radius

    def get_radius(self):
        return self._radius


class Cube3D(Mesh3D):
    def __init__(self, position_3: np.ndarray, size: float):
        vertices = np.array([
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
        ])
        # 12 Triangles, 3 vertexes each, 3 components
        super().__init__(position_3, vertices.reshape(12, 3, 3))
    