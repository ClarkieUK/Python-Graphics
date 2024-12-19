import numpy as np
from vector import Vector3
from math_functions import *

def newtonian_gravitation(t : float, Y_in : np.array) -> np.array : # cant decide between numpy or lists...
    
    # Y_in holds the velocity,acceleration,mass for each body.
    Y_out = np.array([])
    number_of_elements = 3
    number_of_bodies = int(len(Y_in)/number_of_elements) 
    
    # Compute acceleration on i'th body from all j'th bodies , do for all bodies
    for i in range(number_of_bodies) :
        
        v = Y_in[i * number_of_elements + 1]
        a = Vector3(0,0,0)
        
        for j in range(number_of_bodies) :
            if i == j :
                continue # Skip self computation
            else : 
                a = a + acceleration(Y_in[i * number_of_elements + 0],Y_in[j * number_of_elements + 0],Y_in[j * number_of_elements + 2])
                
        # return rates of change of each element
        Y_out = np.append(Y_out,v)
        Y_out = np.append(Y_out,a)            
        Y_out = np.append(Y_out,0)

    return Y_out