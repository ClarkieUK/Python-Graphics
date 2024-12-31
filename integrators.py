from odes import newtonian_gravitation, newtonian_gravitation_2
import numpy as np

def update_bodies_rungekutta(bodies : list[object], delta_time : float) : # cant decide between using numpy or lists...

    Y = np.array([])
    
    fps = 1/delta_time
    
    dt = (3.154e+7) * 1/(8*fps) # 1/a of a year a second (roughly with constant fps)
    t  = 0 # no time dependence
    number_of_elements = 3 # position velocity and mass needed for roc solution space
    
    for body in bodies :
        Y = np.append(Y,body.position)
        Y = np.append(Y,body.velocity)            
        Y = np.append(Y,body.mass)

    k1 = dt * newtonian_gravitation(t,Y)
    k2 = dt * newtonian_gravitation(t+dt/2 , Y + k1/2)
    k3 = dt * newtonian_gravitation(t+dt/2 , Y + k2/2)
    k4 = dt * newtonian_gravitation(t+dt , Y + k3) 
    
    Y_out = Y + 1/6 * (k1 + 2*k2 + 2*k3 + k4) 

    # this way we've integrated the entire system at once instead
    # of a per body basis (physically incorrect)
    for i,body in enumerate(bodies) :

        body.position = Y_out[i*number_of_elements] # technically contains velocity * dt

        body.velocity = Y_out[i*number_of_elements+1] # acc * dt
    
def update_bodies_rungekutta_2(bodies_state : object, delta_time : float) : # cant decide between using numpy or lists...

    dt = (3.154e+7) * delta_time/(8)
    t  = 0 # no time dependence
    
    drs1, dvs1 = newtonian_gravitation_2(t,        bodies_state.positions,          bodies_state.velocities,          bodies_state.masses)
    drs1 *= dt; dvs1 *= dt
    drs2, dvs2 = newtonian_gravitation_2(t + dt/2, bodies_state.positions + drs1/2, bodies_state.velocities + dvs1/2, bodies_state.masses)
    drs2 *= dt; dvs2 *= dt
    drs3, dvs3 = newtonian_gravitation_2(t + dt/2, bodies_state.positions + drs2/2, bodies_state.velocities + dvs2/2, bodies_state.masses)
    drs3 *= dt; dvs3 *= dt
    drs4, dvs4 = newtonian_gravitation_2(t + dt,   bodies_state.positions + drs3,   bodies_state.velocities + dvs3,   bodies_state.masses)
    drs4 *= dt; dvs4 *= dt

    drs = 1/6 * (drs1 + 2*drs2 + 2*drs3 + drs4)
    dvs = 1/6 * (dvs1 + 2*dvs2 + 2*dvs3 + dvs4)

    for i, body in enumerate(bodies_state.bodies) :
        body.position = drs[i]
        body.velocity = dvs[i]   
    
def reset(bodies : list[object]) :
    # no use really :?
    for body in bodies :
        body.velocity       = 0
        body.acceleration   = 0