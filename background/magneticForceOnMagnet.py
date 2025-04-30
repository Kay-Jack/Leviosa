import magpylib as magpy
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import pyvista as pv
import math
from scipy.spatial.transform import Rotation as R
import time
from magpylib_force import getFT

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
    

def main():
    # cannot apply getFT onto magpy collection. Will need to see if principle of superposition applies (try 2 magnets stacked & 1 magnet of double size)
        # YES THIS GENERALLY SEEMS TRUE
    # penMagnetsCol = magpy.Collection(penMagnet1, penMagnet2)
    penMagnet1 = magpy.magnet.Cylinder(polarization=(0,0,1), dimension=(0.01, 0.005), position = (0, 0.01, 0.014))
    penMagnet1.meshing = 15
    # penMagnet1.show()
    penMagnet2 = magpy.magnet.Cylinder(polarization=(0,0,1), dimension=(0.01, 0.005), position = (0, 0.01, 0.014 + 0.005))
    penMagnet2.meshing = 15
    # penMagnet2.show()
    penMagnet3 = magpy.magnet.Cylinder(polarization=(0,0,1), dimension=(0.01, 0.01), position = (0, 0.01, 0.014 + 0.005/2))
    penMagnet3.meshing = 15
    # penMagnet3.show()


    magnetRing1 = magnetRing(0.06, 0, 0, 12)
    magnetRing2 = magnetRing(0.06, 0, -0.02, 12)
    c = magnetRing1.mCol + magnetRing2.mCol

    F1, T1 = getFT(c, penMagnet1) + getFT(c, penMagnet2)
    print(F1, T1)

    F2, T2 = getFT(c, penMagnet3)
    print(F2, T2)

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

    

if __name__ == "__main__":
    main()