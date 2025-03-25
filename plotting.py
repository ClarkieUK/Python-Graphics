import matplotlib.pyplot as plt
import numpy as np
from scipy.constants import au

targets = ['SUN_TRACE', 'EARTH_TRACE', 'MARS_TRACE', 'SATELLITE']

fig = plt.figure()
ax = fig.add_subplot(projection='3d')

ax.set_xlabel('X (AU)')
ax.set_ylabel('Y (AU)')
ax.set_zlabel('Z (AU)')
ax.set_title('Orbit in AU Space')

all_px, all_py, all_pz = [], [], []

for target in targets:
    try :
        data = np.genfromtxt(f'simulation_results/{target}.csv', delimiter=',', skip_header=1)
    except :
        data = np.genfromtxt(f'traces/{target}.csv', delimiter=',', skip_header=1)
        
    px, py, pz = data[:, 1], data[:, 2], data[:, 3]
    
    all_px.extend(px)
    all_py.extend(py)
    all_pz.extend(pz)
    
    ax.plot(px, py, pz, label=target)  # Add label for better visualization


all_px, all_py, all_pz = np.array(all_px), np.array(all_py), np.array(all_pz)

max_range = max(all_px.ptp(), all_py.ptp(), all_pz.ptp()) / 2.0
mid_x = (all_px.max() + all_px.min()) / 2.0
mid_y = (all_py.max() + all_py.min()) / 2.0
mid_z = (all_pz.max() + all_pz.min()) / 2.0

# Set the global limits
ax.set_xlim(mid_x - max_range, mid_x + max_range)
ax.set_ylim(mid_y - max_range, mid_y + max_range)
ax.set_zlim(mid_z - max_range, mid_z + max_range)

ax.legend()  # Show labels

plt.show()