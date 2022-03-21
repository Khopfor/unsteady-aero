colors={"bordeaux":[0.6,0.3,0.3],"darkgreen":[0.3,0.6,0.3]}

def opacity (color,o=0.5):
    if type(color)==type([]):
        res=[((1-o)+color[0]*o),(1-o)+color[1]*o,(1-o)+color[2]*o]
        res=[max(min(1,v),0) for v in res]
        return res
    else :
        return color

def subtractiveColor (c1,c2=[1,1,1],c3=[1,1,1]):
    res=[0,0,0]
    for i in range(len(c1)) :
        res[i]=c1[i]*c2[i]*c3[i]
    return res

def setColor (model,fnLabel):
    if fnLabel == "Cx_mean":
        return opacity(colors["bordeaux"],1-(model not in ["BF","bf","exp"])*0.5)
    elif "ff" in fnLabel :
        return opacity(colors["darkgreen"],1-(model not in ["BF","bf","exp"])*0.5)