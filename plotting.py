import matplotlib.pyplot as plt
import numpy as np
from scipy.constants import au

targets = ['SUN','MERCURY','VENUS','EARTH','MOON','MARS']
# Date-time,px (km),py (km),pz (km),vx (km/s),vy (km/s),vz (km/s)

ax = plt.figure().add_subplot(projection='3d')

ax.set_xlabel('X (AU)')
ax.set_ylabel('Y (AU)')
ax.set_zlabel('Z (AU)')
ax.set_title('Orbit in AU Space')

for target in targets : 
    
    data = np.genfromtxt('simulation_results/'+target+'.csv',delimiter=',',skip_header=1)

    px, py, pz = data[:,1], data[:,2], data[:,3]

    max_range = max(px.ptp(), py.ptp(), pz.ptp()) / 2.0
    
    mid_x = (px.max() + px.min()) * 0.5
    mid_y = (py.max() + py.min()) * 0.5
    mid_z = (pz.max() + pz.min()) * 0.5

    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(mid_z - max_range, mid_z + max_range)

    ax.plot(px,py,pz)


plt.show()