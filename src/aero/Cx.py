import numpy as np
from src.util.util import *
from src.aero.Cz import Cz

class Cx ():
    current=None
    currentQS=None

    # Contributions
    Cx=0
    Cx_Bonnet=0
    steadyCxProj=0
    addedMassTerm=0
    vortexTerm=0
    AMxVTerm=0

    # Quasi-static
    Cx_qs=0

    def __init__ (self,theta,h,Cz,CxPolar):
        self.currentT=None
        self.theta=theta
        self.h=h
        self.Cz=Cz
        self.CxPolar=CxPolar

    def __call__ (self,t,model="theodorsen"):
        if self.currentT != t :
            self.computeCx(t)
            self.currentT=t
        if model in ["theodorsen","theod","tg"] :
            return self.Cx
        elif model in ["rev"]:
            return self.Cx_rev
        elif model in ["qs","quasistatic","quasi-static"]:
            return self.Cx_qs

    def computeCx (self,t):
        Cz0=self.Cz.k_alpha*self.theta.mean
        Czi=self.Cz.vortexTerm
        T1=-Cz0*self.theta.mean+self.Cz.Cz_theod*self.theta(t).real
        T2=np.pi/2*self.theta.d(t).real*(-0.25*self.theta.d(t).real+2*self.theta.mean)
        self.Cx_Bonnet = T1+T2+Czi*(-2*self.theta.mean+self.theta.d(t).real/2-Czi/self.Cz.k_alpha)
        self.Cx_tilde_rev=T1+T2+self.Cz.k_alpha*(self.theta(t).real-self.theta.mean-self.h.d(t).real+(3/4-self.Cz.x_A)*self.theta.d(t).real)*(np.pi/(2*self.Cz.k_alpha)*self.theta.d(t).real+(2*1j/np.pi*Cx.C1Func(self.theta.omega/2)*(self.h.d(t)-2*self.theta(t)+(self.Cz.x_A-1)*self.theta.d(t))+Cz.theodFunc(self.theta.omega/2)*(self.theta(t)-self.theta.mean)).real)
        alphaH=-np.arctan(self.h.d(t).real)
        alpha=alphaH+self.theta(t).real
        self.steadyCxProj=self.steadyCx(alpha)*np.cos(alphaH)
        self.Cx=self.Cx_Bonnet+self.steadyCxProj
        self.Cx_rev=self.Cx_tilde_rev+self.steadyCxProj
        steadyCzProj=-self.Cz.k_alpha*alpha*np.sin(alphaH)
        self.Cx_qs=steadyCzProj+self.steadyCxProj

    def steadyCx (self,alpha):
        if type(self.CxPolar[0]) == type(0.0) :
            return polynome(rad2deg(alpha),self.CxPolar)
        else :
            return interpolatedValue(rad2deg(alpha),self.CxPolar)

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

    def C1Func (k):
        H0= hankel2(0,k)
        H1= hankel2(1,k)
        return 1/k*np.exp(-1j*k)/(H1+1j*H0)