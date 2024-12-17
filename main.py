# imports
import glfw 
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import pyrr
from PIL import Image
import numpy as np
from shader import Shader
from sphere import Sphere
import glm
import imgui
from imgui.integrations.glfw import * 
from texture_loader import texture_load

width,height = 800,800

def window_resize(window, width, height) :
    glViewport(0, 0, width, height)
    projection = pyrr.matrix44.create_perspective_projection_matrix(45, width/height, 0.1, 100)
    cube_shader.setMat4('projection',projection)
 
# geometries

vertices = np.array([-0.5, -0.5,  0.5, 0.0, 0.0,
             0.5, -0.5,  0.5, 1.0, 0.0,
             0.5,  0.5,  0.5, 1.0, 1.0,
            -0.5,  0.5,  0.5, 0.0, 1.0,

            -0.5, -0.5, -0.5, 0.0, 0.0,
             0.5, -0.5, -0.5, 1.0, 0.0,
             0.5,  0.5, -0.5, 1.0, 1.0,
            -0.5,  0.5, -0.5, 0.0, 1.0,

             0.5, -0.5, -0.5, 0.0, 0.0,
             0.5,  0.5, -0.5, 1.0, 0.0,
             0.5,  0.5,  0.5, 1.0, 1.0,
             0.5, -0.5,  0.5, 0.0, 1.0,

            -0.5,  0.5, -0.5, 0.0, 0.0,
            -0.5, -0.5, -0.5, 1.0, 0.0,
            -0.5, -0.5,  0.5, 1.0, 1.0,
            -0.5,  0.5,  0.5, 0.0, 1.0,

            -0.5, -0.5, -0.5, 0.0, 0.0,
             0.5, -0.5, -0.5, 1.0, 0.0,
             0.5, -0.5,  0.5, 1.0, 1.0,
            -0.5, -0.5,  0.5, 0.0, 1.0,

             0.5, 0.5, -0.5, 0.0, 0.0,
            -0.5, 0.5, -0.5, 1.0, 0.0,
            -0.5, 0.5,  0.5, 1.0, 1.0,
             0.5, 0.5,  0.5, 0.0, 1.0],dtype=np.float32)

indices = np.array([ 0,  1,  2,  2,  3,  0,
            4,  5,  6,  6,  7,  4,
            8,  9, 10, 10, 11,  8,
           12, 13, 14, 14, 15, 12,
           16, 17, 18, 18, 19, 16,
           20, 21, 22, 22, 23, 20],dtype=np.uint32)

# initialise glfw
if not glfw.init() :
    raise Exception('glfw library not found...')
    
# create window
window = glfw.create_window(900,900,'OpenGL Practice', None, None)

# check if window creation was good
if not window : 
    glfw.terminate()
    raise Exception('window dogshit')

# set window position
glfw.set_window_pos(window, 500, 300)
glfw.set_window_size_callback(window,window_resize)

# set programs focus on window, all commands called after this 
# effect only this window

glfw.make_context_current(window)

cube_shader = Shader('square_shader.vs','square_shader.fs')
#cube_shader = Shader('square_shader.vs','square_shader.fs')

# actions
sphere = Sphere(2.5,40)

texture = glGenTextures(3)

cube_crate_texture = texture_load('textures/crate.jpg',texture[0])
cube_cat_texture = texture_load('textures/cat.png',texture[1])
cube_smile_texture = texture_load('textures/smiley.png',texture[2])

VBO = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, VBO)
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes , vertices,GL_STATIC_DRAW)

EBO = glGenBuffers(1)
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

glEnableVertexAttribArray(0)
glEnableVertexAttribArray(1)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, np.dtype(np.float32).itemsize*5, ctypes.c_void_p(0))
glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, np.dtype(np.float32).itemsize*5, ctypes.c_void_p(np.dtype(np.float32).itemsize*3))

cube_shader.use()

projection = pyrr.matrix44.create_perspective_projection_matrix(45, width/height, 0.1, 100)

translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([0.0, 0.0, 0.0]))

scale = pyrr.matrix44.create_from_scale(pyrr.Vector3([1.5,1.5,1.5]))

#view = pyrr.matrix44.create_from_translation(pyrr.Vector3([1.0, 0.0, 0.0]))
view = pyrr.matrix44.create_look_at(
    pyrr.Vector3([-5.0, -0.0, -5.0]), pyrr.Vector3([0.0, 0.0, 0.0]), pyrr.Vector3([0.0, 1.0, 0.0])
) # eye pos, target, up vector

cube_shader.setMat4('projection',projection)
cube_shader.setMat4('view',view)

glEnable(GL_DEPTH_TEST)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
glClearColor(0,0.1,0.1,1)
# event loop

while not glfw.window_should_close(window) :
    
    # event handling
    glfw.poll_events()

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
    rot_x = pyrr.Matrix44.from_x_rotation(0.5 * glfw.get_time())
    rot_y = pyrr.Matrix44.from_y_rotation(0.8 * glfw.get_time())

    rotation = pyrr.matrix44.multiply(rot_x,rot_y)
    model   = pyrr.matrix44.multiply(scale, rotation)
    model   = pyrr.matrix44.multiply(scale, translation)

    cube_shader.setMat4('model',model)
    
    glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, ctypes.c_void_p(0))
    
    # swap back and front pages
    glfw.swap_buffers(window)

# free resources
glfw.terminate()