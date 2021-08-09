import os
import os.path
import sys
sys.path.append('./src')
import matplotlib.pyplot as plt
from scipy.special import hankel2
from scipy import optimize
import pandas as pd
from threading import Thread
from maths import *
import json
import time
import glob

CURRENTPARAMSJSON='current-params.json'
PARAMSJSON='params.json'

def writeList (filePath,l):
    file=open(filePath,'w')
    for v in l :
        file.write(str(v)+'\n')
    file.close()

def readList (filePath):
    file=open(filePath,'r')
    lines=file.readlines()
    lines=[p[:-1] for p in lines]
    file.close()
    return lines

def findSubList (l,expr):
    res=[]
    for v in l :
        if v.find(expr) :
            res.append(v)
    return res


def subplotMaker (sub, title="",xlabel="",ylabel="",grid=False,equal=True,xlim=None,ylim=None):
    axis=plt.subplot(*sub)
    axis.set_title(title)
    axis.set_xlabel(xlabel)
    axis.set_ylabel(ylabel)
    if grid :
        axis.grid(axis = grid, ls='-')
        if xlim : axis.plot(xlim,[0,0],'-',color='grey',lw=1)
    if equal : axis.axis('equal')
    if xlim : axis.set_xlim(xlim[0],xlim[1])
    if ylim : axis.set_ylim(ylim[0],ylim[1])
    return axis

def writeDataToFile (X,Y, fileName):
    if len(X)!=len(Y):
        print("Error : X and Y have not the same length.")
    else :
        f = open(fileName,"w")
        for i in range (len(X)):
            if not isnan(X[i]) and not isnan(Y[i]) :
                f.write(str(X[i])+" "+str(Y[i])+"\n")
        f.close()


def printParameters (Re,chord,airfoil,omega,A_heaving):
    if omega ==0 : A=0
    else : A=abs(2*A_heaving*chord)
    St=airfoil.omega*A/(2*np.pi*chord)
    phi=rad2deg(airfoil.phi)
    X=(1-(phi<=-180 or phi>=180)*2)*(airfoil.A_theta+airfoil.theta0)/np.arctan(A_heaving*omega)
    print("====================================================")
    print("Steady angle of attack : ",rad2deg(airfoil.theta0),"deg")
    print("Axis of foil : ", airfoil.x_g)
    print("----------------------------------------------------")
    print("Pitching : Reduced pulsation = ",airfoil.omega,"      Amplitude = ",rad2deg(airfoil.A_theta),"deg")
    print("Heaving  : Reduced pulsation = ",omega,"      Amplitude = ",A_heaving)
    print("Phase between wind and pitching : ", phi,"deg")
    print("----------------------------------------------------")
    print("Strouhal number : ",St)
    print("Reynold number : ",Re)
    print("Feathering parameter : ",X)
    print("====================================================")



def json2Dict (jsonFile):
    s=open(jsonFile,'r').read()
    return json.loads(s)

def dirPath (dir="",folder="",polar=0,comparison=False,create=False) :
    curParams=json2Dict(CURRENTPARAMSJSON)
    params=json2Dict(PARAMSJSON)
    U=params["dim_quantities"]["U"]
    chord=params["dim_quantities"]["chord"]
    if params["polarSource"] in ["exp","expe","experiment"]:
        polarSource="exp"
    else :
        polarSource=params["polarSource"]
    path=dir+"/"*(dir!="" and dir[-1]!="/")+"NACA"+curParams["NACA"]+"_Re"+str(int(curParams["Re"]))+"_"+polarSource+comparison*"_comparison"
    if create and not os.path.isdir(path) :
        os.mkdir(path)
    if polar:
        path+="/xfoil_polar"
        if create and not os.path.isdir(path) :
            os.mkdir(path)
        return path
    f=("000"+str(int(curParams["omega"]*U/(2*np.pi*chord)*100)))[-3:]
    path+="/f"+f+"_omega"+("000"+str(int(curParams["omega"]*100)))[-3:]+"_h"+("000"+str(int(curParams["A_heaving"]*100)))[-3:]+"_a"+str(int(curParams["theta0"]))
    if create and not os.path.isdir(path) :
        os.mkdir(path) 
    path+="/f"+f+"_omega"+("000"+str(int(curParams["omega"]*100)))[-3:]+"_h"+("000"+str(int(curParams["A_heaving"]*100)))[-3:]+"_a"+str(int(curParams["theta0"]))+"_xA"+("000"+str(int(curParams["x_A"]*100)))[-3:]+"_phi"+str(int(curParams["phi"]))+"_pitch"+("000"+str(int(curParams["A_pitching"]*10)))[-3:]
    if create and not os.path.isdir(path) :
        os.mkdir(path) 
    if folder!="" :
        path+="/"+folder
        if not os.path.isdir(path) : os.mkdir(path)
    return path

def filePath (dir="",end="",ext=".csv",folder="",comparison=False,create=False) :
    curParams=json2Dict(CURRENTPARAMSJSON)
    params=json2Dict(PARAMSJSON)
    U=params["dim_quantities"]["U"]
    chord=params["dim_quantities"]["chord"]
    path=dirPath(dir,folder=folder,comparison=comparison,create=create)
    f=("000"+str(int(curParams["omega"]*U/(2*np.pi*chord)*100)))[-3:]
    path+="/"+path.split("/")[-1]+end+ext
    return path

def checkComparison (args):
    return ("comparison" in args) or ("compare" in args) or ("comp" in args)

def prettyPrint (dict):
    s=" ____________________________________________________________________\n"
    for key in dict :
        if key!="dim_quantities":
            s+='  '+key+(15-len(key))*' '
            if type(dict[key])==type(''):
                s+=dict[key]
            elif len(dict[key])==1:
                if type(dict[key])==type(0.0):
                    s+=str(round(dict[key][0],4))
                else :
                    s+=str(dict[key][0])
            else :
                if type(dict[key][0])==type(0.0):
                    s+=str(list(np.round(dict[key],2)))
                else :
                    s+=str(dict[key])
            s+='\n'
    s+=' ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾'
    # s=s[:-1]
    print(s)
    

def checkParamsFile ():
    with open('params.py','r') as f :
        content=f.readlines()
        f.close()
    # for line in ["import json","import numpy as np"]:
    #     if line not in content :
    #         content=[line]+content
    # for line in ['parameters["dim_quantities"]={"U":U,"chord":chord,"span":span,"rho":rho,"S":S,"mu":mu}','with open("params.json","w") as jsonFile :','    json.dump(parameters,jsonFile,indent=2)']:
    #     if line not in content :
    #         content.append(line)
    counter=0
    for i,line in enumerate(content) :
        if "np." in line and ":" in line and "list" not in line :
            ind=line.index(":")
            if "}" in content[i+1]:
                line=line[:ind+1]+"list("+line[ind+1:-1]+")\n"
            else :
                line=line[:ind+1]+"list("+line[ind+1:-2]+"),\n"
        if "polarSource" in line :
            line=line[:line.index(':')]+line[line.index(':'):].split(',')[0]+',\n'
            line=line.replace('[','')
            line=line.replace(']','')
        if counter!=0 :
            counter+=1
        if counter%2==1 and counter <20:
            ind=line.index(":")
            line=line[:ind]+' '*(30-len(line[:ind]))+line[ind:]
        if "parameters" in line and "=" in line and "{" in line and '[' not in line:
            counter=1
        content[i]=line
    with open('params.py','w') as f :
        f.writelines(content)
        f.close()


class FuncThread (Thread):
    def __init__(self, func,args):
        Thread.__init__(self)
        self.func=func
        self.args=args

    def run(self):
        self.func(**self.args)

def remainingTime (showTime):
    for t in range(int(showTime),-1,-1):
        sys.stdout.write("\r Remaining time before figure closing : {} seconds.".format(t))
        sys.stdout.flush()
        time.sleep(1)
    print('\n')

def is_int(string):
    try :
        int(string)
        return True
    except :
        return False

#### Propulsive Efficiency ################################
def eta (T,Cxi,CxN,cp):
    CxiAv = integrate(Cxi,0,T)/T
    CxNAv = integrate(CxN,0,T)/T
    cpAv = integrate(cp, 0, T)/T
    print("Mean drag coefficient : ",CxiAv)
    print("Mean drag coefficient steady flight : ",CxNAv)
    print("Mean moment power coefficient :",cpAv)
    return 1-(CxiAv+cpAv)/CxNAv
###########################################################