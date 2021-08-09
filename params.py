import numpy as np
import json


### Parameters ###
# File where the parameters are set
##################


#####################################
# EDIT ZONE BEGINS ##################
#####################################

# Dimensional quantities ############
U=10 # Steady flow speed
chord=0.205 # Chord of the airfoil
span=0.8 # Span of the airfoil
rho=1.225 # Fluid density 
S=chord*span # Surface of the airfoil
mu=1.85e-5 # Fluid viscosity


# Custom functions ###################
def f2omega (f): # Computes the reduced pulsation (omega) from the frequency (f)
    return 2*np.pi*f*chord/U


# Parameters #########################
parameters = {
    # NACA foil
    "NACA"                    :["0015"],
    # Reynold number                                        
    "Re"                      :[130000],
    # Source for the polars
    "polarSource"             :"xfoil",
    # Reduced pulsation
    "omega"                   :[f2omega(1.6)],
    # Reduced heaving amplitude
    "A_heaving"               :[0.75],                        
    # Mean pitch angle
    "theta0"                  :[0],
    # Normalized axis position
    "x_A"                     :[0.3],
    # Phase shift between heaving and pitching motion (theta(t)=theta0+A_pitching*exp(i(omega*t+phi))  h(t)=A_heaving*exp(i*omega*t))
    "phi"                     :[90],
    # Pitching angle amplitude
    "A_pitching"              :[8]
}
#####################################
# EDIT ZONE ENDS ####################
#####################################






parameters["dim_quantities"]={"U":U,"chord":chord,"span":span,"rho":rho,"S":S,"mu":mu}


with open("params.json",'w') as jsonFile :
    json.dump(parameters,jsonFile,indent=2)