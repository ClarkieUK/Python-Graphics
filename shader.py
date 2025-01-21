# imports
import glfw 
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import pyrr
from PIL import *
import numpy as np
import glm

class Shader :
    def __init__ (self, vertexPath : str, fragmentPath : str) :
    # create shader 
        try : 
            with open(f'shaders/'+vertexPath) as vertexshader : 
                vertexdata = vertexshader.read()
            with open(f'shaders/'+fragmentPath) as fragmentshader : 
                fragmentdata = fragmentshader.read()
        except : 
            print("Could not load shaders! (check path)")

        try :
            self.ID = compileProgram(compileShader(vertexdata, GL_VERTEX_SHADER), 
                                    compileShader(fragmentdata, GL_FRAGMENT_SHADER))
        except :
            info = str
            glGetShaderInfoLog(self.ID,512,None,info)
            print("Could not compile shader!")

    # use
    def use(self) :
        glUseProgram(self.ID)
    
    # uniform Handling
    def setBool(self, uniform_name : str, value : bool) :

        glProgramUniform1i(self.ID,
                           glGetUniformLocation(self.ID , uniform_name),
                           int(value))
    
    def setInt(self, uniform_name : str, value : int) :

        glProgramUniform1i(self.ID,
                           glGetUniformLocation(self.ID , uniform_name),
                           int(value))
    
    def setFloat(self, uniform_name : str, value : float) :

        glProgramUniform1f(self.ID,
                           glGetUniformLocation(self.ID , uniform_name),
                           float(value))
        
    def setVec2(self, uniform_name : str, value : glm.vec2) :

        glProgramUniform2f(self.ID,
                           glGetUniformLocation(self.ID , uniform_name),
                           value[0],value[1])
        
    def setVec3(self, uniform_name : str, value : glm.vec3) :

        glProgramUniform3f(self.ID,
                           glGetUniformLocation(self.ID , uniform_name),
                           value[0],value[1],value[2])
    
    def setMat4(self,uniform_name : str, value) :
        
        glProgramUniformMatrix4fv(self.ID,
                                  glGetUniformLocation(self.ID,uniform_name),
                                  1,
                                  GL_FALSE,
                                  glm.value_ptr(value))