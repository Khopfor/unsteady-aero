import numpy as np
import json


### Parameters ###
# File where the parameters are set
##################


#####################################
# EDIT ZONE BEGINS ##################
#####################################

# Dimensional quantities ############
U=10 # Steady flow speed | exp U= 10
chord=0.208 # Chord of the airfoil | exp chord= 0.208
span=0.8 # Span of the airfoil | exp span= 0.8
rho=1.225 # Fluid density | air rho=1.225 | water rho=1000
S=chord*span # Surface of the airfoil
mu=1.81e-5 # Dynamic viscosity of the fluid | air mu= 1.81e-5 | water mu= 1.00e-3


# Custom functions ###################
def f2omega (f): # Computes the reduced pulsation omega with the frequency f
    return 2*np.pi*f*chord/U
    
def autoRe ():
    return rho*U*chord/mu

# Parameters #########################
parameters = {
    # NACA foil
    "NACA"                    :["0015"],
    # Reynold number                                        
    "Re"                      :[135743],
    # Source for the polars
    "polarSource"             :"xfoil",
    # Reduced pulsation
    "omega"                   :list(np.linspace(0.01,2,100)),
    # Reduced heaving amplitude
    "A_heaving"               :[0.5],
    # Mean pitch angle
    "theta0"                  :[0],
    # Normalized axis position
    "x_A"                     :[0.3],
    # Phase shift between heaving and pitching motion (theta(t)=theta0+A_pitching*exp(i(omega*t+phi))  h(t)=A_heaving*exp(i*omega*t))
    "phi"                     :[90],
    # Pitching angle amplitude
    "A_pitching"              :[6]
}
#####################################
# EDIT ZONE ENDS ####################
#####################################






parameters["dim_quantities"]={"U":U,"chord":chord,"span":span,"rho":rho,"S":S,"mu":mu}

try :
    with open("params/params.json",'w') as jsonFile :
        json.dump(parameters,jsonFile,indent=2)
except :
    print("FATAL ERROR : parameters file 'params.py' not valid.")
