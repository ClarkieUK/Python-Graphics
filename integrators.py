from odes import newtonian_gravitation
import numpy as np

def update_bodies_rungekutta(bodies_state : object, delta_time : float) : # cant decide between using numpy or lists...

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

    bodies_state.positions += drs
    bodies_state.velocities += dvs 
    
def reset(bodies_state : object) :
    # no use really :?
    for body in bodies_state.bodies :
        body.velocity       = np.array([0,0,0])
        body.acceleration   = np.array([0,0,0])