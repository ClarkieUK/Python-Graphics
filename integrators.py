from odes import newtonian_gravitation
import numpy as np

def update_bodies_rungekutta(bodies_state : object, dt : float) -> None :
    
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
    
def update_bodies_butchers_rungekutta(bodies_state : object, dt : float) -> None : 
    
    t  = 0 # no time dependence
    
    drs1, dvs1 = newtonian_gravitation(t,        bodies_state.positions,          bodies_state.velocities,          bodies_state.masses)
    drs1 *= dt; dvs1 *= dt
    drs2, dvs2 = newtonian_gravitation(t + dt/4, bodies_state.positions + drs1/4, bodies_state.velocities + dvs1/4, bodies_state.masses)
    drs2 *= dt; dvs2 *= dt
    drs3, dvs3 = newtonian_gravitation(t + dt/4, bodies_state.positions + drs1/8 + drs2/8, 
                                                 bodies_state.velocities + dvs1/8 + dvs2/8, bodies_state.masses)
    drs3 *= dt; dvs3 *= dt
    drs4, dvs4 = newtonian_gravitation(t + dt/2, bodies_state.positions - drs2/2 + drs3,   
                                                 bodies_state.velocities - dvs2/2 + dvs3,   bodies_state.masses)
    drs4 *= dt; dvs4 *= dt
    drs5, dvs5 = newtonian_gravitation(t + 3/4 * dt, bodies_state.positions + 3/16 * drs1 + 9/16 * drs4, 
                                                     bodies_state.velocities + 3/16 * dvs1 + 9/16 * dvs4, bodies_state.masses)
    drs5 *= dt; dvs5 *= dt
    drs6, dvs6 = newtonian_gravitation(t + dt, bodies_state.positions - 3/7 * drs1 + 2/7 * drs2 + 12/7 * drs3 - 12/7 * drs4 + 8/7 * drs5,
                                               bodies_state.velocities - 3/7 * dvs1 + 2/7 * dvs2 + 12/7 * dvs3 - 12/7 * dvs4 + 8/7 * dvs5, bodies_state.masses) 
    drs6 *= dt; dvs6 *= dt
    
    drs = 1/90 * (7*drs1 + 32*drs3 + 12*drs4 + 32*drs5 + 7*drs6)
    dvs = 1/90 * (7*dvs1 + 32*dvs3 + 12*dvs4 + 32*dvs5 + 7*dvs6)
    
    pb,vb = np.linalg.norm((drs6-drs5)/drs5,axis=1), np.linalg.norm((dvs6-dvs5)/dvs5,axis=1)  
    
    print(bodies_state.bodies[pb.argmax()].ID)
    
    if (pb > 50/100).any() : #or vb.any() > 50/100 :
        update_bodies_butchers_rungekutta(bodies_state,dt/2)
        
    else :
        bodies_state.positions += drs
        bodies_state.velocities += dvs 
    
def update_bodies_fehlberg_rungekutta(bodies_state : object, dt : float) -> float :
    # https://en.wikipedia.org/wiki/Runge%E2%80%93Kutta%E2%80%93Fehlberg_method
    # https://en.wikipedia.org/wiki/Adaptive_step_size
    
    t = 0 # no time dependence
    
    drs1, dvs1 = newtonian_gravitation(t,          bodies_state.positions,
                                                   bodies_state.velocities,          
                                                   bodies_state.masses)
    drs1 *= dt; dvs1 *= dt
    drs2, dvs2 = newtonian_gravitation(t + 1/2*dt, bodies_state.positions + 1/2*drs1,
                                                   bodies_state.velocities + 1/2*dvs1, 
                                                   bodies_state.masses)
    drs2 *= dt; dvs2 *= dt
    drs3, dvs3 = newtonian_gravitation(t + 1/2*dt, bodies_state.positions + 1/4*drs1 + 1/4*drs2,
                                                   bodies_state.velocities + 1/4*dvs1 + 1/4*dvs2, 
                                                   bodies_state.masses)
    drs3 *= dt; dvs3 *= dt
    drs4, dvs4 = newtonian_gravitation(t + dt,     bodies_state.positions + 0*drs1 + (-1)*drs2 + 2*drs3,
                                                   bodies_state.velocities + 0*dvs1 + (-1)*dvs2 + 2*dvs3, 
                                                   bodies_state.masses)
    drs4 *= dt; dvs4 *= dt
    drs5, dvs5 = newtonian_gravitation(t + 2/3*dt, bodies_state.positions + 7/27*drs1 + 10/27*drs2 + 0*drs3 + 1/27*drs4,
                                                   bodies_state.velocities + 7/27*dvs1 + 10/27*dvs2 + 0*dvs3 + 1/27*dvs4, 
                                                   bodies_state.masses)
    drs5 *= dt; dvs5 *= dt
    drs6, dvs6 = newtonian_gravitation(t + 1/5*dt, bodies_state.positions + 28/625*drs1 + (-1/5)*drs2 + 546/625*drs3 + 54/625*drs4 + (-378/625)*drs5,
                                                   bodies_state.velocities + 28/625*dvs1 + (-1/5)*dvs2 + 546/625*dvs3 + 54/625*dvs4 + (-378/625)*dvs5, 
                                                   bodies_state.masses)
    drs6 *= dt; dvs6 *= dt

    drs = 1/24*drs1 + 0*drs2 + 0*drs3 + 5/48*drs4 + 27/56*drs5 + 125/336*drs6 
    dvs = 1/24*dvs1 + 0*dvs2 + 0*dvs3 + 5/48*dvs4 + 27/56*dvs5 + 125/336*dvs6 

    _drse = 1/8*drs1 + 0*drs2 + 2/3*drs3 + 1/16*drs4 + (-27/56)*drs5 + (-125/336)*drs6
    _dvse = 1/8*dvs1 + 0*dvs2 + 2/3*dvs3 + 1/16*dvs4 + (-27/56)*dvs5 + (-125/336)*dvs6

    tolerance = 1/10000

    error = np.linalg.norm(_drse, axis=(0,1))

    _dt = 0.9 * dt * ( tolerance / error) ** (1/5)

    if error > tolerance :
        update_bodies_fehlberg_rungekutta(bodies_state, _dt)

    else : 
        bodies_state.positions += drs
        bodies_state.velocities += dvs 
        
    return _dt
        
def reset(bodies_state : object) :
    # no use really :?
    for body in bodies_state.bodies :
        body.velocity       = np.array([0,0,0])
        body.acceleration   = np.array([0,0,0])