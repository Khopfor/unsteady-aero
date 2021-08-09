import sys
sys.path.append('./src')
from util import *

class Cm ():
    currentT=None

    # Contributions
    Cm=0
    Cm0=0
    addedMassTerm=0
    vortexTerm=0

    #Quasi-static
    Cm_qs=0

    def __init__ (self,theta,h,Cz,x_A,x_A_polar,CmPolar):
        self.theta=theta
        self.h=h
        self.Cz=Cz
        self.x_A=x_A
        self.x_A_polar=x_A_polar
        self.CmPolar=CmPolar

    def __call__ (self,t,model="theodorsen"):
        if self.currentT != t :
            self.computeCm(t)
            self.currentT=t
        if model in ["theodorsen","theod"] :
            return self.Cm
        elif model in ["qs","quasistatic","quasi-static"]:
            return self.Cm_qs

    def computeCm (self,t):
        self.Cm0=self.getCmA_polar(self.theta.mean)
        self.addedMassTerm = np.pi/2*((1/2-self.x_A)*-self.h.dd(t).real+(3/4-self.x_A)*self.theta.d(t).real+(9/32-self.x_A+self.x_A**2)*self.theta.dd(t).real)
        self.vortexTerm = (1/4-self.x_A)*self.Cz.vortexTerm
        self.Cm=self.Cm0+self.addedMassTerm+self.vortexTerm
        alphaH=np.arctan(self.h.d(t).real)
        alpha=alphaH+self.theta(t).real
        self.Cm_qs=self.getCmA_polar(alpha)
        

    def getCmA_polar (self,alpha):
        if type(self.CmPolar[0]) == type(0.0) :
            self.CmA=polynome(rad2deg(alpha),self.CmPolarSource)
        else :
            self.CmA=interpolatedValue(rad2deg(alpha),self.CmPolar)
        return self.CmA+(self.x_A-self.x_A_polar)*self.Cz.Cz0


        # if type(self.CmPolar)==type(""):
        #     df=pd.read_csv(self.CmPolarSource)
        #     self.CmPolar=np.array([df["pitch_angle"].to_numpy(),(df["Cm1"].to_numpy()+df["Cm2"].to_numpy())/2]).T
        # elif type(self.CmPolarSource)==type([]):
        # # print("x_A = ",self.x_A,"  CmAexp = ",self.CmA, "  (self.x_A-0.3)*self.k_alpha*self.theta0 = ",(self.x_A-0.3)*self.k_alpha*self.theta0,"  CmA = ",self.CmA+(self.x_A-0.3)*self.k_alpha*self.theta0)