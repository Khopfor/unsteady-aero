from src.util.util import *

blacklist = ['time','t*','Mx','Cmx','q0','dtheta']

def sc (i,nx,ny):
    return (nx,ny,i)

def showPlot (save, showTime, dir, comp=False):
    plt.tight_layout()
    plt.show(block=not(showTime))
    if save :
        plt.savefig(filePath(dir,ext=".png",comparison=comp,create=True))
    if showTime :
        timer=Thread(target=remainingTime,args=[showTime])
        timer.start()
        plt.pause(showTime)
        plt.close()
        timer.join()