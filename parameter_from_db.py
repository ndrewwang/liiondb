
def function(c_e,T):
    import numpy as np
    # FITTING:
    # Equations taken directly from paper
    
    p1 = 7.98E-1
    p2 = 2.28E2
    p3 = -1.22E0
    p4 = 5.09E-1
    p5 = -4.00E-3
    p6 = 3.79E-3
    
    c_e = np.array(c_e)
    T = np.array(T)
    
    c_e = c_e/1000 #mol/m3 to mol/L
    
    cond = p1 * (1 + (T - p2)) * c_e * ((1 + p3*np.sqrt(c_e) + p4*(1+p5*np.exp(1000/T)) * c_e) / (1 + c_e**4 * (p6*np.exp(1000/T))))
    
    cond = cond/10 #mS/cm to S/m
    
    return cond
