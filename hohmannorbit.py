from scipy.constants import pi
from body import Body, Bodies
import numpy as np
from ellipse_parameters import earth_info, mars_info, rotx, roty, rotz, rotm

    
class Hohmann() :
    def __init__(self,launch_location : object, launch_target : object) :
        self.launch_location = launch_location
        self.launch_target   = launch_target
        
        self.satellite = None
        self.mission_time = 0.0
        self.transfer_time = 0.0
        self.slow_down_burn = False
        self.been_launched  = False
        self.plane_changed  = False
        self.plane_realigned = False
        
        self.mu = 1.32712440042e20 + 1.898e27/1.989e30 * 1.26686534e17#1.32712440042e20
        
        self.angular_seperation = 0.0
        self.required_alignment = 99999.9999
        
    def launch(self, current_state : Bodies) : 
        launch_body = current_state.get_target(self.launch_location)
        launch_pos = launch_body.position
        launch_vel = launch_body.velocity
        
        target_body = current_state.get_target(self.launch_target)
        target_pos = target_body.position
        target_vel = target_body.velocity
        
        self.v1 = 2938.294603906249 #self.v1(np.linalg.norm(launch_pos),np.linalg.norm(target_pos))
        self.v2 = 2643.712689013453 #self.v2(np.linalg.norm(launch_pos),np.linalg.norm(target_pos))
        
        self.transfer_time = self.calculate_transfer_time(np.linalg.norm(launch_pos),np.linalg.norm(target_pos)) 
        
        self.required_alignment = (pi - (self.mu/(np.linalg.norm(target_pos))**3)**(1/2) * self.transfer_time) * 180/pi
        
        self.satellite = Body('SATELLITE',
                              np.array([255,255,255]),
                              0.2,
                              launch_pos,
                              launch_vel + self.v1 * launch_vel/np.linalg.norm(launch_vel),
                              3e3)
        
        self.sun = Body('SATELLITE_SUN',
                              current_state.get_target('SUN').color,
                              current_state.get_target('SUN').radius,
                              current_state.get_target('SUN').position,
                              current_state.get_target('SUN').velocity,
                              current_state.get_target('SUN').mass)
        
        self.bodies_state = Bodies.from_bodies([self.sun,self.satellite]) 
        
        self.dir = np.cross(launch_body.position,np.cross(target_body.velocity,target_body.position))
        self.dir = self.dir/np.linalg.norm(self.dir)
        
        
    def boost(self) :
        if self.slow_down_burn == False : 
            _v = self.bodies_state.get_target('SATELLITE').velocity
            self.bodies_state.update('velocities',-1,_v + self.v2 * _v/np.linalg.norm(_v))
            self.slow_down_burn = True
        
    def plane_change(self) :
        if self.plane_changed == False : 
            _v = self.bodies_state.get_target('SATELLITE').velocity
            self.bodies_state.update('velocities',-1,np.dot(rotm,_v))
            self.plane_changed = True 
            
    def plane_delta(self) :
        if self.plane_changed == False :     
            e = earth_info['eccentricity']
            ws = self.argument_of_periapsis()
            fs = self.true_anomaly()
            n = earth_info['mean_motion']
            a = earth_info['semi_major_axis']

            i = 1.85004 * np.pi/180

            num = 2*np.sin(i/2)*(1+e*np.cos(fs))*(n*a) 
            de = (1-e**2)**(1/2)*np.cos(ws+fs)

            delta_z = num/de
            
            _v = self.bodies_state.get_target('SATELLITE').velocity
            
            self.bodies_state.update('velocities',-1,_v + np.array([0,0,-delta_z]))
            print(-delta_z)
            self.plane_changed = True
            
    def plane_realign(self) :
        if self.plane_realigned == False : 
            _v = self.bodies_state.get_target('SATELLITE').velocity
            self.bodies_state.update('velocities',-1,np.dot(rotz,_v))
            self.plane_realigned = True  
    
    def calculate_transfer_time(self, r1, r2) :
        return pi * ((r1+r2)**3/(8*self.mu))**(1/2)

    def update_required_alignment(self, current_state : Bodies) :     
        target_body = current_state.get_target(self.launch_target)
        target_pos = target_body.position
        
        launch_body = current_state.get_target(self.launch_location)
        launch_pos = launch_body.position
        
        self.required_alignment = (pi - (self.mu/(np.linalg.norm(target_pos))**3)**(1/2) * self.calculate_transfer_time(np.linalg.norm(launch_pos),np.linalg.norm(target_pos)) ) * 180/pi

    def update_angular_seperation(self, current_state : Bodies) :
        launch_body = current_state.get_target(self.launch_location)
        launch_pos = launch_body.position
        
        target_body = current_state.get_target(self.launch_target)
        target_pos = target_body.position        

        self.angular_seperation = self.signed_angle(launch_pos, target_pos, np.array([0,0,1])) * 180/pi
    
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

    def true_anomaly(self) :
        _p = self.satellite.position
        _e = self.eccentricity_vector()
        
        return np.arccos(np.dot(_e,_p)/(np.linalg.norm(_p)*np.linalg.norm(_e)))
        
    def eccentricity_vector(self):    
        _v = self.satellite.velocity
        _p = self.satellite.position
        
        return ((np.cross(_v,np.cross(_p,_v)))/self.mu) - _p/np.linalg.norm(_p)
    
    def argument_of_periapsis(self) :
        _e = self.eccentricity_vector()
        _n = earth_info['ascending_node'] 
        
        _en = np.linalg.norm(_e)
        _nn = np.linalg.norm(_n)
        
        return 2 * np.arctan2(np.linalg.norm(_en*_n-_nn*_e),
                              np.linalg.norm(_en*_n+_nn*_e))
        
        return np.arccos(np.dot(_n,_e)/(np.linalg.norm(_n)*np.linalg.norm(_e)))