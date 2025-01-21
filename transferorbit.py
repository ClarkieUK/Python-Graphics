from scipy.constants import pi
def v1(mu,r1,r2) :
    return (mu/r1)**(1/2) * (((2*r2)/(r1+r2))**(1/2)-1)

def v2(mu,r1,r2) :
    return (mu/r2)**(1/2) * (1-((2*r1)/(r1+r2))**(1/2))

def t(mu,r1,r2) :
    return pi*(
        ((r1+r2)**3)/(8*mu)
        )**(1/2)