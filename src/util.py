import os
import os.path
import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy.special import hankel2
from scipy import optimize
import pandas as pd
from math import *
from time import sleep
import json

from params import *

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

def rotY (angle):
    return np.array([[np.cos(angle),np.sin(angle)],[-np.sin(angle),np.cos(angle)]])

def deg2rad (angle):
    return angle*np.pi/180

def rad2deg (angle):
    return angle*180/np.pi

def integrate (f,a,b,N=100):
    dx=(b-a)/N
    sum=0
    for i in range(N):
        sum+=dx*(f(a+(i+1)*dx)+f(a+i*dx))/2
    return sum


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

def zero (t):
    return 0

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



def levenbergMarquardt (f,x0,g):
   epsilon=1e-4
   x=x0
   n=f(x0).size
   def j (x):
       return g(f,x)
   lam=np.trace(np.dot(j(x),np.transpose(j(x))))*1e-3/n
   iter=0
   maxIter=10000
   while np.norm(f(x))>epsilon and iter<maxIter :
       counter=0
       accepted=False
       while not accepted :
           dx=-np.dot(np.dot(np.linalg.pinv(np.dot(np.transpose(j(x)),j(x))+lam*np.eye(n)),j(x).T),f(x))
           if np.norm(f(x+dx))<np.norm(f(x)) :
               x+=dx
               lam=lam/10
               aceepted=True
           else :
               lam*=10
           counter+=1
           if counter >100 :
               return x
   return x


def newtonVect (f,x0,jac):
    epsilon=1e-4
    c=0
    def j(x):
        return jac(f,x)
    maxIter=10000
    while np.linalg.norm(f(x0))>epsilon and c<maxIter :
        x0=np.linalg.solve(j(x0),-f(x0))+x0
        print("x0 = ",x0)
        c+=1
    if c>=maxIter :
        print ("In newton function, counter reached ",maxIter,". Best solution : x0 = ",x0,"    f(x0) = ",f(x0))
    return x0


def grad (f,x):
    h=1e-6
    g1=(f([x[0]+h,x[1]])-f(x))/h
    g2=(f([x[0],x[1]+h])-f(x))/h
    return [g1,g2]


def polynome (x,coeffs):
    y=0
    for k in range(len(coeffs)):
        y+=coeffs[k]*x**k
    return y

def interpolatedValue (x,l):
    i1=0
    i2=len(l)-1
    while i2-i1 != 1:
        m=(i2+i1)//2
        if x < l[m,0]:
            i2=m
        else :
            i1=m
    x1=l[i1,0]
    x2=l[i1+1,0]
    y1=l[i1,1]
    y2=l[i1+1,1]
    return ( (x2-x)*y1 + (x-x1)*y2 ) / (x2-x1)


def movingMean (l,p):
    mm=[]
    for i,v in enumerate(l):
        if i<=p-1 :
            mm.append(np.mean(l[:i+p+1]))
        elif i>=len(l)-p:
            mm.append(np.mean(l[i-p:]))
        else :
            mm.append(np.mean(l[i-p:i+p+1]))
    return np.array(mm)

def curParamsDict ():
    paramsStr=open('current-params.json','r').read()
    return json.loads(paramsStr)

def dirPath (dir="",source="model",polar=0) :
    curParams=curParamsDict()
    if params["polarSource"] in ["exp","expe","experiment"]:
        polarSource="exp"
    else :
        polarSource=params["polarSource"]
    path=dir+"/"*(dir!="" and dir[-1]!="/")+"NACA"+curParams["NACA"]+"_Re"+str(int(curParams["Re"]))+"_"+polarSource
    if not os.path.isdir(path) :
        os.mkdir(path)
    if polar:
        path+="/xfoil_polar"
        if not os.path.isdir(path) :
            os.mkdir(path)
        return path
    path+="/f"+("000"+str(int(curParams["omega"]*U/(2*np.pi*chord))))[-3:]+"_omega"+("000"+str(int(curParams["omega"]*100)))[-3:]+"_h"+("000"+str(int(curParams["A_heaving"]*100)))[-3:]+str(int(curParams["theta0"]))
    if not os.path.isdir(path) :
        os.mkdir(path)
    path+="/"+source
    if not os.path.isdir(path) :
        os.mkdir(path)
    return path

def filePath (dir="",source="model") :
    curParams=curParamsDict()
    path=dirPath(dir,source)
    path+="/f"+("000"+str(int(curParams["omega"]*U/(2*np.pi*chord))))[-3:]+"_omega"+("000"+str(int(curParams["omega"]*100)))[-3:]+"_h"+("000"+str(int(curParams["A_heaving"]*100)))[-3:]+"_a"+str(int(curParams["theta0"]))+"xA"+("000"+str(int(curParams["x_A"]*100)))[-3:]+"_phi"+str(int(curParams["phi"]))+"_pitch"+("000"+str(int(curParams["A_pitching"]*10)))[-3:]+".csv"
    return path



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