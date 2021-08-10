def function(x): 

#Functional form with 0 -a*exp(b(x-c)) terms and 2 -a*tanh(b(x-c)) terms.
#10 total terms with combinations of tanh() and exp() were attempted. 
#Fit had the lowest number of terms within 0.5 percent of the best mean-squared-error. 

 import numpy as np 
 p =[4.03980138,0.23744244,6.28599571,0.87605954,0.35813992,5.11924927,0.24474335] 
 y = p[0]  - p[1] * np.tanh(p[2] * (x - p[3])) - p[4] * np.tanh(p[5] * (x - p[6]))
 return y