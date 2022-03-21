from src.util.util import *
from src.airfoil import *
import matplotlib as mpl
import matplotlib.animation as animation


def runAnimation ():
    curParams=json2Dict(CURRENTPARAMSJSON)
    params=json2Dict(PARAMSJSON)
    mode=input("Enter 'real' for a real frequency animation or anything else for a normalized animation : ")
    if mode=="real":
        new_U=input("Current incoming flow speed is U="+str(params["dim_quantities"]["U"])+". Enter new value or press 'Enter' to continue : ")
        if is_float(new_U):
            params["dim_quantities"]["U"]=float(new_U)
        new_chord=input("Current chord is chord="+str(params["dim_quantities"]["chord"])+". Enter new value or press 'Enter' to continue : ")
        if is_float(new_chord):
            params["dim_quantities"]["chord"]=float(new_chord)
        frequency=curParams["omega"]*params["dim_quantities"]["U"]/(params["dim_quantities"]["chord"]*2*np.pi)
        period=1/frequency
    else :
        period=6
        frequency=1/period
    df=pd.read_csv(filePath("data",folder="BF"))
    df_eff=pd.read_csv(filePath("data",folder="BF",end="_eff"))
    theta=df2numpy(df,["pitch_angle","pitch_angle"],[1,0])
    h=df2numpy(df,["h*1","h*2"],[1,0])
    alpha=df2numpy(df,["alpha1","alpha2"],[1,0])
    Cz=df2numpy(df,["Cz1","Cz2"],[1,0])
    Cx=df2numpy(df,["Cx1","Cx2"],[1,0])
    Cm=df2numpy(df,["Cm1","Cm2"],[1,0])
    x_Fa=[-(Cm[k]+Cz[k]*curParams["x_A"]-Cx[k]*curParams["x_A"])/(-Cx[k]*np.sin(deg2rad(theta[k]))+Cz[k]*np.cos(deg2rad(theta[k]))) for k in range(len(Cz))]
    # x_Fa=movingMean(x_Fa,3)
    nbFrames=len(theta)
    fps0=nbFrames/period
    fps=min(40,fps0)
    nbFrames=int(fps*period)
    print("===== ANIMATION =======================================")
    print("----- Video -------------------------------------------")
    print("  frequency : ",round(frequency,2))
    print("  period = ",round(period,4))
    print("  frames = ",nbFrames)
    print("  fps = ",round(fps,2))
    print("\n----- Parameters --------------------------------------")
    prettyPrint(curParams)
    print("\n----- Dimensionless values ------------------------------")
    print("  Strouhal number = ",round(curParams["omega"]*curParams["A_heaving"]/np.pi,4))
    print("  Feathering parameter = ",round(deg2rad(curParams["A_pitching"])/np.arctan(curParams["A_heaving"]*curParams["omega"]/params["dim_quantities"]["U"]),4))
    print("  A_Vh* = ",curParams["A_heaving"]*curParams["omega"])
    A_alphaH=round(np.arctan(curParams["A_heaving"]*curParams["omega"]),2)
    print("  A_alphah = ",A_alphaH, "rad = ",rad2deg(A_alphaH),"deg")
    alphaMax=round(np.max(np.abs(alpha)),2)
    if alphaMax>10 : alphaStr = "\033[91m{}\033[00m".format(alphaMax)
    else : alphaStr = str(alphaMax)
    print("  A_alpha =",alphaStr,"deg")
    print("\n----- Efficiency --------------------------------------")
    print("  Mean drag coefficient = ",round(float(df_eff["Cx_mean"].to_numpy()[0]),3 ))
    print("  Propulsion efficiency = ",round(float(df_eff["Eff_prop"].to_numpy()[0]),3))
    print("  Wind gusts efficiency = ",df_eff["Eff_wg"].to_numpy()[0])
    print("=======================================================\n")
    airfoil=Airfoil.NACA_4Digits(curParams["NACA"],150)
    mpl.rcParams['toolbar'] = 'None'
    fig=plt.figure(figsize=(14,7),facecolor="lightgrey") # Creates the figure
    ax=subplotMaker((1,1,1),"","","")
    ax.set_xlabel("x/c")
    ax.set_ylabel("-z/c")
    # plt.plot()
    # thetaMax,thetaMin = rad2deg(airfoil.theta0+airfoil.A_theta), rad2deg(airfoil.theta0-airfoil.A_theta) # Computes alfa min and alfa max
    # windOriginX = max(0.1,airfoil.x_g+0.1)+1/2
    line,=ax.plot(airfoil[0],airfoil[1],color='black')
    A,=ax.plot([0],[0],'.',color="orange")
    forces=ax.quiver([0,0,0],[0,0,0],[0,0,0],[0,0,0],width=0.002,scale=5,color=["purple","green","red"])
    # flow=ax.
    wake=np.array([np.zeros(60),np.zeros(60)])
    wakePlot,=ax.plot(*wake,'.',ms=2,color="#99BBFF")
    ax.axis('equal')
    plt.xlim([-2.5,1.5])
    # plt.ylim([np.min(h)-0.4,np.max(h)+0.4])
    # wind=plt.quiver([windOriginX,windOriginX,0],[0,0,0],[-1/2,0,0],[0,0,0],width=0.005,color=['blue','green','red'],scale=2) # Wind vectors
    # forces=plt.quiver([0,0],[0,0],[0,0],[0,0],width=0.005,color=['purple','green'],scale=2) # Force vectors
    # b=True
    plt.tight_layout()

    def init ():
        global t
        t=time.time()
        # global t, time, Cz, Cx, Cm, theta
        # t=0
        # plt.plot(0,0,'.',color='grey')
        # time,Cz,Cm,Cx,theta=[],[[],[],[],[],[]],[],[[],[],[],[]],[]
        # # return line,CzPlot1,CzPlot2,CzPlot3,CmPlot,

    # dx=2*np.pi/curParams["omega"]/len(theta)*params["dim_quantities"]["chord"]
    dx=2*np.pi/(curParams["omega"]*period)*max(0,1000/fps-0.4)/1000
    points=np.array([airfoil[0]+curParams["x_A"],airfoil[1]])
    # with open("cache/frame_time.txt","r") as f:
    #     N,AVG=f.readlines()
    #     AVG=float(AVG)
    #     f.close()

    def animate (frame0):
        # print(frame0)
        # if frame0 == 0 :
        #     t=time.time()
        #     with open("cache/frame_time.txt","r") as f:
        #         N,avg=f.readlines()
        #         N=1+int(N)
        #         avg=float(avg)*(N-1)
        #         f.close()
        while time.time()-t < frame0*period/nbFrames :
            pass
        frame=int(frame0*fps0/fps)
        pts=np.dot(rotY(-deg2rad(theta[frame])),points)
        pts[1]+=h[frame]
        wake[0]=wake[0]-dx
        wake[:,frame0%(len(wake[0]))]=pts[:,len(pts[0])//2]
        wakePlot.set_data(*wake)
        line.set_data(*pts)
        A.set_data([0,h[frame]])
        O_F=np.array([(x_Fa[frame]+curParams["x_A"])*np.cos(deg2rad(theta[frame])),(x_Fa[frame]+curParams["x_A"])*np.sin(deg2rad(theta[frame]))])
        # O_F=np.dot(rotY(deg2rad(theta[frame])),O_F)
        O_F[1]+=h[frame]
        O_F[0]=max(min(curParams["x_A"],O_F[0]),curParams["x_A"]-1)
        forces.set_offsets([O_F,O_F,O_F])
        forces.set_UVC([0,-Cx[frame],-Cx[frame]],[Cz[frame],0,Cz[frame]])
        # print(time.time()-t)
        # ax.set_xlim([-2,2])
        # ax.set_ylim([np.min(h)-0.4,np.max(h)+0.4])
        # if frame0 == 0 :
        #     new_avg=(avg+time.time()-t)/N
        #     with open("cache/frame_time.txt",'w') as f :
        #         f.writelines([str(N)+'\n',str(new_avg)])
        #         f.close()

    ani = animation.FuncAnimation(fig, animate, init_func=init, frames=nbFrames, blit= False, interval=0, repeat=True)
    plt.show()