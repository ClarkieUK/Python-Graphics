# imports

# display
import glfw 
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import glm
import imgui
from imgui.integrations.glfw import * 
from shader import Shader
from sphere import Sphere
from texture_loader import texture_load

# numeracy
import pyrr
from PIL import Image
import numpy as np

# abstractions
from camera import Camera

# models 

# display
width,height = 1200,1200

# delta_time
last_frame = 0.0
anchor_time = 0.0
frame_count = 0

# camera
main_camera = Camera()
first_mouse = True

# callbacks
def process_input(window,delta_time) :

    if (glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS) : #we check to see if the escape is pressed in the context of the
                                                                #window, if true then we flag the closing of glfw window
        glfw.set_window_should_close(window,True)			    # GetKey returns either GLFW_RELEASE or glfw.PRESS

    #cameraSpeed = float(5.0 * delta_time)
    if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS :
        main_camera.processKeyboard('FORWARD', delta_time)
    if (glfw.get_key(window, glfw.KEY_S) == glfw.PRESS) :
        main_camera.processKeyboard('BACKWARD', delta_time)
    if (glfw.get_key(window, glfw.KEY_A) == glfw.PRESS) :
        main_camera.processKeyboard('LEFT', delta_time)
    if (glfw.get_key(window, glfw.KEY_D) == glfw.PRESS) :
        main_camera.processKeyboard('RIGHT', delta_time) 
    if (glfw.get_key(window, glfw.KEY_LEFT_CONTROL) == glfw.PRESS) :
        main_camera.processKeyboard('DOWN', delta_time)
    if (glfw.get_key(window, glfw.KEY_SPACE) == glfw.PRESS) :
        main_camera.processKeyboard('UP', delta_time) 
    if (glfw.get_key(window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS) :
        main_camera.processKeyboardSpeed('SPEED_UP', delta_time)
    if (glfw.get_key(window, glfw.KEY_LEFT_SHIFT) == glfw.RELEASE) :
        main_camera.processKeyboardSpeed('SLOW_DOWN', delta_time)
  
def window_resize(window, width, height) :
    glViewport(0, 0, width, height)
    projection = pyrr.matrix44.create_perspective_projection_matrix(45, width/height, 0.1, 100)
    
def mouse_callback(window, x_position, y_position) :
    global first_mouse
    global last_x_position 
    global last_y_position
    
    if first_mouse :
        last_x_position = x_position 
        last_y_position = y_position
        first_mouse = False
 
    xoffset = float(x_position - last_x_position)
    yoffset = float(last_y_position - y_position)
    last_x_position = float(x_position)
    last_y_position = float(y_position)
    
    main_camera.processMouseMovement(xoffset,yoffset,True)

def scroll_callback(window,xoffset,yoffset) :
    main_camera.processMouseScroll(yoffset)
 
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
glfw.set_cursor_pos_callback(window,mouse_callback)
glfw.set_scroll_callback(window,scroll_callback)

# set programs focus on window, all commands called after this 
# effect only this window

glfw.make_context_current(window)
glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

sphere_shader = Shader('test.vs','test.fs')

sphere = Sphere(2.5,40)

translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([0.0, 0.0, 0.0]))

scale = pyrr.matrix44.create_from_scale(pyrr.Vector3([1.5,1.5,1.5]))

glEnable(GL_DEPTH_TEST)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
glClearColor(0,0.1,0.1,1)
# event loop

while not glfw.window_should_close(window) :
    
    # delta time
    current_frame = glfw.get_time()
    delta_time = current_frame - last_frame
    last_frame = current_frame
    frame_count += 1
    
    if current_frame - anchor_time >= 1.0 :
        print(frame_count)
        frame_count = 0
        anchor_time = current_frame
        
    
    # key presses
    process_input(window,delta_time)
    
    # begin drawing
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
    # update view and projection matrices from camera manipulation
    view = main_camera.getViewMatrix()
    projection = glm.perspective(glm.radians(main_camera.Zoom), width/height, 0.1,1000.0)
    
    # set uniforms
    sphere_shader.setMat4('view',view)
    sphere_shader.setMat4('projection',projection)

    sphere.draw(sphere_shader)
    
    # swap back and front pages
    glfw.poll_events()
    glfw.swap_buffers(window)

# free resources
glfw.terminate()