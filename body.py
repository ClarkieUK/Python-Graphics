from vector import Vector3
from math_functions import project
import glm
import numpy as np
from sphere import Sphere
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
from shader import *

class Body() :
    
    def __init__(self,color,radius,position,velocity,mass) :
        
        # display
        self.radius        = radius
        self.color         = color
        self.orbit_points  = np.array([],dtype=np.float32)
        
        # physics
        self.position       = position
        self.velocity       = velocity
        self.force          = Vector3(0,0,0) # using my own vector class for computation
        self.mass           = mass
        self.acceleration   = Vector3(0,0,0)
        
        # mesh
        self.mesh = Sphere(self.radius, 50, self.position)
    
    def draw(self, shader, scale) :
        # drawing the body consists of just drawing the sphere
        # mesh at the bodies position
        self.mesh.draw(shader,self.position,scale)

        # pass position to an array for drawing the trail
        self.orbit_points = np.append(self.orbit_points,[self.position[0]*scale,self.position[2]*scale,self.position[1]*scale])
        
    def draw_orbit(self, shader, scale) : 
        # each planet (body), has a trail , the sphere mesh doesnt. That is why
        # this method is located in the body class
        shader.use()
        
        # generate buffer then bind and send data
        VBO = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, VBO)
        glBufferData(GL_ARRAY_BUFFER,self.orbit_points.nbytes,self.orbit_points,GL_STATIC_DRAW)

        # just have the form V : (x,y,z) , no colour or texture information
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))
        
        # check if there is more than one vertice
        if len(self.orbit_points) > 3:
            
            # remove old orbit information
            if len(self.orbit_points) > 1500 : 
                self.orbit_points = np.delete(self.orbit_points,[0,1,2])
                
            # draw lines
            glBegin(GL_LINES)
            for i in range(int(len(self.orbit_points)/3)) :
                glVertex3f(self.orbit_points[i*3+0],self.orbit_points[i*3+1],self.orbit_points[i*3+2])
            glEnd()
            
        # unsure if required, cleanses the vbo. (maybe attach to each body object(?))
        glInvalidateBufferData(VBO)
        