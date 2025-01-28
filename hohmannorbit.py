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
        self.been_launched  = False
        
        self.mu = 1.32712440042e20
        
        self.angular_seperation = 0.0
        self.required_alignment = 99999.9999
        
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
        
        self.required_alignment = (pi - (self.mu/(np.linalg.norm(target_pos))**3)**(1/2) * self.transfer_time) * 180/pi
        
        print(self.required_alignment)
        
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
            
    def update_angular_seperation(self, current_state : Bodies) :
        launch_body = current_state.get_target(self.launch_location)
        launch_pos = launch_body.position
        
        target_body = current_state.get_target(self.launch_target)
        target_pos = target_body.position        

        self.angular_seperation = self.signed_angle(launch_pos, target_pos, np.array([0,0,1])) * 180/pi
        
        
    def update_required_alignment(self, current_state : Bodies) :     
        target_body = current_state.get_target(self.launch_target)
        target_pos = target_body.position
        
        launch_body = current_state.get_target(self.launch_location)
        launch_pos = launch_body.position
        
        self.required_alignment = (pi - (self.mu/(np.linalg.norm(target_pos))**3)**(1/2) * self.calculate_transfer_time(np.linalg.norm(launch_pos),np.linalg.norm(target_pos)) ) * 180/pi
        
    def v1(self, r1, r2) :
        return (self.mu/r1)**(1/2) * (((2*r2)/(r1+r2))**(1/2)-1)
    
    def v2(self, r1, r2) :
        return (self.mu/r2)**(1/2) * (1-((2*r1)/(r1+r2))**(1/2))
    
    def calculate_transfer_time(self, r1, r2) :
        return pi * ((r1+r2)**3/(8*self.mu))**(1/2)
    
    def signed_angle(self, v1, v2, n):
        # Normalize vectors
        v1 = v1 / np.linalg.norm(v1)
        v2 = v2 / np.linalg.norm(v2)
        n = n / np.linalg.norm(n)
        
        # Compute the angle
        dot_product = np.dot(v1, v2)
        angle = np.arccos(np.clip(dot_product, -1.0, 1.0))  # Clip to avoid numerical errors
        
        # Compute the sign
        cross_product = np.cross(v1, v2)
        sign = np.sign(np.dot(cross_product, n))
        
        # Signed angle
        signed_angle = sign * angle
        return signed_angle
