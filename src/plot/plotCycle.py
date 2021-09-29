from src.plot.plotUtil import *


def plotCycle (save=False,showTime=0):
    curParams=json2Dict(CURRENTPARAMSJSON)
    df_theo=pd.read_csv(filePath("data",folder="BF"))
    index=1
    nx=2
    ny=5
    T=2*np.pi/curParams["omega"]
    T1=np.flip(df_theo["t*1"].to_numpy())/T
    T2=df_theo["t*2"].to_numpy()/T
    P=df_theo["pitch_angle"].to_numpy()
    nb=len(df_theo.columns)
    n=nx*ny
    subT,subP=[],[]
    fig=plt.figure(figsize=(14,6))
    i=0
    while i<nb:
        if df_theo.columns[i][0:-1] in blacklist :
            i+=1
        else :
            if i<len(df_theo.columns)-1 and df_theo.columns[i][0:-1]==df_theo.columns[i+1][0:-1] :
                subT.append(subplotMaker(sc(index,nx,ny),"","t*/T*",df_theo.columns[i][0:-1],equal=False))
                index=((index+n//2-1)//n+index+n//2-1)%n+1
                subT[-1].plot(T1,np.flip(df_theo[df_theo.columns[i]].to_numpy()),"-",color="blue",lw=1.4)
                subT[-1].plot(T2,df_theo[df_theo.columns[i+1]].to_numpy(),"-",color="orange",lw=1.4)
                if df_theo.columns[i][0:-1] not in ["h*"] :
                    subP.append(subplotMaker(sc(index,nx,ny),"","pitch_angle",df_theo.columns[i][0:-1],equal=False))
                    index=((index+n//2-1)//n+index+n//2-1)%n+1
                    subP[-1].plot(P,df_theo[df_theo.columns[i]].to_numpy(),"-",color="blue",lw=1.4)
                    subP[-1].plot(P,df_theo[df_theo.columns[i+1]].to_numpy(),"-",color="orange",lw=1.4)
                i+=2
            else :
                subT.append(subplotMaker(sc(index,nx,ny),"","t*",df_theo.columns[i],equal=False))
                index=((index+n//2-1)//n+index+n//2-1)%n+1
                subT[-1].plot(T1,np.flip(df_theo[df_theo.columns[i]].to_numpy()),"-",color="blue",lw=1.4)
                subT[-1].plot(T2,df_theo[df_theo.columns[i]].to_numpy(),"-",color="orange",lw=1.4)
                i+=1

    showPlot(save,showTime,"out/cycle")