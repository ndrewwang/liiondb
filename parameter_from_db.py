
def function(x):
    import numpy as np
    # FITTING:
    # Equations taken directly from paper
    
    U = 0.7222 + 0.13868*x + 0.028952*x**0.5 - 0.017189*(1/x) + 0.0019144*(1/(x**1.5)) + 0.28082*np.exp(15*(0.06-x)) - 0.79844*np.exp(0.44649*(x-0.92))

    return U
