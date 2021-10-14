
def function(x):
    import numpy as np
    # FITTING:
    # Equations taken directly from paper appendices
    import numpy as np
    b1 = 3.85516954
    b2 = 1.247319422
    b3 = -11.15240126
    b4 = 42.8184855
    b5 = -67.71099749
    b6 = 42.50815332
    b7 = -6.13244713E-4
    b8 = -7.657419995
    b9 = 115
    
    x = 1-x
    U = b1 + b2*x + b3*x**2 + b4*x**3 + b5*x**4 + b6*x**5 + b7*np.exp(-b8*(1-x)**b9)
    return U
