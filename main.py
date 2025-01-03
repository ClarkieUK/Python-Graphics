# imports

# display
from win32api import GetSystemMetrics
import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import glm
import imgui
from imgui.integrations.glfw import *
from PIL import Image

# numeracy
import numpy as np
from integrators import update_bodies_rungekutta 

# abstractions
from camera import Camera
from texture_loader import texture_load
from shader import Shader
from body import Body , Bodies
from sphere import Sphere
from vector import *

# debugging
import cProfile, pstats

profiler = cProfile.Profile()

# display
width, height = 1200, 1200

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
LIGHT_BLUE = np.array([173, 216, 230])
YELLOW = np.array([255, 255, 0])
PURPLE = np.array([203, 195, 227])
GRAY = np.array([169, 169, 169])
DIM_GRAY = np.array([16, 16, 16])
ORANGE = np.array([255, 165, 0])
BROWN = np.array([222, 184, 135])

# facts https://nssdc.gsfc.nasa.gov/planetary/planetfact.html , https://ssd.jpl.nasa.gov/tools/sbdb_lookup.html#/ , https://ssd.jpl.nasa.gov/horizons/app.html#/

G = 6.67430e-11
AU = 1.496e11
scale = 8 / AU


# callbacks
def process_input(window, delta_time):

    if (
        glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS
    ):  # we check to see if the escape is pressed in the context of the
        # window, if true then we flag the closing of glfw window
        glfw.set_window_should_close(
            window, True
        )  # GetKey returns either GLFW_RELEASE or glfw.PRESS

    # cameraSpeed = float(5.0 * delta_time)
    if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
        main_camera.processKeyboard("FORWARD", delta_time)
    if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
        main_camera.processKeyboard("BACKWARD", delta_time)
    if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
        main_camera.processKeyboard("LEFT", delta_time)
    if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
        main_camera.processKeyboard("RIGHT", delta_time)
    if glfw.get_key(window, glfw.KEY_LEFT_CONTROL) == glfw.PRESS:
        main_camera.processKeyboard("DOWN", delta_time)
    if glfw.get_key(window, glfw.KEY_SPACE) == glfw.PRESS:
        main_camera.processKeyboard("UP", delta_time)
    if glfw.get_key(window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS:
        main_camera.processKeyboardSpeed("SPEED_UP", delta_time)
    if glfw.get_key(window, glfw.KEY_LEFT_SHIFT) == glfw.RELEASE:
        main_camera.processKeyboardSpeed("SLOW_DOWN", delta_time)


def window_resize(window, width, height):
    glViewport(0, 0, width, height)


def mouse_callback(window, x_position, y_position):
    global first_mouse
    global last_x_position
    global last_y_position

    if first_mouse:
        last_x_position = x_position
        last_y_position = y_position
        first_mouse = False

    xoffset = float(x_position - last_x_position)
    yoffset = float(last_y_position - y_position)
    last_x_position = float(x_position)
    last_y_position = float(y_position)

    main_camera.processMouseMovement(xoffset, yoffset, True)


def scroll_callback(window, xoffset, yoffset):
    main_camera.processMouseScroll(yoffset)


# initialise glfw
if not glfw.init():
    raise Exception("glfw library not found...")

# create window
window = glfw.create_window(width, height, "", None, None)

# check if window creation was good
if not window:
    glfw.terminate()
    raise Exception("window dogshit")

# set window position and callbacks
xbuf, ybuf = (GetSystemMetrics(0) - width) / 2, (GetSystemMetrics(1) - height) / 2
screen_centre = (GetSystemMetrics(0)/2 , GetSystemMetrics(1)/2)
glfw.set_window_pos(window, int(xbuf), int(ybuf))
glfw.set_window_size_callback(window, window_resize)
glfw.set_cursor_pos_callback(window, mouse_callback)
glfw.set_scroll_callback(window, scroll_callback)

# set programs focus on window, all commands called after this
# effect only this window
glfw.make_context_current(window)
glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

# create shader programs
sphere_shader = Shader("pixilated_noise.vs", "pixilated_noise.fs")
orbits_shader = Shader("orbit.vs", "orbit.fs")
skybox_shader = Shader("skybox.vs","skybox.fs")

sun = Body(
    YELLOW,
    2,
    np.array([-8.974133574359094e-03, -4.482427452346882e-04, 2.127030817970091e-04]) * AU,
    np.array([2.943740906566515e-00, -1.522269030106718e01, 5.405294312927581e-02]),
    1.98892e30,
)

earth = Body(
    LIGHT_BLUE,
    1,
    np.array([-9.505921700191389e-01, 3.087952119351821e-01, 1.989011142050173e-04]) * AU,
    np.array([-9.765270895434471e03, -2.842566374064967e04, 1.340272026562062e-00]),
    5.9742e24,
)

mercury = Body(
    GRAY,
    0.383,
    np.array([2.149048126431211e-01, -3.703275102221233e-01, -5.054911078568054e-02]) * AU,
    np.array([3.194733455939798e04, 2.760819992651870e04, -6.726501719165086e02]),
    3.3e23,
)

jupiter = Body(
    BROWN,
    11.21 / 5,
    np.array([4.704772918851717e00, 1.511365399792853e00, -1.115289067637071e-01]) * AU,
    np.array([-4.142495775785003e03, 1.305304733174904e04, 3.854785819752404e01]),
    1.898e27,
)

venus = Body(
    ORANGE,
    0.949,
    np.array([3.767586589387518e-01, 6.096285845914635e-01, -1.366913498677996e-02]) * AU,
    np.array([-2.970885187788254e04, 1.854691206999238e04, 1.969344555554133e03]),
    4.8685e24,
)

mars = Body(
    RED,
    0.532,
    np.array([-7.405291211708632e-01, 1.452944259261813e00, 4.861778406962673e-02]) * AU,
    np.array([-2.072274803097698e04, -8.848861397338558e03, 3.233078954361095e02]),
    6.39e23,
)

uranus = Body(
    BLUE,
    4.01 / 5,
    np.array([1.318193324076657e01, 1.457795067541527e01, -1.166313290118892e-01]) * AU,
    np.array([-5.100987027758054e03, 4.250202813282490e03, 8.207046388370087e01]),
    8.6811e24,
)

neptune = Body(
    BLUE,
    3.88 / 5,
    np.array([2.976877605000455e01, -2.750966044048722e00, -6.294024336722218e-01]) * AU,
    np.array([4.643812712803050e02, 5.444339754400878e03, -1.230818583920708e02]),
    1.02409e26,
)

saturn = Body(
    BROWN,
    9.45 / 5,
    np.array([8.305195501443066e00, -5.220660638189502e00, -2.398939811841545e-01]) * AU,
    np.array([4.600536590796957e03, 8.158326300996555e03, -3.244831811891196e02]),
    5.683e26,
)

# all simulated entities
bodies_state = Bodies.from_bodies([sun, mercury, venus, earth, mars, jupiter, saturn, uranus, neptune])

skybox = Sphere(2500,50)

glEnable(GL_DEPTH_TEST)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
glClearColor(0, 0.1, 0.1, 1)
#glfw.swap_interval(0)

# event loop
while not glfw.window_should_close(window):
    #profiler.enable()
    # delta time
    current_frame_time = glfw.get_time()
    delta_time = current_frame_time - last_frame
    last_frame = current_frame_time
    frame_count += 1

    glfw.set_window_title(window, str(1/delta_time))

    if (current_frame_time - anchor_time) >= 1.0:
        print("Avg. FPS :", frame_count)
        frame_count = 0
        anchor_time = current_frame_time
    elif current_frame_time > 10.0:
        #glfw.set_window_should_close(window, True)
        pass

    # key presses
    process_input(window, delta_time)

    if glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS :
        bodies_state.update('positions',0,bodies_state.positions[0]+np.array([0.01,0.01,0.01])*AU)

    # begin drawing
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # update view and projection matrices from camera manipulation
    view = main_camera.getViewMatrix()
    projection = glm.perspective(
        glm.radians(main_camera.Zoom), width / height, 0.1, 1500.0
    )

    # set uniforms (maybe make this a loop for a shader collection)
    sphere_shader.setMat4("view", view)
    orbits_shader.setMat4("view", view)
    sphere_shader.setMat4("projection", projection)
    orbits_shader.setMat4("projection", projection)
    skybox_shader.setMat4("view", view)
    skybox_shader.setMat4("projection", projection)

    sphere_shader.setFloat("iTime", glfw.get_time())
    skybox_shader.setFloat("iTime", glfw.get_time())

    # -------------------------------------------------------- SIM -------------------------------------------------------- #
    update_bodies_rungekutta(bodies_state, delta_time)
    
    for body in bodies_state:
        body.draw(sphere_shader, scale)
        body.draw_orbit(orbits_shader, scale)

    skybox.draw(skybox_shader,np.array([1.0,1.0,1.0]),1)

    # swap back and front pages
    glBindVertexArray(0)
    glfw.poll_events()
    glfw.swap_buffers(window)
    #profiler.disable()

# free resources
glfw.terminate()

#stats = pstats.Stats(profiler).sort_stats("ncalls")
#stats.print_stats()
