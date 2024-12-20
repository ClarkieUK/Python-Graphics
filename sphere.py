import numpy as np
from OpenGL.GL import *
import glm
import glfw

class Sphere:
    def __init__(self, radius = 5.0, resolution = 10, position = glm.vec3(0,0,0)):
        self.radius = 0.3 * radius 
        self.resolution = resolution

        self.vertices               = []
        self.normals                = []
        self.tex_coords             = []
        self.indices                = []
        self.line_indices           = []
        self.interleaved_vertices   = []

        delta_theta = 2 * np.pi / resolution
        delta_phi   = np.pi / resolution
        length_inv  = 1.0 / radius

        # generate vertices, normals, and texture coordinates
        for i in range(resolution + 1):  # stacks
            phi = np.pi / 2 - i * delta_phi
            #xy = radius * np.cos(phi)
            xy = self.radius * np.cos(phi)
            #z = radius * np.sin(phi)
            y = self.radius * np.sin(phi) # xyz -> xzy

            for j in range(resolution + 1):  # sectors
                theta = j * delta_theta
                x = xy * np.cos(theta)
                z = xy * np.sin(theta) # xyz -> xzy

                # vertex
                self.vertices.extend([x, y, z]) # xyz if in right handed coord system xzy if computed in cartesian

                # normal
                nx = x * length_inv
                ny = y * length_inv
                nz = z * length_inv
                self.normals.extend([nx, ny, nz])

                # texture coordinates
                s = j / resolution
                t = i / resolution
                self.tex_coords.extend([s, t])

        # generate indices
        for i in range(resolution):
            k1 = i * (resolution + 1)
            k2 = k1 + resolution + 1

            for j in range(resolution):
                if i != 0:
                    self.indices.extend([k1, k2, k1 + 1])  # upper triangle
                if i != (resolution - 1):
                    self.indices.extend([k1 + 1, k2, k2 + 1])  # lower triangle

                # line indices
                self.line_indices.extend([k1, k2])
                if i != 0:
                    self.line_indices.extend([k1, k1 + 1])

                k1 += 1
                k2 += 1

        # interleave vertices, texture coordinates, and normals
        for i in range(len(self.vertices) // 3):
            self.interleaved_vertices.extend([
                self.vertices[3 * i], self.vertices[3 * i + 1], self.vertices[3 * i + 2],  # Vertex
                self.tex_coords[2 * i], self.tex_coords[2 * i + 1],  # Texture coords
                self.normals[3 * i], self.normals[3 * i + 1], self.normals[3 * i + 2]  # Normals
            ])

        # openGL buffers
        self.VAO = glGenVertexArrays(1)
        glBindVertexArray(self.VAO)

        self.VBO = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, len(self.interleaved_vertices)*np.dtype(np.float32).itemsize,np.array(self.interleaved_vertices, dtype=np.float32), GL_STATIC_DRAW)

        self.EBO = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(self.indices)*np.dtype(np.uint32).itemsize ,np.array(self.indices, dtype=np.uint32), GL_STATIC_DRAW)

        # set vertex attributes
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * 4, ctypes.c_void_p(0))  # Position

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 8 * 4, ctypes.c_void_p(np.dtype(np.float32).itemsize * 3))  # Texture
        
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 8 * 4, ctypes.c_void_p(np.dtype(np.float32).itemsize * 5))  # Normals

        # unbind VAO and buffers
        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
        
    def draw(self,shader, position, scale) :
        
        shader.use()
        time = glfw.get_time()
        
        # z in and out of the screen, apply xyz -> xzy and scaling transformation
        # the recently attached transformation is applied FIRST, so we attach rotation last
        model = glm.mat4(1.0)   
        model = glm.translate(model, glm.vec3(position[0]*scale,position[2]*scale,position[1]*scale))
        #model = glm.rotate(model, glm.radians(time) * 15, glm.vec3(0.0, 1.0, 0.0)) # potentially modify speed based on body attribute?
        shader.setMat4('model',model) 
        
        # bind vao containing information
        glBindVertexArray(self.VAO)
        
        # draw triangles or lines (for debug)
        glDrawElements(GL_TRIANGLE_STRIP, len(self.indices), GL_UNSIGNED_INT, ctypes.c_void_p(0))
        #glDrawElements(GL_LINE_STRIP, len(self.indices), GL_UNSIGNED_INT, ctypes.c_void_p(0))
        
        # sanitize vao
        glBindVertexArray(0)
        