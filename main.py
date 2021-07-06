from src.util import readList
import sys
import glob
sys.path.append('./src')
sys.path.append(glob.glob('./src/*'))
from util import *
from airfoil import Airfoil
from params import params
from computeCycle import computeCycle
import json

paramsList=list(params)

print(sys.argv)

currentParamsJSON='current-params.json'

for naca in params['NACA']:
    for Re in params['Re']:
        for theta0 in params['theta0']:
            for x_A in params['x_A']:
                for omega in params['omega']:
                    for Ah in params['A_heaving']:
                        for phi in params['phi']:
                            for Ap in params['A_pitching']:
                                currentParams={'NACA':naca,'polarSource':params['polarSource'],'Re':Re,'theta0':theta0,'x_A':x_A,'omega':omega,'A_heaving':Ah,'phi':phi,'A_pitching':Ap}
                                with open(currentParamsJSON,'w') as jsonFile :
                                    json.dump(currentParams,jsonFile,indent=2)
                                computeCycle(sys.argv)
                                # if 'plot' in sys.argv :
                                #     pass
                                # if 'anim' in sys.argv :
                                #     pass
                                # else :
                                #     print('Error : invalid command line argument')