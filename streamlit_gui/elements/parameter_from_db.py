
def function(x,T):
    import numpy as np
    # FITTING:
    # Equations taken directly from paper
    # Only a function of temperature and not composition
    
    R = 8.314 #J/mol.K
    
    D = 1.4523E-13*np.exp((68025.7/R)*((1/318)-(1/T)))
    D = D*(x/x) #every value is D
    return D
