import os
from src.util.var import *

def json2Dict (jsonFile):
    s=open(jsonFile,'r').read()
    return json.loads(s)

def dirPath (dir="",folder="",polar=0,comparison=False,create=False) :
    curParams=json2Dict(CURRENTPARAMSJSON)
    params=json2Dict(PARAMSJSON)
    U=params["dim_quantities"]["U"]
    chord=params["dim_quantities"]["chord"]
    if params["polarSource"] in ["exp","expe","experiment"]:
        polarSource="exp"
    else :
        polarSource=params["polarSource"]
    path=dir+"/"*(dir!="" and dir[-1]!="/")+"NACA"+curParams["NACA"]+"_Re"+str(int(curParams["Re"]))+"_"+polarSource+comparison*"_comparison"
    if create and not os.path.isdir(path) :
        os.mkdir(path)
    if polar:
        path+="/xfoil_polar"
        if create and not os.path.isdir(path) :
            os.mkdir(path)
        return path
    f=("000"+str(int(curParams["omega"]*U/(2*np.pi*chord)*100)))[-3:]
    path+="/f"+f+"_omega"+("000"+str(int(curParams["omega"]*100)))[-3:]+"_h"+("000"+str(int(curParams["A_heaving"]*100)))[-3:]+"_a"+str(int(curParams["theta0"]))
    if create and not os.path.isdir(path) :
        os.mkdir(path) 
    path+="/f"+f+"_omega"+("000"+str(int(curParams["omega"]*100)))[-3:]+"_h"+("000"+str(int(curParams["A_heaving"]*100)))[-3:]+"_a"+str(int(curParams["theta0"]))+"_xA"+("000"+str(int(curParams["x_A"]*100)))[-3:]+"_phi"+str(int(curParams["phi"]))+"_pitch"+("000"+str(int(curParams["A_pitching"]*10)))[-3:]
    if create and not os.path.isdir(path) :
        os.mkdir(path) 
    if folder!="" :
        path+="/"+folder
        if not os.path.isdir(path) : os.mkdir(path)
    return path

def filePath (dir="",end="",ext=".csv",folder="",comparison=False,create=False) :
    # curParams=json2Dict(CURRENTPARAMSJSON)
    # params=json2Dict(PARAMSJSON)
    # U=params["dim_quantities"]["U"]
    # chord=params["dim_quantities"]["chord"]
    path=dirPath(dir,folder=folder,comparison=comparison,create=create)
    # f=("000"+str(int(curParams["omega"]*U/(2*np.pi*chord)*100)))[-3:]
    if ext==".png" :
        path=path[:-1]+end+ext
    else :
        path+="/"+path.split("/")[-1-(folder!="")]+end+ext
    return path