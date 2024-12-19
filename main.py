# imports

# display
from win32api import GetSystemMetrics
import glfw 
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import glm
import imgui
from imgui.integrations.glfw import * 
from sphere import Sphere

# numeracy
import pyrr
from PIL import Image
import numpy as np
from integrators import update_bodies_rungekutta

# abstractions
from camera import Camera
from texture_loader import texture_load
from shader import Shader
from body import Body
from vector import *

# display
width,height = 1200,1200

# delta_time
last_frame = 0.0
anchor_time = 0.0
frame_count = 0

# camera
main_camera = Camera()
first_mouse = True

# setup constants
WHITE = np.array([255, 255, 255])
BLACK = np.array([0, 0, 0])
RED = np.array([255, 0, 0])
GREEN = np.array([0, 255, 0])
BLUE = np.array([0, 0, 255])
LIGHT_BLUE = np.array([173,216,230])
YELLOW = np.array([255,255,0])
PURPLE = np.array([203, 195, 227])
GRAY = np.array([169,169,169])
DIM_GRAY = np.array([16,16,16])
ORANGE = np.array([255,165,0])
BROWN = np.array([222,184,135])

# facts https://nssdc.gsfc.nasa.gov/planetary/planetfact.html , https://ssd.jpl.nasa.gov/tools/sbdb_lookup.html#/ , https://ssd.jpl.nasa.gov/horizons/app.html#/

G = 6.67430e-11
AU = 1.496e11
scale = 8/AU

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
window = glfw.create_window(width,height,'OpenGL Practice', None, None)

# check if window creation was good
if not window : 
    glfw.terminate()
    raise Exception('window dogshit')

# set window position and callbacks
xbuf , ybuf = (GetSystemMetrics(0) - width) / 2 , (GetSystemMetrics(1) - height) / 2
glfw.set_window_pos(window, int(xbuf), int(ybuf))
glfw.set_window_size_callback(window,window_resize)
glfw.set_cursor_pos_callback(window,mouse_callback)
glfw.set_scroll_callback(window,scroll_callback)

# set programs focus on window, all commands called after this 
# effect only this window
glfw.make_context_current(window)
glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

sphere_shader = Shader('pixilated_noise.vs','pixilated_noise.fs')
orbits_shader = Shader('orbit.vs','orbit.fs')

sun = Body(YELLOW,2,
               Vector3(-8.974133574359094E-03 , -4.482427452346882E-04   ,  2.127030817970091E-04    ) * AU,
               Vector3(2.943740906566515E-00  , -1.522269030106718E+01   ,  5.405294312927581E-02   ),
               1.98892e30)
    
earth = Body(LIGHT_BLUE,1,
            Vector3(-9.505921700191389E-01 ,  3.087952119351821E-01 ,  1.989011142050173E-04 ) * AU,
            Vector3(-9.765270895434471E+03 , -2.842566374064967E+04 ,1.340272026562062E-00 ),
            5.9742e24)

mercury = Body(GRAY,0.383,
            Vector3(2.149048126431211E-01, -3.703275102221233E-01, -5.054911078568054E-02) * AU,
            Vector3(3.194733455939798E+04,  2.760819992651870E+04,-6.726501719165086E+02),
            3.3e23)

jupiter = Body(BROWN,11.21/5,
            Vector3(4.704772918851717E+00,  1.511365399792853E+00, -1.115289067637071E-01)*AU,
            Vector3(-4.142495775785003E+03,  1.305304733174904E+04,  3.854785819752404E+01),
            1.898e27)

venus = Body(ORANGE,0.949,
            Vector3(3.767586589387518E-01,  6.096285845914635E-01, -1.366913498677996E-02)*AU,
            Vector3(-2.970885187788254E+04,  1.854691206999238E+04,  1.969344555554133E+03),
            4.8685e24)

mars = Body(RED,0.532,
            Vector3(-7.405291211708632E-01,  1.452944259261813E+00,  4.861778406962673E-02)*AU,
            Vector3(-2.072274803097698E+04, -8.848861397338558E+03,  3.233078954361095E+02),
            6.39e23)

uranus = Body(BLUE,4.01/5,
            Vector3(1.318193324076657E+01,  1.457795067541527E+01, -1.166313290118892E-01)*AU,
            Vector3(-5.100987027758054E+03,  4.250202813282490E+03,  8.207046388370087E+01),
            8.6811e24)

neptune = Body(BLUE,3.88/5,
                Vector3(2.976877605000455E+01, -2.750966044048722E+00, -6.294024336722218E-01)*AU,
                Vector3(4.643812712803050E+02,  5.444339754400878E+03, -1.230818583920708E+02),
                1.02409e26) 

saturn = Body(BROWN,9.45/5,
                Vector3(8.305195501443066E+00, -5.220660638189502E+00, -2.398939811841545E-01)*AU,
                Vector3(4.600536590796957E+03,  8.158326300996555E+03, -3.244831811891196E+02),
                5.683e26)

# all simulated entities 
bodies = [sun,mercury,venus,earth,mars,jupiter,saturn,uranus,neptune] 

glEnable(GL_DEPTH_TEST)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
glClearColor(0,0.1,0.1,1)

# event loop
while not glfw.window_should_close(window) :
    
    # delta time
    current_frame_time = glfw.get_time()
    delta_time = current_frame_time - last_frame
    last_frame = current_frame_time
    frame_count += 1

    if (current_frame_time - anchor_time) >= 1.0 :
        print('Avg. FPS :',frame_count)
        frame_count = 0
        anchor_time = current_frame_time
        
    # key presses
    process_input(window,delta_time)
    
    # begin drawing
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
    # update view and projection matrices from camera manipulation
    view = main_camera.getViewMatrix()
    projection = glm.perspective(glm.radians(main_camera.Zoom), width/height, 0.1,1500.0)
    
    # set uniforms (maybe make this a loop for a shader collection)
    sphere_shader.setMat4('view',view)
    orbits_shader.setMat4('view',view)
    sphere_shader.setMat4('projection',projection)
    orbits_shader.setMat4('projection',projection)
    
    sphere_shader.setFloat('iTime',glfw.get_time())

    # -------------------------------------------------------- SIM -------------------------------------------------------- #
    update_bodies_rungekutta(bodies,delta_time)
    
    for body in bodies :
        body.draw(sphere_shader,scale)
        body.draw_orbit(orbits_shader,scale)
    
    # swap back and front pages
    glBindVertexArray(0)
    glfw.poll_events()
    glfw.swap_buffers(window)

# free resources
glfw.terminate()