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
from integrators import update_bodies_rungekutta , update_bodies_butchers_rungekutta, update_bodies_fehlberg_rungekutta 
from datetime import datetime

# abstractions
from camera import Camera
from shader import Shader
from body   import Body , Bodies
from sphere import Sphere
from vector import *
from deltatime import TimeManager
from hohmannorbit import * 

# debugging
import cProfile, pstats
profiler = cProfile.Profile()

# display
width, height = 900, 900

# camera , sim , setup constants
main_camera = Camera()
first_mouse = True

simming = False
simming_pressed = False

launch = False
launch_pressed = False

fehlberg_timestep = (3.154e+7) * 1/(16 * 144)

G = 6.67430e-11
AU = 1.496e11
scale = 8 / AU

WHITE = np.array([1, 1, 1])
BLACK = np.array([0, 0, 0])
RED = np.array([1, 0.41, 0.38])
GREEN = np.array([0, 1, 0])
BLUE = np.array([0.00000, 0.52157, 0.89020])
LIGHT_BLUE = np.array([0.67843, 0.84706, 0.90196])
YELLOW = np.array([1, 1, 0])
PURPLE = np.array([0.79608, 0.76471, 0.89020])
GRAY = np.array([0.66275, 0.66275, 0.66275])
DIM_GRAY = np.array([0.06275, 0.06275, 0.06275])
ORANGE = np.array([1.00000, 0.64706, 0])
BROWN = np.array([0.87059, 0.72157, 0.52941])
DARK_BROWN = np.array([0.82059, 0.67157, 0.47941])

# facts https://nssdc.gsfc.nasa.gov/planetary/planetfact.html , https://ssd.jpl.nasa.gov/tools/sbdb_lookup.html#/ , https://ssd.jpl.nasa.gov/horizons/app.html#/

# callbacks
def process_input_camera(window, delta_time):

    if (glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS): 
        glfw.set_window_should_close(window, True)  

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

def process_input_sim(window, delta_time, simming, simming_pressed) :

    if glfw.get_key(window, glfw.KEY_R) == glfw.PRESS :
        if not simming_pressed :
            simming = not simming 
            simming_pressed = True
            
    if glfw.get_key(window, glfw.KEY_R) == glfw.RELEASE :
        simming_pressed = False
        
    return simming, simming_pressed

def process_input_launch(window, launch, launch_pressed) :

    if glfw.get_key(window, glfw.KEY_L) == glfw.PRESS :
        if not launch_pressed :
            launch = not launch 
            launch_pressed = True
            
    if glfw.get_key(window, glfw.KEY_L) == glfw.RELEASE :
        launch_pressed = False
        
    return launch, launch_pressed
            
def process_input_scale(window, scale) :
    if glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS :
        scale -= 0.01/AU
    if glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS :
        scale += 0.01/AU
    
    return scale
    
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
    'SUN',
    YELLOW,
    2,
    np.array([-8.572865039469250E+05, -7.346088835335051E+05, 2.685423265526889E+04],dtype=np.longdouble) * 1e3,
    np.array([1.239859639798033E-02, -6.348466611140617E-03, -2.037876555553517E-04],dtype=np.longdouble) * 1e3,
    1.98892e30,
)

earth = Body(
    'EARTH',
    LIGHT_BLUE,
    0.25,
    np.array([-2.758794880287251E+07, 1.439239583084676E+08, 1.921064327326417E+04],dtype=np.longdouble) * 1e3,
    np.array([-2.977686364628585E+01, -5.535813340802556E+00, -1.943387942073826E-04],dtype=np.longdouble) * 1e3,
    5.9742e24,
)


moon = Body(
    'MOON',
    GRAY,
    0.05,
    np.array([-2.743589644230116E+07, 1.435751546419631E+08, -1.145344989768416E+04],dtype=np.longdouble) * 1e3,
    np.array([-2.884424012475249E+01, -5.089320873036412E+00, 3.814177365090332E-02],dtype=np.longdouble) * 1e3,
    7.34767309e22,
)

mercury = Body(
    'MERCURY',
    GRAY,
    0.05,
    np.array([-5.879699189509091E+07, -2.492820404148239E+07, 3.364042452841429E+06],dtype=np.longdouble) * 1e3,
    np.array([8.711982611106873E+00, -4.284856986770977E+01, -4.299279282370732E+00],dtype=np.longdouble) * 1e3,
    3.3e23,
)

jupiter = Body(
    'JUPITER',
    DARK_BROWN,
    0.05,
    np.array([1.571230833020991E+08, 7.429840488421507E+08, -6.597049828231782E+06],dtype=np.longdouble) * 1e3,
    np.array([-1.293244436609816E+01, 3.325781476287804E+00, 2.755437569190042E-01],dtype=np.longdouble) * 1e3,
    1.898e27,
)

hektor = Body(
    'HEKTOR',
    WHITE,
    1,
    np.array([-6.397833140104287E+08, 4.247999539310665E+08, 7.136157349165726E+07],dtype=np.longdouble) * 1e3,
    np.array([-7.236765128973537E+00, -1.039386299736063E+01, -3.955885153432084E+00],dtype=np.longdouble) * 1e3,
    7.9e18,
)

io = Body(
    'IO',
    DARK_BROWN,
    0.05,
    np.array([1.567913160787357E+08, 7.427243216977766E+08, -6.610965628552347E+06],dtype=np.longdouble) * 1e3,
    np.array([-2.289626937008920E+00, -1.036623645612734E+01, -5.726257077059449E-02],dtype=np.longdouble) * 1e3,
    8.9319e22 ,
)

ganymede = Body(
    'GANYMEDE',
    DARK_BROWN,
    0.05,
    np.array([1.580935027059082E+08, 7.425362306939588E+08, -6.600282950611502E+06],dtype=np.longdouble) * 1e3,
    np.array([-8.370291186955019E+00, 1.321209554904819E+01, 7.178620386576879E-01],dtype=np.longdouble) * 1e3,
    1.4819e23 ,
)

callisto = Body(
    'CALLISTO',
    DARK_BROWN,
    0.05,
    np.array([1.557607915780463E+08, 7.442947293729103E+08, -6.574354439074993E+06],dtype=np.longdouble) * 1e3,
    np.array([-1.862955468746259E+01, -2.522420287457085E+00, 1.607200062736558E-02],dtype=np.longdouble) * 1e3,
    1.4819e23 ,
)

venus = Body(
    'VENUS',
    ORANGE,
    0.05,
    np.array([6.697319534635594E+07, 8.337171945245868E+07, -2.731933993919346E+06],dtype=np.longdouble) * 1e3,
    np.array([-2.735548307021769E+01, 2.182743070706988E+01, 1.878804135388283E+00],dtype=np.longdouble) * 1e3,
    4.8685e24,
)

mars = Body(
    'MARS',
    RED,
    0.25,
    np.array([-7.890038131682467E+07, 2.274372361241295E+08, 6.722196400986686E+06],dtype=np.longdouble) * 1e3,
    np.array([-2.199759485544059E+01, -5.787405095467102E+00, 4.184257990348734E-01],dtype=np.longdouble) * 1e3,
    6.39e23,
)

uranus = Body(
    'URANUS',
    LIGHT_BLUE,
    0.05,
    np.array([1.660222886897103E+09, 2.406966367551249E+09, -1.256907181827700E+07],dtype=np.longdouble) * 1e3,
    np.array([-5.655911180719731E+00, 3.549247278075849E+00, 8.652020191096454E-02],dtype=np.longdouble) * 1e3,
    8.6811e24,
)

neptune = Body(
    'NEPTUNE',
    BLUE,
    0.05,
    np.array([4.469116222588663E+09, -9.560778256566879E+07, -1.010264767638457E+08],dtype=np.longdouble) * 1e3,
    np.array([8.064561683471368E-02, 5.465730017544922E+00, -1.151205185674022E-01],dtype=np.longdouble) * 1e3,
    1.02409e26,
)

saturn = Body(
    'SATURN',
    BROWN,
    0.05,
    np.array([1.414498231862034E+09, -2.647172137275474E+08, -5.171551879510410E+07],dtype=np.longdouble) * 1e3,
    np.array([1.240660798615463E+00, 9.473546595187154E+00, -2.135791731559418E-01],dtype=np.longdouble) * 1e3,
    5.683e26,
)

apophis = Body(
    'APOPHIS',
    WHITE,
    0.25,
    np.array([-1.388590916653571E+07, -1.234509623050680E+08,  6.268048407716118E+06],dtype=np.longdouble) * 1e3,
    np.array([3.439172035549679E+01,  1.959859020846836E+00,  7.080954494745844E-01],dtype=np.longdouble) * 1e3,
    26.99e9,
)

phaethon = Body(
    'PHAETHON',
    WHITE,
    0.25,
    np.array([ 8.585091792232600E+07,  2.223008152743238E+08,  2.765340291757229E+07],dtype=np.longdouble) * 1e3,
    np.array([-1.447962788665931E+01, -1.281750466432390E+01, -5.476238152002450E+00],dtype=np.longdouble) * 1e3,
    140e12,
)

halley = Body(
    'HALLEY',
    WHITE,
    0.25,
    np.array([-2.743463616483468E+07,  5.418791471225091E+08, -1.217565221037149E+06],dtype=np.longdouble) * 1e3,
    np.array([-1.441794752002886E+01, -1.482371781457716E-01,  8.705224613619507E-01],dtype=np.longdouble) * 1e3,
    2.2e14,
)

pallas = Body(
    'PALLAS',
    WHITE,
    0.25,
    np.array([8.853809364617355E+07, -4.056591726129397E+08,  2.728616038316103E+08],dtype=np.longdouble) * 1e3,
    np.array([1.459429397879125E+01,  1.321865397329125E-01, -1.354242197397608E+00],dtype=np.longdouble) * 1e3,
    2.108e20,
)

cruithne = Body(
    'CRUITHNE',
    WHITE,
    0.25,
    np.array([-4.111637811442459E+07, -8.138893722436616E+07,  2.887304667707837E+07],dtype=np.longdouble) * 1e3,
    np.array([2.754848884955035E+01, -3.401272336953449E+01, -7.721202003270804E-01],dtype=np.longdouble) * 1e3,
    1.3e14,
)

adonis = Body(
    'ADONIS',
    WHITE,
    0.25,
    np.array([-2.654228146090347E+08, -3.328148809833249E+08, -8.614353902873442E+06],dtype=np.longdouble) * 1e3,
    np.array([1.231267573721459E+01,  5.659796970775487E-01,  6.479334856113178E-02],dtype=np.longdouble) * 1e3,
    0.13e12,
)

######

test_sun = Body(
    'SUN',
    YELLOW,
    2,
    np.array([0,0,0],dtype=np.longdouble) * 1e3,
    np.array([0,0,0],dtype=np.longdouble) * 1e3,
    1.98892e30,
)

test_earth = Body(
    'TEST_EARTH',
    LIGHT_BLUE,
    0.25,
    np.array([1.496e+8,0,0],dtype=np.longdouble) * 1e3,
    np.array([0,29.778,0],dtype=np.longdouble) * 1e3,
    5.9742e24
)

test_mars = Body(
    'TEST_MARS',
    RED,
    0.25,
    np.array([0,2*1.496e+8,0],dtype=np.longdouble) * 1e3,
    np.array([-21.056,0,0],dtype=np.longdouble) * 1e3,
    6.39e23,
)
# entities
#bodies_state = Bodies.from_bodies([sun, mercury, venus, earth, moon, mars, jupiter, hektor, ganymede, io, callisto, saturn, uranus, neptune])
#bodies_state = Bodies.from_bodies(np.array([sun, mercury, venus, earth, moon, mars, jupiter, saturn, uranus, neptune, apophis, phaethon, halley, cruithne, adonis]))
bodies_state = Bodies.from_bodies(np.array([sun,earth,mars]))
#bodies_state = Bodies.from_bodies(np.array([test_sun,test_earth,test_mars]))
#bodies_state.check_csvs()

skybox = Sphere(2500,15)

# opengl / glfw settings
glEnable(GL_DEPTH_TEST)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
glClearColor(0, 0, 0, 1)
glfw.swap_interval(0)  # uncap fps

satellite = Hohmann('EARTH','MARS')
# event loop
while not glfw.window_should_close(window):

    # delta time
    delta_time = TimeManager.calculate_deltatime(glfw.get_time())
    TimeManager.update_sim_date()

    # set window title as framerate
    glfw.set_window_title(window, str(1/delta_time))

    # do stuff per 1 second
    TimeManager.update_average_framerate(glfw.get_time())

    # key presses
    process_input_camera(window, delta_time)
    simming , simming_pressed = process_input_sim(window, delta_time, simming, simming_pressed)
    scale = process_input_scale(window, scale)

    # update view and projection matrices from camera manipulation
    view = main_camera.getViewMatrix()
    projection = glm.perspective(
        glm.radians(main_camera.Zoom), width / height, 0.1, 1500.0
    )

    # set uniforms (maybe make this a loop for a shader collection)
    sphere_shader.setMat4("view", view)
    orbits_shader.setMat4("view", view)
    skybox_shader.setMat4("view", view)
    sphere_shader.setMat4("projection", projection)
    orbits_shader.setMat4("projection", projection)
    skybox_shader.setMat4("projection", projection)
    
    sphere_shader.setFloat("iTime", glfw.get_time())
    skybox_shader.setFloat("iTime", glfw.get_time())
    orbits_shader.setFloat("iTime", glfw.get_time())

    # -------------------------------------------------------- SIM -------------------------------------------------------- #
    
    if simming :
        launch, launch_pressed = process_input_launch(window, launch, launch_pressed)
        satellite.update_angular_seperation(bodies_state)
        satellite.update_required_alignment(bodies_state)
        
        print(np.linalg.norm(bodies_state.get_target('EARTH').velocity))
        
        if launch :
            satellite = Hohmann('EARTH','MARS')
            satellite.launch(bodies_state)
            launch = False
        """  
        # log info for each body
        #[body.log(TimeManager.sim_date.translate({ord(','): None})) for body in bodies_state.bodies]
           
        """    
        if satellite.satellite != None :
            _ = update_bodies_fehlberg_rungekutta(satellite.bodies_state, fehlberg_timestep)
            satellite.mission_time += fehlberg_timestep
            
            #satellite.update(bodies_state)
            if glfw.get_key(window, glfw.KEY_B) == glfw.PRESS :
                satellite.update(bodies_state)
        
        
        #profiler.enable()
        fehlberg_timestep = update_bodies_fehlberg_rungekutta(bodies_state, fehlberg_timestep)
        #profiler.disable()
        
        TimeManager.simulated_time += fehlberg_timestep
    
    # begin drawing
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    for body in bodies_state:
        body.draw(sphere_shader, scale, simming)
        body.draw_orbit(orbits_shader, scale)
    
    if satellite.satellite != None :
        for body in satellite.bodies_state:
            body.draw(sphere_shader, scale, simming)
            body.draw_orbit(orbits_shader, scale)
    
    #skybox.draw(skybox_shader,np.array([0.0,0.0,0.0]),1)

    # swap back and front pages
    glfw.poll_events()
    glfw.swap_buffers(window)

# free resources
[body.file.close() for body in bodies_state.bodies]
glfw.terminate()

#stats = pstats.Stats(profiler).sort_stats("ncalls")
#stats.print_stats()
