import sys
sys.path.append('./src')
from util import *
from airfoil import *
from copy import deepcopy


def computeCycle(args):
    curParams=curParamsDict()
    success=True

    if 'compare' in args or 'comparison' in args :
        if not os.path.isfile(filePath("data","exp")) :
            print(filePath("data","exp")+"  doesn't exist.")
            success=False
        else :
            df=pd.read_csv(filePath("data","exp"))

            T1=df["t*1"].to_numpy()
            T2=df["t*2"].to_numpy()
            T=np.concatenate([np.flip(T1),T2])
            P=np.concatenate([np.flip(df["pitch_angle"].to_numpy()),df["pitch_angle"].to_numpy()])
            H=np.concatenate([np.flip(df["h*1"].to_numpy()),df["h*2"].to_numpy()])

            def squaredError (X,Y,params,c=0):
                A,phase=params
                return np.sum(np.power(c+A*np.cos(curParams["omega"]*X+phase)-Y,2*np.ones_like(X)))

            def sqErrPitch (params):
                return squaredError(T,P,np.array(params),c=curParams["theta0"])

            def sqErrHeaving (params):
                return squaredError(T,H,np.array(params))

            opRes_p = optimize.minimize(sqErrPitch,[2,0.0],constraints=optimize.LinearConstraint(np.eye(2),[0.0,-np.pi],[20,np.pi]))
            opRes_h = optimize.minimize(sqErrHeaving,[5,0.1],constraints=optimize.LinearConstraint(np.eye(2),[-10,-np.pi],[10,np.pi]))
            A_p,phi_p=opRes_p.x
            A_h,phi_h=opRes_h.x
            # print("A_p = ",A_p," phi_p = ",phi_p)
            # print("A_h = ",A_h," phi_h = ",phi_h)
            curParams["A_pitching"],curParams["A_heaving"],curParams["phi"]=A_p,A_h,phi_p
    else :
        phi_h = 0
        period=2*np.pi/curParams["omega"]
        T1=np.linspace(period/2,0,50)
        print(T1)
        T2=np.linspace(period/2,period,50)

    if success :
        airfoil=Airfoil(curParams,phi_h=phi_h)

        m=len(T1)
        CzList,CxList,CmList=[],[],[]
        for i,t in enumerate(np.concatenate([T1,T2])) :
            CzList.append(deepcopy(airfoil.Cz))
            CxList.append(deepcopy(airfoil.Cx))
            CmList.append(deepcopy(airfoil.Cm))
        # CzList=np.array(CzList).T
        # CxList=np.array(CxList).T
        # CmList=np.array(CmList).T
        
        # Model
        dict_theo={'pitch_angle':[rad2deg(airfoil.theta(t).real) for t in T1],
                't*1':T1,
                't*2':T2,
                'h*1':[airfoil.h(t).real for t in T1],
                'h*2':[airfoil.h(t).real for t in T2],
                'dtheta1':[airfoil.theta.d(t).real  for t in T1],
                'dtheta2':[airfoil.theta.d(t).real  for t in T2],
                'alpha1': [rad2deg(airfoil.alpha(t)) for t in T1],
                'alpha2': [rad2deg(airfoil.alpha(t)) for t in T2],
                'Cx1':[cx.Cx for cx in CxList[0:m]],
                'Cx2':[cx.Cx for cx in CxList[m:]],
                'Cz1':[cz.Cz for cz in CzList[0:m]],
                'Cz2':[cz.Cz for cz in CzList[m:]],
                'Cm1':[cm.Cm for cm in CmList[0:m]],
                'Cm2':[cm.Cm for cm in CmList[m:]],}
        df_theo=pd.DataFrame(dict_theo)
        df_theo.to_csv(filePath('data','model'), index=False)   # Writes the DataFrame of the model to a csv file

        # # Contributions
        # dict_contrib={
        #         'Cz_AM':
        #         'Cz_VE':
        #         'Cx_bonnet':
        #         'Cx_steady':
        # }
        # df_contrib


        # # Quasi-static
        # dict_qs=dict_theo   # Copies the dictionnary of the model to create the dictionnary of the quasi-static theory
        # dict_qs["Cx1"]=Cx_theo[1,0:m]   # Replaces the coefficient values with quasi-static values
        # dict_qs["Cx2"]=Cx_theo[1,m:]
        # dict_qs["Cz1"]=Cz_theo[1,0:m]
        # dict_qs["Cz2"]=Cz_theo[1,m:]
        # dict_qs["Cm1"]=Cm_theo[1,0:m]
        # dict_qs["Cm2"]=Cm_theo[1,m:]
        # df_qs=pd.DataFrame(dict_qs)     # Creates the quasi-static DataFrame from the dictionnary
        # df_qs.to_csv(filePath('data/qs',pitch), index=False)    # Writes the quasi-static DataFrame to csv file
        # airfoil=Airfoil(currentParams)
    return success

