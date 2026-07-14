from typing import Tuple, Optional, override
import pygui_cython as pygui
from abc import ABC, abstractmethod


def add_tuple(a, b):
    return (a[0] + b[0], a[1] + b[1])


def add_vec2(a: pygui.Vec2, b: pygui.Vec2):
    return pygui.Vec2(a.x + b.x, a.y + b.y)


def clamp(value: float, low: float, high: float) -> float:
    if value < low:
        return low
    if value > high:
        return high
    return value


def clamp_vec2(value: pygui.Vec2, low: Tuple[float, float], high: Tuple[float, float]):
    if value.x < low[0]:
        value.x = low[0]
    if value.x > high[0]:
        value.x = high[0]
    
    if value.y < low[1]:
        value.y = low[1]
    if value.y > high[1]:
        value.y = high[1]


class Shape(ABC):
    def __init__(self, position: pygui.Vec2, colour: pygui.Vec4):
        self.position = position
        self.colour = colour

    def get_colour_u32(self) -> int:
        self.colour.to_u32()
    
    def set_colour_rbg(self, red: float, green: float, blue: float):
        """RBG: 0 to 1"""
        self.colour.x = red
        self.colour.y = green
        self.colour.z = blue
    
    def set_colour_hsv(self, hue: float, saturation: float, vibrance: float):
        """Hue: 0 to 255. Saturation: 0 to 255. Vibrance: 0 to 255"""
        colour = pygui.color_convert_hsv_to_rgb(hue / 255, saturation / 255, vibrance / 255)
        self.colour.x = colour[0]
        self.colour.y = colour[1]
        self.colour.z = colour[2]
        self.colour.w = colour[3]

    @abstractmethod
    def draw(self, origin: Tuple[float, float], draw_list: pygui.ImDrawList):
        pass


class Circle(Shape):
    def __init__(self, position: pygui.Vec2, colour: pygui.Vec4, radius: pygui.Float, is_filled: pygui.Bool = None, thickness: Optional[pygui.Float] = None):
        """Thickness only relevant if is_filled is False"""
        super().__init__(position, colour)
        self.radius = radius
        self.is_filled = is_filled
        self.thickness = thickness or pygui.Float(1)

    @override
    def draw(self, origin: Tuple[float, float], draw_list: pygui.ImDrawList):
        if self.is_filled:
            draw_list.add_circle_filled(
                add_tuple(origin, self.position.tuple()),
                self.radius.value,
                self.colour.to_u32(),
            )
        else:
            draw_list.add_circle(
                add_tuple(origin, self.position.tuple()),
                self.radius.value,
                self.colour.to_u32(),
                0,
                self.thickness.value,
            )


class Rect(Shape):
    def __init__(self, position: pygui.Vec2, colour: pygui.Vec4, size: pygui.Vec2, is_filled: pygui.Bool = None, thickness: Optional[pygui.Float] = None):
        """Thickness only relevant if is_filled is False"""
        super().__init__(position, colour)
        self.size = size
        self.is_filled = is_filled
        self.thickness = thickness or pygui.Float(1)

    @override
    def draw(self, origin: Tuple[float, float], draw_list: pygui.ImDrawList):
        top_left = (
            self.position.x - self.size[0] / 2,
            self.position.y - self.size[1] / 2
        )
        bottom_right = (
            self.position.x + self.size[0] / 2,
            self.position.y + self.size[1] / 2
        )
        if self.is_filled:
            draw_list.add_rect_filled(
                add_tuple(origin, top_left),
                add_tuple(origin, bottom_right),
                self.colour.to_u32(),
            )
        else:
            draw_list.add_rect(
                add_tuple(origin, top_left),
                add_tuple(origin, bottom_right),
                self.colour.to_u32(),
                thickness=self.thickness.value,
            )
