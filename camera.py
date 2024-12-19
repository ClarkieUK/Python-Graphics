import glm
from math import cos,sin
import pyrr

class Camera_Movement :
    FORWARD = 'FORWARD'
    BACKWARD = 'BACKWARD' 
    LEFT = 'LEFT'
    RIGHT = 'RIGHT'
    UP = 'UP'
    DOWN = 'DOWN'
    
class Camera_State :
    SPEED_UP = 'SPEED_UP'
    SLOW_DOWN = 'SLOW_DOWN'
    
class Camera() : 
    
    YAW = 0.0
    PITCH = 0.0
    SPEED = 5.0
    SENSITIVITY = 0.1
    ZOOM = 45.0
    
    def __init__(self, Position = glm.vec3(0.0,0.0,0.0),WorldUp = glm.vec3(0.0,1.0,0.0)) : # vectors
        # camera Attribs
        self.Position   = Position
        self.WorldUp    = WorldUp
        
        # euler Angles
        self.Yaw    = Camera.YAW
        self.Pitch  = Camera.PITCH
        
        # camera Options
        self.MovementSpeed      = Camera.SPEED
        self.MouseSensitivity   = Camera.SENSITIVITY
        self.Zoom               = Camera.ZOOM
        
        # calculated front, right, up
        self.updateCameraVectors() 
    
    def updateCameraVectors(self) :
        front = glm.vec3() 
        front.x = cos(glm.radians(self.Yaw)) * cos(glm.radians(self.Pitch))
        front.y = sin(glm.radians(self.Pitch))
        front.z = sin(glm.radians(self.Yaw)) * cos(glm.radians(self.Pitch))
        self.Front = glm.normalize(front)
        
        # also re-calculate the Right and Up vector
        self.Right = glm.normalize(glm.cross(self.Front, self.WorldUp))  # normalize the vectors, because their length gets closer to 0 the more you look up or down which results in slower movement.
        self.Up = glm.normalize(glm.cross(self.Right, self.Front))
    
    def getViewMatrix(self) :
         # eye pos, target, up vector
        return glm.lookAt(self.Position,self.Position + self.Front, self.Up)
    
    def processKeyboard(self, state : Camera_Movement, delta_time : float) : # movement
        
        velocity = float(self.MovementSpeed * delta_time)
        if state == Camera_Movement.FORWARD : 
            self.Position += self.Front * velocity
        if state == Camera_Movement.BACKWARD : 
            self.Position -= self.Front * velocity
        if state == Camera_Movement.LEFT : 
            self.Position -= self.Right * velocity
        if state == Camera_Movement.RIGHT : 
            self.Position += self.Right * velocity
        if state == Camera_Movement.UP : 
            self.Position += self.Up * velocity
        if state == Camera_Movement.DOWN : 
            self.Position -= self.Up * velocity
        
    
    def processKeyboardSpeed(self, state : Camera_State, delta_time : float) : # speed
        
        if state == Camera_State.SPEED_UP :
            self.MovementSpeed = self.SPEED * 4
        if state == Camera_State.SLOW_DOWN :
            self.MovementSpeed = self.SPEED 
             
    
    def processMouseMovement(self, xoffset : float, yoffset : float, constrainPitch : bool) :
        xoffset *= self.MouseSensitivity * self.Zoom / 50 
        yoffset *= self.MouseSensitivity * self.Zoom / 50 
        
        self.Yaw += xoffset 
        self.Pitch += yoffset
        
        if constrainPitch : 
            if self.Pitch > 89.0 :
                self.Pitch = 89.0
            if self.Pitch < -89.0 :
                self.Pitch = -89.0
                
        self.updateCameraVectors()
    
    def processMouseScroll(self,yoffset : float) :
        self.Zoom -= float(yoffset)
        if self.Zoom < 1.0 :
            self.Zoom = 1.0 
        if self.Zoom > 45 :
            self.Zoom = 45.0