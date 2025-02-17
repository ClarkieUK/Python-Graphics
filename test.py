import numpy as np
import matplotlib.pyplot as plt
from scipy.constants import au

mu = 1.32712440042e20 + 1.898e27/1.989e30 * 1.26686534e17

def properties(target : str) -> dict :

    _data = np.genfromtxt(f'simulation_results\{target}_TRACE.csv',delimiter=',',usecols=[1,2,3],skip_header=True) # loads i'th row for j'th component of row [i][j]
    _data_v = np.genfromtxt(f'simulation_results\{target}_TRACE.csv',delimiter=',',usecols=[4,5,6],skip_header=True) 
    
    _sun = np.genfromtxt('simulation_results\SUN_TRACE.csv',delimiter=',',usecols=[1,2,3],skip_header=True)
    _sun_v = np.genfromtxt('simulation_results\SUN_TRACE.csv',delimiter=',',usecols=[4,5,6],skip_header=True)

    # Data now heliocentric for purpose of GM param
    data = _data - _sun
    data_velocities = _data_v - _sun_v

    norms = np.linalg.norm(data,axis=-1)

    loc_min = np.argmin(norms) # perigee / perigee
    loc_max = np.argmax(norms) # apoapsis / apogee
    
    axs = plt.figure().add_subplot(projection='3d')
    axs.plot(data[:,0],data[:,1],data[:,2])
    axs.scatter(data[loc_min][0], data[loc_min][1], data[loc_min][2],color='red')
    axs.scatter(data[loc_max][0], data[loc_max][1], data[loc_max][2],color='black')
    axs.plot([0,data[loc_min][0]],[0,data[loc_min][1]],[0,data[loc_min][2]],color='red')
    axs.plot([0,data[loc_max][0]],[0,data[loc_max][1]],[0,data[loc_max][2]],color='black')
    axs.set(title=f'{target}')
    
    
    peri = np.linalg.norm(data[loc_min])
    peri_v = data[loc_min]
    apog = np.linalg.norm(data[loc_max])
    apog_v = data[loc_max]
    actual_v_peri = np.linalg.norm(data_velocities[loc_min]) 
    actual_v_apo = np.linalg.norm(data_velocities[loc_max])  

    
    e = 1 - (2/(apog/peri + 1))
    a = (peri+apog)/2
    v_apo = np.sqrt(mu * ((2/apog) - (1/a))) 
    v_peri = np.sqrt(mu * ((2/peri) - (1/a))) 

    r0 = data[2]
    
    side_1 = data[3]-r0
    side_2 = data[1]-r0
    
    unit_normal = np.cross(side_1,side_2)/np.linalg.norm(np.cross(side_1,side_2))

    return {
    "perigee": peri,
    "apogee": apog,
    "perigee_vector": peri_v,
    "apogee_vector": apog_v,
    "velocity_perigee": v_peri, 
    "velocity_apogee": v_apo,
    "velocity_perigee_trace":actual_v_peri,
    "velocity_apogee_trace":actual_v_apo,
    "eccentricity": e,
    "semi_major_axis": a,
    "plane_normal": unit_normal,
    "r0":r0
    }
    
earth_info = properties('EARTH')
print('\n')
mars_info = properties('MARS')

print(np.arccos(np.dot(earth_info['plane_normal'],mars_info['plane_normal']))*180/np.pi)

r_i = earth_info['semi_major_axis'] 
r_t = earth_info['semi_major_axis'] + (mars_info['semi_major_axis']-earth_info['semi_major_axis'])

dv1 = (mu/r_i)**(1/2) * (((2*r_t)/(r_i+r_t))**(1/2)-1)
dv2 = (mu/r_t)**(1/2) * (1-((2*r_i)/(r_i+r_t))**(1/2))

r_tf = 2 * mars_info['semi_major_axis']

print(earth_info)

plt.show()