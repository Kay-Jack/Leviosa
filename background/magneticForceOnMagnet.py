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
MAGNET_D = 0.01
MAGNET_H = 0.005

class magnetRing:
    def __init__(self, diameter, angle, zPos, numMagnets, magnetization = 1.6e6): # for default use the old silver magnets
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
                    magnetization = (0,0,magnetization),
                    dimension = (MAGNET_D, MAGNET_H),
                    position = (self.diameter/2, 0, self.zPos),
                    orientation = R.from_rotvec((0, self.angle, 0), degrees = True)
                ).rotate_from_angax(angle = theta, axis = 'z', anchor = (0, 0, 0), degrees = False)
            )

def plotSysB(
    magnetCollection:magpy.Collection, 
    ax,
    fig,
    norm = False,
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
    if norm:
        sPlot = ax.streamplot(X, Z, Bx, Bz, color = norm(np.log(Bx**2+Bz**2)), density=1.)
    else: 
        sPlot = ax.streamplot(X, Z, Bx, Bz, color = np.log(Bx**2+Bz**2), density=1.)
        ax.contour(X, Z, np.log(Bx**2+Bz**2), levels=10, cmap='viridis')
    ax.set_aspect('equal')
    # fig.colorbar(sPlot.lines, ax = ax) # not sure what this returns tbh...
    
def experiment4(showPlots = True):
    # measures force on magnet. Useful for validating magnetic strength...
    mag1 = magpy.magnet.Cylinder(magnetization=(0,0,1), dimension=(MAGNET_D, MAGNET_H), position = (0, 0, 0))
    mag1.meshing = 15
    # for magnetization in [1e1, 1e2, 1e3, 1e4, 1e5, 1e6, 1e7, 1e8, 1e9, 1e10]:
        # coarse pass. Seems like 1e6 is pretty close. Slightly too small
    # for magnetization in [1e6, 2e6, 3e6, 4e6, 5e6]:
        # old silver magnets seems to be [1e6, 2e6]
        # new silver magnets seem very close to 2e6. Something very slightly smaller
    # for magnetization in [1.1e6, 1.2e6, 1.3e6, 1.4e6, 1.5e6, 1.6e6, 1.7e6, 1.8e6, 1.9e6, 2.0e6]:
        # old silver magnets seems to be [1.6e6, 1.7e6]
        # new silver magnets seems to be [1.9e6, 2.0e6]
    # for magnetization in np.linspace(1.6e6, 1.7e6, 11): # for some reason somtimes has issues with pyvista
    # for magnetization in [1.5e6, 1.52e6, 1.54e6, 1.56e6, 1.58e6, 1.6e6]:
        # 1.6e6 seems pretty close for old silver magnets? Unsure if issue with test process. Far values are less than IRL. CLoose are bigger than IRL
    for magnetization in [1.8e6, 1.82e6, 1.84e6, 1.86e6, 1.88e6, 1.9e6]:
        # 1.88e6 seems pretty close for new silver magnets. Unsure if issue with test process but Far values are less than IRL. Close values are bigger than IRL
        mag1.magnetization = (0, 0, magnetization)
        print(f'---magnetization: {magnetization}---')
        for separation in [0.0019, 0.0054, 0.0089]:
            mag2 = mag1.copy() # note that .meshing also translates correctly (I guess discretization is calculated in getFT())
            mag2.position = (0, 0, MAGNET_D + separation)
            F, _ = getFT(mag1, mag2)
            print(separation, F)
    return
    # penMagnet2 = magpy.magnet.Cylinder(magnetization=(0,0,1), dimension=(MAGNET_D, MAGNET_H), position = (0, 0.01, 0.014))
    # penMagnet2.meshing = 15
    

def experiment1(showPlots = True):
    # cannot apply getFT onto magpy collection. Will need to see if principle of superposition applies (try 2 magnets stacked & 1 magnet of double size)
        # YES THIS GENERALLY SEEMS TRUE
    # penMagnetsCol = magpy.Collection(penMagnet1, penMagnet2)
    penMagnet1 = magpy.magnet.Cylinder(polarization=(0,0,1), dimension=(MAGNET_D, MAGNET_H), position = (0, 0.01, 0.014))
    penMagnet1.meshing = 15
    penMagnet2 = magpy.magnet.Cylinder(polarization=(0,0,1), dimension=(MAGNET_D, MAGNET_H), position = (0, 0.01, 0.014 + MAGNET_H))
    penMagnet2.meshing = 15
    penMagnet3 = magpy.magnet.Cylinder(polarization=(0,0,1), dimension=(MAGNET_D, MAGNET_H*2), position = (0, 0.01, 0.014 + MAGNET_H/2))
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
    arrowF = pv.Arrow(start=(0, 0.01, 0.014 + MAGNET_H/2), direction=F1, scale = 0.05)
    pl.add_mesh(arrowF, color="blue")
    arrowT = pv.Arrow(start=(0, 0.01, 0.014 + MAGNET_H/2), direction=T1, scale = 0.05)
    pl.add_mesh(arrowT, color="yellow")
    pl.show()

    p2 = magpy.show(c, penMagnet3, backend='pyvista', return_fig=True)
    arrowF = pv.Arrow(start=(0, 0.01, 0.014 + MAGNET_H/2), direction=F1, scale = 0.05)
    p2.add_mesh(arrowF, color="blue")
    arrowT = pv.Arrow(start=(0, 0.01, 0.014 + MAGNET_H/2), direction=T1, scale = 0.05)
    p2.add_mesh(arrowT, color="yellow")
    p2.show()
    
    return

def experiment2(showPlot = True):
    magnetization = 1.6e6 #use this for floating pen for now?
    # hoverHeight = 0.0025 + MAGNET_H + 0.0105
    hoverHeight = MAGNET_D/2 + 0.005 + 0.0105 + MAGNET_D/2
    # hover height as a MASSIVE impact on stability... if lower, then best to have gap. If higher no good to have gap
    penMagnet1 = magpy.magnet.Cylinder(
        magnetization=(0,0,magnetization), dimension=(MAGNET_D, MAGNET_H), position = (0, 0.00, hoverHeight),
        orientation = R.from_rotvec((0, 15, 0), degrees = True))
    penMagnet1.meshing = 15

    magnetRing1 = magnetRing(0.06, 0, 0, 14)
    magnetRing2 = magnetRing(0.06, 0, -0.02, 14)
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
            magnetization=(0,0,magnetization), dimension=(MAGNET_D, MAGNET_H), position = (0, 0.00, hoverHeight + MAGNET_H + gap),
            # orientation = R.from_rotvec((0, 15, 0), degrees = True)
            )
        penMagnet2.rotate_from_angax(angle = 15, axis = 'y', anchor = (0, 0, hoverHeight), degrees = True)
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

def experiment3(showPlot = True):
    magnetization = 1.6e6 #use this for floating pen for now?

    hoverHeight = MAGNET_D/2 + 0.005 + 0.0105 + MAGNET_D/2# half magnet (datum is mid of 1st magnet ring) + thickness of plastic + hover height measured from plastic + half magnet
    penMagnet1 = magpy.magnet.Cylinder(
        magnetization=(0,0,magnetization), dimension=(MAGNET_D, MAGNET_H), position = (0, 0.00, hoverHeight),
        orientation = R.from_rotvec((0, 15, 0), degrees = True)
        )
    penMagnet2 = magpy.magnet.Cylinder(
        magnetization=(0,0,magnetization), dimension=(MAGNET_D, MAGNET_H), position = (0, 0.00, hoverHeight + MAGNET_H),
        )
    penMagnet2.rotate_from_angax(angle = 15, axis = 'y', anchor = (0, 0, hoverHeight), degrees = True)
    penMagnet1.meshing = 15
    penMagnet2.meshing = 15

    magnetRing1 = magnetRing(0.06, 0, 0, 14)
    magnetRing2 = magnetRing(0.06, 0, -0.02, 14)
    c1 = magnetRing1.mCol + magnetRing2.mCol
    # c1.show()

    magnetRing3 = magnetRing(0.06, 0, 0, 14)
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

    # what is change as 2nd ring drops?
    expVals = {
        'gap': [],
        'torque': [],
        'forceZ': [],
        'sensorZ': [],
    }
    # first base case of just 1 magnet ring
    F3, T3 = getFT(c2, penMagnet1) + getFT(c2, penMagnet2)
    _,_,Bz = magpy.getB(c2, [0,0,sensorZPos])
    expVals['gap'].append(0)
    expVals['torque'].append(abs(T3[1]))
    expVals['forceZ'].append(F3[2])
    expVals['sensorZ'].append(Bz)
    for lv1 in range(20):
        zPos = MAGNET_H + 0.0025*lv1
        magnetRing4 = magnetRing(0.06, 0, -zPos, 14)
        c3 = magnetRing4.mCol # may need override_parent = True    
        c3.add(magnetRing1.mCol, override_parent = True)
        F3, T3 = getFT(c3, penMagnet1) + getFT(c3, penMagnet2) 
        expVals['gap'].append(zPos - MAGNET_H)
        expVals['torque'].append(abs(T3[1]))
        expVals['forceZ'].append(F3[2])
        _,_,Bz = magpy.getB(c3, [0,0,sensorZPos])
        expVals['sensorZ'].append(Bz)

    # print(expVals['gap'], expVals['torque'])
    fig, axs = plt.subplots(1,3)
    # print(expVals['gap'])
    # print(expVals['torque'])
    axs[0].plot(expVals['gap'], expVals['torque'])
    axs[0].set_ylabel('absolute value of torque [N*m]')
    axs[0].grid()
    axs[1].plot(expVals['gap'], expVals['forceZ'])
    axs[1].set_ylabel('forceZ [N]')
    axs[1].grid()
    axs[2].plot(expVals['gap'], expVals['sensorZ'])
    axs[2].set_ylabel('sensor B [T]')
    axs[2].grid()

    fig.supxlabel('gap between permanent magnet rings[m]')
    fig.suptitle('impact of magnet gap separation on floating pen characteristics')
    plt.show()

def experiment5(showPlot = True):
    
    magnetization = 1.6e6 #use this for floating pen for now?    
    hoverHeight = 0.003+0.0024+0.005+0.0025*2+0.003+0.001#MAGNET_D/2 + 0.005 + 0.0105 + MAGNET_D/2# half magnet (datum is mid of 1st magnet ring) + thickness of plastic + hover height measured from plastic + half magnet
    sensorZPos = hoverHeight - 0.0025 - 0.0028 - 0.0063 # hoverheight - 1/2 thickness of magnet - hover height from top of secureEM - sensorPos from top of secureEM

    penMagnet1 = magpy.magnet.Cylinder(
        magnetization=(0,0,magnetization), dimension=(MAGNET_D, MAGNET_H), position = (0, 0.00, hoverHeight),
        orientation = R.from_rotvec((0, 15, 0), degrees = True)
        )
    penMagnet2 = magpy.magnet.Cylinder(
        magnetization=(0,0,magnetization), dimension=(MAGNET_D, MAGNET_H), position = (0, 0.00, hoverHeight + MAGNET_H),
        )
    penMagnet2.rotate_from_angax(angle = 15, axis = 'y', anchor = (0, 0, 0.014), degrees = True)
    penMagnet1.meshing = 15
    penMagnet2.meshing = 15

    # PART 1 COMPARE EXISTING SYSTEMS
    print('PART 1 COMPARE EXISTING SYSTEMS')
    magnetRing1 = magnetRing(0.06, 0, 0, 14)
    magnetRing2 = magnetRing(0.06, 0, -0.02, 14)
    c2 = magnetRing1.mCol + magnetRing2.mCol
    
    magnetRing3 = magnetRing(0.06, 0, 0, 12, 1.88e6)
    c1 = magnetRing3.mCol
    
    F2, T2 = getFT(c2, penMagnet1) + getFT(c2, penMagnet2) 
    _,_,B2 = magpy.getB(c2, [0,0,sensorZPos])
    F1, T1 = getFT(c1, penMagnet1) + getFT(c1, penMagnet2) 
    _,_,B1 = magpy.getB(c1, [0,0,sensorZPos])
    print('forces', '2 rings', F2, '1 ring', F1)
    print('torques', '2 rings', T2, '1 ring', T1)
    print('hall sensor', '2 rings', B2, '1 ring', B1)
    print('OUTCOME: clearly does not match with IRL. Expect approx same force but significantly weaker torque & ~ same hall sensor reading. Expect ferrite core to be the diff')

    # PART 2 TEST DIFF SYSTEMS
    print('PART 2 TEST DIFF SYSTEMS')
    print('OUTCOME: more magnets in low ring reduces force and increases torque')
    hoverHeight2 = 0.003+0.0024+0.005+0.0025*2+0.003 # hoverHeight - 0.001
    sensorZPos2 = 0.003+0.0024-0.0064+0.005+0.0025
    # ring->post + post->EMFastening-> ring->magnet + 1/2magnetH*2 + EMFastening->Pen
    penMagnet3 = magpy.magnet.Cylinder(
        magnetization=(0,0,magnetization), dimension=(MAGNET_D, MAGNET_H), position = (0, 0.00, hoverHeight2),
        orientation = R.from_rotvec((0, 15, 0), degrees = True)
        )
    penMagnet4 = magpy.magnet.Cylinder(
        magnetization=(0,0,magnetization), dimension=(MAGNET_D, MAGNET_H), position = (0, 0.00, hoverHeight2 + MAGNET_H),
        )
    penMagnet4.rotate_from_angax(angle = 15, axis = 'y', anchor = (0, 0, 0.014), degrees = True)
    penMagnet3.meshing = 15
    penMagnet4.meshing = 15

    magnetRing1 = magnetRing(0.06, 0, 0, 14)
    magnetRing2 = magnetRing(0.06, 0, -0.02, 14)
    c1 = magnetRing1.mCol + magnetRing2.mCol
    
    magnetRing3 = magnetRing(0.06, 0, 0, 10, 1.88e6)
    magnetRing4 = magnetRing(0.06, 0, -0.025, 12, 1.88e6)
    c2 = magnetRing3.mCol + magnetRing4.mCol
    
    F1, T1 = getFT(c1, penMagnet1) + getFT(c1, penMagnet2) 
    _,_,B1 = magpy.getB(c1, [0,0,sensorZPos])
    
    F2, T2 = getFT(c2, penMagnet3) + getFT(c2, penMagnet4) 
    _,_,B2 = magpy.getB(c2, [0,0,sensorZPos2])
    
    print('forces:', 'baseline', F1[2], '2025/05/06', F2[2])
    print('torques:', 'baseline', T1[1], '2025/05/06', T2[1])
    print('hall sensor:', 'baseline', B1, '2025/05/06', B2)

    hoverHeight3 = 0.003+0.0024+0.005+0.0025*2+0.003 # hoverHeight - 0.001
    sensorZPos3 = 0.003+0.0024-0.0064+0.005+0.0025
    # ring->post + post->EMFastening-> ring->magnet + 1/2magnetH*2 + EMFastening->Pen
    del magnetRing1, magnetRing2
    penMagnet1 = magpy.magnet.Cylinder(
        magnetization=(0,0,magnetization), dimension=(MAGNET_D, MAGNET_H), position = (0, 0.00, hoverHeight3),
        orientation = R.from_rotvec((0, 15, 0), degrees = True)
        )
    penMagnet2 = magpy.magnet.Cylinder(
        magnetization=(0,0,magnetization), dimension=(MAGNET_D, MAGNET_H), position = (0, 0.00, hoverHeight3 + MAGNET_H),
        )
    penMagnet2.rotate_from_angax(angle = 15, axis = 'y', anchor = (0, 0, 0.014), degrees = True)
    penMagnet1.meshing = 15
    penMagnet2.meshing = 15
    
    magnetRing1 = magnetRing(0.06, 0, 0, 8, 1.88e6)
    magnetRing2 = magnetRing(0.06, 0, -0.025, 14, 1.88e6)
    c = magnetRing1.mCol + magnetRing2.mCol
    
    F, T = getFT(c, penMagnet1) + getFT(c, penMagnet2) 
    _,_,B = magpy.getB(c, [0,0,sensorZPos2])

    print('forces:', '2025/05/07', F[2])
    print('torques:', '2025/05/07', T[1])
    print('hall sensor:', '2025/05/07', B)
    del magnetRing1, magnetRing2
    hoverHeight3 = 0.003+0.0024+0.005+0.0025*2+0.003 # hoverHeight - 0.001
    sensorZPos3 = 0.003+0.0024-0.0064+0.005+0.0025
    # ring->post + post->EMFastening-> ring->magnet + 1/2magnetH*2 + EMFastening->Pen
    penMagnet1 = magpy.magnet.Cylinder(
        magnetization=(0,0,magnetization), dimension=(MAGNET_D, MAGNET_H), position = (0, 0.00, hoverHeight3),
        orientation = R.from_rotvec((0, 15, 0), degrees = True)
        )
    penMagnet2 = magpy.magnet.Cylinder(
        magnetization=(0,0,magnetization), dimension=(MAGNET_D, MAGNET_H), position = (0, 0.00, hoverHeight3 + MAGNET_H),
        )
    penMagnet2.rotate_from_angax(angle = 15, axis = 'y', anchor = (0, 0, 0.014), degrees = True)
    penMagnet1.meshing = 15
    penMagnet2.meshing = 15
    
    magnetRing1 = magnetRing(0.06, 0, 0, 9, 1.88e6)
    magnetRing2 = magnetRing(0.06, -5, -0.02, 15, 1.88e6)
    c = magnetRing1.mCol + magnetRing2.mCol
    
    F, T = getFT(c, penMagnet1) + getFT(c, penMagnet2) 
    _,_,B = magpy.getB(c, [0,0,sensorZPos3])

    print('forces:', 'proposed', F)
    print('torques:', 'proposed', T[1])
    print('hall sensor:', 'proposed', B)
    
    # c.show()

def experiment6(plot = True):
    print('Get magmetic field strength at measured positions')
    newSilver = magpy.magnet.Cylinder(
        magnetization=(0, 0, 1.88e6), dimension=(MAGNET_D, MAGNET_H), position = (0, 0, -0.0025)
        )
    oldSilver = magpy.magnet.Cylinder(
        magnetization=(0, 0, 1.6e6), dimension=(MAGNET_D, MAGNET_H), position = (0, 0, -0.0025)
        )
    for zPos in [6e-3, 7e-3, 8e-3, 11e-3]:
        zPos += 0.9e-3 # add half the sensor. Assume symmetry for now. TODO: WILL CALCULATE OFFSET IN SECOND PASS
        #print at each zPos
        _, _, B1 = magpy.getB(newSilver, [0, 0, zPos])
        _, _, B2 = magpy.getB(oldSilver, [0, 0, zPos])
        print('newSilver, ', B1, ', oldSilver, ',B2)
    
    # to calculate sensor offset inside casing
    sensorOffset = -0.3e-3 #-0.1e-3# 0 # negative number = sensor is closer to small (sensing) face
    zPos1 = 15e-3 + 0.9e-3 + sensorOffset
    zPos2 = 15e-3 + 0.9e-3 - sensorOffset
    newSilver2 = newSilver.copy(deep = True)
    newSilver2.position = (0, 0, -0.0075)
    c = magpy.Collection(newSilver, newSilver2)
    if plot == True:
        c.show()
    _, _, B1 = magpy.getB(c, [0, 0, zPos1])
    _, _, B2 = magpy.getB(c, [0, 0, zPos2])
    print(B1, B2)
    print('likely reading variation if this does not match perfectly, datasheet shows 0.3mm offset towards small face. Note also bias away from prongs')

    #SECOND PASS, assume 0.3e-3 sensor offset
    print('second pass with 0.3e-3 sensor offset')
    for zPos in [6e-3, 7e-3, 8e-3, 11e-3]:
        zPos += 0.6e-3 # account for sensor position (sensor location + 0.1mm for fitment in 3DP part)
        #print at each zPos
        _, _, B1 = magpy.getB(newSilver, [0, 0, zPos])
        _, _, B2 = magpy.getB(oldSilver, [0, 0, zPos])
        print('newSilver, ', B1, ', oldSilver, ',B2)
    
def magneticFieldToSensorReading(magField):
    return(511.5 - 3765.2*magField)

def sensorReadingToMagneticField(sensorReading):
    return((-sensorReading + 511.5) / 3765.2)

def experiment7(plot = True):
    print('Est. model for ferrite core in permanent magnet field. Top [of secure EM] as datum')
    
    MAGNET_TO_RING_FACE = 5e-3
    POST_TO_SENSOR = -3e-3 - 0.6e-3 # post to top face of sensor cutout + sensing position relative to sensor cutout
    POST_TO_TOP = 2.4e-3
    HOVER_HEIGHT = 3e-3
    MAG_RING_TO_POST = 2e-3
    MAGNET_RING_GAP = 18.5e-3
    FERRITE_H = 12e-3
    FERRITE_D = 8e-3
    TOP_TO_FERRITE = 12.4e-3 + FERRITE_H/2# second value is coilH/2

    MAGNETIZATION = 1.51e6

    magnetRing1ZPos = - POST_TO_TOP - MAG_RING_TO_POST - MAGNET_TO_RING_FACE - MAGNET_H/2
    magnetRing2ZPos = magnetRing1ZPos - MAGNET_H - MAGNET_RING_GAP
    sensorZPos = - POST_TO_TOP + POST_TO_SENSOR

    magnetRing1 = magnetRing(0.06, 0, magnetRing1ZPos, 9, MAGNETIZATION)
    magnetRing2 = magnetRing(0.06, 0, magnetRing2ZPos, 12, MAGNETIZATION)
    c = magnetRing1.mCol + magnetRing2.mCol

    if plot:
        c.show()
    
    _, _, B = magpy.getB(c, [0, 0, sensorZPos])
    print(B, magneticFieldToSensorReading(B), 'expect ~557.5')
    # MAGNETIZATION = 1.88e6    -->     568.7
    # MAGNETIZATION = 1.7e6     -->     563.2
    # MAGNETIZATION = 1.51e6    -->     557.5
    print('likely relationship between B and hall sensor reading is off, but given relationship looks linear, probably OK for modelling? IRL is off by 20%; unsure if accounted for in magnet variation + polarity variance')

    # for ferriteMagnetization in [1e1, 1e2, 1e3, 1e4, 1e5, 1e6]: # will be between 1e5 and 1e6. Closer to 1e5
    # for ferriteMagnetization in [1e5, 2e5, 3e5, 4e5, 5e5]: # between 1e5 and 2e5
    # for ferriteMagnetization in [1e5, 1.2e5, 1.4e5, 1.6e5, 1.8e5]: # between 1.4e5 and 1.6e5
    # for ferriteMagnetization in [1.4e5, 1.5e5, 1.6e5]: # slightly more than 1.5e5
    for ferriteMagnetization in [1.5e5, 1.51e5, 1.52e5, 1.53e5]: # slightly more than 1.5e5
        cf = c.copy(deep = True)
        cf = cf + magpy.magnet.Cylinder(
            dimension = (FERRITE_D, FERRITE_H),
            position = (0, 0, - TOP_TO_FERRITE),
            magnetization = (0, 0, -ferriteMagnetization)
        )
        _, _, B = magpy.getB(cf, [0, 0, sensorZPos])
        print(ferriteMagnetization, magneticFieldToSensorReading(B), 'expect 603.7')
        del cf
    print('ferrite magnetization is 1.51e5')

def experiment8(plot = True):
    # note: take top of secure EM as datum
    MAGNET_TO_RING_FACE = 5e-3
    POST_TO_SENSOR = -3e-3 - 0.6e-3 # post to top face of sensor cutout + sensing position relative to sensor cutout
    POST_TO_TOP = 2.4e-3
    HOVER_HEIGHT = 3e-3
    MAG_RING_TO_POST = 2e-3
    MAGNET_RING_GAP = 18.5e-3
    FERRITE_H = 12e-3
    FERRITE_D = 8e-3
    TOP_TO_FERRITE = 12.4e-3 + FERRITE_H/2# second value is coilH/2

    MAGNETIZATION = 1.51e6
    FERRITE_MAGNETIZATION_EM_OFF = 1.51e5 # magnetization of ferrite core from permanent magnets

    magnetRing1ZPos = - POST_TO_TOP - MAG_RING_TO_POST - MAGNET_TO_RING_FACE - MAGNET_H/2
    magnetRing2ZPos = magnetRing1ZPos - MAGNET_H - MAGNET_RING_GAP
    sensorZPos = - POST_TO_TOP + POST_TO_SENSOR

    magnetRing1 = magnetRing(0.06, 0, magnetRing1ZPos, 9, MAGNETIZATION)
    magnetRing2 = magnetRing(0.06, 0, magnetRing2ZPos, 12, MAGNETIZATION)
    ferriteEMoff = magpy.magnet.Cylinder(
        dimension = (FERRITE_D, FERRITE_H),
        position = (0, 0, - TOP_TO_FERRITE),
        magnetization = (0, 0, -FERRITE_MAGNETIZATION_EM_OFF)
    )
    
    penMagnet1 = magpy.magnet.Cylinder(
        magnetization=(0,0,MAGNETIZATION/1.175), dimension=(MAGNET_D, MAGNET_H), position = (0, 0.00, HOVER_HEIGHT + MAGNET_H/2)
        )
    penMagnet1.meshing = 15
    penMagnet2 = penMagnet1.copy(deep = True)
    penMagnet2.position = (0, 0.00, HOVER_HEIGHT + 3*MAGNET_H/2)
    
    c = magnetRing1.mCol + magnetRing2.mCol
    print('passive field at ferrite without ferrite')
    F, T = getFT(c, penMagnet1) + getFT(c, penMagnet2)
    B = magpy.getB(c, (0,0,sensorZPos))
    print(f'{F}')   # [-6.6375e-02 -9.1537e-14  6.8583e-01]
    print(B, magneticFieldToSensorReading(B[2]))        # [ 1.0192e-17  1.2143e-17 -1.2206e-02] 557.4579490367918

    print('passive field + pen at ferrite without ferrite')
    c2 = c + penMagnet1 + penMagnet2
    B = magpy.getB(c2, (0,0,sensorZPos))
    print(B, magneticFieldToSensorReading(B[2]))        # [-4.4324e-03  1.2143e-17  6.2902e-02] 274.66025870373954
    # it is clear ferrite plays a big role in value of set point since it pulls the value from 274.6 to ~120

    print('passive field + pen at ferrite with estimate ferrite contribution')
    ferriteEMoffWithPen = ferriteEMoff.copy(deep = True)
    ferriteEMoffWithPen.magnetization = (0, 0, FERRITE_MAGNETIZATION_EM_OFF * 3.35)
    c3 = c2 + ferriteEMoffWithPen
    B = magpy.getB(c3, (0,0,sensorZPos))
    print(B, magneticFieldToSensorReading(B[2]))
    # when magnetizatoin = FERRITE_MAGNETIZATION_EM_OFF * 6.29 / 1.22:  [-4.4324e-03  1.2143e-17  1.2609e-01] 36.74382670510283
    #   TOO MUCH: makes sense since non-linear (drops off) as strength increases (approaches asymptote). 6.29/1.22 = 5.16
    # when magnetizatoin = FERRITE_MAGNETIZATION_EM_OFF * 3.35:         [-4.4324e-03  1.2143e-17  1.0396e-01] 120.07131473260625
    del c2, c3

    # rotate pen magnets for torque stabilization calculations
    penMagnet1.rotate_from_angax(angle = 5, axis = 'y', anchor = (0, 0, HOVER_HEIGHT + MAGNET_H/2), degrees = True)
    penMagnet2.rotate_from_angax(angle = 5, axis = 'y', anchor = (0, 0, HOVER_HEIGHT + MAGNET_H/2), degrees = True)

    if plot:
        fig, axs = plt.subplots(1,4)

    # without pen
    c2 = magpy.Collection(magnetRing1.mCol, magnetRing2.mCol, ferriteEMoff, override_parent = True)
    if plot:
        plotSysB(c2, axs[0], fig)
        hovering = mpl.patches.Rectangle((-MAGNET_D/2, HOVER_HEIGHT), MAGNET_D, 2*MAGNET_H, linewidth=1, edgecolor='r', facecolor='green', alpha=0.3)
        axs[0].add_patch(hovering)
        axs[0].set_title('permanent magnets +\n ferriteEMoff')

        c2_ = magpy.Collection(magnetRing1.mCol, magnetRing2.mCol, ferriteEMoffWithPen, override_parent = True)
        plotSysB(c2_, axs[1], fig)
        hovering = mpl.patches.Rectangle((-MAGNET_D/2, HOVER_HEIGHT), MAGNET_D, 2*MAGNET_H, linewidth=1, edgecolor='r', facecolor='green', alpha=0.3)
        axs[1].add_patch(hovering)
        axs[1].set_title('permanent magnets +\n ferriteEMoffWithPen')

    # with pen
    c3 = magpy.Collection(magnetRing1.mCol, magnetRing2.mCol, ferriteEMoffWithPen, penMagnet1, penMagnet2, override_parent = True)
    F3, T3 = getFT(c3, penMagnet1) + getFT(c3, penMagnet2)
    print(f'with  pen: F{F3}, T{T3}')
    if plot:
        plotSysB(c3, axs[2], fig)
        axs[2].set_title('permanent magnets +\n ferriteEMoffWithPen + pen')
    
    # with EM ON:
    print('ignore impacts of EM on the ferrite for now. TODO: account for this with more linear interpolation? Expect drop of 6 in hall sensor reading')
    # add coil
    coil = magpy.Collection()

    coilH = 24e-3
    coilOD = 19.6e-3
    coilID = 8e-3
    wireD = 0.3e-3
    coilCurrent = 0.123 # (totalPower - arduinoPower)/voltage = (2.08W-0.6W)/12V = 0.12333...
    # this is based on average, so we are calculating steady state (not peak) 
    # this results in net attractive force of 2.1e-1 (compared to OFF state of 2.4e-1)

    #
    
    coilPosTop = 0.4e-3
    for z in np.arange(coilPosTop - wireD/2 + 1e-6, coilPosTop - coilH + wireD/2 - 1e-6, -wireD): # add -1e-6 from end given arange excludes max values...
        for r in np.arange((coilID + wireD)/2, (coilOD - wireD)/2 + 1e-6, wireD):
            winding = magpy.current.Circle(
                current=coilCurrent,
                diameter=2*r,
                position=(0,0,z),
            )
            coil.add(winding)
    
    c4 = magpy.Collection(magnetRing1.mCol, magnetRing2.mCol, ferriteEMoffWithPen, penMagnet1, penMagnet2, coil, override_parent = True)
    F4, T4 = getFT(c4, penMagnet1) + getFT(c4, penMagnet2)
    print(f'with pen & coil: F{F4}, T{T4}')
    if plot:
        plotSysB(c4, axs[3], fig)
        axs[3].set_title('permanent magnets + \nferriteEMoffWithPen +\n pen + coil')
        plt.show()

    

def main():
    # validateSuperposition
    # experiment1()

    # test for strength of permanent magnets
    # experiment4()

    # validate stability of floating pen based on separation of floating magnets
    # experiment2()

    # what does the 2nd ring do?
    # experiment3()
    
    # try and calc our existing system & initial test of new magnets
    # experiment5()

    # compare 2 rings vs 1 stronger ring assuming approx same vertical force on magnet

    # correlate hall sensor to B
    # experiment6(False)

    # determine ferrite core stuff
    # experiment7(False)

    # try and calc our existing system (also try to see what happens when coil turns on?)
    experiment8()


if __name__ == "__main__":
    main()