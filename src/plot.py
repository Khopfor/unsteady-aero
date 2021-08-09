import sys
sys.path.append('./src')
import time
from util import *

blacklist = ['time','t*','Mx','Cmx','q0','dtheta']

def sc (i,nx,ny):
    return (nx,ny,i)

def plotCycle(save=False,showTime=0):
    curParams=json2Dict(CURRENTPARAMSJSON)

def plotComparison (save=False,showTime=0):
    curParams=json2Dict(CURRENTPARAMSJSON)
    if not os.path.isfile(filePath("data_exp")) :
        print(filePath("data_exp")+"  doesn't exist.")
    else :
        df_exp=pd.read_csv(filePath("data_exp"))
        df_theo=pd.read_csv(filePath("data",comparison=True))
        df_qs=pd.read_csv(filePath("data",end="_qs",comparison=True,folder="quasi-static"))
        index=1
        # ny=ceil(sqrt(len(df_theo)+1))
        # nx=ceil(len(df_theo)/ny)
        nx=2
        ny=5
        T=2*np.pi/curParams["omega"]
        T1=np.flip(df_exp["t*1"].to_numpy())/T
        T2=df_exp["t*2"].to_numpy()/T
        P=df_exp["pitch_angle"].to_numpy()
        nb=len(df_theo.columns)
        n=nx*ny
        subT,subP=[],[]
        fig=plt.figure(figsize=(14,6))
        i=0
        while i<nb:
            # print(i)
            if df_theo.columns[i][0:-1] in blacklist :
                i+=1
            else :
                if i<len(df_theo.columns)-1 and df_theo.columns[i][0:-1]==df_theo.columns[i+1][0:-1] :
                    subT.append(subplotMaker(sc(index,nx,ny),"","t*/T*",df_theo.columns[i][0:-1],equal=False))
                    index=((index+n//2-1)//n+index+n//2-1)%n+1
                    subT[-1].plot(T1,np.flip(df_qs[df_theo.columns[i]].to_numpy()),"-",color="#BBEEFF",lw=1.4)
                    subT[-1].plot(T2,df_qs[df_theo.columns[i+1]].to_numpy(),"-",color="#FFEEBB",lw=1.4)
                    subT[-1].plot(T1,np.flip(df_exp[df_theo.columns[i]].to_numpy()),"--",color="blue",lw=1.4)
                    subT[-1].plot(T2,df_exp[df_theo.columns[i+1]].to_numpy(),"--",color="orange",lw=1.4)
                    subT[-1].plot(T1,np.flip(df_theo[df_theo.columns[i]].to_numpy()),"-",color="blue",lw=1.4)
                    subT[-1].plot(T2,df_theo[df_theo.columns[i+1]].to_numpy(),"-",color="orange",lw=1.4)
                    if df_theo.columns[i][0:-1] not in ["h*"] :
                        subP.append(subplotMaker(sc(index,nx,ny),"","pitch_angle",df_theo.columns[i][0:-1],equal=False))
                        index=((index+n//2-1)//n+index+n//2-1)%n+1
                        subP[-1].plot(P,df_qs[df_theo.columns[i]].to_numpy(),"-",color="#BBEEFF",lw=1.4)
                        subP[-1].plot(P,df_qs[df_theo.columns[i+1]].to_numpy(),"-",color="#FFEEBB",lw=1.4)
                        subP[-1].plot(P,df_exp[df_theo.columns[i]].to_numpy(),"--",color="blue",lw=1.4)
                        subP[-1].plot(P,df_exp[df_theo.columns[i+1]].to_numpy(),"--",color="orange",lw=1.4)
                        subP[-1].plot(P,df_theo[df_theo.columns[i]].to_numpy(),"-",color="blue",lw=1.4)
                        subP[-1].plot(P,df_theo[df_theo.columns[i+1]].to_numpy(),"-",color="orange",lw=1.4)
                    i+=2
                else :
                    subT.append(subplotMaker(sc(index,nx,ny),"","t*",df_theo.columns[i],equal=False))
                    index=((index+n//2-1)//n+index+n//2-1)%n+1
                    subT[-1].plot(T1,np.flip(df_qs[df_theo.columns[i]].to_numpy()),"-",color="#BBEEFF",lw=1.4)
                    subT[-1].plot(T2,df_qs[df_theo.columns[i]].to_numpy(),"-",color="#FFEEBB",lw=1.4)
                    subT[-1].plot(T1,np.flip(df_exp[df_theo.columns[i]].to_numpy()),"--",color="blue",lw=1.4)
                    subT[-1].plot(T2,df_exp[df_theo.columns[i]].to_numpy(),"--",color="orange",lw=1.4)
                    subT[-1].plot(T1,np.flip(df_theo[df_theo.columns[i]].to_numpy()),"-",color="blue",lw=1.4)
                    subT[-1].plot(T2,df_theo[df_theo.columns[i]].to_numpy(),"-",color="orange",lw=1.4)
                    i+=1
        plt.tight_layout()
        plt.show(block=0)
        if save :
            plt.savefig(filePath("out/comparison",ext="",comparison=True,create=True))
        plt.pause(showTime)
        plt.close()


def plotContrib (save=False,showTime=0,comp=False):
    curParams=json2Dict(CURRENTPARAMSJSON)
    if not os.path.isfile(filePath("data",end="_contrib",comparison=comp,ext=".csv")) :
        print(filePath("data",end="_contrib",comparison=comp,ext=".csv")+"  doesn't exist.")
    else :
        df_contrib=pd.read_csv(filePath("data",end="_contrib",comparison=comp,ext=".csv"))
        df_cycle=pd.read_csv(filePath("data",end="",comparison=comp,ext=".csv"))
        nx=2
        ny=4
        T=2*np.pi/curParams["omega"]
        T1=np.flip(df_cycle["t*1"].to_numpy())/T
        T2=df_cycle["t*2"].to_numpy()/T
        T1T2=np.concatenate((T1,T2))
        P=df_cycle["pitch_angle"].to_numpy()
        PP=np.concatenate((np.flip(P),P))

        fig=plt.figure(figsize=(14,6))
        pitchSub=subplotMaker((nx,ny,1),"","t*/T*","pitch angle",equal=False)
        pitchSub.plot(T1T2,PP,color='blue')
        heavingSub=subplotMaker((nx,ny,5),"","t*/T*","h*",equal=False)
        heavingSub.plot(T1,np.flip(df_cycle["h*1"].to_numpy()),color='gray')
        heavingSub.plot(T2,df_cycle["h*2"].to_numpy(),color='gray')

        # Contributions of Cz
        CzTime=subplotMaker((nx,ny,2),"","t*/T*","Cz",equal=False)
        CzPitch=subplotMaker((nx,ny,6),"","pitch angle","Cz",equal=False)

        # Cz
        Cz1,Cz2=df_cycle["Cz1"].to_numpy(),df_cycle["Cz2"].to_numpy()
        CzTime.plot(T1T2,np.concatenate((np.flip(Cz1),Cz2)),color='#CC88CC',label='Cz')
        CzPitch.plot(PP,np.concatenate((np.flip(Cz1),Cz2)),color='#CC88CC',label='Cz')

        # Cz_AM
        Cz_AM1,Cz_AM2=df_contrib["Cz_AM1"].to_numpy(),df_contrib["Cz_AM2"].to_numpy()
        CzTime.plot(T1T2,np.concatenate((np.flip(Cz_AM1),Cz_AM2)),color='#BB88DD',label='Added mass')
        CzPitch.plot(PP,np.concatenate((np.flip(Cz_AM1),Cz_AM2)),color='#BB88DD',label='Added mass')

        # Cz_VE
        Cz_VE1,Cz_VE2=df_contrib["Cz_VE1"].to_numpy(),df_contrib["Cz_VE2"].to_numpy()
        CzTime.plot(T1T2,np.concatenate((np.flip(Cz_VE1),Cz_VE2)),color='#DD88BB',label='Vortex')
        CzPitch.plot(PP,np.concatenate((np.flip(Cz_VE1),Cz_VE2)),color='#DD88BB',label='Vortex')
        CzTime.legend()
        CzPitch.legend()

        # Contributions of Cx
        CxTime=subplotMaker((nx,ny,3),"","t*/T*","Cx",equal=False)
        CxPitch=subplotMaker((nx,ny,7),"","pitch angle","Cx",equal=False)

        # Cx
        Cx1,Cx2=df_cycle["Cx1"].to_numpy(),df_cycle["Cx2"].to_numpy()
        CxTime.plot(T1T2,np.concatenate((np.flip(Cx1),Cx2)),color='#CC88CC',label='Cx')
        CxPitch.plot(PP,np.concatenate((np.flip(Cx1),Cx2)),color='#CC88CC',label='Cx')

        # Cx_bonnet
        Cx_bonnet1,Cx_bonnet2=df_contrib["Cx_bonnet1"].to_numpy(),df_contrib["Cx_bonnet2"].to_numpy()
        CxTime.plot(T1T2,np.concatenate((np.flip(Cx_bonnet1),Cx_bonnet2)),color='#FFAAAA',label='Unsteady')
        CxPitch.plot(PP,np.concatenate((np.flip(Cx_bonnet1),Cx_bonnet2)),color='#FFAAAA',label='Unsteady')

        # Cx_steady
        Cx_steady1,Cx_steady2=df_contrib["Cx_steady1"].to_numpy(),df_contrib["Cx_steady2"].to_numpy()
        CxTime.plot(T1T2,np.concatenate((np.flip(Cx_steady1),Cx_steady2)),color='#DDDDFF',label='Steady')
        CxPitch.plot(PP,np.concatenate((np.flip(Cx_steady1),Cx_steady2)),color='#DDDDFF',label='Steady')
        CxTime.legend()
        CxPitch.legend()

        
        plt.tight_layout()
        plt.show(block=0)
        if save :
            plt.savefig(filePath("out/contributions",ext="",comparison=comp,create=True))
        timer=Thread(target=remainingTime,args=[showTime])
        timer.start()
        plt.pause(showTime)
        plt.close()
        timer.join()


# def plotEff (save=False,showTime=0):