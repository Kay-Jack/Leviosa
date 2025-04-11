import magpylib as magpy
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import math
from scipy.spatial.transform import Rotation as R
import time

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
    xs:np.array = np.linspace(-0.05, 0.05, 29),
    zs:np.array = np.linspace(-0.05, 0.05, 29),
    ) -> None:

    if floatingMagnet: 
        magnetCollection.add(floatingMagnet, override_parent = True)
    Bs = np.array([[magnetCollection.getB([x,0,z]) for x in xs] for z in zs]) # may be possible to vectorize this: https://magpylib.readthedocs.io/en/5.0.3/_pages/user_guide/examples/examples_app_coils.html
    X,Z = np.meshgrid(xs,zs)
    U,V = Bs[:,:,0], Bs[:,:,2]
    print(np.max(U**2+V**2), np.min(U**2+V**2))
    sPlot = ax.streamplot(X, Z, U, V, color = norm(np.log(U**2+V**2)), density=1.)
    ax.set_aspect('equal')
    # fig.colorbar(sPlot.lines, ax = ax) # not sure what this returns tbh...
    

def main():

    penMagnet1 = magpy.magnet.Cylinder(polarization=(0,0,1), dimension=(0.01, 0.005), position = (0, 0, 0.014))
    penMagnet2 = magpy.magnet.Cylinder(polarization=(0,0,1), dimension=(0.01, 0.005), position = (0, 0, 0.014 + 0.005))
    penMagnetsCol = magpy.Collection(penMagnet1, penMagnet2)

    ### Coil exp.
    
    fig, axs = plt.subplots(1,3)

    for lv1, (coilOD, coilH) in enumerate(zip([12e-3, 24e-3, 48e-3], [39.2e-3, 19.6e-3, 9.65e-3])):
        coil = magpy.Collection()
        wireD = 0.3e-3
        coilID = 8e-3
        # coilOD = 19.6e-3
        # coilH = 24e-3
        coilPosTop = 6e-3
        for z in np.arange(coilPosTop - wireD/2 + 1e-6, coilPosTop - coilH + wireD/2 - 1e-6, -wireD): # add -1e-6 from end given arange excludes max values...
            for r in np.arange((coilID + wireD)/2, (coilOD - wireD)/2 + 1e-6, wireD):
                winding = magpy.current.Circle(
                    current=0.25,
                    diameter=2*r,
                    position=(0,0,z),
                )
                coil.add(winding)
        # coil.show()
        ### METHOD 1
        t0 = time.time()
        xs = np.linspace(-0.05, 0.05, 29)
        zs = np.linspace(-0.05, 0.05, 29)
        Bs = np.array([[coil.getB([x,0,z]) for x in xs] for z in zs])
        X,Z = np.meshgrid(xs,zs)
        U,V = Bs[:,:,0], Bs[:,:,2]
        print(time.time() - t0)
        ### METHOD 2: much faster.... look to vectorize everything...
        t0 = time.time()
        grid = np.mgrid[-0.05:0.05:29j, 0:0:1j, -0.05:0.05:29j].T[:,0]
        # 'j' here is imaginary number to enable setting number of steps insetad of step size
        # note that here the slicint of [:,0] == [:,0,:,:]
        _, Y, Z = np.moveaxis(grid, 2, 0)
        B = magpy.getB(coil, grid)
        _, By, Bz = np.moveaxis(B, 2, 0)
        print(time.time() - t0)


        print(np.max(U**2+V**2), np.min(U**2+V**2))
        axs[lv1].streamplot(X, Z, U, V, color = np.log(U**2+V**2), density=1.)
        axs[lv1].set_aspect('equal')
    fig.suptitle('Compare different coil shapes')
    plt.show()

    ## Exp 1: Compare zPos of 2nd permanent magnet ring
    fig, axs = plt.subplots(2,3, figsize = (10, 15))

    for lv1, zPos in enumerate([-0.005, -0.02, -0.04]):
        # determine norm by running once & then use values output in terminal
        norm = mpl.colors.Normalize(vmin = 0, vmax = 0.7)

        magnetRing1 = magnetRing(0.06, 0, 0, 12)
        magnetRing2 = magnetRing(0.06, 0, zPos, 12)
        c = magnetRing1.mCol + magnetRing2.mCol
        plotSysB(c, axs[0, lv1], fig, norm)
        plotSysB(c, axs[1, lv1], fig, norm, penMagnetsCol)
        axs[0, lv1].set_title(f'Gap between rings = {-np.round(zPos+0.005, 3)} m')

    fig.suptitle('Compare variable spacing of magnet rings')
    # fig.colorbar()
    plt.show()

    ## Exp 2: Compare impacts of changing angle of top magnet ring
    fig, axs = plt.subplots(2,3, figsize = (10, 15))

    for lv1, angle in enumerate([-15, 0, 15]):
        # determine norm by running once & then use values output in terminal
        norm = mpl.colors.Normalize(vmin = 0, vmax = 0.7)

        magnetRing1 = magnetRing(0.06, angle, 0, 12)
        magnetRing2 = magnetRing(0.06, 0, -0.02, 12)
        c = magnetRing1.mCol + magnetRing2.mCol
        plotSysB(c, axs[0, lv1], fig, norm)
        plotSysB(c, axs[1, lv1], fig, norm, penMagnetsCol)
        axs[0, lv1].set_title(f'Angle of top ring = {angle} degrees')

    fig.suptitle('Compare variable angle of bot magnet ring')
    # fig.colorbar()
    plt.show()

    ## Exp 3: Compare impacts of changing angle of bot magnet ring
    fig, axs = plt.subplots(2,3, figsize = (10, 15))

    for lv1, angle in enumerate([-15, 0, 15]):
        # determine norm by running once & then use values output in terminal
        norm = mpl.colors.Normalize(vmin = 0, vmax = 0.7)

        magnetRing1 = magnetRing(0.06, 0, 0, 12)
        magnetRing2 = magnetRing(0.06, angle, -0.02, 12)
        c = magnetRing1.mCol + magnetRing2.mCol
        plotSysB(c, axs[0, lv1], fig, norm)
        plotSysB(c, axs[1, lv1], fig, norm, penMagnetsCol)
        axs[0, lv1].set_title(f'Angle of bot ring = {angle} degrees')

    fig.suptitle('Compare variable angle of top magnet ring')
    # fig.colorbar()
    plt.show()

    ## Exp 4: Compare impacts of changing diameter of magnet rings
    fig, axs = plt.subplots(2,3, figsize = (10, 15))

    for lv1, ringD in enumerate([0.04, 0.06, 0.08]):
        # determine norm by running once & then use values output in terminal
        norm = mpl.colors.Normalize(vmin = 0, vmax = 0.7)

        magnetRing1 = magnetRing(ringD, 0, 0, 12)
        magnetRing2 = magnetRing(ringD, 0, -0.02, 12)
        c = magnetRing1.mCol + magnetRing2.mCol
        plotSysB(c, axs[0, lv1], fig, norm)
        plotSysB(c, axs[1, lv1], fig, norm, penMagnetsCol)
        axs[0, lv1].set_title(f'Diameter of ring = {ringD} m')

    fig.suptitle('Compare variable diameter of magnet rings')
    # fig.colorbar()
    plt.show()
    

if __name__ == "__main__":
    main()