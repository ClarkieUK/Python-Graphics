import math
import numpy as np
from scipy.constants import G

# vector shit
def magnitude(a : list) -> list :
    return math.sqrt(a[0]**2+a[1]**2+a[2]**2)

def position_vector(a : list , b : list ) -> list : 
    return b - a # for P->Q , Q-P

def unit_vector(a : list) -> list :
    return a * 1/magnitude(a)

def cross_product(a : list , b : list) -> list : 
    return [a[1]*b[2] - a[2]*b[1],a[2]*b[0] - a[0]*b[2],a[0]*b[1] - a[1]*b[0]]

def dot_product(a : list, b : list) -> list : 
    return [a[0]*b[0]+a[1]*b[1]+a[2]*b[2]]

def angle(a : list , b : list) -> float :
    return math.acos(dot_product(a,b)/(magnitude(a)*magnitude(b))) * 180/np.pi # return in degrees

def project(matrix,vector_input) :
    
    vector = [vector_input[0],vector_input[1],vector_input[2],1]
    
    return [
        sum(matrix[0][i] * vector[i] for i in range(4)),  # First row
        sum(matrix[1][i] * vector[i] for i in range(4)),  # Second row
        sum(matrix[2][i] * vector[i] for i in range(4)),  # Third row
        sum(matrix[3][i] * vector[i] for i in range(4))   # Fourth row
    ]
    
# physics shit
def force(a : list , b : list ,m_a : float , m_b : float) -> list :
    p = position_vector(a,b)
    return (G * m_a * m_b) / magnitude(p**2) * p

def acceleration(a , b , m_b) : 
    p = position_vector(a,b)
    return ((G * m_b)/(magnitude(p))**3) * p 

# list shit
def list_add(a : list, scalar : float) :
    return [a_i + scalar for a_i in a]

def list_subtract(a : list, scalar : float) :
    return [a_i - scalar for a_i in a]

def list_multiply(a : list, scalar : float) :
    return [a_i * scalar for a_i in a]

def list_add(a : list, scalar : float) :
    return [a_i / scalar for a_i in a]