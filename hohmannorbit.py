from scipy.constants import pi
from body import Body, Bodies
import numpy as np

    
class Hohmann() :
    def __init__(self,launch_location : object, launch_target : object) :
        self.launch_location = launch_location
        self.launch_target   = launch_target
        
        self.satellite = None
        self.mission_time = 0.0
        self.transfer_time = 0.0
        self.slow_down_burn = False
        
        self.mu = 1.32712440042e20
        
    def launch(self, current_state : Bodies) : 
        launch_body = current_state.get_target(self.launch_location)
        launch_pos = launch_body.position
        launch_vel = launch_body.velocity
        
        target_body = current_state.get_target(self.launch_target)
        target_pos = target_body.position
        target_vel = target_body.velocity
        
        self.v1 = self.v1(np.linalg.norm(launch_pos),np.linalg.norm(target_pos))
        self.v2 = self.v2(np.linalg.norm(launch_pos),np.linalg.norm(target_pos))
        
        self.transfer_time = self.calculate_transfer_time(np.linalg.norm(launch_pos),np.linalg.norm(target_pos))
        
        self.satellite = Body('SATELLITE',
                              np.array([255,255,255]),
                              0.2,
                              launch_pos,
                              launch_vel + self.v1 * launch_vel/np.linalg.norm(launch_vel),
                              3e3)
        
        self.bodies_state = Bodies.from_bodies([current_state.get_target('SUN'),self.satellite]) 
        
    def update(self, current_state : Bodies) :
        if self.mission_time >= self.transfer_time and self.slow_down_burn == False :
            
            _v = self.bodies_state.get_target('SATELLITE').velocity
            self.bodies_state.update('velocities',-1,_v + self.v2 * _v/np.linalg.norm(_v))
            self.slow_down_burn = True
        
    def v1(self, r1, r2) :
        return (self.mu/r1)**(1/2) * (((2*r2)/(r1+r2))**(1/2)-1)
    
    def v2(self, r1, r2) :
        return (self.mu/r2)**(1/2) * (1-((2*r1)/(r1+r2))**(1/2))
    
    def calculate_transfer_time(self, r1, r2) :
        return pi * ((r1+r2)**3/(8*self.mu))**(1/2)
