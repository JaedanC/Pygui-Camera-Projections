import math

import pygui_cython as pygui
from shapes import *
from r_shape import Camera2D, Rect2D, Circle2D, Camera3D, Triangle3D, Line3D, Cube3D, Polygon3D


import numpy as np


class Game:
    def __init__(self):
        self.first_frame = True

    def on_start(self):
        """
        On game start do this. Save any variables you want to initilise with
        self.variable_name = [value_to_start_with]
        """
        self.sandbox_size = pygui.Vec2(1000, 500)
        self.basic_rect = Rect2D(np.array([0, 0]), np.array([20, 10]))
        self.basic_circle = Circle2D(np.array([0, 50]), 20)
        self.camera = Camera2D(np.array([0, 0]), 1)

        self.camera_3d = Camera3D(np.array([0, 0, -5]))
        self.triangle_3d = Triangle3D(np.array([50, 0, 0]))
        self.cube_3d = Cube3D(np.array([0, 0, 0]), 100)
        self.line_3d_x = Line3D(np.array([0, 0, 0]), np.array([[0, 0, 0], [50, 0,  0]]))
        self.line_3d_y = Line3D(np.array([0, 0, 0]), np.array([[0, 0, 0], [0,  50, 0]]))
        self.line_3d_z = Line3D(np.array([0, 0, 0]), np.array([[0, 0, 0], [0,  0,  50]]))
        self.has_mouse_capture = False

    def _push_game_window(self):
        """All this function does is give us the drawing 'Sandbox' we see in the
        Game window. The origin is the TOP LEFT coordinate of the Game Sandbox. This
        value is called the origin.

        When drawing, it's important that we pass the origin to the draw function.
        Therefore, treat game entities as relative to this. i.e. And entity with
        Position (0, 0) should be drawn at the TOP LEFT of the sandbox (origin + pos).
        The draw funtion will handle this.
        """
        self.window_size = pygui.get_content_region_avail()
        origin = pygui.get_cursor_screen_pos()
        draw_list = pygui.get_window_draw_list()

        # First clip rect is the whole window so the sandbox doesn't go outside the window.
        draw_list.push_clip_rect(
            origin,
            add_tuple(origin, self.window_size),
        )
        centre_of_window = (self.window_size[0] / 2, self.window_size[1] / 2)
        top_left_sandbox = (
            centre_of_window[0] - self.sandbox_size.x / 2,
            centre_of_window[1] - self.sandbox_size.y / 2
        )
        bottom_right_sandbox = (
            centre_of_window[0] + self.sandbox_size.x / 2,
            centre_of_window[1] + self.sandbox_size.y / 2,
        )
        # Second clip rect is for the Sandbox so that the game doesn't draw outside the sandbox.
        draw_list.push_clip_rect(
            add_tuple(origin, top_left_sandbox),
            add_tuple(origin, bottom_right_sandbox),
            intersect_with_current_clip_rect=True
        )
        draw_list.add_rect(
            add_tuple(origin, top_left_sandbox),
            add_tuple(origin, bottom_right_sandbox),
            pygui.Vec4(0.7, 0.7, 0.7, 1).to_u32(),
            thickness=5
        )
        pygui.set_cursor_screen_pos(add_tuple(origin, top_left_sandbox))
        origin = pygui.get_cursor_screen_pos()
        pygui.dummy((0, 0))

        return origin, draw_list

    def _pop_game_window(self, draw_list: pygui.ImDrawList):
        draw_list.pop_clip_rect()
        draw_list.pop_clip_rect()

    def draw(self):
        """
        Every game tick/frame this is called. This is where your game logic goes
        """
        ds = pygui.dock_space_over_viewport(
            pygui.get_id("Main view"),
            pygui.get_main_viewport()
        )
        # This forces the Game window to be "docked" inside the Viewport.
        pygui.set_next_window_dock_id(ds, pygui.COND_ALWAYS)

        # To create a window, we must use a pygui.begin() and a pygui.end().
        # The pygui.end() must ALWAYS be called. It must not be "nested" inside
        # the pygui.begin().
        if pygui.begin("Game window"):
            if self.first_frame:
                self.on_start()
                self.first_frame = False

            origin, draw_list = self._push_game_window()

            # --------------------------------------------------------------------------------------------
            # --------------------------------------------------------------------------------------------

            # Let's make the player rainbow. We'll use the frame count to do
            # this
            frames_since_start = pygui.get_frame_count()

            # --------------------------------------------------------------------------------------------
            # --------------------------------------------------------------------------------------------

            # For dragging, we consider the world scale when we drag as ImGui
            # gives us the drag in screen coordinates. We can simply divide the
            # mouse delta by the scale.
            if pygui.is_mouse_down(pygui.MOUSE_BUTTON_LEFT):
                camera_offset_screen_2 = np.array(pygui.get_io().mouse_delta) / self.camera.get_scale()
                self.camera.set_position(self.camera.get_position() - camera_offset_screen_2)
            
            # For scrolling, we apply a multiplier so that as we zoom in more,
            # we zoom in less, and vice versa, so to speak.
            SCALE_SPEED = 1.3
            if pygui.get_io().mouse_wheel != 0:
                if pygui.get_io().mouse_wheel > 0:
                    self.camera.set_scale(self.camera.get_scale() * SCALE_SPEED)
                if pygui.get_io().mouse_wheel < 0:
                    self.camera.set_scale(self.camera.get_scale() / SCALE_SPEED)
            
            # global_mouse_pos = pygui.get_mouse_pos()
            # game_mouse_pos = add_tuple(global_mouse_pos, (-origin[0], -origin[1]))
            
            if pygui.is_key_pressed(pygui.KEY_HOME) or pygui.is_key_pressed(pygui.KEY_C):
                self.camera.set_position(np.array([0, 0]))
                self.camera.set_scale(1)

            left_right = int(pygui.is_key_down(pygui.KEY_D)) - int(pygui.is_key_down(pygui.KEY_A))
            up_down = int(pygui.is_key_down(pygui.KEY_LEFT_CTRL)) - int(pygui.is_key_down(pygui.KEY_SPACE))
            self.camera.set_position(np.array(self.camera.get_position() + np.array([left_right, up_down])))

            self.camera.update_matrices(np.array(self.sandbox_size.tuple()))
            camera_matrix_3_3 = self.camera.get_camera_matrix_3_3()

            rect_screen_points = self.basic_rect.convert_to_screen_coordinates(camera_matrix_3_3)
            circle_screen_points = self.basic_circle.convert_to_screen_coordinates(camera_matrix_3_3)
            
            mouse_game_coord = self.camera.convert_screen_to_world_coord(np.array(pygui.get_mouse_pos()) - np.array(origin))
            inside_circle = math.dist(self.basic_circle.get_position(), mouse_game_coord) < self.basic_circle.get_radius()

            # Imgui doesn't like really large fonts. We clamp the scale to 300 to prevent fonts from getting too large
            # such it crashes.
            # --------------------------------------------------------------------------------------------
            # 2D
            # --------------------------------------------------------------------------------------------
            
            draw_list.add_convex_poly_filled(np.array(origin) + rect_screen_points, pygui.Vec4(0, 1, 0, 1).to_u32())
            draw_list.add_circle_filled(
                np.array(origin) + circle_screen_points[0],
                self.basic_circle.get_screen_radius(self.camera.get_scale()),
                pygui.Vec4(0, 1, 0, 1).to_u32() if inside_circle else pygui.Vec4(1, 1, 1, 1).to_u32(),
            )
            draw_list.add_text_im_font_ptr(
                pygui.get_font(),
                pygui.get_font_size() * self.camera.get_scale(),
                add_tuple(origin, rect_screen_points[0]),
                pygui.Vec4(1, 0, 1, 1).to_u32(),
                "Hello world"
            )

            # --------------------------------------------------------------------------------------------
            # 3D
            # --------------------------------------------------------------------------------------------
            if pygui.is_mouse_clicked(pygui.MOUSE_BUTTON_RIGHT) and pygui.is_window_hovered():
                self.has_mouse_capture = not self.has_mouse_capture

            if self.has_mouse_capture:
                pygui.set_mouse_cursor(pygui.MOUSE_CURSOR_NONE)
                yaw, pitch = self.camera_3d.get_rotation_degrees()
                yaw += pygui.get_io().mouse_delta[0]
                pitch += pygui.get_io().mouse_delta[1]
                self.camera_3d.set_rotation_degrees(yaw, pitch)


            in_out = int(pygui.is_key_down(pygui.KEY_W)) - int(pygui.is_key_down(pygui.KEY_S))
            fov_edit = int(pygui.is_key_down(pygui.KEY_1)) - int(pygui.is_key_down(pygui.KEY_2))

            camera_3d_position = self.camera_3d.get_position()
            new_x = camera_3d_position[0] + left_right
            new_y = camera_3d_position[1] + up_down
            new_z = camera_3d_position[2] + in_out
            self.camera_3d.set_position(np.array([new_x, new_y, new_z]))
            self.camera_3d.set_fov(self.camera_3d.get_fov() + fov_edit)


            # 3D Stuff
            self.camera_3d.update_matrices(np.array(self.sandbox_size.tuple()))
            c3 = self.camera_3d.get_camera_matrix_4_4()
            # triangle_screen_coords = self.triangle_3d.get_vtx_screen_coords(c3)
            # draw_list.add_convex_poly_filled(np.array(list(origin) + [0]) + triangle_screen_coords, pygui.Vec4(0, 1, 0, 1).to_u32())

            cube_screen_coords = self.cube_3d.get_vtx_screen_coords(c3, self.camera_3d.get_near_plane())
            cube_world_coords = self.cube_3d.get_vtx_world_coords()

            
            def map_from_top_corner_to_screen(x, y):
                # (-1,  1) = top-left
                # ( 1,  1) = top-right
                # (-1, -1) = bottom-left
                # ( 1, -1) = bottom-right
                # ( 0,  0) = center
                return np.array([
                    (1 - x) * self.sandbox_size.x / 2,
                    (1 - y) * self.sandbox_size.y / 2
                ])
        
            def squared_dist(point_a_3: np.ndarray, point_b_3: np.ndarray):
                return sum((px - qx) ** 2.0 for px, qx in zip(point_a_3, point_b_3))
        
            def get_average_position_of_triangle(triangle_3_3: np.ndarray):
                a_3, b_3, c_3 = triangle_3_3
                return np.array([
                    (a_3[0] + b_3[0] + c_3[0]) / 3,
                    (a_3[1] + b_3[1] + c_3[1]) / 3,
                    (a_3[2] + b_3[2] + c_3[2]) / 3,
                ])

            cube_screen_coords_triangles_3_n_3 = Polygon3D.group_into_triangles(cube_screen_coords)
            cube_world_coords_triangles_3_n_3 = Polygon3D.group_into_triangles(cube_world_coords)

            def distance_from_triangle_to_camera(triangle_world_coords_3_3: np.ndarray, camera_world_coord_3: np.ndarray):
                triangle_world_coords_3 = get_average_position_of_triangle(triangle_world_coords_3_3)
                squared_distance_to_camera = squared_dist(triangle_world_coords_3, camera_world_coord_3)
                return squared_distance_to_camera
            
            def sort_triangles_by_distance_to_camera(
                    triangle_screen_coords_3_3: np.ndarray,
                    triangle_world_coords_3_3: np.ndarray,
                    camera_world_coords_3: np.ndarray
                ):
                combined = [(sc_3, wc_3) for sc_3, wc_3 in zip(triangle_screen_coords_3_3, triangle_world_coords_3_3)]
                combined.sort(key=lambda x: -distance_from_triangle_to_camera(x[1], camera_world_coords_3))
                return combined


            ordered_triangles = sort_triangles_by_distance_to_camera(
                cube_screen_coords_triangles_3_n_3,
                cube_world_coords_triangles_3_n_3,
                self.camera_3d.get_position()
            )


            for i, (triangle_sc_3_3, triangle_wc_3_3) in enumerate(ordered_triangles):
                a, b, c = triangle_sc_3_3
                triangle_average_world_position_3 = get_average_position_of_triangle(triangle_wc_3_3)
                triangle_average_world_position_screen_position_3 = Polygon3D.convert_world_coord_to_screen_coord(triangle_average_world_position_3, self.camera_3d.get_camera_matrix_4_4())
                triangle_distance_to_camera = distance_from_triangle_to_camera(triangle_wc_3_3, self.camera_3d.get_position())
                pygui.begin("Test")
                pygui.slider_float3(f"Tri {i}", [pygui.Float(p) for p in triangle_average_world_position_3], 0, 1000)
                pygui.same_line()
                pygui.text(f"Dist: {triangle_distance_to_camera}")
                pygui.end()
                col = pygui.Vec4(
                    ((i * 60)  % 255) / 255,
                    ((i * 40) % 255) / 255,
                    ((i * 25)  % 255) / 255,
                    1
                ).to_u32()
                draw_list.add_text(
                    origin + map_from_top_corner_to_screen(*triangle_average_world_position_screen_position_3[:2]),
                    col,
                    "{}".format(triangle_distance_to_camera)
                )
                draw_list.add_circle(
                    origin + map_from_top_corner_to_screen(*triangle_average_world_position_screen_position_3[:2]),
                    2,
                    col,
                )
                draw_list.add_triangle(
                    origin + map_from_top_corner_to_screen(*a[:2]),
                    origin + map_from_top_corner_to_screen(*b[:2]),
                    origin + map_from_top_corner_to_screen(*c[:2]),
                    col,
                )
            # ordered_triangles = sort_triangles_by_distance_to_camera(
            #     cube_screen_coords_triangles,
            #     cube_world_coords_triangles,
            #     self.camera.get_position()
            # )
            # draw_list.add_triangle(
            #     origin + map_from_top_corner_to_screen(cube_points[i][0],   cube_points[i][1]),
            #     origin + map_from_top_corner_to_screen(cube_points[i+1][0], cube_points[i+1][1]),
            #     origin + map_from_top_corner_to_screen(cube_points[i+2][0], cube_points[i+2][1]),
            #     pygui.Vec4(
            #         ((i * 60)  % 255) / 255,
            #         ((i * 40) % 255) / 255,
            #         ((i * 25)  % 255) / 255,
            #         1
            #     ).to_u32()
            # )

            # for i, (a, b, c) in enumerate(ordered_triangles):
                # draw_list.add_text(
                #     origin + map_from_top_corner_to_screen(tri_position[0], tri_position[1]),
                #     pygui.Vec4(
                #         ((i * 60)  % 255) / 255,
                #         ((i * 40) % 255) / 255,
                #         ((i * 25)  % 255) / 255,
                #         1
                #     ).to_u32(),
                #     "{}".format(squared_dist(tri_position, self.camera_3d.get_position()))
                # )
                # draw_list.add_circle(
                #     origin + map_from_top_corner_to_screen(tri_position[0], tri_position[1]),
                #     2,
                #     pygui.Vec4(
                #         ((i * 60)  % 255) / 255,
                #         ((i * 40) % 255) / 255,
                #         ((i * 25)  % 255) / 255,
                #         1
                #     ).to_u32(),
                # )
                # draw_list.add_triangle_filled(
                #     origin + map_from_top_corner_to_screen(a[0], a[1]),
                #     origin + map_from_top_corner_to_screen(b[0], b[1]),
                #     origin + map_from_top_corner_to_screen(c[0], c[1]),
                #     pygui.Vec4(
                #         ((i * 60)  % 255) / 255,
                #         ((i * 40) % 255) / 255,
                #         ((i * 25)  % 255) / 255,
                #         1
                #     ).to_u32()
                # )
                pass
            
            
            points = self.line_3d_x.get_vtx_screen_coords(self.camera_3d.get_camera_matrix_4_4(), self.camera_3d.get_near_plane())
            if len(points) == 2:
                start, end = points
                draw_list.add_line(
                    origin + map_from_top_corner_to_screen(start[0], start[1]),
                    origin + map_from_top_corner_to_screen(end[0], end[1]),
                    pygui.Vec4(1, 0, 0, 1).to_u32(),
                    thickness=5,
                )

            points = self.line_3d_y.get_vtx_screen_coords(self.camera_3d.get_camera_matrix_4_4(), self.camera_3d.get_near_plane())
            if len(points) == 2:
                start, end = points
                draw_list.add_line(
                    origin + map_from_top_corner_to_screen(start[0], start[1]),
                    origin + map_from_top_corner_to_screen(end[0], end[1]),
                    pygui.Vec4(0, 1, 0, 1).to_u32(),
                    thickness=5,
                )

            points = self.line_3d_z.get_vtx_screen_coords(self.camera_3d.get_camera_matrix_4_4(), self.camera_3d.get_near_plane())
            if len(points) == 2:
                start, end = points
                draw_list.add_line(
                    origin + map_from_top_corner_to_screen(start[0], start[1]),
                    origin + map_from_top_corner_to_screen(end[0], end[1]),
                    pygui.Vec4(0, 0, 1, 1).to_u32(),
                    thickness=5,
                )
            

                # draw_list.add_triangle(
                #     cube_points_screen[i][:2],
                #     cube_points_screen[i+1][:2],
                #     cube_points_screen[i+2][:2],
                #     pygui.Vec4(
                #         ((i * 50)  % 255) / 255,
                #         ((i * 100) % 255) / 255,
                #         ((i * 25)  % 255) / 255,
                #         1
                #     ).to_u32()
                # )


            # for obj in self.game_objects + self.balls:
            #     obj.draw(origin, draw_list)


            self._pop_game_window(draw_list)
        pygui.end()

        if pygui.begin("Tools"):
            if pygui.tree_node("Camera"):
                if pygui.button("Reset"):
                    self.camera.set_position(np.array([0, 0]))
                    self.camera.set_scale(1)
                pygui.slider_float2("Position", pygui.Vec2(*self.camera.get_position()).as_floatptrs(), 0, 1000)
                pygui.slider_float("Scale",     pygui.Float(self.camera.get_scale()),                   0, 1000)
                pygui.tree_pop()
            
            if pygui.tree_node("Mouse"):
                mouse_screen_coord = np.array(pygui.get_mouse_pos())
                game_screen_coord = mouse_screen_coord - np.array(origin)
                game_coord = self.camera.convert_screen_to_world_coord(game_screen_coord)

                pygui.slider_float2("Screen Cood",       pygui.Vec2(*mouse_screen_coord).as_floatptrs(), 0, 1000)
                pygui.slider_float2("Game Screen Coord", pygui.Vec2(*game_screen_coord).as_floatptrs(),  0, 1000)
                pygui.slider_float2("Game Cood",         pygui.Vec2(*game_coord).as_floatptrs(),         0, 1000)
                pygui.tree_pop()
            
            if pygui.tree_node("Camera3D"):
                pygui.slider_float3("Camera Cood", [pygui.Float(coord) for coord in self.camera_3d.get_position()], 0, 1000)
                pygui.slider_float("fov",          pygui.Float(self.camera_3d.get_fov()), 0, 1000)
                pygui.tree_pop()
            
            if pygui.tree_node("Cube3D"):
                for i, point in enumerate(self.cube_3d.get_vtx_screen_coords(self.camera_3d.get_camera_matrix_4_4(), self.camera_3d.get_near_plane())):
                    x, y, z = point
                    x = (x + 1) * self.sandbox_size.x / 2
                    y = (1 - y) * self.sandbox_size.y / 2
                    pygui.slider_float3(f"Point {i}", [pygui.Float(x), pygui.Float(y), pygui.Float(z)], 0, 1000)
                pygui.tree_pop()
            
        pygui.end()
