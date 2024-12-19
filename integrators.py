from odes import newtonian_gravitation
import numpy as np

def update_bodies_rungekutta(bodies : list[object],fps) : # cant decide between using numpy or lists...

    Y = np.array([])
    
    dt = (3.154e+7) * 1/(8*144) # 1/a of a year a second
    #dt = fps
    t  = 0
    number_of_elements = 3
    
    for body in bodies :
        Y = np.append(Y,body.position)
        Y = np.append(Y,body.velocity)            
        Y = np.append(Y,body.mass)

    k1 = dt * newtonian_gravitation(t,Y)
    k2 = dt * newtonian_gravitation(t+dt/2 , Y + k1/2)
    k3 = dt * newtonian_gravitation(t+dt/2 , Y + k2/2)
    k4 = dt * newtonian_gravitation(t+dt , Y + k3) 

    Y_out = Y + 1/6 * (k1 + 2*k2 + 2*k3 + k4) # no time dependence but put there for completeness

    for i,body in enumerate(bodies) :

        body.position = Y_out[i*number_of_elements]

        body.velocity = Y_out[i*number_of_elements+1]
    
def reset(bodies : list[object]) :
    for body in bodies :
        body.velocity       = 0
        body.acceleration   = 0