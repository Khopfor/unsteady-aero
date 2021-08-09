from src.util import readList
import sys
import platform
import os
import glob
sys.path.append('./src')
sys.path.append(glob.glob('./src/*'))
from util import *
from airfoil import Airfoil
from params import params
from computeCycle import computeCycle
from plot import plotComparison, plotContrib
import json

CURRENTPARAMSJSON='current-params.json'
argv=sys.argv

for naca in params['NACA']:
    for Re in params['Re']:
        for theta0 in params['theta0']:
            for x_A in params['x_A']:
                for omega in params['omega']:
                    for Ah in params['A_heaving']:
                        for phi in params['phi']:
                            for Ap in params['A_pitching']:
                                currentParams={'NACA':naca,'polarSource':params['polarSource'],'Re':Re,'theta0':theta0,'x_A':x_A,'omega':omega,'A_heaving':Ah,'phi':phi,'A_pitching':Ap}
                                with open(CURRENTPARAMSJSON,'w') as jsonFile :
                                    json.dump(currentParams,jsonFile,indent=2)
                                computeCycle(argv)
                                showTime=0 if not ("show" in argv) else int(argv[argv.index("show")+1]) if argv.index("show")+1 < len(argv) and type(int(argv[argv.index("show")+1]))==type(0) else 5
                                if 'plot' in argv and checkComparison(argv) :
                                    plotComparison(save=("save" in argv),showTime=showTime)
                                if 'plot' in argv and 'contrib' in argv :
                                    plotContrib(save=("save" in argv),showTime=showTime,comp=checkComparison(argv))
        # for p1 in params :
        #     if p1 not in ['NACA','Re'] and len(params[p1])>1:
        #         for p2 in params :
        #             if p2 not in ['NACA','Re',p1] and len(params[p2])>1: