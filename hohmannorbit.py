from scipy.constants import pi
from body import Body, Bodies
import numpy as np

    
class Hohmann() :
    def __init__(self,launch_location : object, launch_target : object) :
        self.launch_location = launch_location
        self.launch_target   = launch_target
    
        self.Satellite = None
        self.launch_time = 0
        self.bumped = False
        
        self.good = False

    def launch(self, state : Bodies) :
        
        current_sun = state.get_target('SUN')
        launch_body = state.get_target(self.launch_location)
        target_body = state.get_target(self.launch_target)
        
        launch_pos = launch_body.position
        launch_vel = launch_body.velocity
        
        target_pos       = target_body.position
        target_velocity = target_body.velocity
        
        self.Satellite = Body(
        'SATELLITE',
        np.array([255,255,255]),
        0.25,
        launch_pos,
        (launch_vel + (launch_vel/np.linalg.norm(launch_vel))*self.v1(1.3271244e20, np.linalg.norm(launch_pos), np.linalg.norm(target_pos))),
        3e3
        )
        
        self.Sun = Body(
        'PSUEDO_SUN',
        current_sun.color,
        2,
        current_sun.position,
        current_sun.velocity,
        current_sun.mass
        )
        
        self.bodies_state = Bodies.from_bodies(np.array([self.Sun,self.Satellite]))
        
        self.v2 = self.v2(1.3271244e20, np.linalg.norm(launch_pos), np.linalg.norm(target_pos))
        
        self.transfer_time = self.calculate_transfer_time(1.3271244e20, np.linalg.norm(launch_pos), np.linalg.norm(target_pos))
        
        self.optimal = pi - (1.3271244e20/np.linalg.norm(target_pos)**3)**(1/2) * self.transfer_time
        
    def check(self, state : Bodies, simulated_time) :

        launch_targetp = state.get_target(self.launch_target).position
        launch_positionp = state.get_target(self.launch_location).position
        
        print(Hohmann.angle_between(launch_positionp,launch_targetp)*180/pi)
        

        if self.launch_time > self.transfer_time and not self.bumped :
            
            unitv = state.get_target(self.launch_target).velocity / np.linalg.norm(state.get_target(self.launch_target).velocity)

            self.bodies_state.update('velocities', -1, self.Satellite.velocity + self.v2 * unitv)
            
            self.bumped = True
            
            print('bumped')
         
    def v1(self, mu, r1, r2) :
        return (mu/r1)**(1/2) * (((2*r2)/(r1+r2))**(1/2)-1)

    def v2(self, mu, r1, r2) :
        return (mu/r2)**(1/2) * (1-((2*r1)/(r1+r2))**(1/2))

    def calculate_transfer_time(self, mu, r1, r2) :
        return pi*(((r1+r2)**3)/(8*mu))**(1/2)
    
    
        test_a = np.arccos((np.dot(bodies_state.get_target('MARS').position,bodies_state.get_target('EARTH').position)) /
                           (np.linalg.norm(bodies_state.get_target('MARS').position) * np.linalg.norm(bodies_state.get_target('EARTH').position))) 
        
        if np.isclose(test_a,45,atol = 0.2) :
            print('set')
            hohmann.good = True
            
    @classmethod
    def unit_vector(cls,vector):
        """ Returns the unit vector of the vector.  """
        return vector / np.linalg.norm(vector)

    @classmethod
    def angle_between(cls,v1, v2):
        """ Returns the angle in radians between vectors 'v1' and 'v2'::

                >>> angle_between((1, 0, 0), (0, 1, 0))
                1.5707963267948966
                >>> angle_between((1, 0, 0), (1, 0, 0))
                0.0
                >>> angle_between((1, 0, 0), (-1, 0, 0))
                3.141592653589793
        """
        v1_u = Hohmann.unit_vector(v1)
        v2_u = Hohmann.unit_vector(v2)
        return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))