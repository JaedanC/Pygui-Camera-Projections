import math

import pygui_cython as pygui
from shapes import *
from r_shape import Camera, Rect2D, Circle2D


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
        self.camera = Camera(np.array([0, 0]), 1)

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
            up_down = int(pygui.is_key_down(pygui.KEY_S)) - int(pygui.is_key_down(pygui.KEY_W))
            self.camera.set_position(np.array(self.camera.get_position() + np.array([left_right, up_down])))

            self.camera.update_matrices(np.array(self.sandbox_size.tuple()))
            camera_matrix_3_3 = self.camera.get_camera_matrix_3_3()

            rect_screen_points = self.basic_rect.convert_to_screen_coordinates(camera_matrix_3_3)
            circle_screen_points = self.basic_circle.convert_to_screen_coordinates(camera_matrix_3_3)
            
            mouse_game_coord = self.camera.convert_screen_to_world_coord(np.array(pygui.get_mouse_pos()) - np.array(origin))
            inside_circle = math.dist(self.basic_circle.get_position(), mouse_game_coord) < self.basic_circle.get_radius()

            # Imgui doesn't like really large fonts. We clamp the scale to 300 to prevent fonts from getting too large
            # such it crashes.
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
            # --------------------------------------------------------------------------------------------


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
        pygui.end()
