#from math_functions import project
import glm
import numpy as np
from sphere import Sphere
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
from shader import *
from dataclasses import dataclass
from collections.abc import MutableSequence
import csv
import os

class Body:
    def __init__(self, ID, color, radius, position, velocity, mass):

        # display
        self.radius = radius
        self.color = color

        # physics
        self.position = position
        self.velocity = velocity
        self.force = np.array([0,0,0])
        self.mass = mass
        self.acceleration = np.array([0,0,0])

        # mesh
        self.mesh = Sphere(self.radius, 50, self.position)
        self.ID = ID

        # orbit
        self.max_orbit_points = 10000
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
        
        # logging
        self.file = open(os.path.join('simulation_results', self.ID+'.csv'), 'a', newline='') 
        self.writer = csv.writer(self.file)

    def draw(self, shader, scale, simming):
        # drawing the body consists of just drawing the sphere
        # mesh at the bodies position
        self.mesh.draw(shader, self.position, scale)
        
        if simming : 
            # pass position to an array for drawing the trail
            self.orbit_points[self.orbit_index] = [
                -self.position[0] * scale,
                self.position[2] * scale,
                self.position[1] * scale,
            ]

            # cycle over the 500 index points in a circular fashion
            self.orbit_index = (self.orbit_index + 1) % self.max_orbit_points

    def draw_orbit(self, shader : Shader, scale):
        # each planet (body), has a trail , the sphere mesh doesnt. That is why
        # this method is located in the body class, doesn't require scale
        # as information passed has already been scaled.

        shader.use()
        shader.setVec3('bodyColor',self.color)
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

        # set up vertex attributes for shader
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))

        # draw orbit
        glDrawArrays(GL_LINE_STRIP, 0, self.max_orbit_points)

        # frees the vbo.
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        
    def log(self,date) :
        self.writer.writerow([date,
                            self.position[0], self.position[1], self.position[2],
                            self.velocity[0], self.velocity[1], self.velocity[2]])  

class Bodies(MutableSequence):
    def __init__(self, bodies : list[Body], positions: np.array, velocities: np.array, masses: np.array) -> None:
        assert positions.shape[0] == velocities.shape[0] == masses.shape[0], "mismatched array dimensions"
        self.bodies = bodies
        self.positions = positions
        self.velocities = velocities
        self.masses = masses
        self.body_map = {body.ID: body for body in bodies}

    @classmethod
    def from_bodies(cls, bodies: list[Body]) -> 'Bodies':
        positions = np.array([body.position for body in bodies])
        velocities = np.array([body.velocity for body in bodies])
        masses = np.array([body.mass for body in bodies])
        return cls(bodies, positions, velocities, masses)
                
    def __len__(self) -> int:
        return len(self.bodies)
    
    def __getitem__(self, key) -> Body:
        body = self.bodies[key]
        body.position = self.positions[key]
        body.velocity = self.velocities[key]
        body.mass = self.masses[key]
        return body
    
    def __setitem__(self, key, index, value) -> None :
        self.__dict__[key][index] = value
        self.bodies[index] = self.__getitem__(index)
    
    def update(self, key, index, value) -> None : 
        self.__setitem__(key,index,value)
    
    def __delitem__(self, index) -> None :
        del self.bodies[index]
        del self.body_map[self.bodies[index].ID]
        self.positions = np.delete(self.positions, index, axis=0)
        self.velocities = np.delete(self.velocities, index, axis=0)
        self.masses = np.delete(self.masses, index, axis=0)
    
    def insert(self, body : Body) -> None :
        self.bodies = np.append(self.bodies, body)
        self.body_map[body.ID] = body
        self.positions = np.append(self.positions, [body.position], axis=0)
        self.velocities = np.append(self.velocities, [body.velocity], axis=0)
        self.masses = np.append(self.masses, [body.mass], axis=0)
    
    def get_target(self, target_id) -> Body :
        return self.body_map.get(target_id)
        
    def check_csvs(self) -> None :
        for body in self.bodies :
            with open(os.path.join('simulation_results', body.ID+'.csv'), 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Date-time', 'px (m)', 'py (m)', 'pz (m)', 'vx (m/s)', 'vy (m/s)', 'vz (m/s)'])  # Header row