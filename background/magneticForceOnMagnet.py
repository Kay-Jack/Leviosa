import magpylib as magpy
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import pyvista as pv
import math
from scipy.spatial.transform import Rotation as R
import time
from magpylib_force import getFT

np.set_printoptions(precision = 4)

class magnetRing:
    def __init__(self, diameter, angle, zPos, numMagnets):
        # diameter = diameter of 
        # angle = angle of magnets in ring. Positive means outwards (assuming vector going 'up'). In radians
        # zPos = z displacement of the ring
        # numMagnets = number of magnets in the ring
        self.diameter = diameter
        self.angle = angle
        self.zPos = zPos
        self.numMagnets = numMagnets

        self.mCol = magpy.Collection()
        for lv1 in range(numMagnets):
            theta = lv1*2*math.pi/numMagnets
            self.mCol.add(
                magpy.magnet.Cylinder(
                    polarization = (0,0,1),
                    dimension = (0.01, 0.005),
                    position = (self.diameter/2, 0, self.zPos),
                    orientation = R.from_rotvec((0, self.angle, 0), degrees = True)
                ).rotate_from_angax(angle = theta, axis = 'z', anchor = (0, 0, 0), degrees = False)
            )

def plotSysB(
    magnetCollection:magpy.Collection, 
    ax,
    fig,
    norm,
    floatingMagnet:bool or magpy.Collection = False,
    grid = np.mgrid[-0.05:0.05:29j, 0:0:1j, -0.05:0.05:29j].T[:,0],
    # 'j' here is imaginary number to enable setting number of steps insetad of step size
    # note that here the slicing of [:,0] == [:,0,:,:]
    ) -> None:

    if floatingMagnet: 
        magnetCollection.add(floatingMagnet, override_parent = True)
    X, _, Z = np.moveaxis(grid, 2, 0)
    B = magpy.getB(magnetCollection, grid)
    Bx, _, Bz = np.moveaxis(B, 2, 0)
    print(np.max(Bx**2+Bz**2), np.min(Bx**2+Bz**2))
    sPlot = ax.streamplot(X, Z, Bx, Bz, color = norm(np.log(Bx**2+Bz**2)), density=1.)
    ax.set_aspect('equal')
    # fig.colorbar(sPlot.lines, ax = ax) # not sure what this returns tbh...
    
def experiment1(showPlots = True):
    # cannot apply getFT onto magpy collection. Will need to see if principle of superposition applies (try 2 magnets stacked & 1 magnet of double size)
        # YES THIS GENERALLY SEEMS TRUE
    # penMagnetsCol = magpy.Collection(penMagnet1, penMagnet2)
    penMagnet1 = magpy.magnet.Cylinder(polarization=(0,0,1), dimension=(0.01, 0.005), position = (0, 0.01, 0.014))
    penMagnet1.meshing = 15
    penMagnet2 = magpy.magnet.Cylinder(polarization=(0,0,1), dimension=(0.01, 0.005), position = (0, 0.01, 0.014 + 0.005))
    penMagnet2.meshing = 15
    penMagnet3 = magpy.magnet.Cylinder(polarization=(0,0,1), dimension=(0.01, 0.01), position = (0, 0.01, 0.014 + 0.005/2))
    penMagnet3.meshing = 15

    magnetRing1 = magnetRing(0.06, 0, 0, 12)
    magnetRing2 = magnetRing(0.06, 0, -0.02, 12)
    c = magnetRing1.mCol + magnetRing2.mCol

    F1, T1 = getFT(c, penMagnet1) + getFT(c, penMagnet2)
    print('Force and Torque for 2 smaller floating magnets\n', F1, T1)

    F2, T2 = getFT(c, penMagnet3)
    print('Force and Torque for 1 larger floating magnet\n', F2, T2)

    print('Results show that principle of superposition applies to forces and torques experienced by the floating magnet')

    if not showPlots:
        return

    pl = magpy.show(c, penMagnet1, penMagnet2, backend='pyvista', return_fig=True)
    arrowF = pv.Arrow(start=(0, 0.01, 0.014 + 0.005/2), direction=F1, scale = 0.05)
    pl.add_mesh(arrowF, color="blue")
    arrowT = pv.Arrow(start=(0, 0.01, 0.014 + 0.005/2), direction=T1, scale = 0.05)
    pl.add_mesh(arrowT, color="yellow")
    pl.show()

    p2 = magpy.show(c, penMagnet3, backend='pyvista', return_fig=True)
    arrowF = pv.Arrow(start=(0, 0.01, 0.014 + 0.005/2), direction=F1, scale = 0.05)
    p2.add_mesh(arrowF, color="blue")
    arrowT = pv.Arrow(start=(0, 0.01, 0.014 + 0.005/2), direction=T1, scale = 0.05)
    p2.add_mesh(arrowT, color="yellow")
    p2.show()
    
    return

def experiment2(showPlot = True):
    hoverHeight = 0.0025 + +0.005 + 0.0105
    penMagnet1 = magpy.magnet.Cylinder(
        polarization=(0,0,1), dimension=(0.01, 0.005), position = (0, 0.00, hoverHeight),
        orientation = R.from_rotvec((0, 15, 0), degrees = True))
    penMagnet1.meshing = 15

    magnetRing1 = magnetRing(0.06, 0, 0, 12)
    magnetRing2 = magnetRing(0.06, 0, -0.02, 12)
    c = magnetRing1.mCol + magnetRing2.mCol
    # c.show()

    F1, T1 = getFT(c, penMagnet1)

    expVals = {
        'gap': [],
        'torque': [],
        'forceZ': [],
        'forceX': [],
    }

    for lv1 in range(20):
        gap = 0.001*lv1
        penMagnet2 = magpy.magnet.Cylinder(
            polarization=(0,0,1), dimension=(0.01, 0.005), position = (0, 0.00, hoverHeight + 0.005 + gap),
            # orientation = R.from_rotvec((0, 15, 0), degrees = True)
            )
        penMagnet2.rotate_from_angax(angle = 15, axis = 'y', anchor = (0, 0, 0.014), degrees = True)
        penMagnet2.meshing = 15
        F2, T2 = getFT(c, penMagnet2)
        Ft = F1 + F2
        Tt = T1 + T2
        # print('Force', Ft)
        print('Torque', Tt)
        expVals['gap'].append(gap)
        expVals['torque'].append(abs(Tt[1]))
        expVals['forceZ'].append(Ft[2])
        expVals['forceX'].append(Ft[0])
    # print(expVals['gap'], expVals['torque'])
    fig, axs = plt.subplots(1,3)
    axs[0].plot(expVals['gap'], expVals['torque'])
    axs[0].set_ylabel('absolute value of torque [N*m]')
    axs[0].grid()
    axs[1].plot(expVals['gap'], expVals['forceZ'])
    axs[1].set_ylabel('forceZ [N]')
    axs[1].grid()
    axs[2].plot(expVals['gap'], expVals['forceX'])
    axs[2].set_ylabel('forceX [N]')
    axs[2].grid()
    fig.supxlabel('gap between floating magnets [m]')
    fig.suptitle('impact of magnet gap separation on floating pen characteristics')
    plt.show()
    # pl = magpy.show(c, penMagnet1, penMagnet2, backend='pyvista', return_fig=True)
    # arrowF = pv.Arrow(start=(0, 0, 0), direction=Ft, scale = 0.05)
    # pl.add_mesh(arrowF, color="blue")
    # arrowT = pv.Arrow(start=(0, 0, 0), direction=Tt, scale = 0.05)
    # pl.add_mesh(arrowT, color="yellow")
    # pl.show()

def experiment3():
    hoverHeight = 0.0025 + 0.005 + 0.0105 + 0.0025# half magnet (datum is mid of 1st magnet ring) + thickness of plastic + hover height measured from plastic + half magnet
    penMagnet1 = magpy.magnet.Cylinder(
        polarization=(0,0,1), dimension=(0.01, 0.005), position = (0, 0.00, hoverHeight),
        orientation = R.from_rotvec((0, 15, 0), degrees = True)
        )
    penMagnet2 = magpy.magnet.Cylinder(
        polarization=(0,0,1), dimension=(0.01, 0.005), position = (0, 0.00, hoverHeight + 0.005),
        )
    penMagnet2.rotate_from_angax(angle = 15, axis = 'y', anchor = (0, 0, 0.014), degrees = True)
    penMagnet1.meshing = 15
    penMagnet2.meshing = 15

    magnetRing1 = magnetRing(0.06, 0, 0, 12)
    magnetRing2 = magnetRing(0.06, 0, -0.02, 12)
    c1 = magnetRing1.mCol + magnetRing2.mCol
    # c1.show()

    magnetRing3 = magnetRing(0.06, 0, 0, 12)
    c2 = magnetRing3.mCol
    # c2.show()

    F2, T2 = getFT(c2, penMagnet1) + getFT(c2, penMagnet2) 
    F1, T1 = getFT(c1, penMagnet1) + getFT(c1, penMagnet2) 
    print('forces', '2 rings', F1, '1 ring', F2)
    print('torques', '2 rings', T1, '1 ring', T2)
    print('OUTCOME 1: extra ring actually weakens field strength in z but massively increases strength of field')
    
    sensorZPos = hoverHeight - 0.0025 - 0.0028 - 0.0063 # hoverheight - 1/2 thickness of magnet - hover height from top of secureEM - sensorPos from top of secureEM
    B1 = magpy.getB(c1, [0, 0, sensorZPos])
    B2 = magpy.getB(c2, [0, 0, sensorZPos])
    print('2 rings', B1)
    print('1 ring', B2)
    print('OUTCOME 2: does not correspond to expected outcome. Expected 2 coil system to have stronger field. Ferrite core (lower down) must be magnetizing in permanent field, thus changing sensor readings')


def main():
    # validateSuperposition
    # experiment1()

    # validate stability of floating pen based on separation of floating magnets
    # experiment2()

    # what does the 2nd ring do?
    experiment3()
    
    # compare 2 rings vs 1 stronger ring assuming approx same vertical force on magnet
    

if __name__ == "__main__":
    main()