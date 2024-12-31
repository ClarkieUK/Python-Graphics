import numpy as np
import time
from body import *
from itertools import chain
from scipy.constants import G
start_time = time.time()


class t :
    def __init__(self,position,velocity,mass) :
        self.position = position 
        self.velocity = velocity 
        self.mass = mass

def position_vector(a : list , b : list ) -> list : 
    return b - a # for P->Q , Q-P

def magnitude(a : list) -> list :
    return np.abs(a)

def acceleration(a , b , m_b) : 
    p = position_vector(a,b)
    return ((G * m_b)/(magnitude(p))**3) * p 

def update_bodies_rungekutta(bodies_state : Bodies, delta_time : float) : # cant decide between using numpy or lists...

    dt = (3.154e+7) * delta_time/(8)
    t  = 0 # no time dependence
    
    drs1, dvs1 = newtonian_gravitation(t,        bodies_state.positions,          bodies_state.velocities,          bodies_state.masses)
    drs1 *= dt; dvs1 *= dt
    drs2, dvs2 = newtonian_gravitation(t + dt/2, bodies_state.positions + drs1/2, bodies_state.velocities + dvs1/2, bodies_state.masses)
    drs2 *= dt; dvs2 *= dt
    drs3, dvs3 = newtonian_gravitation(t + dt/2, bodies_state.positions + drs2/2, bodies_state.velocities + dvs2/2, bodies_state.masses)
    drs3 *= dt; dvs3 *= dt
    drs4, dvs4 = newtonian_gravitation(t + dt,   bodies_state.positions + drs3,   bodies_state.velocities + dvs3,   bodies_state.masses)
    drs4 *= dt; dvs4 *= dt

    drs = 1/6 * (drs1 + 2*drs2 + 2*drs3 + drs4)
    dvs = 1/6 * (dvs1 + 2*dvs2 + 2*dvs3 + dvs4)

    for i, body in enumerate(bodies_state.bodies) :
        body[i].position = drs[i]
        body[i].velocity = dvs[i]  

def newtonian_gravitation(t: float, positions: np.array, velocities: np.array, masses: np.array) -> tuple[np.array, np.array] : # cant decide between numpy or lists...
    drs = positions[np.newaxis] - positions[:, np.newaxis]
    norms = np.linalg.norm(drs, axis=-1)[..., np.newaxis]
    norms[norms == 0] = 1 # mitigate division by zero
    as_ = G * np.sum(masses[np.newaxis, :, np.newaxis] * drs / norms**3, axis=1)
    return np.copy(velocities), as_


b1 = Body(np.array([3,5,6]),np.array([62,12,44]),130)
b2 = Body(np.array([30,50,60]),np.array([67,12,45]),230)
b3 = Body(np.array([32,25,62]),np.array([6,312,4]),310)
b4 = Body(np.array([13,15,62]),np.array([26,12,4]),330)
b5 = Body(np.array([53,54,63]),np.array([26,122,41]),303)

bodies = Bodies.from_bodies([b1,b2,b3,b4,b5])

# start
start_time = time.time()

# Combine all data into a single 1D array without flattening or intermediate lists

update_bodies_rungekutta(bodies,1/144)

# end
end_time = time.time()

print(f'Time : {end_time-start_time:.10e}')