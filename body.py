from vector import Vector3
from math_functions import project
import glm
import numpy as np
from sphere import Sphere
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
from shader import *


class Body:

    def __init__(self, color, radius, position, velocity, mass):

        # display
        self.radius = radius
        self.color = color

        # physics
        self.position = position
        self.velocity = velocity
        self.force = Vector3(0, 0, 0)  # using my own vector class for computation
        self.mass = mass
        self.acceleration = Vector3(0, 0, 0)

        # mesh
        self.mesh = Sphere(self.radius, 50, self.position)

        # orbit
        self.max_orbit_points = 100
        self.orbit_points = np.full((self.max_orbit_points, 3), None, dtype=np.float32)
        self.orbit_index = 0

        # orbit buffer of fixed length
        self.VBO = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(
            GL_ARRAY_BUFFER,
            self.max_orbit_points * 3 * np.dtype(np.float32).itemsize,
            None,
            GL_DYNAMIC_DRAW,
        )
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def draw(self, shader, scale):
        # drawing the body consists of just drawing the sphere
        # mesh at the bodies position
        self.mesh.draw(shader, self.position, scale)

        # pass position to an array for drawing the trail
        self.orbit_points[self.orbit_index] = [
            self.position[0] * scale,
            self.position[2] * scale,
            self.position[1] * scale,
        ]

        # cycle over the 500 index points in a circular fashion
        self.orbit_index = (self.orbit_index + 1) % self.max_orbit_points

    def draw_orbit(self, shader, scale):
        # each planet (body), has a trail , the sphere mesh doesnt. That is why
        # this method is located in the body class, doesn't require scale
        # as information passed has already been scaled.

        shader.use()
        # bind buffer then bind and send data
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)

        # sends the trailing part of the orbit to the vbo
        glBufferSubData(
            GL_ARRAY_BUFFER,
            0,
            (self.max_orbit_points - self.orbit_index)
            * 3
            * np.dtype(np.float32).itemsize,
            self.orbit_points[self.orbit_index : self.max_orbit_points],
        )

        # sends the new overwriting part of the trail to the vbo
        glBufferSubData(
            GL_ARRAY_BUFFER,
            (self.max_orbit_points - self.orbit_index)
            * 3
            * np.dtype(np.float32).itemsize,
            (self.orbit_index) * 3 * np.dtype(np.float32).itemsize,
            self.orbit_points[0 : self.orbit_index],
        )

        # set up vertex attributes
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))

        # draw orbit
        glDrawArrays(GL_LINE_STRIP, 0, self.max_orbit_points)

        # unsure if required, frees the vbo.
        glBindBuffer(GL_ARRAY_BUFFER, 0)
