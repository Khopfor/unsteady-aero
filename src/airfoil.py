import sys
import glob
from src.util.util import *
# from aero import *
from src.util.expFunc import *
from src.aero.Cz import *
from src.aero.Cm import *
from src.aero.Cx import *

class Airfoil :
    airfoil=[]
    alpha_h=[0,0]
    polar=None
    # k_alpha=0.76*2*np.pi # =4.775

    def __init__ (self,x_A=0.25,theta0=0,omega=0,A_pitching=0,A_heaving=0,phi=0,Re=130000,nacaDigits='0015',phi_p=0,polarSource="xfoil",x_A_polar=0.3):
        self.x_A=x_A
        self.theta=ExpFunc(deg2rad(A_pitching),omega,phi_p,theta0)
        self.h=ExpFunc(A_heaving,omega,-phi,0)
        self.airfoil=Airfoil.NACA_4Digits(int(nacaDigits), 200)
        if polarSource == "xfoil" :
            x_A_polar=0.25
        else :
            x_A_polar=0.3


        # Aerodynamic coefficients
        self.Cz=Cz(self.theta,self.h,self.x_A,self.getPolar(polarSource,'Cz',nacaDigits,Re))
        self.Cx=Cx(self.theta,self.h,self.Cz,self.getPolar(polarSource,'Cx',nacaDigits,Re))
        self.Cz.Cx=self.Cx
        self.Cm=Cm(self.theta,self.h,self.Cz,self.x_A,x_A_polar,self.getPolar(polarSource,'Cm',nacaDigits,Re))

    def __init__ (self,params,phi_p=0):
        self.x_A=params["x_A"]
        self.theta=ExpFunc(deg2rad(params["A_pitching"]),params["omega"],phi_p,deg2rad(params["theta0"]))
        self.h=ExpFunc(params["A_heaving"],params["omega"],-deg2rad(params["phi"]),0)
        self.airfoil=Airfoil.NACA_4Digits(int(params["NACA"]), 200)
        if params["polarSource"] == "xfoil" :
            x_A_polar=0.25
        else :
            x_A_polar=0.3

        polarSource=params["polarSource"]
        if polarSource in ["exp","experiment"] :
            s="data_exp/NACA"+params["NACA"]+"_Re"+str(params["Re"])+"_exp/*_omega000_h000_a0*/*_omega000_h000_a0*/*.csv"
            l=glob.glob(s)
            if len(l)==0 :
                print("Error : experimental polar file not found at ",s)
            else :
                polarSource=l[0]

        # Aerodynamic coefficients
        self.Cz=Cz(self.theta,self.h,self.x_A,self.getPolar(polarSource,'Cz',params["NACA"],params['Re']))
        self.Cx=Cx(self.theta,self.h,self.Cz,self.getPolar(polarSource,'Cx',params["NACA"],params['Re']))
        self.Cz.Cx=self.Cx
        self.Cm=Cm(self.theta,self.h,self.Cz,self.x_A,x_A_polar,self.getPolar(polarSource,'Cm',params["NACA"],params['Re']))


    def alphaH (self,t):
        if self.alpha_h[0] != t or self.alpha_h[0] == 0 :
            self.alpha_h=[t,-np.arctan(self.h.d(t).real)]
        return self.alpha_h[1]

    def alpha (self,t):
        return self.theta(t).real+self.alphaH(t)
    
    # def computeForces (self,t):
    #     Cz_th=Cz_theod(t,self.theta,self.h,self.x_A, self.k_alpha).real
    #     self.Cm=self._Cm(t,Cz_th=Cz_th)
    #     self.Cz=self._Cz(t,Cz_th=Cz_th)
    #     self.Cx=self._Cx(t,Cz_th=Cz_th)

    def plotAirfoil (self,ax,t):
        points=np.dot(rotY(-self.alpha(t).real),self.airfoil)
        ax.plot(points[0],points[1],color='red')
        ax.axis('equal')
        # ax.grid()

    def setData (self,line,t):
        points=np.array([self.airfoil[0]+self.x_A,self.airfoil[1]])
        points=np.dot(rotY(-self.theta(t).real),points)
        line.set_data(points[0],points[1])

    def getPolar (self,polarSource,coeff,nacaDigits,Re):
        if type(polarSource)==type("") :
            if polarSource=="xfoil" :
                if type(self.polar) == type(None) :
                    polarName = dirPath("data",polar=1,create=1)+"/NACA"+nacaDigits+"_Re"+str(int(Re))+".pol"
                    if not os.path.isfile(polarName) :
                        alphaMin=-15
                        alphaMax=15
                        alphaStep = (alphaMax-alphaMin)/100
                        instFile = open("inst.in",'w') # Creates the file containing the instructions
                        instFile.write("naca"+nacaDigits+"\noper\n") # Chooses the airfoil and enters the 'OPER' mode
                        instFile.write("visc\n"+str(Re)+"\n") # Toggles viscid mode and inputs the Reynolds number
                        instFile.write("pacc\n"+polarName+"\n\n") # Enters 'PACC' mode
                        instFile.write("aseq "+str(alphaMin)+" "+str(alphaMax+alphaStep)+" "+str(alphaStep)+"\n") # Sets the alfa sequence
                        instFile.write("\n\n\nquit\n") # Quits XFoil
                        instFile.close()
                        os.system("xfoil < inst.in\n") # Gives the instruction file to XFoil
                        print("\n")
                        os.remove("inst.in")
                        os.remove(":00.bl")
                    polarFile = open(polarName,'r')
                    self.polar = np.loadtxt(polarFile,skiprows=12)
                    polarFile.close()
                if coeff == 'Cz' :
                    return np.array([self.polar[:,0],self.polar[:,1]]).T
                elif coeff == 'Cx' :
                    return np.array([self.polar[:,0] , np.sum(self.polar[:,[2,3]],axis=1).T]).T
                elif coeff == 'Cm' :
                    return np.array([self.polar[:,0],self.polar[:,4]]).T
            else :
                self.polar=pd.read_csv(polarSource)
                THETA=self.polar["pitch_angle"].to_numpy()
                n=len(THETA)
                if coeff == 'Cz' :
                    Cz1=self.polar["Cz1"].to_numpy()
                    Cz2=self.polar["Cz2"].to_numpy()
                    CZ=np.array([max(Cz1[k],Cz2[k],key=abs) for k in range(len(Cz1))])
                    return np.array([THETA,CZ]).T
                elif coeff == 'Cx' :
                    MMCX=movingMean(np.minimum(self.polar["Cx1"].to_numpy(),self.polar["Cx2"].to_numpy()),n//30)
                    return np.array([THETA,MMCX]).T
                elif coeff == 'Cm' :
                    MMCM=movingMean(np.minimum(self.polar["Cm1"].to_numpy(),self.polar["Cm2"].to_numpy()),n//50)
                    return np.array([THETA,MMCM]).T
        elif type(polarSource)==type([]) :
            print("Error : Polar source parameter is a list.")
        else :
            print("Error : Polar source not valid. Type ",type(polarSource), " instead of type string.")


    # def getCxPolar (self,nacaDigits,Re):
    #     if not os.path.isdir("polars") :
    #         os.mkdir("polars")
    #     if type(self.CxPolarSource)==type("") and self.CxPolarSource=="xfoil" :
    #         polarName = "polars/NACA"+nacaDigits+"_Re"+str(Re)+"_Cd.pol"
    #         if not os.path.isfile(polarName) :
    #             alphaMin=-15
    #             alphaMax=15
    #             # alphaMin=rad2deg(self.alpha0-self.A_alpha-np.arctan(vWindFunc[0](0).real))
    #             # alphaMax=rad2deg(self.alpha0+self.A_alpha+np.arctan(vWindFunc[0](0).real))
    #             alphaStep = (alphaMax-alphaMin)/300
    #             instFile = open("inst.in",'w') # Creates the file containing the instructions
    #             instFile.write("naca"+nacaDigits+"\noper\n") # Chooses the airfoil and enters the 'OPER' mode
    #             instFile.write("visc\n"+str(Re)+"\n") # Toggles viscid mode and inputs the Reynolds number
    #             instFile.write("pacc\n"+polarName+"\n\n") # Enters 'PACC' mode
    #             instFile.write("aseq "+str(alphaMin)+" "+str(alphaMax+alphaStep)+" "+str(alphaStep)+"\n") # Sets the alfa sequence
    #             instFile.write("\n\n\nquit\n") # Quits XFoil
    #             instFile.close()
    #             os.system("xfoil < inst.in\n") # Gives the instruction file to XFoil
    #             print("\n")
    #         polarFile = open(polarName,'r')
    #         self.CxPolar = np.loadtxt(polarFile,skiprows=12)
    #         if len(np.shape(self.CxPolar))==1:
    #             self.CxPolar=np.array([self.CxPolar[0],np.sum(self.CxPolar[2,3])])
    #         else :
    #             self.CxPolar=np.array([self.CxPolar[:,0] , np.sum(self.CxPolar[:,[2,3]],axis=1).T]).T
    #             # self.CxPolar=self.CxPolar[:,[0,2,3]]
    #         polarFile.close()
    #     elif type(self.CxPolarSource)==type(""):
    #         static_df=pd.read_csv(self.CxPolarSource)
    #         q=16
    #         THETA=static_df["pitch_angle"].to_numpy()
    #         n=len(THETA)
    #         # THETA_TRUNC=THETA[n//q:(q-1)*n//q+1]
    #         CX1=static_df["Cx1"].to_numpy()
    #         CX2=static_df["Cx2"].to_numpy()
    #         # CX=(np.minimum(CX1,CX2))[n//q:(q-1)*n//q+1]
    #         MMCX=movingMean(np.minimum(CX1,CX2),50)
    #         self.CxPolar=np.array([THETA,MMCX]).T
    #         # polarFile = open(self.CxPolarSource,'r')
    #         # df = pd.read_csv(self.CxPolarSource)
    #         # alphaList = df["pitch_angle"].tolist()
    #         # CxList=np.minimum(np.array(df["Cx1"].tolist())+np.array(df["Cx2"].tolist()))
    #         # self.CxPolar=np.array([alphaList,CxList]).T
    #     elif len(self.CxPolarSource)>30:
    #         self.CxPolar=self.CxPolarSource
    #     elif len(self.CxPolarSource)>0:
    #         self.CxPolar=[]
    #     else :
    #         print("Cx polar format not valid.")
        
    def NACA_4Digits (digits,N) :
        digits=int(digits)
        p,m,e=digits//1000/10,(digits%1000)//100/100,digits%100/100
        X=np.linspace(0,1,N)
        y_t=5*e*(0.2969*np.sqrt(X)-0.1260*X-0.3516*X**2+0.2843*X**3-0.1015*X**4)
        y_c,y_U,y_L=[],[],[]
        if p==0 and m==0 :
            y_U,y_L=y_t,-y_t
        else :
            theta=[]
            for x in X :
                if x<=p :
                    theta.append(2*m/p**2*(p-x))
                    y_c.append(m/p**2*(2*p*x-x**2))
                else :
                    theta.append(2*m/(1-p)**2*(p-x))
                    y_c.append(m/(1-p)**2*((1-2*p)+2*p*x-x**2))
            theta,y_c=np.array(theta),np.array(y_c)
            X_U=X-y_t*np.sin(theta),X+y_t*np.sin(theta)
            y_U,y_L=y_c+y_t*np.cos(theta),y_c-y_t*np.cos(theta)
        return np.array([np.concatenate((-X,np.flip(-X))),np.concatenate((y_U,np.flip(y_L)))])

# airfoil=Airfoil()
# profile=np.array([airfoil.airfoil[0]+0.3,airfoil.airfoil[1]])
# np.savetxt("naca0015.dat",profile.T,delimiter=" ")
# plt.figure(figsize=(17,10))
# plt.plot(airfoil.airfoil[0],airfoil.airfoil[1])
# plt.axis('equal')
# plt.show()