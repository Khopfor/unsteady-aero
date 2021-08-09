import sys
sys.path.append('./src')
from util import *
from airfoil import *
from copy import deepcopy


def computeCycle(args=[]):
    curParams=json2Dict(CURRENTPARAMSJSON)
    success=True

    if checkComparison(args) :
        if not os.path.isfile(filePath("data_exp")) :
            print(filePath("data_exp")+"  doesn't exist.")
            success=False
        else :
            df=pd.read_csv(filePath("data_exp"))

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
            curParams["A_pitching"],curParams["A_heaving"],curParams["phi"]=A_p,A_h,-phi_h
    else :
        phi_p = 0
        if curParams["omega"] > 0 :
            period=2*np.pi/curParams["omega"]
            T1=np.linspace(period/2,0,50)
            T2=np.linspace(period/2,period,50)
        elif curParams["omega"]==0:
            T1=[0]
            T2=[0]
        else :
            raise ("Error : omega can't be a negative number.")

    if success :
        airfoil=Airfoil(curParams,phi_p=phi_p)

        m=len(T1)
        CzList,CxList,CmList=[],[],[]
        T1T2=np.concatenate([T1,T2])
        for i,t in enumerate(T1T2) :
            airfoil.Cz(t)
            airfoil.Cx(t)
            airfoil.Cm(t)
            CzList.append(deepcopy(airfoil.Cz))
            CxList.append(deepcopy(airfoil.Cx))
            CmList.append(deepcopy(airfoil.Cm))
        # CzList=np.array(CzList).T
        # CxList=np.array(CxList).T
        # CmList=np.array(CmList).T
        # print(CzList[0:m][0].Cz)

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
        df_theo.to_csv(filePath('data',end="",ext=".csv",comparison=checkComparison(args),create=True), na_rep=" ", index=False)   # Writes the DataFrame of the model to a csv file

        # # Contributions
        dict_contrib={
                'Cz_AM1':[cz.addedMassTerm for cz in CzList[0:m]],
                'Cz_AM2':[cz.addedMassTerm for cz in CzList[m:]],
                'Cz_VE1':[cz.vortexTerm for cz in CzList[0:m]],
                'Cz_VE2':[cz.vortexTerm for cz in CzList[m:]],
                'Cx_bonnet1':[cx.Cx_Bonnet for cx in CxList[0:m]],
                'Cx_bonnet2':[cx.Cx_Bonnet for cx in CxList[m:]],
                'Cx_steady1':[cx.steadyCxProj for cx in CxList[0:m]],
                'Cx_steady2':[cx.steadyCxProj for cx in CxList[m:]],
        }
        df_contrib=pd.DataFrame(dict_contrib)
        df_contrib.to_csv(filePath('data',end="_contrib",ext=".csv",comparison=checkComparison(args),create=True), index=False)

        # Efficiency
        dict_eff={
                'Cx_mean':np.mean([cx.Cx for cx in CxList]),
                'Cz_mean':np.mean([cz.Cz for cz in CzList]),
                'Cm_mean':np.mean([cm.Cm for cm in CmList]),
                'CPp_mean':np.mean([-CmList[i].Cm*airfoil.theta.d(T1T2[i]).real for i in range(len(CxList))]),
                'CPh_mean':np.mean([-CzList[i].Cz*airfoil.h.d(T1T2[i]).real for i in range(len(CzList))]),
        }
        if curParams['A_pitching']==0 :
            dict_eff['Eff_wg']=[0]
        else :
            path_np=filePath('data',comparison=checkComparison(args)).replace('pitch'+("000"+str(int(curParams["A_pitching"]*10)))[-3:],'pitch000')
            if os.path.isfile(path_np) :
                Cx_np=pd.read_csv(path_np)['Cx_mean'].to_numpy()[0]
                dict_eff['Eff_wg']=[1-(dict_eff['Cx_mean']+dict_eff['CP_mean'])/Cx_np]
            else :
                print('Impossible to compute Eff_wg')
                dict_eff['Eff_wg']=['None']
        dict_eff['Eff_prop']= dict_eff['Cx_mean']/(dict_eff['CPp_mean']+dict_eff['CPh_mean'])
        df_eff=pd.DataFrame(dict_eff)
        df_eff.to_csv(filePath('data',end="_eff",ext=".csv",comparison=checkComparison(args),create=True), index=False)



        # Quasi-static
        dict_qs=dict_theo   # Copies the dictionnary of the model to create the dictionnary of the quasi-static theory
        dict_qs["Cx1"]=[cx.Cx_qs for cx in CxList[0:m]]   # Replaces the coefficient values with quasi-static values
        dict_qs["Cx2"]=[cx.Cx_qs for cx in CxList[m:]]
        dict_qs["Cz1"]=[cz.Cz_qs for cz in CzList[0:m]]
        dict_qs["Cz2"]=[cz.Cz_qs for cz in CzList[m:]]
        dict_qs["Cm1"]=[cm.Cm_qs for cm in CmList[0:m]]
        dict_qs["Cm2"]=[cm.Cm_qs for cm in CmList[m:]]
        df_qs=pd.DataFrame(dict_qs)     # Creates the quasi-static DataFrame from the dictionnary
        df_qs.to_csv(filePath('data',end="_qs",ext=".csv",folder="quasi-static",comparison=checkComparison(args),create=True), index=False)    # Writes the quasi-static DataFrame to csv file
    return success

