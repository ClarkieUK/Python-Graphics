import numpy as np
from vector import Vector3
from math_functions import *

def newtonian_gravitation(t: float, positions: np.array, velocities: np.array, masses: np.array) -> tuple[np.array, np.array] : # cant decide between numpy or lists...
    drs = positions[np.newaxis] - positions[:, np.newaxis]
    norms = np.linalg.norm(drs, axis=-1)[..., np.newaxis]
    norms[norms == 0] = 1 # mitigate division by zero
    as_ = G * np.sum(masses[np.newaxis, :, np.newaxis] * drs / norms**3, axis=1)
    return np.copy(velocities), as_