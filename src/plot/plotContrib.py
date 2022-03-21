from src.plot.plotUtil import *


def plotContrib (save=False,showTime=0,comp=False):
    curParams=json2Dict(CURRENTPARAMSJSON)
    curModels=json2Dict(CURRENTMODELS)
    df_contrib,df_cycle={},{}
    for key in curModels :
        if curModels[key]!="NONE":
            filename=filePath("data",end="_contrib",comparison=comp,folder=curModels[key])
            if os.path.isfile(filename) :
                df_contrib[key]=pd.read_csv(filename)
                df_cycle[key]=pd.read_csv(filePath("data",end="",comparison=comp,folder=curModels[key]))
            else :
                print(filename+"  doesn't exist.")
    
    # print(df_contrib)
    if df_contrib!={} :
        nx=2
        ny=4
        T=2*np.pi/curParams["omega"]
        T1T2=df2numpy(list(df_cycle.values())[0],["t*1","t*2"],[1,0])
        PP=df2numpy(list(df_cycle.values())[0],["pitch_angle","pitch_angle"],[1,0])

        fig=plt.figure(figsize=(15,6))
        pitchSub=subplotMaker((nx,ny,1),"","t*/T*","pitch angle",equal=False)
        pitchSub.plot(T1T2,PP,color='blue')
        heavingSub=subplotMaker((nx,ny,5),"","t*/T*","h*",equal=False)
        heavingSub.plot(T1T2,df2numpy(df_cycle["main"],["h*1","h*2"],[1,0]),color='gray')

        def plotCurve (subTime,subPitch,df,modelKey,dataName,color,label):
            data=df2numpy(df,[dataName+"1",dataName+"2"],[1,0])
            subTime.plot(T1T2,data,'-'+'-'*(modelKey!="main"),color=color,label=label)
            subPitch.plot(PP,data,'-'+'-'*(modelKey!="main"),color=color,label=label)


        # Contributions of Cz
        CzTime=subplotMaker((nx,ny,2),"","t*/T*","Cz",equal=False)
        CzPitch=subplotMaker((nx,ny,6),"","pitch angle","Cz",equal=False)
        # Contributions of Cx
        CxTime=subplotMaker((nx,ny,3),"","t*/T*","Cx",equal=False)
        CxPitch=subplotMaker((nx,ny,7),"","pitch angle","Cx",equal=False)

        for modelKey in df_contrib :
            # print("modelKey = ",modelKey)
            # Cz_AM
            Cz_AM_color=[0.7,0.7,1]
            plotCurve(CzTime,CzPitch,df_contrib[modelKey],modelKey,'Cz_AM',Cz_AM_color,'Added mass')

            # Cz_VE
            Cz_VE_color=[1,0.7,0.7]
            plotCurve(CzTime,CzPitch,df_contrib[modelKey],modelKey,'Cz_VE',Cz_VE_color,'Vortex')

            # Cz
            plotCurve(CzTime,CzPitch,df_cycle[modelKey],modelKey,'Cz',opacity(subtractiveColor(Cz_AM_color,Cz_VE_color),1.5),'Cz')

            # Cx_bonnet
            plotCurve(CxTime,CxPitch,df_contrib[modelKey],modelKey,'Cx_bonnet',"#DDDD99",'Unsteady')

            # Cx_steady
            plotCurve(CxTime,CxPitch,df_contrib[modelKey],modelKey,'Cx_steady',"#99DDDD",'Steady')

            # Cx
            plotCurve(CxTime,CxPitch,df_cycle[modelKey],modelKey,'Cx',"#337733",'Cx')

        # Plot legend
        CzTime.legend()
        CzPitch.legend()
        CxTime.legend()
        CxPitch.legend()

        showPlot(save,showTime,"out/contributions",comp=comp)