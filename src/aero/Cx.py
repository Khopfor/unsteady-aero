import os
import sys
import numpy as np
sys.path.append('./src')
from util import *

class Cx ():
    current=None
    currentQS=None

    # Contributions
    Cx=0
    CxBonnet=0
    steadyCxProj=0
    addedMass=0
    vortex=0
    AMxV=0

    # Quasi-static
    Cx_qs=0

    def __init__ (self,theta,h,Cz,CxPolar):
        self.theta=theta
        self.h=h
        self.Cz=Cz
        self.CxPolar=CxPolar

    def __call__ (self,t,model="theodorsen"):
        if self.currentT != t :
            self.computeCx(t)
            self.currentT=t
        if model in ["theodorsen","theod"] :
            return self.Cx
        elif model in ["qs","quasistatic","quasi-static"]:
            return self.Cx_qs

    def computeCx (self,t):
        Cz0=self.k_alpha*self.theta.theta0
        Czi=self.Cz.getVortexTerm(t)
        T1=-Cz0*self.theta.theta0+self.Cz.Cz_theod*self.theta(t).real
        self.CxBonnet = T1+np.pi/2*self.theta.d(t).real*(-0.25*self.theta.d(t).real+2*self.theta.theta0)+Czi*(-2*self.theta.theta0+self.theta.d(t).real/2-Czi/self.Cz.k_alpha)
        alphaH=np.arctan(self.h.d(t).real)
        alpha=alphaH+self.theta(t).real
        self.steadyCxProj=self.steadyCx(alpha)*np.cos(alphaH)
        self.Cx=self.CxBonnet+self.steadyCxProj
        steadyCzProj=-self.Cz.k_alpha*np.sin(alphaH)
        Cx_qs=steadyCzProj+self.steadyCxProj

    def steadyCx (self,alpha):
        if type(self.CxPolar)==type([]) :
            if type(self.CxPolar[0]) == type(0.0) :
                return polynome(rad2deg(alpha),self.CxPolar)
            elif type(self.CxPolar[0]) == type([]) :
                return interpolatedValue(rad2deg(alpha),self.CxPolar)
        else :
            print("Error : Cx polar not defined. CxPolar is : ",self.CxPolar)

    def plotCxPolar (self):
        polarFig = plt.figure()
        # ax=polarFig.get_axes()
        # polarFig.axis.grid()
        plt.tight_layout()
        plt.plot(self.CxPolar[:,0],self.CxPolar[:,1],color='#DDFFEE', label="Cdv")
        plt.plot(self.CxPolar[:,0],self.CxPolar[:,2],color='#DDFFCC', label="Cdp")
        plt.plot(self.CxPolar[:,0],self.CxPolar[:,1]+self.CxPolar[:,2],color='#00FF00', label="Cd")
        plt.xlabel("alpha (deg)")
        plt.ylabel("Drag coefficient Cd")
        plt.legend()
        plt.grid()
        plt.show()