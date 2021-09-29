from src.plot.plotUtil import *


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

        def plotCurve (subTime,subPitch,df,dataName,color,label):
            data=df2numpy(df,[dataName+"1",dataName+"2"],[1,0])
            subTime.plot(T1T2,data,color=color,label=label)
            subPitch.plot(PP,data,color=color,label=label)


        # Contributions of Cz
        CzTime=subplotMaker((nx,ny,2),"","t*/T*","Cz",equal=False)
        CzPitch=subplotMaker((nx,ny,6),"","pitch angle","Cz",equal=False)

        # Cz_AM
        plotCurve(CzTime,CzPitch,df_contrib,'Cz_AM',"#CCCCFF",'Added mass')

        # Cz_VE
        plotCurve(CzTime,CzPitch,df_contrib,'Cz_VE',"#FFCCCC",'Vortex')

        # Cz
        plotCurve(CzTime,CzPitch,df_cycle,'Cz',"#882288",'Cz')

        # Plot legend
        CzTime.legend()
        CzPitch.legend()

        # Contributions of Cx
        CxTime=subplotMaker((nx,ny,3),"","t*/T*","Cx",equal=False)
        CxPitch=subplotMaker((nx,ny,7),"","pitch angle","Cx",equal=False)

        # Cx_bonnet
        plotCurve(CxTime,CxPitch,df_contrib,'Cx_bonnet',"#DDDD99",'Unsteady')

        # Cx_steady
        plotCurve(CxTime,CxPitch,df_contrib,'Cx_steady',"#99DDDD",'Steady')

        # Cx
        plotCurve(CxTime,CxPitch,df_cycle,'Cx',"#337733",'Cx')

        CxTime.legend()
        CxPitch.legend()

        showPlot(save,showTime,"out/contributions",comp=comp)