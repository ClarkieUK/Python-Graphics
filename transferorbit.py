from scipy.constants import pi
from body import Body, Bodies
import numpy as np
from lambert import lambert
    
class Spaceship() :
    def __init__(self,launch_location : object, launch_target : object) :
        self.launch_location = launch_location
        self.launch_target   = launch_target
        
        self.satellite = None
        self.mission_time = 0.0
        self.transfer_time = 0.0

        self.boosted = False
        
    def launch(self, t0 : float, current_state : Bodies) : 
    
        launch_body = current_state.get_target(self.launch_location)
        launch_pos = launch_body.position
        launch_vel = launch_body.velocity
        
        target_body = current_state.get_target(self.launch_target)
        target_pos = target_body.position
        target_vel = target_body.velocity
        
        v_i, self.v_f, self.t = lambert(self.launch_location,self.launch_target, t0, launch_pos, 300)

        self.satellite = Body('SATELLITE',
                              np.array([255,255,255]),
                              0.2,
                              launch_pos,
                              v_i,
                              3e3)
        
        self.sun = Body('SATELLITE_SUN',
                              current_state.get_target('SUN').color,
                              current_state.get_target('SUN').radius,
                              current_state.get_target('SUN').position,
                              current_state.get_target('SUN').velocity,
                              current_state.get_target('SUN').mass)
        
        self.bodies_state = Bodies.from_bodies([self.sun,self.satellite]) 

    def second_impulse(self) :
        if self.boosted == False :
            self.bodies_state.update('velocities',-1,self.v_f)
            self.boosted = True