import numpy as np
from math import *

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