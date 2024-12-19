from odes import newtonian_gravitation
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
    
def reset(bodies : list[object]) :
    # no use really :?
    for body in bodies :
        body.velocity       = 0
        body.acceleration   = 0