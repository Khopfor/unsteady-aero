import pandas as pd
# import plotly.express as px
import matplotlib.pyplot as plt
from util import *

blacklist = ['time','t*','Mx','Cmx','q0','dtheta']

def sc (i,nx,ny):
    return (nx,ny,i)

def autoPlot (index, nx,ny,df, xlabels, ylabels, n):
    if n>1 : sub=subplotMaker(sc(index,nx,ny),"",xlabels[0][0:-1],ylabels[0][0:-1],equal=False)
    elif n==1 : sub=subplotMaker(sc(index,nx,ny),"",xlabels[0],ylabels[0])
    else : 
        print("Error no value to plot")
        return n
    for i in range(n):
        X=df[xlabels[i]].tolist()
        Y=df[ylabels[i]].tolist()
        # if xlabels[i] == "time1" : Y.reverse()
        sub.plot(X,Y)
    return sub

def plotData (filePath):
    df=pd.read_csv(filePath)
    nx=3
    ny=3
    def plotAllWrtTime (index,nb="all"):
        i=0
        if nb=="max" or nb=="all": nb=len(df.columns)
        while i<nb:
            if i<len(df.columns)-1 and df.columns[i][0:-1]==df.columns[i+1][0:-1] and df.columns[i][0:-1] not in blacklist :
                autoPlot (index,nx,ny,df,["time1","time2"],df.columns[i:i+2],2)
                i+=2
                index+=1
            elif df.columns[i][0:-1] not in blacklist :
                autoPlot (index,nx,ny,df,["time1","time2"],[df.columns[i],df.columns[i]],2)
                i+=1
                index+=1
            else :
                i+=1
    # plotAllWrtTime(1)
    # autoPlot (1,1,1,df,["pitch_angle","pitch_angle"],["Fx1","Fx2"],2)
    X=df["pitch_angle"].tolist()
    n=len(X)
    q=5
    X=X[n//q:(q-1)*n//q+1]
    Y=(np.array(df["Mz1"].tolist())+np.array(df["Mz2"].tolist()))[n//q:(q-1)*n//q+1]/2
    reg=np.polyfit(X,Y,7)
    # print(reg)
    def p (x,coeffs):
        res=0
        n=len(coeffs)
        for i in range(n):
            res+=coeffs[n-i-1]*x**i
        return res
    P=[p(x,reg) for x in X]
    plt.plot(X,Y)
    plt.plot(X,P)
    # print(X[0])
    # autoPlot (2,["time1","time2"],["Fy1","Fy2"],2)
    plt.tight_layout()
    plt.show()

# plotData("data/exp/res_pitchF005_V10_pitch15_ampl000_alpha00.txt")
# plotData("data/exp/f16_h50_a13/res_pitchF160_V10_pitch00_ampl050_alpha13_100_filtre_rejet_cycles.txt")