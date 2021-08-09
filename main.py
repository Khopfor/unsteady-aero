import sys
import platform
import os
import glob
sys.path.append('./src')
sys.path.append(glob.glob('./src/*'))
from util import *
import shutil
# from params import params
from computeCycle import computeCycle
from plot import plotComparison, plotContrib
from anim import runAnimation
import json

VERSION = 1.0
OS = platform.system()
CURRENTPARAMSJSON='current-params.json'
PARAMSJSON='params.json'
MAXLASTCMD=20

# with open("params.txt",'r') as f :
#     eval(f.read())

exit=False
params={}

def updateParams ():
    global params
    checkParamsFile()
    os.system("python params.py")
    params=json2Dict(PARAMSJSON)

print("\n=====================================================================")
print(" UNSTEADY AERODYNAMICS PROGRAM  Version "+str(VERSION))
print(" Aymeric Braud    2021")
print("=====================================================================")

def printHelp ():
    print("\nCOMMANDS\n")
    print("    exit OR quit      Exit program")
    print("    edit              Open the parameters python file to edit them")
    print("    set <parameter>   Set the specified parameter")
    print("    param             Show current parameters namely parameters file content")
    print("    exp               Show available experimental results for comparison")
    print("    run               Run program. No argument only computes cycles and save data in text files.")
    print("      - plot              Plot graphs")
    print("      - save              Save graphs and animations as images and videos")
    print("      - comparison        Compute comparison between model and experiment and plot it if the plot command is passed")
    print("      - contrib           Plot contributions if the plot command is passed")
    print("      - eff               Compute efficiency and plot it if the plot command is passed")
    print("    anim              Show animation")
    print("    clean             Delete all data, images and videos")
    print("    help              Show this help")
    print()

def printParam():
    print("\nPARAMETERS")
    prettyPrint(params)

updateParams()
printHelp()
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

    if cmd in ["exit",'quit','q'] :
        exit=True

    elif cmd in ["platform",'os'] :
        print(OS)

    elif cmd in ["edit"]:
        if OS == "Linux":
            os.system("gedit params.py")
        elif OS == "Windows":
            os.system("params.py")
        elif OS == "MACOS":
            os.system("open -e params.py")
        updateParams()
        printParam()

    elif "set" in cmd:
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
        if 'np.' not in v and 'range' not in v and '[' and v not in ']' and ',' not in v:
            v='['+v+']'
        if 'np.' in v :
            v="list("+v+")"
        with open("params.py",'r') as f :
            lines=f.readlines()
            f.close()
        with open("params.py",'w') as f :
            for i,line in enumerate(lines):
                if '"'+p+'"' in line:
                    line="    "+'"'+p+'"'+":"+str(v)
                    if p!="A_pitching":
                        line+=","
                    line+='\n'
                f.write(line)
            f.close()
        updateParams()
        printParam()

    elif cmd in ["param","params"]:
        printParam()

    elif cmd in ["exp"]:
        os.system("ls data_exp/*")

    elif cmd in ["h","help"]:
        printHelp()

    elif cmd in ["clean","clear"]:
        if input("Are you sure to delete all data (y/n) ? ") == "y" :
            for d in glob.glob("data/*"):
                shutil.rmtree(d)
            for d in glob.glob("out/*"):
                for dd in glob.glob(d+"/*"):
                    shutil.rmtree(dd)
        print("Data deleted.")

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
                else :
                    anim_params[p]=float(anim_params[p])
        anim_params["polarSource"]=params["polarSource"]
        with open(CURRENTPARAMSJSON,'w') as jsonFile :
            json.dump(anim_params,jsonFile,indent=2)
        computeCycle()
        runAnimation()

    elif "run" in cmd :
        cmdList=cmd.split(' ')
        if len(cmdList)==1 and cmdList[0]=="run" :
            argv=input("    run>> ").split(' ')
        elif len(cmdList)>1:
            argv=cmdList[1:]
            keep=True
        for a in argv:
            for char in ['-',' ',',']:
                a.replace(char,'')
        updateParams()
        for naca in params['NACA']:
            for Re in params['Re']:
                for theta0 in params['theta0']:
                    for x_A in params['x_A']:
                        for omega in params['omega']:
                            for Ah in params['A_heaving']:
                                for phi in params['phi']:
                                    for Ap in params['A_pitching']:
                                        currentParams={'NACA':naca,'polarSource':params['polarSource'],'Re':Re,'theta0':theta0,'x_A':x_A,'omega':omega,'A_heaving':Ah,'phi':phi,'A_pitching':Ap}
                                        with open(CURRENTPARAMSJSON,'w') as jsonFile :
                                            json.dump(currentParams,jsonFile,indent=2)
                                        computeCycle(argv)
                                        showTime=0.01 if not ("show" in argv) else int(float(argv[argv.index("show")+1])) if argv.index("show")+1 < len(argv) and type(int(float(argv[argv.index("show")+1])))==type(0) else 5
                                        if 'plot' in argv and checkComparison(argv) :
                                            plotComparison(save=("save" in argv),showTime=showTime)
                                        if 'plot' in argv and 'contrib' in argv :
                                            plotContrib(save=("save" in argv),showTime=showTime,comp=checkComparison(argv))
                # for p1 in params :
                #     if p1 not in ['NACA','Re'] and len(params[p1])>1:
                #         for p2 in params :
                #             if p2 not in ['NACA','Re',p1] and len(params[p2])>1:

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
                    autocmd=lines[int(end)-1]
            else :
                for i,line in enumerate(lines):
                    if i+1<=5 :
                        if line[-1]=='\n':line=line[:-1]
                        print(str(i+1)+'. '+line)
                number=input("Enter the number of the command : ")
                while (not is_int(number) or int(number)>nbLines) and (number not in ['q']) :
                    number=input("Enter a valid number (or press 'q' to quit) : ")
                if number not in ['q'] :
                    autocmd=lines[int(number)-1]
    else :
        print("Command not valid.")
    if keep :
        f=open("cache/last-commands.txt",'r')
        lines=f.readlines()
        f.close()
        if len(lines)>MAXLASTCMD :
            del(lines[0:len(lines)-MAXLASTCMD])
        if len(lines)!=0:
            if cmd != lines[-1]:
                lines[-1]+='\n'
                lines.append(cmd)
        else :
            lines.append(cmd)
        f=open("cache/last-commands.txt",'w')
        f.writelines(lines)
        f.close()