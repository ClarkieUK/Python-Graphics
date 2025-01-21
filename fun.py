import numpy as np
G = 0
def newtonian_gravitation(t: float, positions: np.array, velocities: np.array, masses: np.array) -> tuple[np.array, np.array] : # cant decide between numpy or lists...
    drs = positions[np.newaxis] - positions[:, np.newaxis]
    norms = np.linalg.norm(drs, axis=-1)[..., np.newaxis]
    norms[norms == 0] = 1 # mitigate division by zero
    as_ = G * np.sum(masses[np.newaxis, :, np.newaxis] * drs / norms**3, axis=1)
    return np.copy(velocities), as_

v = np.array([[10,20,30],[40,50,60],[70,80,90]])
m = np.array([100,200,300])
"""
print(v[np.newaxis])
print(v[np.newaxis].shape)
print(v[:, np.newaxis])
print(v[:, np.newaxis].shape)
m = (v[np.newaxis]-v[:, np.newaxis])
print(m)
print(np.linalg.norm(m,axis=-1))
print(np.linalg.norm(m,axis=-1)[..., np.newaxis])
"""
print(v-m[np.newaxis, :, np.newaxis])