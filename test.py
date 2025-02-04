import numpy as np
import matplotlib.pyplot as plt
from scipy.constants import au

mu = 1.32712440042e20

def properties(target : str) -> dict :

    data = np.genfromtxt(f'simulation_results\{target}.csv',delimiter=',',usecols=[1,2,3],skip_header=True) # loads i'th row for j'th component of row [i][j]
    sun = np.genfromtxt('simulation_results\SUN.csv',delimiter=',',usecols=[1,2,3],skip_header=True)

    norms = np.linalg.norm(data-sun,axis=-1)

    loc_min = np.argmin(norms) # perigee / perigee
    loc_max = np.argmax(norms) # apoapsis / apogee

    """
    axs = plt.figure().add_subplot(projection='3d')

    axs.plot(data[:,0],data[:,1],data[:,2])

    axs.scatter(data[loc_min][0], data[loc_min][1], data[loc_min][2])
    axs.scatter(data[loc_max][0], data[loc_max][1], data[loc_max][2])

    axs.plot([sun[loc_min][0],data[loc_min][0]],[sun[loc_min][1],data[loc_min][1]],[sun[loc_min][2],data[loc_min][2]])
    axs.plot([sun[loc_max][0],data[loc_max][0]],[sun[loc_max][1],data[loc_max][1]],[sun[loc_max][2],data[loc_max][2]])
    """
    peri = np.linalg.norm(data[loc_min]-sun[loc_min])
    #peri_v = data[np.where(np.linalg.norm(data) == peri)]
    apog = np.linalg.norm(data[loc_max]-sun[loc_max])
    #apog_v = data[np.where(np.linalg.norm(data) == apog)]
    
    e = 1 - (2/(apog/peri + 1))
    a = (peri+apog)/2
    v_apo = np.sqrt(mu * ((2/apog) - (1/a))) 
    v_peri = np.sqrt(mu * ((2/peri) - (1/a))) 
    
    print(e,a,peri,apog)
    
    return {
    "perigee": peri,
    "apogee": apog,
    #"perigee_vector": peri_v,
    #"apogee_vector": apog_v,
    "eccentricity": e,
    "semi_major_axis": a,
    "velocity_apogee": v_apo,
    "velocity_perigee": v_peri    
    }
    
earth_info = properties('EARTH')
mars_info = properties('MARS')

#angle_b = np.arccos(np.dot(earth_info['perigee_vector'],mars_info['apogee_vector'])/(np.linalg.norm(earth_info['perigee_vector'])*np.linalg.norm(mars_info['perigee_vector']))) * 180/np.pi
#print(angle_b)

#plt.show()

r_i = earth_info['semi_major_axis'] 
r_t = earth_info['semi_major_axis'] + (mars_info['semi_major_axis']-earth_info['semi_major_axis'])

dv1 = (mu/r_i)**(1/2) * (((2*r_t)/(r_i+r_t))**(1/2)-1)
dv2 = (mu/r_t)**(1/2) * (1-((2*r_i)/(r_i+r_t))**(1/2))

r_tf = 2 * mars_info['semi_major_axis']

print(dv1,dv2)