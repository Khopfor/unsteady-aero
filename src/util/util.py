import os.path
import sys
import time
import json
import glob
import matplotlib.pyplot as plt
from scipy.special import hankel2
from scipy import optimize
import pandas as pd
from threading import Thread
from copy import deepcopy
from src.util.pathMaker import *
from src.util.maths import *
from src.util.colors import *

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


# def printParameters (Re,chord,airfoil,omega,A_heaving):
#     if omega ==0 : A=0
#     else : A=abs(2*A_heaving*chord)
#     St=airfoil.omega*A/(2*np.pi*chord)
#     phi=rad2deg(airfoil.phi)
#     X=(1-(phi<=-180 or phi>=180)*2)*(airfoil.A_theta+airfoil.theta0)/np.arctan(A_heaving*omega)
#     print("====================================================")
#     print("Steady angle of attack : ",rad2deg(airfoil.theta0),"deg")
#     print("Axis of foil : ", airfoil.x_g)
#     print("----------------------------------------------------")
#     print("Pitching : Reduced pulsation = ",airfoil.omega,"      Amplitude = ",rad2deg(airfoil.A_theta),"deg")
#     print("Heaving  : Reduced pulsation = ",omega,"      Amplitude = ",A_heaving)
#     print("Phase between wind and pitching : ", phi,"deg")
#     print("----------------------------------------------------")
#     print("Strouhal number : ",St)
#     print("Reynold number : ",Re)
#     print("Feathering parameter : ",X)
#     print("====================================================")



def checkComparison (args):
    return ("comparison" in args) or ("compare" in args) or ("comp" in args)

def prettyPrint (dict):
    s=""
    for key in dict :
        if key!="dim_quantities":
            s+='  '+key+(15-len(key))*' '
            if type(dict[key])==type(''):
                s+=dict[key]
            elif type(dict[key]) in [type(0),type(0.0)]:
                s+=str(round(dict[key],4))
            elif len(dict[key])==1:
                if type(dict[key])==type(0.0):
                    s+=str(round(dict[key][0],4))
                else :
                    s+=str(dict[key][0])
            else :
                l=dict[key]
                if type(dict[key][0])==type(0.0):
                    l=list(np.round(l,2))
                if len(l)>10:
                    l=l[:4]+["..."]+l[-4:]
                s+=str(l).replace("'",'')
            s+='\n'
    # s=s[:-1]
    print(s,end='')
    

def checkParamsFile ():
    with open(PARAMSFILE,'r') as f :
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
        if ("np." in line or "range" in line) and ":" in line and "list(" not in line :
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
    with open(PARAMSFILE,'w') as f :
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

def is_float(string):
    try :
        float(string)
        return True
    except :
        return False

def df2numpy (df,cols,flip=[]):
    array=[]
    for i,col in enumerate(cols) :
        if flip!=[] and flip[i] :
            array=np.concatenate((array,np.flip(df[col].to_numpy())))
        else :
            array=np.concatenate((array,df[col].to_numpy()))
    return array

def setShowTime(argv):
    if not ("show" in argv) :
        showTime=0.001
    elif argv.index("show")+1 < len(argv) and is_float(argv[argv.index("show")+1]):
        showTime=int(float(argv[argv.index("show")+1]))
    else :
        showTime=0
    return showTime




def ajustCurParams(curParams):
    df=pd.read_csv(filePath("data_exp"))

    T1=df["t*1"].to_numpy()
    T2=df["t*2"].to_numpy()
    T=np.concatenate([np.flip(T1),T2])
    P=np.concatenate([np.flip(df["pitch_angle"].to_numpy()),df["pitch_angle"].to_numpy()])
    H=np.concatenate([np.flip(df["h*1"].to_numpy()),df["h*2"].to_numpy()])

    def squaredError (X,Y,params,c=0):
        A,phase=params
        return np.sum(np.power(c+A*np.cos(curParams["omega"]*X+phase)-Y,2*np.ones_like(X)))

    def sqErrPitch (params):
        return squaredError(T,P,np.array(params),c=curParams["theta0"])

    def sqErrHeaving (params):
        return squaredError(T,H,np.array(params))

    opRes_p = optimize.minimize(sqErrPitch,[2,0.0],constraints=optimize.LinearConstraint(np.eye(2),[0.0,-np.pi],[20,np.pi]))
    opRes_h = optimize.minimize(sqErrHeaving,[5,0.1],constraints=optimize.LinearConstraint(np.eye(2),[-10,-np.pi],[10,np.pi]))
    A_p,phi_p=opRes_p.x
    A_h,phi_h=opRes_h.x
    curParams["A_pitching"],curParams["A_heaving"],curParams["phi"]=A_p,A_h,-rad2deg(phi_h)
    return curParams,phi_p


def changeValue (line,var,newValue):
    index=0
    if "#" in line :
        index=line.index('#')
    newLine=var+'='+newValue
    if index :
        newLine+=' '+line[index:]
    return newLine


def jokerReplace (string,sub,nbJokerChar,newSub):
    index=string.find(sub)
    if index==-1 :
        print("Error: substring not in string.")
    else :
        return string.replace(string[index:index+len(sub)+nbJokerChar],newSub)




#### Propulsive Efficiency ################################
# def eta (T,Cxi,CxN,cp):
#     CxiAv = integrate(Cxi,0,T)/T
#     CxNAv = integrate(CxN,0,T)/T
#     cpAv = integrate(cp, 0, T)/T
#     print("Mean drag coefficient : ",CxiAv)
#     print("Mean drag coefficient steady flight : ",CxNAv)
#     print("Mean moment power coefficient :",cpAv)
#     return 1-(CxiAv+cpAv)/CxNAv
###########################################################