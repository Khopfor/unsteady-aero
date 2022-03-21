from pandas.io.parsers import CParserWrapper
from src.util.util import *

def computeEffProp (filename):
    if "_eff" in filename:
        df=pd.read_csv(filename)
        dataDict=df.to_dict()
        print(filename)
        # print(dataDict)
        # try :
        dataDict["Eff_prop"]=-dataDict["Cx_mean"][0]/(dataDict["CPp_mean"][0]+dataDict["CPh_mean"][0])
        df=pd.DataFrame(dataDict)
        df.to_csv(filename,index=False)
        # except :
        #     pass


def computeCPh_mean (filename):
    if "_eff" not in filename :
        print(filename)
        df=pd.read_csv(filename)
        h=df2numpy(df,["h*1","h*2"],[1,0])
        t=df2numpy(df,["t*1","t*2"],[1,0])
        dh=np.array([(h[(k+1)%len(h)]-h[(k-1)%len(h)])/(t[(k+1)%len(t)]-t[(k-1)%len(t)]) for k in range(0,len(h))])
        Cz=df2numpy(df,["Cz1","Cz2"],[1,0])
        CPh_mean=np.mean(-Cz*dh)
        fileList=glob.glob(filename[:-4]+"*_eff*")
        if len(fileList)>0:
            df_eff=pd.read_csv(fileList[0])
            df_eff["CPh_mean"]=CPh_mean
            df_eff.to_csv(fileList[0],index=False)


def treeExec (dir,func):
    # print(dir)
    if len(glob.glob(dir+"/*"))>0 and os.path.isfile(glob.glob(dir+"/*")[0]) :
        for f in glob.glob(dir+"/*"):
            if func == "computeEffProp":
                computeEffProp(f)
            elif func == "computeCPh_mean":
                computeCPh_mean(f)
    else :
        for d in glob.glob(dir+"/*"):
            treeExec(d,func)
        
# treeExec("data_exp/NACA0015_Re135743_exp","computeCPh_mean")
# treeExec ("data_exp/NACA0015_Re135743_exp","computeEffProp")