from typing import List

import numpy as np
from shape_3d import Camera3D, Shape3D, Cube3D, Line3D, Circle3D
from abc import ABC, abstractmethod
import pygui_cython as pygui
from extras import *



class Py3dDrawable(ABC):
    def __init__(self, shape: Shape3D):
        self._shape = shape
        pass

    def get_shape(self):
        return self._shape

    @abstractmethod
    def draw(self, camera: Camera3D, origin_2: np.ndarray, draw_list: pygui.ImDrawList, sandbox_size_2: np.ndarray):
        pass


class Py3dCube(Py3dDrawable):
    def __init__(self, position_3: np.ndarray, size: float):
        super().__init__(Cube3D(position_3, size))
    
    def draw(self, camera: Camera3D, origin_2: np.ndarray, draw_list: pygui.ImDrawList, sandbox_size_2: np.ndarray):
        self._shape: Cube3D
        # cube_screen_positions_3_3_n = self._shape.get_vertex_screen_positions_n_n(camera)
        # cube_world_positions_3_3_n = self._shape.get_vertex_world_position_n_n()
        # ordered_triangles = [(sc_3, wc_3) for sc_3, wc_3 in zip(cube_screen_positions_3_3_n, cube_world_positions_3_3_n)]
        # for i, (triangle_sc_3_3, triangle_wc_3_3) in enumerate(ordered_triangles):
        #     a, b, c = triangle_sc_3_3
        #     triangle_average_world_position_3 = average_points_3_3(triangle_wc_3_3)
        #     triangle_average_world_position_screen_position_3 = Shape3D.convert_world_position_to_screen_position(triangle_average_world_position_3, camera)
        #     triangle_distance_to_camera = distance_between_triangle_world_position_3_3_to_world_position_3(triangle_wc_3_3, camera.get_position_3())
        #     pygui.begin("Test")
        #     pygui.slider_float3(f"Tri {i}", [pygui.Float(p) for p in triangle_average_world_position_3], 0, 1000)
        #     pygui.same_line()
        #     pygui.text(f"Dist: {triangle_distance_to_camera}")
        #     pygui.end()
        #     col = pygui.Vec4(
        #         ((i * 60)  % 255) / 255,
        #         ((i * 40) % 255) / 255,
        #         ((i * 25)  % 255) / 255,
        #         1
        #     ).to_u32()
        #     draw_list.add_text(
        #         origin_2 + convert_screen_position_2_to_pixel_position_2(triangle_average_world_position_screen_position_3[:2], sandbox_size_2),
        #         col,
        #         "{}".format(triangle_distance_to_camera)
        #     )
        #     draw_list.add_circle(
        #         origin_2 + convert_screen_position_2_to_pixel_position_2(triangle_average_world_position_screen_position_3[:2], sandbox_size_2),
        #         2,
        #         col,
        #     )
        #     draw_list.add_triangle(
        #         origin_2 + convert_screen_position_2_to_pixel_position_2(a[:2], sandbox_size_2),
        #         origin_2 + convert_screen_position_2_to_pixel_position_2(b[:2], sandbox_size_2),
        #         origin_2 + convert_screen_position_2_to_pixel_position_2(c[:2], sandbox_size_2),
        #         col,
        #     )
        cube_triangles_screen_positions = self._shape.get_visible_triangle_screen_positions_n_n(camera)
        for i, triangle_3_3 in enumerate(cube_triangles_screen_positions):
            pygui.begin("Test")
            for j, point_3 in enumerate(triangle_3_3):
                pixel_pos_2 = origin_2 + convert_screen_position_2_to_pixel_position_2(point_3[:2], sandbox_size_2)
                pygui.slider_float2(f"Tri {i} {j}", [pygui.Float(p) for p in pixel_pos_2], 0, 1000)
            pygui.end()

            draw_list.add_triangle(
                origin_2 + convert_screen_position_2_to_pixel_position_2(triangle_3_3[0][:2], sandbox_size_2),
                origin_2 + convert_screen_position_2_to_pixel_position_2(triangle_3_3[1][:2], sandbox_size_2),
                origin_2 + convert_screen_position_2_to_pixel_position_2(triangle_3_3[2][:2], sandbox_size_2),
                col = pygui.Vec4(
                    ((i * 60)  % 255) / 255,
                    ((i * 40) % 255) / 255,
                    ((i * 25)  % 255) / 255,
                    1
                ).to_u32()
            )


class Py3dLine(Py3dDrawable):
    def __init__(self, start_position_3: np.ndarray, end_position_3: np.ndarray):
        super().__init__(Line3D(start_position_3, end_position_3))
    
    def draw(self, camera: Camera3D, origin_2: np.ndarray, draw_list: pygui.ImDrawList, sandbox_size_2: np.ndarray):
        start, end = self._shape.get_vertex_screen_positions_n_n(camera)
        draw_list.add_line(
            origin_2 + convert_screen_position_2_to_pixel_position_2(start[:2], sandbox_size_2),
            origin_2 + convert_screen_position_2_to_pixel_position_2(end[:2],   sandbox_size_2),
            pygui.Vec4(1, 0, 0, 1).to_u32(),
            thickness=5,
        )


class Py3dCircle(Py3dDrawable):
    def __init__(self, position_3: np.ndarray, radius):
        super().__init__(Circle3D(position_3, radius))
        pass

    def draw(self, camera: Camera3D, origin_2: np.ndarray, draw_list: pygui.ImDrawList, sandbox_size_2: np.ndarray):
        self._shape: Circle3D
        screen_position_2 = Shape3D.convert_world_position_to_screen_position(self._shape.get_position_3(), camera)
        draw_list.add_circle_filled(
            origin_2 + convert_screen_position_2_to_pixel_position_2(screen_position_2, sandbox_size_2),
            self._shape.get_radius(),
            pygui.Vec4(1, 0, 0, 1).to_u32(),
        )

    
class Py3dWorldSpawn:
    def __init__(self, camera: Camera3D):
        self.camera = camera
        self.tree: List[Py3dDrawable] = []
    
    def tick(self, sandbox_size_2: np.ndarray):
        self.camera.update_matrices(sandbox_size_2)
    
    def add_drawable(self, drawable: Py3dDrawable):
        self.tree.append(drawable)

    def draw(self, origin_2: np.ndarray, draw_list: pygui.ImDrawList, sandbox_size_2: np.ndarray):
        for drawable in self.tree:
            drawable.draw(self.camera, origin_2, draw_list, sandbox_size_2)

