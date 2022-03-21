import os
import glob
import shutil
from params import params
from src.util.util import *
from src.computeCycle import computeCycle
from src.plot.plotComparison import *
from src.plot.plotContrib import *
from src.plot.plotCycle import *
from src.plot.plotEff import *
from src.plot.plotUtil import *
from src.anim import runAnimation
from src.util.var import *
import json


# with open("params.txt",'r') as f :
#     eval(f.read())

exit=False
params={}
curModels=json2Dict(CURRENTMODELS)

def updateParams ():
    global params
    checkParamsFile()
    os.system("python "+PARAMSFILE)
    params=json2Dict(PARAMSJSON)

print("\n=====================================================================")
print(" UNSTEADY AERODYNAMICS PROGRAM  Version "+str(VERSION))
print(" Aymeric Braud    2021")
print("=====================================================================")

def printHelp ():
    print("\nCOMMANDS\n")
    print("    exit OR quit                   Exit program")
    print("    edit                           Open the parameters python file to edit them")
    print("    set <parameter> <value>        Set the specified parameter")
    print("    param                          Show current parameters namely parameters file content")
    print("    model <option>                 Show main model and second model in use.")
    print("        set [main|second] <model>       Choose main or second model.")
    print("    exp                            Show available experimental results for comparison")
    print("    plot <options>                 Plot graphs. Options for plotting are the following. No option only plots cycle data")
    print("        show <seconds>                  Show graphs. The time in seconds before which figures close themselves can be specified")
    print("        save                            Save graphs as images")
    print("        cycle                           Plot cycle data")
    print("        comparison                      Compute comparison between model and experiment and plot it")
    print("        contrib                         Plot contributions")
    print("        eff                             Plot efficiency and mean drag")
    print("    anim                           Show animation")
    print("    optimize                       Enter optimizing mode. Optimize the parameters of your choice with respect to mean drag or efficiency.")
    print("    clean                          Delete all data, images and videos")
    print("    help                           Show this help")
    print()


def printModels():
    global curModels
    curModels=json2Dict(CURRENTMODELS)
    with open(AVAILABLEMODELS,'r') as f :
        avModels=f.read().replace(" ",'').replace("\n"," | ")
        f.close()
    print("\nMODELS")
    print("  Current main model : ",curModels["main"])
    print("  Current second model : ",curModels["second"])
    print("  -------------------------------------------")
    print("  Available models : ",avModels,"\n")

def printParam():
    print("\nPARAMETERS")
    print(" ____________________________________________________________________")
    prettyPrint(params)
    print(" ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\n")



updateParams()
printHelp()
printModels()
printParam()

autocmd=False

while not exit :
    updateParams()
    keep=False
    if autocmd : 
        cmd = autocmd+input(" > "+autocmd)
        autocmd=False
    else :
        cmd=input(" > ")

    # Exit command
    if cmd in ["exit",'quit','q'] :
        exit=True

    # Platform command
    elif cmd in ["platform",'os'] :
        print(OS)

    # Edit command
    elif cmd in ["edit"]:
        if OS == "Linux":
            os.system("gedit "+PARAMSFILE)
        elif OS == "Windows":
            os.system(PARAMSFILE)
        elif OS == "MACOS":
            os.system("open -e "+PARAMSFILE)
        updateParams()
        printParam()

    # Set command
    elif "set" in cmd and "model" not in cmd :
        cmdList=cmd.split(' ')
        if len(cmdList)==1:
            cmdList.append(input("Enter a parameter : "))
            while cmdList[1] not in params.keys():
                cmdList[1]=input("This parameter is not valid. Please enter a valid parameter : ")
        p=cmdList[1]
        if len(cmdList)==2:
            v=input("Enter new value or range for parameter "+'"'+p+'" : ')
            keep=True
        elif len(cmdList)==3:
            v=cmdList[2]
            keep=True
        if p!="fluid":
            if 'np.' not in v and 'range' not in v and '[' and v not in ']' and ',' not in v:
                v='['+v+']'
            if 'np.' in v :
                v="list("+v+")"
        with open(PARAMSFILE,'r') as f :
            lines=f.readlines()
            f.close()
        with open(PARAMSFILE,'w') as f :
            for i,line in enumerate(lines):
                if p=="fluid" :
                    if v=="air":
                        if "rho=" in line : line=changeValue(line,"rho","1.225")
                        if "mu=" in line : line=changeValue(line,"mu","1.81e-5")
                    if v=="water" :
                        if "rho=" in line : line=changeValue(line,"rho","1000")
                        if "mu=" in line : line=changeValue(line,"mu","1.00e-3")
                elif '"'+p+'"' in line:
                    line="    "+'"'+p+'"'+":"+str(v)
                    if p!="A_pitching":
                        line+=","
                    line+='\n'
                f.write(line)
            f.close()
        updateParams()
        printParam()

    # Parameters command
    elif cmd in ["param","params"]:
        printParam()

    # Choose model
    elif "model" in cmd :
        cmd=cmd.split(' ')
        which="main"
        if len(cmd)==1 :
            printModels()
        else :
            if len(cmd)==2 and cmd[1]=="set":
                which=input("Which model do you want to change ? (main/second) : ")
                model=input("Enter new "+which+" model : ")
            elif len(cmd)==3:
                if cmd[1:]==["set","main"]:
                    which="main"
                elif cmd[1:]==["set","second"]:
                    which=="second"
                model=input("Enter new "+which+" model : ")
            elif len(cmd)==4 and cmd[1]=="set":
                if cmd[2] in ["main","second"]:
                    which=cmd[2]
                    model=cmd[3]
            with open(AVAILABLEMODELS,'r') as f :
                model=model.upper().replace(" ",'')
                if model in f.read() :
                    curModels[which]=model
                    json.dump(curModels,open(CURRENTMODELS,'w'),indent=2)
                    print(which[0].upper()+which[1:].lower()+" model is now : ",model)
                else :
                    print("Invalid model : ",model,". Try again.")
                f.close()

    # Exp command
    elif cmd in ["exp"]:
        if OS == "Linux":
            os.system("ls data_exp/*")

    # Help command
    elif cmd in ["h","help"]:
        printHelp()

    # Clean command
    elif cmd in ["clean","clear"]:
        if input("Are you sure to delete all data (y/n) ? ") == "y" :
            for d in glob.glob("data/*"):
                shutil.rmtree(d)
            for d in glob.glob("out/*"):
                for dd in glob.glob(d+"/*"):
                    shutil.rmtree(dd)
        print("Data deleted.")

    # Animation command
    elif cmd in ['anim','animation']:
        anim_params={}
        for p in params.keys() :
            if p != "dim_quantities" and p != "polarSource" :
                if len(params[p])>1 :
                    anim_params[p]=input('Enter only one value for parameter "'+p+'" : ')
                    while "[" in anim_params[p] or "]" in anim_params[p] or "," in anim_params[p]:
                        anim_params[p]=input('Entry not valid. Enter only one value for parameter "'+p+'" : ')
                else :
                    anim_params[p]=params[p][0]
                if p=='NACA' :
                    anim_params[p].replace('"','')
                elif p=='Re':
                    anim_params[p]=int(anim_params[p])
                else :
                    anim_params[p]=float(anim_params[p])
        anim_params["polarSource"]=params["polarSource"]
        with open(CURRENTPARAMSJSON,'w') as jsonFile :
            json.dump(anim_params,jsonFile,indent=2)
        computeCycle()
        runAnimation()

    # Plot command
    elif "run" in cmd or "plot" in cmd:
        cmdList=cmd.split(' ')
        if len(cmdList)==1 and cmdList[0] in ["plot","run"] :
            argv=input("    <plot> Enter options>> ").split(' ')
        elif len(cmdList)>1:
            argv=cmdList[1:]
            keep=True
        for a in argv:
            for char in ['-',' ',',']:
                a.replace(char,'')
        updateParams()
        showTime=setShowTime(argv)

        absData=[]
        ptsData=[]
        for p in params :
            if len(params[p])>20:
                absData.append(p)
            elif len(params[p])>1 and type(params[p])!=type("") and type(params[p])!=type({}) :
                ptsData.append(p)
        if len(absData)>2:
            print("Error : Too many parameter ranges.")
        else :
            if len(absData)==0 and len(ptsData)>0:
                if "eff" in argv :
                    for i in range(min(2,len(ptsData))):
                        absData.append(ptsData[-1])
                        del(ptsData[-1])
            
            def rec (i,currentParams,eff=True):
                if i>=len(params)-1:
                    with open(CURRENTPARAMSJSON,'w') as jsonFile :
                        json.dump(currentParams,jsonFile,indent=2)
                    computeCycle(argv)
                    if "cycle" in argv or (not checkComparison(argv) and not "contrib" in argv and not "eff" in argv):
                        plotCycle(save=("save" in argv),showTime=showTime)
                    if checkComparison(argv) and not "eff" in argv:
                        plotComparison(save=("save" in argv),showTime=showTime)
                    if 'contrib' in argv :
                        plotContrib(save=("save" in argv),showTime=showTime,comp=checkComparison(argv))
                else :
                    paramLabel=list(params)[i]
                    if paramLabel in absData :
                        for k,v in enumerate(params[paramLabel]):
                            rec(i+1,{**currentParams,paramLabel:params[paramLabel][0]},k==0)
                    if type(params[paramLabel])==type("") :
                        rec(i+1,{**currentParams,paramLabel:params[paramLabel]})
                    else :
                        for v in params[paramLabel]:
                            rec(i+1,{**currentParams,paramLabel:v})

            rec(0,{})
            if 'eff' in argv :
                plotEff(absData,save=("save" in argv),showTime=showTime,comp=checkComparison(argv))

        # for naca in params['NACA']:
        #     for Re in params['Re']:
        #         for theta0 in params['theta0']:
        #             for x_A in params['x_A']:
        #                 for omega in params['omega']:
        #                     for Ah in params['A_heaving']:
        #                         for phi in params['phi']:
        #                             for Ap in params['A_pitching']:
        #                                 currentParams={'NACA':naca,'polarSource':params['polarSource'],'Re':int(Re),'theta0':theta0,'x_A':x_A,'omega':omega,'A_heaving':Ah,'phi':phi,'A_pitching':Ap}
        #                                 with open(CURRENTPARAMSJSON,'w') as jsonFile :
        #                                     json.dump(currentParams,jsonFile,indent=2)
        #                                 computeCycle(argv)
        #                                 if "cycle" in argv or (not checkComparison(argv) and not "contrib" in argv and not "eff" in argv):
        #                                     plotCycle(save=("save" in argv),showTime=showTime)
        #                                 if checkComparison(argv) :
        #                                     plotComparison(save=("save" in argv),showTime=showTime)
        #                                 if 'contrib' in argv :
        #                                     plotContrib(save=("save" in argv),showTime=showTime,comp=checkComparison(argv))
        # else :
        #     absData=[]
        #     ptsData=[]
        #     for p in params :
        #         if len(params[p])>10:
        #             absData.append(p)
        #         elif len(params[p])>1:
        #             ptsData.append(p)
        #     if len(absData)>2:
        #         print("Error : Too many parameter ranges.")
        #     else :
        #         if len(absData)==0 and len(ptsData)>0:
        #             for i in min(2,len(ptsData)):
        #                 absData.append(ptsData[-i-1])
        #                 del(ptsData[-i-1])
                
        #         ptsData=[]
            


                    # for p2 in params :
                    #     if p2!=p1 and len(params[p2])>1:
                    #         plotEff(save=("save" in argv),showTime=showTime,comp=checkComparison(argv))


    # Optimize
    elif cmd in ["optimize","optimise","opti","opt"]:
        func=input("    <optimize> Choose 'meanCx', 'eff_prop' or 'eff_wg'>> ")
        paramLabels=input("    <optimize> Enter the labels of the parameters to optimize>> ").replace(',',' ').split(' ')
        # optimizeMode(func,paramLabels)


    # Last command
    elif "last" in cmd or "^[[A" in cmd :
        f=open("cache/last-commands.txt",'r')
        lines=f.readlines()
        f.close()
        nbLines=len(lines)
        if len(lines)==0 :
            print("No previous command.")
        else :
            end=cmd[cmd.index("last")+4:]
            if is_int(end) :
                if int(end)<len(lines):
                    autocmd=lines[int(end)-1][-1]
                elif int(end)==len(lines):
                    autocmd=lines[int(end)-1].replace('\n','')
            else :
                for i,line in enumerate(lines):
                    if i+1<=5 :
                        if line[-1]=='\n':line=line[:-1]
                        print(str(i+1)+'. '+line)
                number=input("Enter the number of the command : ")
                while (not is_int(number) or int(number)>nbLines) and (number not in ['q']) :
                    number=input("Enter a valid number (or press 'q' to quit) : ")
                if number not in ['q'] :
                    autocmd=lines[int(number)-1].replace('\n','')
    else :
        print("Command not valid.")
    if keep :
        f=open("cache/last-commands.txt",'r')
        lines=f.readlines()
        f.close()
        if len(lines)!=0:
            if cmd != lines[0]:
                lines=[cmd+'\n']+lines
        else :
            lines=[cmd]+lines
        if len(lines)>MAXLASTCMD :
            del(lines[MAXLASTCMD:])
        f=open("cache/last-commands.txt",'w')
        f.writelines(lines)
        f.close()

    for f in glob.glob("tmp/*"):
        shutil.rmtree(f)