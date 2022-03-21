from numpy.lib.function_base import extract
from src.plot.plotUtil import *
from src.efficiency import *

def plotEff (absData,model="model",save=False,showTime=0,comp=0):
    global fnLabels
    params=json2Dict(PARAMSJSON)
    curParams=json2Dict(CURRENTPARAMSJSON)
    # if comp :
    #     if not os.path.isfile(filePath("data_exp")) :
    #         print(filePath("data_exp")[:52]+"..."+filePath("data_exp")[-52:]+"  doesn't exist.")
    #     else :
    #         curParams=ajustCurParams()
    fig=plt.figure(figsize=(18,6))

    abscissaMatrix=[params[paramLabel] for paramLabel in absData]
    dim=len(absData)
    X=[]
    Y={}
    fnLabels=[]

    def extractData (filename,model):
        global fnLabels
        if model not in Y.keys() :
            Y[model]={}
        if os.path.isfile(filename) :
            dataDict=pd.read_csv(filename).to_dict()
            valueExists=True
            if fnLabels ==[]:
                fnLabels=dataDict.keys()
        else :
            valueExists=False
        for fnLabel in fnLabels :
            if fnLabel not in Y[model].keys() :
                Y[model][fnLabel]=[]
            if valueExists and fnLabel in dataDict.keys():
                value=dataDict[fnLabel][0]
            else :
                value=np.nan
            Y[model][fnLabel].append(value)

    for paramLabel in absData :
        X.append(params[paramLabel])
        for x in params[paramLabel]:
            curParams[paramLabel]=x
            with open(CURRENTPARAMSJSON,'w') as jsonFile :
                json.dump(curParams,jsonFile,indent=2)
            for filename in glob.glob(filePath("tmp",end='*',ext='',comparison=comp)):
                extractData(filename,filename.split('.')[0].split('_')[-1])
            if comp :
                extractData(filePath("data_exp","_eff"),"exp")



    if dim==1:
        X=np.array(X[0])
        # for model in Y.keys():
            # prettyPrint(Y[model])
        subs={}
        for i,fnLabel in enumerate(Y[list(Y.keys())[0]]) :
            subs[fnLabel]=subplotMaker((1,len(Y[list(Y.keys())[0]]),i+1),fnLabel+" with respect to "+absData[0],absData[0],fnLabel,equal=False)
            if absData[0]=="omega":
                ax2=subs[fnLabel].twiny()
                
                new_tick_locations = np.linspace(0.1,0.9,5)

                def tick_function(X):
                    St = X*curParams["A_heaving"]/np.pi
                    return ["%.3f" % z for z in St]

                # ax2.set_xlim(ax1.get_xlim())
                ax2.set_xticks(new_tick_locations)
                ax2.set_xticklabels(tick_function(new_tick_locations))
            for model in Y :
                Y[model][fnLabel]=np.array(Y[model][fnLabel])
                mask=np.isfinite(Y[model][fnLabel].astype(np.double))
                subs[fnLabel].plot(X[mask],Y[model][fnLabel][mask],'-'+'-'*(model=="exp"),label=model,marker='o'*(len(X)<20),color=setColor(model,fnLabel))
            subs[fnLabel].legend()

        # Shows and saves if required
        showPlot(save,showTime,"out/eff",comp=comp)

    else :
        print("dim = ",dim)