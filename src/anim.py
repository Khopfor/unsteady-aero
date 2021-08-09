import sys
sys.path.append('./src')
from util import *
from airfoil import *
import matplotlib.animation as animation


def runAnimation ():
    mode=input("Enter 'real' for a real frequency animation or anything else for a normalized animation : ")
    if mode=="real":
        U=input("Enter the incoming flow speed U = ")
    curParams=json2Dict(CURRENTPARAMSJSON)
    df=pd.read_csv(filePath("data"))
    theta=np.concatenate((np.flip(df["pitch_angle"].to_numpy()),df["pitch_angle"].to_numpy()))
    h=np.concatenate((np.flip(df["h*1"].to_numpy()),df["h*2"].to_numpy()))
    Cz=np.concatenate((np.flip(df["Cz1"].to_numpy()),df["Cz2"].to_numpy()))
    Cx=np.concatenate((np.flip(df["Cx1"].to_numpy()),df["Cx2"].to_numpy()))
    nbFrames=len(theta)
    frequency=curParams["omega"]*params["dim_quantities"]["U"]
    period=1/frequency
    fps=nbFrames/period
    print("frames : ",nbFrames)
    print("fps : ",fps)
    print("frequency : ",frequency)
    airfoil=Airfoil.NACA_4Digits(curParams["NACA"],500)
    fig=plt.figure(figsize=(14,7)) # Creates the figure
    ax=subplotMaker((1,1,1),"","","")
    # plt.plot()
    # thetaMax,thetaMin = rad2deg(airfoil.theta0+airfoil.A_theta), rad2deg(airfoil.theta0-airfoil.A_theta) # Computes alfa min and alfa max
    # windOriginX = max(0.1,airfoil.x_g+0.1)+1/2
    line,=ax.plot(airfoil[0],airfoil[1],color='black')
    A,=ax.plot([0],[0],'.',color="orange")
    forces=ax.quiver([0,0,0],[0,0,0],[0,0,0],[0,0,0],width=0.002,scale=5,color=["purple","green","red"])
    # wake,=ax.plot()
    ax.axis('equal')
    plt.xlim([-2,2])
    # plt.ylim([np.min(h)-0.4,np.max(h)+0.4])
    # wind=plt.quiver([windOriginX,windOriginX,0],[0,0,0],[-1/2,0,0],[0,0,0],width=0.005,color=['blue','green','red'],scale=2) # Wind vectors
    # forces=plt.quiver([0,0],[0,0],[0,0],[0,0],width=0.005,color=['purple','green'],scale=2) # Force vectors
    # b=True
    plt.tight_layout()

    def init ():
        pass
        # global t, time, Cz, Cx, Cm, theta
        # t=0
        # plt.plot(0,0,'.',color='grey')
        # time,Cz,Cm,Cx,theta=[],[[],[],[],[],[]],[],[[],[],[],[]],[]
        # # return line,CzPlot1,CzPlot2,CzPlot3,CmPlot,

    def animate (frame):
        points=np.array([airfoil[0]+curParams["x_A"],airfoil[1]])
        points=np.dot(rotY(-deg2rad(theta[frame])),points)
        line.set_data(points[0],points[1]+h[frame])
        A.set_data([0,h[frame]])
        forces.set_offsets([[0,h[frame]],[0,h[frame]],[0,h[frame]]])
        forces.set_UVC([0,-Cx[frame],-Cx[frame]],[Cz[frame],0,Cz[frame]])
        # ax.set_xlim([-2,2])
        # ax.set_ylim([np.min(h)-0.4,np.max(h)+0.4])

    ani = animation.FuncAnimation(fig, animate, init_func=init, frames=nbFrames, blit= False, interval=1000/fps, repeat=True)
    plt.show()