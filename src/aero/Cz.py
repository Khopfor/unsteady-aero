import sys
sys.path.append('./src')
from scipy.special import hankel2
from util import *

### Lift coefficient class ###
# This class computes the lift coefficient and its contributions
##############################

class Cz ():
    currentT=None
    Cx=None

    # Contributions
    Cz=0
    Cz0=0
    addedMassTerm=0
    vortexTerm=0
    Cz_theod=0
    steadyCxProj=0

    # Quasi-static
    Cz_qs=0

    def __init__ (self,theta,h,x_A,CzPolar):
        self.theta=theta
        self.h=h
        self.x_A=x_A
        self.CzPolar=CzPolar
        self.getKAlpha()

    def __call__ (self,t,model="theodorsen"):
        if self.currentT != t :
            self.computeCz(t)
            self.currentT=t
        if model in ["theodorsen","theod"] :
            return self.Cz
        elif model in ["qs","quasistatic","quasi-static"]:
            return self.Cz_qs

    def computeCz (self,t):
        k=self.theta.omega/2
        C=self.theodFunc(k)
        self.Cz0=self.k_alpha*self.theta.mean
        self.addedMassTerm = np.pi/2*(-self.h.dd(t).real+self.theta.d(t).real+(1/2-self.x_A)*self.theta.dd(t).real)
        self.vortexTerm = (self.k_alpha*(self.theta(t)-self.theta.mean-self.h.d(t)+(3/4-self.x_A)*self.theta.d(t))*C).real
        alphaH=np.arctan(self.h.d(t).real)
        alpha=alphaH+self.theta(t).real
        self.steadyCxProj=self.Cx.steadyCx(alpha)*np.sin(alphaH)
        self.Cz_theod=self.Cz0+self.addedMassTerm+self.vortexTerm
        self.Cz=self.Cz_theod+self.steadyCxProj
        self.Cz_qs=self.k_alpha*alpha*np.cos(alphaH)+self.steadyCxProj

    def getKAlpha (self):
        i1,i2=1,0
        alphaLim=10
        while self.CzPolar[i1,0]<-alphaLim or self.CzPolar[i1-1,0]>-alphaLim : i1+=1
        while self.CzPolar[i2,0]>alphaLim or self.CzPolar[i2+1,0]<alphaLim : i2+=1
        # print(self.CzPolar[i1:i2+1,0])
        self.k_alpha=rad2deg(np.polyfit(self.CzPolar[i1:i2+1,0],self.CzPolar[i1:i2+1,1],1)[0])

    def theodFunc (self,k):
        if k==0 :
            return 1
        else :
            H0= hankel2(0,k)
            H1= hankel2(1,k)
            return H1/(H1+1j*H0)

    def plotTheodFunc (self,show=True,file=False):
        K=np.linspace(0,3,300)
        C=[self.theodFunc(k) for k in K]
        Re=[c.real for c in C]
        Im=[c.imag for c in C]
        if file :
            writeDataToFile(K,np.abs(C), "../data/theodFuncMod.txt")
            writeDataToFile(K,np.angle(C), "../data/theodFuncPhase.txt")
        if show :
            plt.plot(K,Re,label="Real part")
            # plt.plot(K,Im)
            plt.ylim(0,1)
            plt.xlabel("Reduced frequency k")
            plt.xlim(0,1)
            plt.plot(K,np.abs(C),label="Modulus")
            plt.title("Theodorsen function")
            plt.legend()
            plt.show()