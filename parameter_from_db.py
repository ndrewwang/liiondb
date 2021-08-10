
def function(c_e):
    import numpy as np
    # Fitting from Chen2020 Manuscript - fitted from Nyman2008
    c_e = np.array(c_e)
    c = c_e/1000 #mol/m3 to mol/L
    
    De = 8.794E-11*c**2 - 3.972E-10*c + 4.862E-10 #m2/s 
    
    return De
