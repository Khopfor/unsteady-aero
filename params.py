import numpy as np

U=10
chord=0.205
span=0.8
rho=1.225
S=chord*span
mu=1.85e-5

params = {
    "NACA":["0015"],
    "Re":[int(rho*U*chord/mu)],
    "polarSource":"xfoil",
    "omega":[0.2],
    "A_heaving":[0.05],
    "theta0":[-3],
    "x_A":[0.3],
    "phi":[-90],
    "A_pitching":range(5)
}