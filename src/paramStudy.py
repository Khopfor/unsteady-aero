from matplotlib.pyplot import xlabel, ylabel
import pandas as pd
from os.path import exists
from glob import glob

from pandas.io.parsers import read_csv
from airfoil import *
from util import *

#### Flight parameters ###############################
nacaDigits='0015'
chord=0.205
span=0.8
U=10
rho=1.225
mu=1.85e-5
Re=1.225*U*chord/mu
qS=0.5*rho*chord*span*U**2

f=0.8
omega=2*np.pi*f*chord/U #omega_pitching=0.6 # Reduced pulsation for pitching #omega_heaving=0#omega_pitching # Reduced pulsation for heaving

A_heaving=0.1

theta0=-3
###############################################

def dirPath (dir):
    dirPath=dir
    if f>0.05 :
        dirPath+="/f"+("00"+str(floor(f*10)))[-2:]+"_h"+str(floor(A_heaving*1000))+"_a13"
        if not os.path.isdir(dirPath):
            os.mkdir(dirPath)
    return dirPath

domain={"A_theta":[0,6],"x_A":[-1,2],"phi":[-180,180]}
N=200
N_int=100
T=2*np.pi/omega

staticCaseFile="data/exp/res_pitchF005_V10_pitch15_ampl000_alpha00.txt"


def computeStudy (domain):
    A_THETA=np.linspace(domain["A_theta"][0],domain["A_theta"][1],N)
    X_A=np.linspace(domain["x_A"][0],domain["x_A"][1],N)
    PHI=np.linspace(domain["phi"][0],domain["phi"][1],N)
    airfoil_np=Airfoil(0.3,theta0,omega,0,A_heaving,90,Re,nacaDigits,CxPolarSource=staticCaseFile,CmPolarSource=staticCaseFile)
    def Cx_np(t): return airfoil_np._Cx(t)[0].real
    CT_np=integrate(Cx_np,0,T,N_int)/T
    eta=[]
    meanCx=[]
    for p1 in A_THETA :
        print(p1)
        for p2 in X_A :
            for p3 in [90] :
                airfoil=Airfoil(p2,theta0,omega,p1,A_heaving,p3,Re,nacaDigits,CxPolarSource=staticCaseFile,CmPolarSource=staticCaseFile)
                def Cx (t): return airfoil._Cx(t)[0].real
                def p (t): return airfoil._Cm(t)[0].real*airfoil.dtheta(t).real
                CT=integrate(Cx,0,T,N_int)/T
                CP=integrate(p,0,T,N_int)/T
                eta.append([p2,p1,1-(CT-CP)/CT_np])
                meanCx.append([p2,p1,CT])
    # print(eta)
    eta=np.array(eta)
    meanCx=np.array(meanCx)
    np.savetxt(dirPath("data/paramStudy")+"/efficiency_A_pitching"+str(domain["A_pitching"][0])+str(domain["A_pitching"][1])+"phi"+str(domain["phi"][0])+str(domain["phi"][1]),eta,delimiter=" ")
    np.savetxt(dirPath("data/paramStudy")+"/meanCx_A_pitching"+str(domain["A_pitching"][0])+str(domain["A_pitching"][1])+"phi"+str(domain["phi"][0])+str(domain["phi"][1]),meanCx,delimiter=" ")

# computeStudy (domain)

def plotStudy ():
    eta=np.loadtxt(dirPath("data/paramStudy")+"/efficiency_A_pitching"+str(domain["A_pitching"][0])+str(domain["A_pitching"][1])+"phi"+str(domain["phi"][0])+str(domain["phi"][1]),delimiter=" ")
    meanCx=np.loadtxt(dirPath("data/paramStudy")+"/meanCx_A_pitching"+str(domain["A_pitching"][0])+str(domain["A_pitching"][1])+"phi"+str(domain["phi"][0])+str(domain["phi"][1]),delimiter=" ")
    data_eta=[]
    data_cx=[]
    last=np.inf
    for i in range(len(eta)):
        if eta[i][1]!=last:
            data_eta=[[]]+data_eta
            data_cx=[[]]+data_cx
            last=eta[i][1]
        data_eta[0].append(eta[i][2])
        data_cx[0].append(meanCx[i][2])
    # print(data_eta)
    minAtheta=eta[0][1]
    print(minAtheta)
    maxAtheta=eta[-1][1]
    minxA=eta[0][0]
    maxxA=eta[-1][0]


    fig=plt.figure()
    ax=subplotMaker((1,2,2),"Efficiency","x_A","A_theta", equal=0)
    heatmap_eff=ax.imshow(data_eta, interpolation='nearest', extent=[-1,1,-1,1])
    ax.set_xticks(np.linspace(-1,1,5))
    ax.set_xticklabels(np.round(np.linspace(minxA,maxxA,5),decimals=2))
    ax.set_yticks(np.linspace(-1,1,int(maxAtheta)+1))
    ax.set_yticklabels(range(0,int(maxAtheta)+1))
    fig.colorbar(heatmap_eff)
    ax1=subplotMaker((1,2,1),"Mean Cx","x_A","A_theta",equal=0)
    heatmap_cx=ax1.imshow(data_cx, cmap="plasma", interpolation='nearest', extent=[-1,1,-1,1])
    ax1.set_xticks(np.linspace(-1,1,5))
    ax1.set_xticklabels(np.round(np.linspace(minxA,maxxA,5),decimals=2))
    ax1.set_yticks(np.linspace(-1,1,int(maxAtheta)+1))
    ax1.set_yticklabels(range(0,int(maxAtheta)+1))
    fig.colorbar(heatmap_cx)
    plt.show()

# plotStudy()


def studyPhi ():
    PHI=np.linspace(domain["phi"][0],domain["phi"][1],N)
    airfoil_np=Airfoil(0.3,theta0,omega,0,A_heaving,90,Re,nacaDigits,CxPolarSource=staticCaseFile,CmPolarSource=staticCaseFile)
    def Cx_np(t): return airfoil_np._Cx(t)[0].real
    CT_np=integrate(Cx_np,0,T,N_int)/T
    eta=[]
    meanCx=[]
    for phi in PHI :
        eta.append([phi])
        meanCx.append([phi])
        for Ap in [2,3,4,5,6,7]:
            airfoil=Airfoil(0.3,theta0,omega,Ap,A_heaving,phi,Re,nacaDigits,CxPolarSource=staticCaseFile,CmPolarSource=staticCaseFile)
            def Cx (t): return airfoil._Cx(t)[0].real
            def p (t): return airfoil._Cm(t)[0].real*airfoil.dtheta(t).real
            CT=np.mean([Cx(t) for t in np.linspace(0,T,N_int)])#integrate(Cx,0,T,N_int)/T
            CP=np.mean([p(t) for t in np.linspace(0,T,N_int)])#integrate(p,0,T,N_int)/T
            eta[-1].append(1-(CT-CP)/CT_np)
            meanCx[-1].append(CT)
    eta=np.array(eta)
    meanCx=np.array(meanCx).T
    for i in range (1,len(meanCx)):
        meanCx[i]=movingMean(meanCx[i],3)
    meanCx=meanCx.T
    np.savetxt(dirPath("data/paramStudy")+"/efficiency_A_pitching2-7_phi",eta,delimiter=" ")
    np.savetxt(dirPath("data/paramStudy")+"/meanCx_A_pitching2-7_phi",meanCx,delimiter=" ")

# studyPhi()

def studyxA ():
    X_A=np.linspace(domain["x_A"][0],domain["x_A"][1],N)
    # airfoil_np=Airfoil(0.3,theta0,omega,0,A_heaving,90,Re,nacaDigits,CxPolarSource=staticCaseFile,CmPolarSource=staticCaseFile)
    # def Cx_np(t): return airfoil_np._Cx(t)[0].real
    # CT_np=integrate(Cx_np,0,T,N_int)/T
    eta=[]
    meanCx=[]
    for xa in X_A :
        # eta.append([phi])
        meanCx.append([xa])
        # for Ap in [2,3,4,5,6,7]:
        airfoil=Airfoil(xa,theta0,omega,4,A_heaving,-90,Re,nacaDigits,CxPolarSource=staticCaseFile,CmPolarSource=staticCaseFile)
        def Cx (t): return airfoil._Cx(t)[0].real
        def p (t):
            # print("Cm = ",airfoil._Cm(t)[0].real,"  dtheta = ",airfoil.dtheta(t).real)
            return -airfoil._Cm(t)[0].real*airfoil.dtheta(t).real
        CT=integrate(Cx,0,T,N_int)/T
        CP=integrate(p,0,T,N_int)/T
        # eta[-1].append(1-(CT-CP)/CT_np)
        meanCx[-1].append(CT)
        meanCx[-1].append(CP)
        meanCx[-1].append(CT+CP)
    # eta=np.array(eta)
    meanCx=np.array(meanCx)#.T
    # for i in range (1,len(meanCx)):
    #     meanCx[i]=movingMean(meanCx[i],3)
    # meanCx=meanCx.T
    # np.savetxt(dirPath("data/paramStudy")+"/efficiency_A_pitching4_phi-90_x_A.dat",eta,delimiter=" ")
    np.savetxt(dirPath("data/paramStudy")+"/meanCx_A_pitching4_phi-90_x_A.dat",meanCx,delimiter=" ")

studyxA ()