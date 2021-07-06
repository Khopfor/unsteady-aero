import pandas as pd
from os.path import exists
from glob import glob
from airfoil import *
from util import *
from plotData import *

#### Flight parameters ###############################
nacaDigits='0015'
chord=0.205
span=0.8
U=10
rho=1.225
mu=1.85e-5
Re=1.225*U*chord/mu
qS=0.5*rho*chord*span*U**2

f=0.05
omega=2*np.pi*f*chord/U #omega_pitching=0.6 # Reduced pulsation for pitching #omega_heaving=0#omega_pitching # Reduced pulsation for heaving

A_pitching=2 # Pitching amplitude (deg)
A_heaving=0.0

phi= 90# Phase shift between vertical wind and pitching
x_g=0.3
theta0=0
###############################################
staticCaseFile="data/exp/res_pitchF005_V10_pitch15_ampl000_alpha00.txt"

def normalize (t):
    return t*U/chord


def dirPath (dir,params):
    dirPath=dir+"/NACA"+params["NACA"]+"_Re"+str(params['Re'])
    omega=params[]
    dirPath+="/f"+("00"+str(floor(f*10)))[-2:]+"_h"+str(floor(A_heaving*1000))+
    # if f>0.05 :
    #     dirPath+="/f"+("00"+str(floor(f*10)))[-2:]+"_h"+str(floor(A_heaving*1000))+"_a13"
    #     if not os.path.isdir(dirPath):
    #         os.mkdir(dirPath)
    return dirPath


def filePath (dir,params):
    filePath=dirPath(dir)
    fStr=("00"+str(int(f*100)))[-3:]
    amplStr=("000"+str(int(A_heaving*1000)))[-3:]
    alpha0Str=("00"+(theta0<0)*"1"+str(abs(theta0)))[-2:]
    filePath+="/res_pitchF"+fStr+"_V"+str(U)+"_pitch"+str(pitch)+"_ampl"+amplStr+"_alpha"+alpha0Str+".txt"
    # print (filePath)
    return filePath

def squaredError (X,Y,params,c=0):
    A,phase=params
    return np.sum(np.power(c+A*np.cos(omega*X+phase)-Y,2*np.ones_like(X)))

def computeCycle (pitch):
    global f
    global A_pitching
    if not exists(filePath("data/exp",pitch)) :
        print(filePath("data/exp",pitch)+"  doesn't exist.")
        raise "Error : file doesn't exist."
    df=pd.read_csv(filePath("data/exp",pitch))
    m=len(df["t*1"].to_numpy())

    T=np.concatenate([np.flip(df["t*1"].to_numpy()),df["t*2"].to_numpy()])
    P=np.concatenate([np.flip(df["pitch_angle"].to_numpy()),df["pitch_angle"].to_numpy()])
    H=np.concatenate([np.flip(df["h*1"].to_numpy()),df["h*2"].to_numpy()])

    def sqErrPitch (params):
        return squaredError(T,P,np.array(params),c=theta0)

    def sqErrHeaving (params):
        return squaredError(T,H,np.array(params))

    opRes_p = optimize.minimize(sqErrPitch,[2,0.0],constraints=optimize.LinearConstraint(np.eye(2),[0.0,-np.pi],[20,np.pi]))
    opRes_h = optimize.minimize(sqErrHeaving,[5,0.1],constraints=optimize.LinearConstraint(np.eye(2),[-10,-np.pi],[10,np.pi]))
    A_p,phi_p=opRes_p.x
    A_h,phi_h=opRes_h.x
    print("A_p = ",A_p," phi_p = ",phi_p)
    print("A_h = ",A_h," phi_h = ",phi_h)
    A_pitching=A_p

    airfoil=Airfoil(x_g,theta0,omega,A_p,A_h,phi_p,Re,nacaDigits,phi_h,staticCaseFile,staticCaseFile)
    Cz_theo, Cx_theo, Cm_theo = [],[],[]

    for i,t in enumerate(np.concatenate([df["t*1"].to_numpy(),df["t*2"].to_numpy()])) :
        # pitch_angle_theo.append(airfoil.theta(t))
        # y_theo.append(airfoil.h(t))
        airfoil.computeForces(t)
        Cz_theo.append(airfoil.Cz[[0,-1]].real)
        Cx_theo.append(airfoil.Cx[[0,-1]].real)
        Cm_theo.append(airfoil.Cm[[0,-1]].real)
    Cz_theo=np.array(Cz_theo).T
    Cx_theo=np.array(Cx_theo).T
    Cm_theo=np.array(Cm_theo).T
    # print(Cz_theo)
    dict_theo={'pitch_angle':[rad2deg(airfoil.theta(t).real) for t in df["t*1"].to_numpy()],
             't*1':df["t*1"].to_numpy(),
             't*2':df["t*2"].to_numpy(),
             'h*1':[airfoil.h(t).real for t in df["t*1"].to_numpy()],
             'h*2':[airfoil.h(t).real for t in df["t*2"].to_numpy()],
             'dtheta1':[airfoil.dtheta(t).real  for t in df["t*1"].to_numpy()],
             'dtheta2':[airfoil.dtheta(t).real  for t in df["t*2"].to_numpy()],
             'alpha1': [rad2deg(airfoil.alphaEff(t)) for t in df["t*1"].to_numpy()],
             'alpha2': [rad2deg(airfoil.alphaEff(t)) for t in df["t*2"].to_numpy()],
             'Cx1':Cx_theo[0,0:m],
             'Cx2':Cx_theo[0,m:],
             'Cz1':Cz_theo[0,0:m],
             'Cz2':Cz_theo[0,m:],
             'Cm1':Cm_theo[0,0:m],
             'Cm2':Cm_theo[0,m:]}
    df_theo=pd.DataFrame(dict_theo)
    df_theo.to_csv(filePath('data/theo',pitch), index=False)
    dict_qs=dict_theo
    dict_qs["Cx1"]=Cx_theo[1,0:m]
    dict_qs["Cx2"]=Cx_theo[1,m:]
    dict_qs["Cz1"]=Cz_theo[1,0:m]
    dict_qs["Cz2"]=Cz_theo[1,m:]
    dict_qs["Cm1"]=Cm_theo[1,0:m]
    dict_qs["Cm2"]=Cm_theo[1,m:]
    df_qs=pd.DataFrame(dict_qs)
    df_qs.to_csv(filePath('data/qs',pitch), index=False)


def plotComparison (pitch):
    df_exp=pd.read_csv(filePath("data/exp",pitch))
    df_theo=pd.read_csv(filePath("data/theo",pitch))
    df_qs=pd.read_csv(filePath("data/qs",pitch))
    index=1
    # ny=ceil(sqrt(len(df_theo)+1))
    # nx=ceil(len(df_theo)/ny)
    nx=2
    ny=5
    T=2*np.pi/omega
    T1=np.flip(df_exp["t*1"].to_numpy())/T
    T2=df_exp["t*2"].to_numpy()/T
    P=df_exp["pitch_angle"].to_numpy()
    nb=len(df_theo.columns)
    n=nx*ny
    subT,subP=[],[]
    fig=plt.figure(num="Theory validation f="+str(f)+"  pitch amplitude="+str(A_pitching),figsize=(13,5))
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
    plt.savefig(filePath("out/comparison",pitch)[:-4])
    plt.pause(1)
    plt.close()


def compareCycle (pitch=A_pitching,reset=False):
    if exists(filePath('data/theo',pitch)) :
        computeCycle(pitch)
        plotComparison(pitch)
    else :
        print("Wrong parameters.")


def computeEfficiency (reset=False):
    pureHeavingRef=0
    for pitch in ["00","02","03","04","05","06","07","08","10"]:
        fileExists=1
        if exists(filePath('data/exp',pitch)[:-4]+"_moy.txt") :
            df_exp=pd.read_csv(filePath('data/exp',pitch)[:-4]+"_moy.txt")
            if 'Eff' not in df_exp.columns or reset:
                if pitch=="00":
                    df_exp["Eff"]=0
                    pureHeavingRef=1
                elif pureHeavingRef :
                    df_np=pd.read_csv(filePath('data/exp',"00")[:-4]+"_moy.txt")
                    df_exp["Eff"]=np.ones(1)-(df_exp["CXmoy"]-df_exp["CPowerMmoy"])/df_np["CXmoy"]
                df_exp.to_csv(filePath('data/exp',pitch)[:-4]+"_moy.txt", index=False)
        if not exists(filePath('data/theo',pitch)) or reset :
            try :
                computeCycle(pitch)
            except:
                fileExists=0
        for case in ['theo','qs']:
            if fileExists and (not exists(filePath('data/'+case,pitch)[:-4]+"_moy.txt") or reset) :
                df_cycle=pd.read_csv(filePath('data/'+case,pitch))
                df_moy={"CXmoy":np.array([np.mean(df_cycle[["Cx1","Cx2"]].to_numpy())]),
                        "CZmoy":np.array([np.mean(df_cycle[["Cz1","Cz2"]].to_numpy())]),
                        "CMmoy":np.array([np.mean(df_cycle[["Cm1","Cm2"]].to_numpy())]),
                        "CPowerXmoy":np.array([np.mean(df_cycle[["Cx1","Cx2"]].to_numpy())]),
                        "CPowerMmoy":np.array([np.mean(np.multiply(df_cycle[["Cm1","Cm2"]].to_numpy(),df_cycle[["dtheta1","dtheta2"]].to_numpy()))])}
                if pitch=="00":
                    df_moy["Eff"]=0
                elif pureHeavingRef :
                    df_np=pd.read_csv(filePath('data/exp',"00")[:-4]+"_moy.txt")
                    df_moy["Eff"]=np.ones(1)-(df_moy["CXmoy"]-df_moy["CPowerMmoy"])/df_np["CXmoy"]
                df_moy=pd.DataFrame(df_moy)
                df_moy.to_csv(filePath('data/'+case,pitch)[:-4]+"_moy.txt", index=False)
    
def plotEfficiency():
    eff_theo,eff_exp,eff_qs=[],[],[]
    meanCx_theo,meanCx_exp,meanCx_qs=[],[],[]
    CP_theo,CP_exp,CP_qs=[],[],[]
    pitch_exp,pitch_theo=[],[]
    for p in range(9):
        pitch_angle=("0"+str(p))[-2:]
        if exists(filePath('data/theo',pitch_angle)[:-4]+"_moy.txt"):
            df_exp=pd.read_csv(filePath('data/exp',pitch_angle)[:-4]+"_moy.txt")
            df_theo=pd.read_csv(filePath('data/theo',pitch_angle)[:-4]+"_moy.txt")
            df_qs=pd.read_csv(filePath('data/qs',pitch_angle)[:-4]+"_moy.txt")
            if "Eff" in df_exp.columns :
                eff_exp.append(df_exp["Eff"].to_numpy()[0])
                eff_theo.append(df_theo["Eff"].to_numpy()[0])
                eff_qs.append(df_qs["Eff"].to_numpy()[0])
            meanCx_exp.append(df_exp["CXmoy"].to_numpy()[0])
            meanCx_theo.append(df_theo["CXmoy"].to_numpy()[0])
            meanCx_qs.append(df_qs["CXmoy"].to_numpy()[0])
            CP_exp.append(df_exp["CPowerMmoy"].to_numpy()[0])
            CP_theo.append(df_theo["CPowerMmoy"].to_numpy()[0])
            CP_qs.append(df_qs["CPowerMmoy"].to_numpy()[0])
            pitch_exp.append(p)
    fig=plt.figure(figsize=(10,5))

    pitch_theo=np.linspace(0,pitch_exp[-1]+0.5,100)

    if "Eff" in df_exp.columns :
        ny=2
        subEff=subplotMaker((1,ny,2),"","Pitch angle amplitude","Energy harvesting efficiency",grid='y',equal=0,xlim=[pitch_exp[0],pitch_exp[-1]])

        subEff.plot(pitch_exp,eff_qs,"-",color="#CCFFCC",label="quasi-static",lw=1)
        # for i,v in enumerate(eff_qs):
        #     subEff.annotate(str(round(v,2)),xy=(pitch[i],v),xytext=(-7,7),textcoords="offset points",color="#BBFFBB")
        subEff.plot(pitch_exp,eff_exp,"--",color="green",label="experiment",lw=1)
        # for i,v in enumerate(eff_exp):
        #     subEff.annotate(str(round(v,2)),xy=(pitch[i],v),xytext=(-7,7),textcoords="offset points",color="#99FF99")
        subEff.plot(pitch_exp,eff_theo,"-",color="green",label="model",lw=1)
        # for i,v in enumerate(eff_theo):
        #     subEff.annotate(str(round(v,2)),xy=(pitch[i],v),xytext=(-7,7),textcoords="offset points",color="green")
        subEff.legend()
        np.savetxt(dirPath("data/comparison")+"/efficiency.txt",np.array([pitch_exp,eff_theo,eff_exp,eff_qs]).T,delimiter=" ")
    else :
        ny=1

    subCx=subplotMaker((1,ny,1),"","Pitch angle amplitude","Mean drag coefficient",grid='y',equal=0,xlim=[pitch_exp[0],pitch_exp[-1]])
    subCx.plot(pitch_exp,meanCx_qs,"-",color="#FFCCCC",label="quasi-static",lw=1)
    subCx.plot(pitch_exp,meanCx_exp,"--",color="#AA8888",label="experiment",lw=1)
    subCx.plot(pitch_exp,meanCx_theo,"-",color="#AA8888",label="model",lw=1)
    # subCx.plot([x*2 for x in subCx.get_xlim()],[0,0],color='grey',lw=1)
    subCx.legend()
    np.savetxt(dirPath("data/comparison")+"/meanCx.txt",np.array([pitch_exp,meanCx_theo,meanCx_exp,meanCx_qs]).T,delimiter=" ")
    np.savetxt(dirPath("data/comparison")+"/CP.txt",np.array([pitch_exp,CP_theo,CP_exp,CP_qs]).T,delimiter=" ")
    # plt.tight_layout()
    plt.savefig(dirPath("out/comparison")+"/efficiency")
    plt.show()

def compareEfficiency(reset=False):
    computeEfficiency(reset)
    plotEfficiency()


compareCycle ("15",1)

# compareCycle ("00",reset=True)
# compareCycle ("02",1)
# compareCycle ("03",1)
compareCycle ("04",1)
# compareCycle ("05",1)
# compareCycle ("06",1)
# compareCycle ("07",1)
# compareCycle ("08",1)
# compareCycle ("10",1)

# compareEfficiency(1)


# for f in glob(dirPath('data/exp')+"/*ampl000_alpha00.txt"):
#     df=pd.read_csv(f,skipinitialspace=1)
#     print(df)
#     # df["alpha1"]=np.round(df["alpha1"].to_numpy()+df["pitch_angle"].to_numpy(),6)
#     # df["alpha2"]=np.round(df["alpha2"].to_numpy()+df["pitch_angle"].to_numpy(),6)
#     # print((df["Cmx1"].to_numpy()))
#     df["Cz1"]=np.round(df["Cz1"].to_numpy()/(0.5*rho*chord*span*U**2),6)
#     df["Cz2"]=np.round(df["Cz2"].to_numpy()/(0.5*rho*chord*span*U**2),6)
#     df["Cx1"]=np.round(df["Cx1"].to_numpy()/(0.5*rho*chord*span*U**2),6)
#     df["Cx2"]=np.round(df["Cx2"].to_numpy()/(0.5*rho*chord*span*U**2),6)
#     df["Cm1"]=np.round(df["Cm1"].to_numpy()/(0.5*rho*chord**2*span*U**2),6)
#     df["Cm2"]=np.round(df["Cm2"].to_numpy()/(0.5*rho*chord**2*span*U**2),6)
#     df["Cmx1"]=np.round(df["Cmx1"].to_numpy()/(0.5*rho*chord**2*span*U**2),6)
#     df["Cmx2"]=np.round(df["Cmx2"].to_numpy()/(0.5*rho*chord**2*span*U**2),6)
#     df["t*1"]=np.round(df["t*1"].to_numpy()*(U/chord),6)
#     df["t*2"]=np.round(df["t*2"].to_numpy()*(U/chord),6)
#     df["h*1"]=np.round(df["h*1"].to_numpy()/chord/1000,6)
#     df["h*2"]=np.round(df["h*2"].to_numpy()/chord/1000,6)
#     df.to_csv(f,index=0)
