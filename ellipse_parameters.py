import numpy as np
import matplotlib.pyplot as plt
from scipy.constants import au,pi

mu = 1.32712440042e20 + 1.898e27/1.989e30 * 1.26686534e17

def properties(target : str) -> dict :

    # load positions [x,y,z] , velocities [vx,vy,vz]
    _data = np.genfromtxt(f'traces\{target}_TRACE.csv',delimiter=',',usecols=[1,2,3],skip_header=True) # loads i'th row for j'th component of row [i][j]
    _data_v = np.genfromtxt(f'traces\{target}_TRACE.csv',delimiter=',',usecols=[4,5,6],skip_header=True) 
    
    _sun = np.genfromtxt('traces\SUN_TRACE.csv',delimiter=',',usecols=[1,2,3],skip_header=True)
    _sun_v = np.genfromtxt('traces\SUN_TRACE.csv',delimiter=',',usecols=[4,5,6],skip_header=True)

    # Convert to heliocentric as we use a GM parameter for the sun + jupiter
    data = _data - _sun
    data_velocities = _data_v - _sun_v

    norms = np.linalg.norm(data,axis=-1)

    loc_min = np.argmin(norms) # perihilion / perigee
    loc_max = np.argmax(norms) # apoapsis / apogee
    
    # minimise the z coordinate in order to get the ascending node
    ascending_node = data[np.argmin(np.abs(data[:, 2]))]
    
    
    axs = plt.figure().add_subplot(projection='3d')
    axs.plot(data[:,0],data[:,1],data[:,2])
    axs.scatter(data[loc_min][0], data[loc_min][1], data[loc_min][2],color='red')
    axs.scatter(data[loc_max][0], data[loc_max][1], data[loc_max][2],color='black')
    axs.plot([0,data[loc_min][0]],[0,data[loc_min][1]],[0,data[loc_min][2]],color='red')
    axs.plot([0,data[loc_max][0]],[0,data[loc_max][1]],[0,data[loc_max][2]],color='black')
    axs.plot([0,ascending_node[0]],[0,ascending_node[1]],[0,ascending_node[2]],color='purple')
    axs.set(title=f'{target}')
    
    
    # numerically find extrema of ellipse and corresponding velocities
    peri_distance = np.linalg.norm(data[loc_min])
    peri_vector = data[loc_min]
    apog_distance = np.linalg.norm(data[loc_max])
    apog_vector = data[loc_max]
    peri_velocity = np.linalg.norm(data_velocities[loc_min]) 
    apog_velocity = np.linalg.norm(data_velocities[loc_max])  

    
    e = 1 - (2/(apog_distance/peri_distance + 1))
    a = (peri_distance+apog_distance)/2
    apog_calculated_velocity = np.sqrt(mu * ((2/apog_distance) - (1/a))) 
    peri_calculated_velocity = np.sqrt(mu * ((2/peri_distance) - (1/a))) 

    period = 2*pi*(a**3/mu)**(1/2)

    mean_motion = (2*pi)/period
    mean_motion = (mu/a**3)**(1/2)

    r0 = data[2]
    side_1 = data[3]-r0
    side_2 = data[1]-r0
    
    unit_normal = np.cross(side_1,side_2)/np.linalg.norm(np.cross(side_1,side_2))
    
    # eccentricity vectors
    eccentricity_vectors = (np.cross(data_velocities,np.cross(data,data_velocities))/mu) - data/np.linalg.norm(data,axis=-1,keepdims=True)
    
    # true anomalies
    true_anomalies = np.arccos(np.einsum('ij,ij->i', eccentricity_vectors, data)/
                               (np.linalg.norm(eccentricity_vectors,axis=-1)*np.linalg.norm(data,axis=-1))
                               )
    
    # arg of periapsis
    arg_of_periapsis = np.arccos(
        np.dot(eccentricity_vectors,ascending_node)/
        (np.linalg.norm(ascending_node,axis=-1)*np.linalg.norm(eccentricity_vectors,axis=-1))
    )
    
    #plt.plot(range(len(true_anomalies)),true_anomalies)
    #plt.show()
    
    """
    ds = np.dot((data-r0),unit_normal)
    counts, bins = np.histogram(ds)
    axs = plt.figure().add_subplot()
    axs.stairs(counts,bins)
    plt.show()
    """

    return {
    "data": data,
    "data_velocities": data_velocities,    
    "perigee": peri_distance,
    "apogee": apog_distance,
    "perigee_vector": peri_vector,
    "apogee_vector": apog_vector,
    "velocity_perigee": peri_calculated_velocity, 
    "velocity_apogee": apog_calculated_velocity,
    "velocity_perigee_trace":peri_velocity,
    "velocity_apogee_trace":apog_velocity,
    "eccentricity": e,
    "eccentricity_vectors": eccentricity_vectors,
    "semi_major_axis": a,
    "plane_normal": unit_normal,
    "r0":r0,
    "ascending_node": ascending_node,
    "true_anomalies": true_anomalies,
    "mean_motion": mean_motion,
    "argument_periapsis":arg_of_periapsis,
    }
    
earth_info = properties('EARTH')
#print('\n')
mars_info = properties('MARS')

#print(np.arccos(np.dot(earth_info['plane_normal'],mars_info['plane_normal']))*180/np.pi)

a = np.array([earth_info['apogee_vector'][0],earth_info['apogee_vector'][1]])
b = np.array([mars_info['apogee_vector'][0],mars_info['apogee_vector'][1]])

#print(np.arccos(np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b)))*180/np.pi)

r_i = earth_info['semi_major_axis'] 
r_t = earth_info['semi_major_axis'] + (mars_info['semi_major_axis']-earth_info['semi_major_axis'])

dv1 = (mu/r_i)**(1/2) * (((2*r_t)/(r_i+r_t))**(1/2)-1)
dv2 = (mu/r_t)**(1/2) * (1-((2*r_i)/(r_i+r_t))**(1/2))

r_tf = 2 * mars_info['semi_major_axis']

theta = 1.8500452432988448 * (np.pi / 180) 

theta_z = (-4) * (np.pi / 180) 

#theta = np.pi/2

rotx = np.array([[1, 0, 0],[0, np.cos(theta), -np.sin(theta)],[0, np.sin(theta), np.cos(theta)]])
roty = np.array([[np.cos(theta), 0, np.sin(theta)],[0, 1, 0],[-np.sin(theta), 0, np.cos(theta)]])
rotz = np.array([[np.cos(theta_z), -np.sin(theta_z), 0],[np.sin(theta_z), np.cos(theta_z), 0],[0, 0, 1]])

rotv = earth_info['data'][500]/np.linalg.norm(earth_info['data'][500])
rotm = np.array([[0, -rotv[2], rotv[1]],[rotv[2], 0, -rotv[0]],[-rotv[1], rotv[0], 0]])
rotm = np.array([[1,0,0],[0,1,0],[0,0,1]]) + (np.sin(theta))*rotm + (2*(np.sin(theta/2))**2)*np.dot(rotm,rotm) 


e = earth_info['eccentricity']
ws = earth_info['argument_periapsis']
fs = earth_info['true_anomalies']
n = earth_info['mean_motion']
a = earth_info['semi_major_axis']

i = 1.85004 * np.pi/180

num = 2*np.sin(i/2)*(1+e*np.cos(fs))*(n*a) 
de = (1-e**2)**(1/2)*np.cos(ws+fs)