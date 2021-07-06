import numpy as np

class ExpFunc ():
    def __init__(self,A,omega,phi=0,mean=0):
        self.A=A
        self.omega=omega
        self.phi=phi
        self.mean=mean

    def __call__ (self,t):
        return self.mean+self.A*np.exp((self.omega*t+self.phi)*1j)

    def d (self,t):
        return self.A*self.omega*1j*np.exp((self.omega*t+self.phi)*1j)

    def dd (self,t):
        return -self.A*self.omega**2*np.exp((self.omega*t+self.phi)*1j)