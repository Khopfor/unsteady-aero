import numpy as np
from src.util.util import *
from scipy.special import hankel2
from src.aero.Cz import Cz

def C1Func (k):
    H0= hankel2(0,k)
    H1= hankel2(1,k)
    return 1/k*np.exp(-1j*k)/(H1+1j*H0)

def meanCx(NACA,polarSource,Re,theta0,x_A,omega,A_heaving,phi,A_pitching,model="TG"):
    A_pitching=deg2rad(A_pitching)  
    phi=deg2rad(phi)
    if omega==0 : omega=0.001
    C=Cz.theodFunc(omega/2)
    C1=C1Func(omega/2)
    F,G=C.real,C.imag
    F1,G1=C1.real,C1.imag
    if model in ["TG","tg","T-G"]:
        Vz2Term=-np.pi*(A_heaving*omega)**2*abs(C)**2
        Ap2Term=-np.pi*A_pitching**2*((1+(x_A-3/4)**2*omega**2)*abs(C)**2+2*(x_A-3/4)*(F-1/2)*(omega/2)**2-(x_A-1/4)*omega*G-F)
        ApVzTerm=-np.pi*A_pitching*(A_heaving*omega)*((-2*abs(C)**2+omega/2*G+F)*np.sin(phi)+(omega/2*(x_A-3/4)+omega/2*F-G-omega/4)*np.cos(phi))
    elif model in ["model"]:
        Vz2Term=-k_alpha/2*(A_heaving*omega)**2*abs(C)**2
        Ap2Term=-k_alpha/2*A_pitching**2*((1+(x_A-3/4)**2*omega**2)*abs(C)**2+(x_A-3/4)*(2*F-np.pi/k_alpha)*(omega/2)**2-(x_A-1/4)*omega*G-F)
        ApVzTerm=-k_alpha/2*A_pitching*(A_heaving*omega)*((-abs(C)**2+omega/2*G+F)*np.sin(phi)+(omega/2*(x_A-3/4)+omega/2*F-G-omega/(2*k_alpha))*np.cos(phi))
    elif model in ["rev"]:
        a=2*x_A-1
        k=omega/2
        Vz2Term=2*(A_heaving*omega)**2*G1
        Ap2Term=-A_pitching**2*(2*np.pi*F+2*a*k*F1+2*(2+k**2*(a-1)*(a-1/2))*G1)
        ApVzTerm=A_pitching*(A_heaving*omega)*(-(2*F1+k*(4*a-3)*G1)*np.cos(phi)+(2*np.pi*F+k*F1+6*G1)*np.sin(phi))
    return Vz2Term+Ap2Term+ApVzTerm


def meanCzVz (NACA,polarSource,Re,theta0,x_A,omega,A_heaving,phi,A_pitching,model="fb"):
    A_pitching=deg2rad(A_pitching)  
    phi=deg2rad(phi)
    C=Cz.theodFunc(omega/2)
    F,G=C.real,C.imag
    if model in ["fb","model"]:
        k_alpha=4.7
    else :
        k_alpha=2*np.pi
    Vz2Term=-k_alpha/2*A_heaving**2*omega**2*F
    ApVzTerm=k_alpha/2*A_pitching*A_heaving*omega*((np.pi/(2*k_alpha)*omega**2*(x_A-1/2)+F-G*omega*(3/4-x_A))*np.sin(phi)+(np.pi/(2*k_alpha)*omega+G-F*omega*(3/4-x_A))*np.cos(phi))
    return Vz2Term+ApVzTerm

def meanCmdtheta (NACA,polarSource,Re,theta0,x_A,omega,A_heaving,phi,A_pitching,model="fb"):
    A_pitching=deg2rad(A_pitching)  
    phi=deg2rad(phi)
    C=Cz.theodFunc(omega/2)
    F,G=C.real,C.imag
    if model in ["fb","model"]:
        k_alpha=4.7
    else :
        k_alpha=2*np.pi
    ApVzTerm=k_alpha/2*A_pitching*A_heaving*omega*((np.pi/(8*k_alpha)*omega*(1/2-x_A)+G*(1/4-x_A))*np.sin(phi)+F*(1/4-x_A)*np.cos(phi))
    Ap2Term=k_alpha/2*A_pitching**2*omega*(np.pi/(2*k_alpha)*omega*(x_A-3/4)+G*(x_A-1/4)-F*omega*(x_A**2-x_A+3/16))
    return ApVzTerm+Ap2Term


def effProp (Cx_mean,CPh_mean,CPp_mean):
    CP_mean=max(0,CPh_mean)+max(0,CPp_mean)
    if CP_mean==0:
        return np.nan
    return -Cx_mean/CP_mean

# def eff (curParams,model="TG",type="prop"):
#     if type=="prop":
#         if model in ["TG","rev"]:
#             return meanCx(**curParams,model=model)/(meanCzVz(**curParams)+0*meanCmdtheta(**curParams))#+meanCmdtheta(**curParams))
#         else :
#             return meanCx(**curParams,model=model)/(meanCzVz(**curParams)+0*meanCmdtheta(**curParams))#+meanCmdtheta(**curParams))

#     elif type in ["wg", "gusts","wind"]:
#         NGParams=deepcopy(curParams)
#         NGParams["A_heaving"]=0
#         NGParams["A_pitching"]=0
#         return 1-(meanCx(**curParams,model=model)+meanCmdtheta(**curParams))

