# Primitive Types - COPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPYCOPY
jaedan = 1      # Int 4 bytes
noah = "hello"  # String
eric = 5.5      # Float
peter = True    # Truth nuke - Boolean

# Reference type
lily = [1, 2, 3, 4, 5]   # 8 bytes

import pygui_cython as pygui

john = pygui.Int(5)
john2 = pygui.Bool(False)
pygui.checkbox("Truth nukeify", john2)

pygui.color_edit4()
pygui.color_picker4()
