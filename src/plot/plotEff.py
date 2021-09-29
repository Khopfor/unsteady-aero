from src.plot.plotUtil import *
from src.efficiency import *

def plotEff (absData,model="model",save=False,showTime=0,comp=0):
    params=json2Dict(PARAMSJSON)
    curParams=json2Dict(CURRENTPARAMSJSON)
    # if comp :
    #     if not os.path.isfile(filePath("data_exp")) :
    #         print(filePath("data_exp")[:52]+"..."+filePath("data_exp")[-52:]+"  doesn't exist.")
    #     else :
    #         curParams=ajustCurParams()
    fig=plt.figure(figsize=(14,6))

    abscissaMatrix=[params[paramLabel] for paramLabel in absData]
    dim=len(absData)
    X=[]
    Y={}
    for paramLabel in absData :
        X.append(params[paramLabel])
        for x in params[paramLabel]:
            curParams[paramLabel]=x
            with open(CURRENTPARAMSJSON,'w') as jsonFile :
                json.dump(curParams,jsonFile,indent=2)
            for filename in glob.glob(filePath("tmp",end='*',ext='')):
                model=filename.split('.')[0].split('_')[-1]
                if model not in Y.keys() :
                    Y[model]={}
                dataDict=pd.read_csv(filename).to_dict()
                # print(dataDict)
                for fnLabel in dataDict.keys() :
                    if fnLabel not in Y[model].keys() :
                        Y[model][fnLabel]=[]
                    Y[model][fnLabel].append(dataDict[fnLabel][0])

    if dim==1:
        subs={}
        for i,fnLabel in enumerate(Y[list(Y.keys())[0]]) :
            subs[fnLabel]=subplotMaker((1,len(Y[list(Y.keys())[0]]),i+1),fnLabel+" with respect to "+absData[0],absData[0],fnLabel,equal=False)
            for model in Y :
                subs[fnLabel].plot(X[0],Y[model][fnLabel],label=model)
            subs[fnLabel].legend()

        # Shows and saves if required
        showPlot(save,showTime,"out/eff",comp=comp)

    else :
        print("dim = ",dim)