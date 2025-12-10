import magpylib as magpy
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import pyvista as pv
import math
from scipy.spatial.transform import Rotation as R
import time
from magpylib_force import getFT
import copy
import csv

np.set_printoptions(precision = 4)
MAGNET_D = 0.01
MAGNET_H = 0.005

class magnetRing:
    def __init__(self, diameter, angle, zPos, numMagnets, magnetization = 1.6e6, theta_i = 0): # for default use the old silver magnets
        # diameter = diameter of 
        # angle = angle of magnets in ring. Positive means outwards (assuming vector going 'up'). In degrees
        # zPos = z displacement of the ring
        # numMagnets = number of magnets in the ring
        self.diameter = diameter
        self.angle = angle
        self.zPos = zPos
        self.numMagnets = numMagnets

        self.mCol = magpy.Collection()
        for lv1 in range(numMagnets):
            theta = lv1*2*math.pi/numMagnets + theta_i
            
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
    _, _, B_f = magpy.getB(c, [0, 0, -TOP_TO_FERRITE])
    print(B, magneticFieldToSensorReading(B), 'expect ~557.5')
    print('B at ferrite', B_f)
    # MAGNETIZATION = 1.88e6    -->     568.7
    # MAGNETIZATION = 1.7e6     -->     563.2
    # MAGNETIZATION = 1.51e6    -->     557.5
    print('likely relationship between B and hall sensor reading is off, but given relationship looks linear, probably OK for modelling? IRL is off by 20%; unsure if accounted for in magnet variation + polarity variance')

    # for ferriteMagnetization in [1e1, 1e2, 1e3, 1e4, 1e5, 1e6]: # will be between 1e5 and 1e6. Closer to 1e5
    # for ferriteMagnetization in [1e5, 2e5, 3e5, 4e5, 5e5]: # between 1e5 and 2e5
    # for ferriteMagnetization in [1e5, 1.2e5, 1.4e5, 1.6e5, 1.8e5]: # between 1.4e5 and 1.6e5
    # for ferriteMagnetization in [1.4e5, 1.5e5, 1.6e5]: # slightly more than 1.5e5
    for ferriteMagnetization in [0, 1.5e5, 1.51e5, 1.52e5, 1.53e5]: # slightly more than 1.5e5
        cf = c.copy(deep = True)
        cf = cf + magpy.magnet.Cylinder(
            dimension = (FERRITE_D, FERRITE_H),
            position = (0, 0, - TOP_TO_FERRITE),
            magnetization = (0, 0, -ferriteMagnetization)
        )
        _, _, B = magpy.getB(cf, [0, 0, sensorZPos])
        print(B, ferriteMagnetization, magneticFieldToSensorReading(B), 'expect 603.7')
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
        position = (0, 0, -TOP_TO_FERRITE),
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
    B_f = magpy.getB(c, (0,0,-TOP_TO_FERRITE))
    print(f'{F}')   # [-6.6375e-02 -9.1537e-14  6.8583e-01]
    print(B, magneticFieldToSensorReading(B[2]))        # [ 1.0192e-17  1.2143e-17 -1.2206e-02] 557.4579490367918
    print('at ferrite', B_f)                            # [-7.1557e-18  2.7105e-18 -2.0677e-02]

    print('passive field + pen at ferrite without ferrite')
    c2 = c + penMagnet1 + penMagnet2
    B = magpy.getB(c2, (0,0,sensorZPos))
    B_f = magpy.getB(c2, (0,0,-TOP_TO_FERRITE))
    print(B, magneticFieldToSensorReading(B[2]))        # [-4.4324e-03  1.2143e-17  6.2902e-02] 274.66025870373954
    print('at ferrite', B_f)                            # [-7.1557e-18  2.7105e-18 -9.5472e-03]
    # it is clear ferrite plays a big role in value of set point since it pulls the value from 274.6 to ~120

    print('passive field + pen at ferrite with estimate ferrite contribution')
    ferriteEMoffWithPen = ferriteEMoff.copy(deep = True)
    ferriteEMoffWithPen.magnetization = (0, 0, FERRITE_MAGNETIZATION_EM_OFF * 3.35)
    c3 = c2 + ferriteEMoffWithPen
    B = magpy.getB(c3, (0,0,sensorZPos))
    print(B, magneticFieldToSensorReading(B[2]))
    # when magnetizatoin = FERRITE_MAGNETIZATION_EM_OFF * 6.29 / 1.22:  [-4.4324e-03  1.2143e-17  1.2609e-01] 36.74382670510283
    #   TOO MUCH: makes sense since non-linear (drops off) as strength increases (approaches asymptote). 6.29/1.22 = 5.16
    #       ^ is based off of the magneticField results comparing passive field at ferrite without ferrite with & without a pen (lines 533 and 538)
    #       note that field direction change is implicitly accounted for based on sign of magnetization in the ferrite magnet definition
    # when magnetizatoin = FERRITE_MAGNETIZATION_EM_OFF * 3.35:         [-4.4324e-03  1.2143e-17  1.0396e-01] 120.07131473260625

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

    B = magpy.getB(c2, (0,0,sensorZPos))
    print('!!!BNOMAGNET', B)
    # with pen
    c3 = magpy.Collection(magnetRing1.mCol, magnetRing2.mCol, ferriteEMoffWithPen, penMagnet1, penMagnet2, override_parent = True)
    F3, T3 = getFT(c3, penMagnet1) + getFT(c3, penMagnet2)
    print(f'with  pen: F{F3}, T{T3}')
    if plot:
        plotSysB(c3, axs[2], fig)
        axs[2].set_title('permanent magnets +\n ferriteEMoffWithPen + pen')
    
    B = magpy.getB(c3, (0,0,sensorZPos))
    print('!!!BNOMAGNET', B)
    # with EM ON:
    print('ignore impacts of EM on the ferrite for now. TODO: account for this with more linear interpolation? Expect drop of 6 in hall sensor reading')
    # add coil
    coil = magpy.Collection()

    coilH = 24e-3
    coilOD = 19.6e-3
    coilID = 8e-3
    wireD = 0.35e-3 # assume wire diameter from https://www.aliexpress.com/item/1005007539263147.html?spm=a2g0o.detail.pcDetailBottomMoreOtherSeller.4.ad14UWzRUWzR8E&gps-id=pcDetailBottomMoreOtherSeller&scm=1007.40050.354490.0&scm_id=1007.40050.354490.0&scm-url=1007.40050.354490.0&pvid=9bdcbb99-2488-4a53-a188-dcab84615b92&_t=gps-id:pcDetailBottomMoreOtherSeller,scm-url:1007.40050.354490.0,pvid:9bdcbb99-2488-4a53-a188-dcab84615b92,tpp_buckets:668%232846%238116%232002&pdp_ext_f=%7B%22order%22%3A%222%22%2C%22eval%22%3A%221%22%2C%22sceneId%22%3A%2230050%22%7D&pdp_npi=4%40dis%21CAD%216.38%214.60%21%21%214.54%213.27%21%402101c5bf17483994196241774eb97f%2112000041207734322%21rec%21CA%212712658390%21X&utparam-url=scene%3ApcDetailBottomMoreOtherSeller%7Cquery_from%3A
    coilCurrent = 0.123 # (totalPower - arduinoPower)/voltage = (2.08W-0.6W)/12V = 0.12333...
    # this is based on average, so we are calculating steady state (not peak) 
    # this results in net attractive force of 2.1e-1 (compared to OFF state of 2.4e-1)
    
    coilPosTop = -0.4e-3
    for z in np.arange(coilPosTop - wireD/2 + 1e-6, coilPosTop - coilH + wireD/2 - 1e-6, -wireD): # add -1e-6 from end given arange excludes max values...
        for r in np.arange((coilID + wireD)/2, (coilOD - wireD)/2 + 1e-6, wireD):
            winding = magpy.current.Circle(
                current=coilCurrent,
                diameter=2*r,
                position=(0,0,z),
            )
            coil.add(winding)
            # ~1k coil windings
    
    c4 = magpy.Collection(magnetRing1.mCol, magnetRing2.mCol, ferriteEMoffWithPen, penMagnet1, penMagnet2, coil, override_parent = True)
    F4, T4 = getFT(c4, penMagnet1) + getFT(c4, penMagnet2)
    
    print(f'with pen & coil: F{F4}, T{T4}')
    if plot:
        plotSysB(c4, axs[3], fig)
        axs[3].set_title('permanent magnets + \nferriteEMoffWithPen +\n pen + coil')
        plt.show()

        # search region around the middle & determine force on pen after moving it around

        ## rotate pen magnets back to vertical
        penMagnet1.rotate_from_angax(angle = -5, axis = 'y', anchor = (0, 0, HOVER_HEIGHT + MAGNET_H/2), degrees = True)
        penMagnet2.rotate_from_angax(angle = -5, axis = 'y', anchor = (0, 0, HOVER_HEIGHT + MAGNET_H/2), degrees = True)

        # grid...
        xs = np.linspace(-5e-3, 5e-3, 21)
        zs = np.linspace(1e-3, 6e-3, 11)
        # zs = np.linspace(-1e-3, 12e-3, 5)
        Fs = np.zeros(shape = (11, 21, 3))
        for lv1, x in enumerate(xs):
            for lv2, z in enumerate(zs): # hoverheight is 3e-3. z replaces hoverHeight
                penMagnet1.position = (x, 0.00, z + MAGNET_H/2)
                penMagnet2.postion = (x, 0.00, z + 3*MAGNET_H/2)
                F, _ = getFT(c4, penMagnet1) + getFT(c4, penMagnet2)
                Fs[lv2, lv1] = F - np.array([0, 0, 9e-3*9.81])
        
        fig, axs = plt.subplots(1,3)

        axs[0].imshow(Fs[:,:,2], extent=[xs.min(), xs.max(), zs.min(), zs.max()], origin='lower', cmap='viridis')
        axs[0].set_title('permanent magnets + \nferriteEMoffWithPen +\n pen + coil\n Z force')

        axs[1].imshow(Fs[:,:,0], extent=[xs.min(), xs.max(), zs.min(), zs.max()], origin='lower', cmap='viridis')
        axs[1].set_title('permanent magnets + \nferriteEMoffWithPen +\n pen + coil\n X force')

        axs[2].streamplot(xs, zs, Fs[:,:,0], Fs[:,:,2], color = np.log(Fs[:,:,0]**2+Fs[:,:,2]**2), density=1.)
        axs[2].set_aspect('equal')
        axs[2].set_title('permanent magnets + \nferriteEMoffWithPen +\n pen + coil\n Force Streamlines')
        print('note for the force streamplot, I do not account for varying ferrite magnetization')
        plt.show()

def experiment9(plot=True):
    # impact of different shaped coil(s)
    MAGNET_TO_RING_FACE = 5e-3
    POST_TO_SENSOR = -3e-3 - 0.6e-3 # post to top face of sensor cutout + sensing position relative to sensor cutout
    POST_TO_TOP = 2.4e-3
    HOVER_HEIGHT = 3e-3
    MAG_RING_TO_POST = 2e-3 # adjust based on fat upper coil run 1?
    MAGNET_RING_GAP = 18.5e-3
    FERRITE_H = 12e-3
    FERRITE_D = 8e-3
    TOP_TO_FERRITE = 12.4e-3 + FERRITE_H/2# second value is coilH/2

    MAGNETIZATION = 1.51e6
    FERRITE_MAGNETIZATION_EM_OFF = 1.51e5 # magnetization of ferrite core from permanent magnets + pens?

    
    coilOffset = -7e-4 # for testing diff EM positions. Need because need at minimum stability afforded by torque interaction with permanent magnets at the tested point (where pen hovers at 3mm above old top face)

    magnetRing1ZPos = - POST_TO_TOP - MAG_RING_TO_POST - MAGNET_TO_RING_FACE - MAGNET_H/2
    magnetRing2ZPos = magnetRing1ZPos - MAGNET_H - MAGNET_RING_GAP
    sensorZPos = - POST_TO_TOP + POST_TO_SENSOR

    magnetRing1 = magnetRing(0.06, 0, magnetRing1ZPos, 9, MAGNETIZATION)
    magnetRing2 = magnetRing(0.06, 0, magnetRing2ZPos, 12, MAGNETIZATION)
    ferriteEMoffWithPen = magpy.magnet.Cylinder(
        dimension = (FERRITE_D, FERRITE_H),
        position = (0, 0, -TOP_TO_FERRITE+coilOffset),
        magnetization = (0, 0, FERRITE_MAGNETIZATION_EM_OFF * 3.35)
    )

    penMagnet1 = magpy.magnet.Cylinder(
        magnetization=(0,0,MAGNETIZATION/1.175), dimension=(MAGNET_D, MAGNET_H), position = (0, 0.00, HOVER_HEIGHT + MAGNET_H/2)
        )
    penMagnet1.meshing = 15
    penMagnet2 = penMagnet1.copy(deep = True)
    penMagnet2.position = (0, 0.00, HOVER_HEIGHT + 3*MAGNET_H/2)

    penMagnet1.rotate_from_angax(angle = -5, axis = 'y', anchor = (0, 0, HOVER_HEIGHT + MAGNET_H/2), degrees = True)
    penMagnet2.rotate_from_angax(angle = -5, axis = 'y', anchor = (0, 0, HOVER_HEIGHT + MAGNET_H/2), degrees = True)


    # add coil
    coil = magpy.Collection()

    coilH = 24e-3
    coilOD = 25e-3#19.6e-3
    coilID = 8e-3
    wireD = 0.35e-3 # assume wire diameter from https://www.aliexpress.com/item/1005007539263147.html?spm=a2g0o.detail.pcDetailBottomMoreOtherSeller.4.ad14UWzRUWzR8E&gps-id=pcDetailBottomMoreOtherSeller&scm=1007.40050.354490.0&scm_id=1007.40050.354490.0&scm-url=1007.40050.354490.0&pvid=9bdcbb99-2488-4a53-a188-dcab84615b92&_t=gps-id:pcDetailBottomMoreOtherSeller,scm-url:1007.40050.354490.0,pvid:9bdcbb99-2488-4a53-a188-dcab84615b92,tpp_buckets:668%232846%238116%232002&pdp_ext_f=%7B%22order%22%3A%222%22%2C%22eval%22%3A%221%22%2C%22sceneId%22%3A%2230050%22%7D&pdp_npi=4%40dis%21CAD%216.38%214.60%21%21%214.54%213.27%21%402101c5bf17483994196241774eb97f%2112000041207734322%21rec%21CA%212712658390%21X&utparam-url=scene%3ApcDetailBottomMoreOtherSeller%7Cquery_from%3A
    coilCurrent = 0.123 # (totalPower - arduinoPower)/voltage = (2.08W-0.6W)/12V = 0.12333...
    # this is based on average, so we are calculating steady state (not peak) 
    # this results in net attractive force of 2.1e-1 (compared to OFF state of 2.4e-1)
    
    numCoils = 0
    coilPosTop = 0.4e-3
    for z in np.arange(coilPosTop - wireD/2 + 1e-6, coilPosTop - coilH/2 + wireD/2 - 1e-6, -wireD): # add -1e-6 from end given arange excludes max values...
        for r in np.arange((coilID + wireD)/2, (coilOD - wireD)/2 + 1e-6, wireD):
            winding = magpy.current.Circle(
                current=coilCurrent,
                diameter=2*r,
                position=(0,0,z+coilOffset),
            )
            coil.add(winding)
            numCoils+=1
            # ~1k coil windings
    coilOD = 19.6e-3
    for z in np.arange(coilPosTop - coilH/2 - wireD/2 + 1e-6, coilPosTop - coilH + wireD/2 - 1e-6, -wireD): # add -1e-6 from end given arange excludes max values...
        for r in np.arange((coilID + wireD)/2, (coilOD - wireD)/2 + 1e-6, wireD):
            winding = magpy.current.Circle(
                current=coilCurrent,
                diameter=2*r,
                position=(0,0,z+coilOffset),
            )
            coil.add(winding)
            numCoils+=1
            # ~1k coil windings
    print('number of coils', numCoils)
    # return
    # base coil has 1088 windings
    # when coilOD = 22e-3 through entire coil, have 1360 windings (+272)
    # if just coilOD = 22e-3 on upper coil, have 1224 windings (+136)
    # if just coilOD = 25e-3 on upper coil, have 1360 windings (+272)

    c0 = magpy.Collection(magnetRing1.mCol, magnetRing2.mCol, ferriteEMoffWithPen, penMagnet1, penMagnet2, coil, override_parent = True)
    F0, T0 = getFT(c0, penMagnet1) + getFT(c0, penMagnet2)
    print(F0, T0)
    
    B = magpy.getB(c0, (0,0,sensorZPos))
    if plot:
        #
        penMagnet1.rotate_from_angax(angle = 5, axis = 'y', anchor = (0, 0, HOVER_HEIGHT + MAGNET_H/2), degrees = True)
        penMagnet2.rotate_from_angax(angle = 5, axis = 'y', anchor = (0, 0, HOVER_HEIGHT + MAGNET_H/2), degrees = True)


        # define grid
        xs = np.linspace(-5e-3, 5e-3, 11)
        zs = np.linspace(1e-3, 6e-3, 6)
        Fs = np.zeros(shape = (6, 11, 3))
        for lv1, x in enumerate(xs):
            for lv2, z in enumerate(zs): # hoverheight is 3e-3. z replaces hoverHeight
                penMagnet1.position = (x, 0.00, z + MAGNET_H/2)
                penMagnet2.postion = (x, 0.00, z + 3*MAGNET_H/2)
                F, _ = getFT(c0, penMagnet1) + getFT(c0, penMagnet2)
                Fs[lv2, lv1] = F - np.array([0, 0, 9e-3*9.81])
        
        fig, axs = plt.subplots(1,3)

        axs[0].imshow(Fs[:,:,2], extent=[xs.min(), xs.max(), zs.min(), zs.max()], origin='lower', cmap='viridis')
        axs[0].set_title('permanent magnets + \nferriteEMoffWithPen +\n pen + coil\n Z force')

        axs[1].imshow(Fs[:,:,0], extent=[xs.min(), xs.max(), zs.min(), zs.max()], origin='lower', cmap='viridis')
        axs[1].set_title('permanent magnets + \nferriteEMoffWithPen +\n pen + coil\n X force')

        axs[2].streamplot(xs, zs, Fs[:,:,0], Fs[:,:,2], color = np.log(Fs[:,:,0]**2+Fs[:,:,2]**2), density=1.)
        axs[2].set_aspect('equal')
        axs[2].set_title('permanent magnets + \nferriteEMoffWithPen +\n pen + coil\n Force Streamlines')
        print('note for the force streamplot, I do not account for varying ferrite magnetization')
        plt.show()

def experiment10(plot = True):
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
    # magnetRing1 = magnetRing(0.06, 0, magnetRing1ZPos, 10, MAGNETIZATION)
    magnetRing2 = magnetRing(0.06, 0, magnetRing2ZPos, 12, MAGNETIZATION)
    ferriteEMoff = magpy.magnet.Cylinder(
        dimension = (FERRITE_D, FERRITE_H),
        position = (0, 0, -TOP_TO_FERRITE),
        magnetization = (0, 0, -FERRITE_MAGNETIZATION_EM_OFF)
    )
    ferriteSysOn = ferriteEMoff.copy(deep = True)
    ferriteSysOn.magnetization = (0, 0, FERRITE_MAGNETIZATION_EM_OFF * 3.35)

    # add coil
    coil = magpy.Collection()

    coilH = 24e-3
    coilOD = 19.6e-3
    coilID = 8e-3
    wireD = 0.35e-3 # assume wire diameter from https://www.aliexpress.com/item/1005007539263147.html?spm=a2g0o.detail.pcDetailBottomMoreOtherSeller.4.ad14UWzRUWzR8E&gps-id=pcDetailBottomMoreOtherSeller&scm=1007.40050.354490.0&scm_id=1007.40050.354490.0&scm-url=1007.40050.354490.0&pvid=9bdcbb99-2488-4a53-a188-dcab84615b92&_t=gps-id:pcDetailBottomMoreOtherSeller,scm-url:1007.40050.354490.0,pvid:9bdcbb99-2488-4a53-a188-dcab84615b92,tpp_buckets:668%232846%238116%232002&pdp_ext_f=%7B%22order%22%3A%222%22%2C%22eval%22%3A%221%22%2C%22sceneId%22%3A%2230050%22%7D&pdp_npi=4%40dis%21CAD%216.38%214.60%21%21%214.54%213.27%21%402101c5bf17483994196241774eb97f%2112000041207734322%21rec%21CA%212712658390%21X&utparam-url=scene%3ApcDetailBottomMoreOtherSeller%7Cquery_from%3A
    coilCurrent = 0.123 # [A] average. (totalPower - arduinoPower)/voltage = (2.08W-0.6W)/12V = 0.12333...
    coilPosTop = -0.4e-3
    for z in np.arange(coilPosTop - wireD/2 + 1e-6, coilPosTop - coilH + wireD/2 - 1e-6, -wireD): # add -1e-6 from end given arange excludes max values...
        for r in np.arange((coilID + wireD)/2, (coilOD - wireD)/2 + 1e-6, wireD):
            winding = magpy.current.Circle(
                current=coilCurrent,
                diameter=2*r,
                position=(0,0,z),
            )
            coil.add(winding) # ~1k coil windings
    
    penMagnet1 = magpy.magnet.Cylinder(
        magnetization=(0,0,MAGNETIZATION/1.175), dimension=(MAGNET_D, MAGNET_H), position = (0, 0.00, HOVER_HEIGHT + MAGNET_H/2)
        )
    penMagnet1.meshing = 15
    penMagnet2 = penMagnet1.copy(deep = True)
    penMagnet2.position = (0, 0.00, HOVER_HEIGHT + 3*MAGNET_H/2)
    
    c = magnetRing1.mCol + magnetRing2.mCol + ferriteSysOn

    # rotate magnet for scanning restoring moment
    penMagnet1.rotate_from_angax(angle = 5, axis = 'y', anchor = (0, 0, HOVER_HEIGHT + MAGNET_H/2), degrees = True)
    penMagnet2.rotate_from_angax(angle = 5, axis = 'y', anchor = (0, 0, HOVER_HEIGHT + MAGNET_H/2), degrees = True)

    # loop thru find optimal placement for extra magnet
    print('loop thru to find optimal placement for extra magnet')
    F, T = getFT(c, penMagnet1) + getFT(c, penMagnet2)
    print('F', F, 'T', T)
    for zPos in [-26e-3, -27e-3, -28e-3, -29e-3, -30e-3]:
        # baseMagnet = magpy.magnet.Cylinder(
        # magnetization=(0,0,MAGNETIZATION/3), dimension=(MAGNET_D, MAGNET_H), position = (0, 0, zPos)
        # )
        baseMagnet = magpy.magnet.Cylinder(
        magnetization=(0,0,MAGNETIZATION/5), dimension=(MAGNET_D, MAGNET_H), position = (0, 0, zPos)
        )

        F2, T2 = getFT(baseMagnet, penMagnet1) + getFT(baseMagnet, penMagnet2)
        Ft = F + F2
        Tt = T + T2
        print('F', Ft, 'T', Tt)
        # from this see that lower having magnet higher is generallly better. Let magnet be at -27e-3
    
    baseMagnet.position = (0,0,-27e-3)

    if plot:
        fig, axs = plt.subplots(1,4)
        for lv1 in range(4):
            axs[lv1].set_xlim(-0.05, 0.05)  # Set x-range for the first subplot
            axs[lv1].set_ylim(-0.05, 0.05) # Set y-range for the first subplot

    # without pen
    c2 = magpy.Collection(magnetRing1.mCol, magnetRing2.mCol, ferriteEMoff, baseMagnet, override_parent = True)
    if plot:
        plotSysB(c2, axs[0], fig)
        hovering = mpl.patches.Rectangle((-MAGNET_D/2, HOVER_HEIGHT), MAGNET_D, 2*MAGNET_H, linewidth=1, edgecolor='r', facecolor='green', alpha=0.3)
        axs[0].add_patch(hovering)
        axs[0].set_title('permanent magnets +\n ferriteEMoff')

        c2_ = magpy.Collection(magnetRing1.mCol, magnetRing2.mCol, ferriteSysOn, override_parent = True)
        plotSysB(c2_, axs[1], fig)
        hovering = mpl.patches.Rectangle((-MAGNET_D/2, HOVER_HEIGHT), MAGNET_D, 2*MAGNET_H, linewidth=1, edgecolor='r', facecolor='green', alpha=0.3)
        axs[1].add_patch(hovering)
        axs[1].set_title('permanent magnets +\n ferriteSysOn')

    B = magpy.getB(c2, (0,0,sensorZPos))
    print('permanent magnets without pen. Field at sensor: ', B)
    # with pen
    c3 = magpy.Collection(magnetRing1.mCol, magnetRing2.mCol, ferriteSysOn, baseMagnet, penMagnet1, penMagnet2, override_parent = True)
    F3, T3 = getFT(c3, penMagnet1) + getFT(c3, penMagnet2)
    print(f'with  pen: F{F3}, T{T3}')
    if plot:
        plotSysB(c3, axs[2], fig)
        axs[2].set_title('permanent magnets +\n ferriteSysOn + pen (no EM)')
    
    B = magpy.getB(c3, (0,0,sensorZPos))
    print('permanent magnets with pen (assume ferriteSysOn). Field at sensor: ', B)
    
    c4 = magpy.Collection(magnetRing1.mCol, magnetRing2.mCol, ferriteSysOn, baseMagnet, penMagnet1, penMagnet2, coil, override_parent = True)
    F4, T4 = getFT(c4, penMagnet1) + getFT(c4, penMagnet2)
    
    print(f'with pen & coil: F{F4}, T{T4}')
    if plot:
        plotSysB(c4, axs[3], fig)
        axs[3].set_title('permanent magnets + \nferriteSysOn +\n pen + coil')
        plt.show()

        # search region around the middle & determine force on pen after moving it around

        ## rotate pen magnets back to vertical
        penMagnet1.rotate_from_angax(angle = -5, axis = 'y', anchor = (0, 0, HOVER_HEIGHT + MAGNET_H/2), degrees = True)
        penMagnet2.rotate_from_angax(angle = -5, axis = 'y', anchor = (0, 0, HOVER_HEIGHT + MAGNET_H/2), degrees = True)

        # grid...
        xs = np.linspace(-5e-3, 5e-3, 21)
        zs = np.linspace(1e-3, 6e-3, 11)
        # zs = np.linspace(-1e-3, 12e-3, 5)
        Fs = np.zeros(shape = (11, 21, 3))
        for lv1, x in enumerate(xs):
            for lv2, z in enumerate(zs): # hoverheight is 3e-3. z replaces hoverHeight
                penMagnet1.position = (x, 0.00, z + MAGNET_H/2)
                penMagnet2.postion = (x, 0.00, z + 3*MAGNET_H/2)
                F, _ = getFT(c4, penMagnet1) + getFT(c4, penMagnet2)
                Fs[lv2, lv1] = F - np.array([0, 0, 9e-3*9.81])
        
        fig, axs = plt.subplots(1,3)

        axs[0].imshow(Fs[:,:,2], extent=[xs.min(), xs.max(), zs.min(), zs.max()], origin='lower', cmap='viridis')
        axs[0].set_title('permanent magnets + \nferriteSysOn +\n pen + coil\n Z force')

        axs[1].imshow(Fs[:,:,0], extent=[xs.min(), xs.max(), zs.min(), zs.max()], origin='lower', cmap='viridis')
        axs[1].set_title('permanent magnets + \ferriteSysOn +\n pen + coil\n X force')

        axs[2].streamplot(xs, zs, Fs[:,:,0], Fs[:,:,2], color = np.log(Fs[:,:,0]**2+Fs[:,:,2]**2), density=1.)
        axs[2].set_aspect('equal')
        axs[2].set_title('permanent magnets + \nferriteSysOn +\n pen + coil\n Force Streamlines')
        print('note for the force streamplot, I do not account for varying ferrite magnetization')
        plt.show()

def experiment11(plot=True):
    # same as exp 10 but try a few things and update constants experimentally based on heavier pen
    # note: take top of secure EM as datum
    MAGNET_TO_RING_FACE = 5e-3
    POST_TO_SENSOR = -3e-3 - 0.6e-3 # post to top face of sensor cutout + sensing position relative to sensor cutout
    POST_TO_TOP = 2.4e-3
    HOVER_HEIGHT = 5e-3
    MAG_RING_TO_POST = -8e-4
    MAGNET_RING_GAP = 18.4e-3
    FERRITE_H = 12e-3
    FERRITE_D = 8e-3
    TOP_TO_FERRITE = 12.4e-3 + FERRITE_H/2# second value is coilH/2

    MAGNETIZATION = 1.51e6
    FERRITE_MAGNETIZATION_EM_OFF = 1.51e5 # magnetization of ferrite core from permanent magnets

    penMass = 1.28e-2 #kg

    magnetRing1ZPos = - POST_TO_TOP - MAG_RING_TO_POST - MAGNET_TO_RING_FACE - MAGNET_H/2
    magnetRing2ZPos = magnetRing1ZPos - MAGNET_H - MAGNET_RING_GAP
    sensorZPos = - POST_TO_TOP + POST_TO_SENSOR

    # magnetRing1 = magnetRing(0.06, 0, magnetRing1ZPos, 9, MAGNETIZATION)
    magnetRing1 = magnetRing(0.058, 0, magnetRing1ZPos, 9, MAGNETIZATION)
    # magnetRing1 = magnetRing(0.056, 0, magnetRing1ZPos, 9, MAGNETIZATION)
    # magnetRing1 = magnetRing(0.06, 0, magnetRing1ZPos, 10, MAGNETIZATION)
    magnetRing2 = magnetRing(0.06, 0, magnetRing2ZPos, 12, MAGNETIZATION)
    ferriteEMoff = magpy.magnet.Cylinder(
        dimension = (FERRITE_D, FERRITE_H),
        position = (0, 0, -TOP_TO_FERRITE),
        magnetization = (0, 0, -FERRITE_MAGNETIZATION_EM_OFF)
    )
    ferriteSysOn = ferriteEMoff.copy(deep = True)
    ferriteSysOn.magnetization = (0, 0, FERRITE_MAGNETIZATION_EM_OFF * 3.35)

    # add coil
    coil = magpy.Collection()

    coilH = 24e-3
    coilOD = 19.6e-3
    coilID = 8e-3
    wireD = 0.35e-3 # assume wire diameter from https://www.aliexpress.com/item/1005007539263147.html?spm=a2g0o.detail.pcDetailBottomMoreOtherSeller.4.ad14UWzRUWzR8E&gps-id=pcDetailBottomMoreOtherSeller&scm=1007.40050.354490.0&scm_id=1007.40050.354490.0&scm-url=1007.40050.354490.0&pvid=9bdcbb99-2488-4a53-a188-dcab84615b92&_t=gps-id:pcDetailBottomMoreOtherSeller,scm-url:1007.40050.354490.0,pvid:9bdcbb99-2488-4a53-a188-dcab84615b92,tpp_buckets:668%232846%238116%232002&pdp_ext_f=%7B%22order%22%3A%222%22%2C%22eval%22%3A%221%22%2C%22sceneId%22%3A%2230050%22%7D&pdp_npi=4%40dis%21CAD%216.38%214.60%21%21%214.54%213.27%21%402101c5bf17483994196241774eb97f%2112000041207734322%21rec%21CA%212712658390%21X&utparam-url=scene%3ApcDetailBottomMoreOtherSeller%7Cquery_from%3A
    coilCurrent = 0.123 # [A] average. (totalPower - arduinoPower)/voltage = (2.08W-0.6W)/12V = 0.12333...
    coilPosTop = -0.4e-3
    for z in np.arange(coilPosTop - wireD/2 + 1e-6, coilPosTop - coilH + wireD/2 - 1e-6, -wireD): # add -1e-6 from end given arange excludes max values...
        for r in np.arange((coilID + wireD)/2, (coilOD - wireD)/2 + 1e-6, wireD):
            winding = magpy.current.Circle(
                current=coilCurrent,
                diameter=2*r,
                position=(0,0,z),
            )
            coil.add(winding) # ~1k coil windings
    
    penMagnet1 = magpy.magnet.Cylinder(
        magnetization=(0,0,MAGNETIZATION/1.175), dimension=(MAGNET_D, MAGNET_H), position = (0, 0.00, HOVER_HEIGHT + MAGNET_H/2)
        )
        # THIS INACCRATELY CHARACERIZES PEN MAGNET BUT GOOD ENUF SINCE ONLY CARE ABOUT RELATIVE FOR NOW
    penMagnet1.meshing = 15
    penMagnet2 = penMagnet1.copy(deep = True)
    penMagnet2.position = (0, 0.00, HOVER_HEIGHT + 3*MAGNET_H/2)
    
    c = magnetRing1.mCol + magnetRing2.mCol + ferriteSysOn

    # rotate magnet for scanning restoring moment
    penMagnet1.rotate_from_angax(angle = 5, axis = 'y', anchor = (0, 0, HOVER_HEIGHT + MAGNET_H/2), degrees = True)
    penMagnet2.rotate_from_angax(angle = 5, axis = 'y', anchor = (0, 0, HOVER_HEIGHT + MAGNET_H/2), degrees = True)

    # loop thru find optimal placement for extra magnet
    print('loop thru to find optimal placement for extra magnet')
    F, T = getFT(c, penMagnet1) + getFT(c, penMagnet2)
    print('F', F, 'T', T)
    for zPos in [-29e-3]:
        # baseMagnet = magpy.magnet.Cylinder(
        # magnetization=(0,0,MAGNETIZATION/3), dimension=(MAGNET_D, MAGNET_H), position = (0, 0, zPos)
        # )
        # baseMagnet = magpy.magnet.Cylinder(
        # magnetization=(0,0,MAGNETIZATION*0.7), dimension=(MAGNET_D, MAGNET_H), position = (0, 0, zPos)
        # )
        baseMagnet = magpy.magnet.Cylinder(
        magnetization=(0,0,MAGNETIZATION), dimension=(MAGNET_D, MAGNET_H), position = (0, 0, zPos)
        )

        F2, T2 = getFT(baseMagnet, penMagnet1) + getFT(baseMagnet, penMagnet2)
        Ft = F + F2
        Tt = T + T2
        print('F', Ft, 'T', Tt)
        # from this see that lower having magnet higher is generallly better. Let magnet be at -27e-3
    
    baseMagnet.position = (0,0,-27e-3)

    if plot:
        fig, axs = plt.subplots(1,4)
        for lv1 in range(4):
            axs[lv1].set_xlim(-0.05, 0.05)  # Set x-range for the first subplot
            axs[lv1].set_ylim(-0.05, 0.05) # Set y-range for the first subplot

    # without pen
    c2 = magpy.Collection(magnetRing1.mCol, magnetRing2.mCol, ferriteEMoff, baseMagnet, override_parent = True)
    if plot:
        plotSysB(c2, axs[0], fig)
        hovering = mpl.patches.Rectangle((-MAGNET_D/2, HOVER_HEIGHT), MAGNET_D, 2*MAGNET_H, linewidth=1, edgecolor='r', facecolor='green', alpha=0.3)
        axs[0].add_patch(hovering)
        axs[0].set_title('permanent magnets +\n ferriteEMoff')

        c2_ = magpy.Collection(magnetRing1.mCol, magnetRing2.mCol, ferriteSysOn, override_parent = True)
        plotSysB(c2_, axs[1], fig)
        hovering = mpl.patches.Rectangle((-MAGNET_D/2, HOVER_HEIGHT), MAGNET_D, 2*MAGNET_H, linewidth=1, edgecolor='r', facecolor='green', alpha=0.3)
        axs[1].add_patch(hovering)
        axs[1].set_title('permanent magnets +\n ferriteSysOn')

    B = magpy.getB(c2, (0,0,sensorZPos))
    print('permanent magnets without pen. Field at sensor: ', B)
    # with pen
    c3 = magpy.Collection(magnetRing1.mCol, magnetRing2.mCol, ferriteSysOn, baseMagnet, penMagnet1, penMagnet2, override_parent = True)
    F3, T3 = getFT(c3, penMagnet1) + getFT(c3, penMagnet2)
    print(f'with  pen: F{F3}, T{T3}')
    if plot:
        plotSysB(c3, axs[2], fig)
        axs[2].set_title('permanent magnets +\n ferriteSysOn + pen (no EM)')
    
    B = magpy.getB(c3, (0,0,sensorZPos))
    print('permanent magnets with pen (assume ferriteSysOn). Field at sensor: ', B)
    
    c4 = magpy.Collection(magnetRing1.mCol, magnetRing2.mCol, ferriteSysOn, baseMagnet, penMagnet1, penMagnet2, coil, override_parent = True)
    F4, T4 = getFT(c4, penMagnet1) + getFT(c4, penMagnet2)
    
    print(f'with pen & coil: F{F4}, T{T4}')
    if plot:
        plotSysB(c4, axs[3], fig)
        axs[3].set_title('permanent magnets + \nferriteSysOn +\n pen + coil')
        plt.show()

        # search region around the middle & determine force on pen after moving it around

        ## rotate pen magnets back to vertical
        penMagnet1.rotate_from_angax(angle = -5, axis = 'y', anchor = (0, 0, HOVER_HEIGHT + MAGNET_H/2), degrees = True)
        penMagnet2.rotate_from_angax(angle = -5, axis = 'y', anchor = (0, 0, HOVER_HEIGHT + MAGNET_H/2), degrees = True)

        # grid...
        xs = np.linspace(-5e-3, 5e-3, 21)
        zs = np.linspace(1e-3, 6e-3, 11)
        # zs = np.linspace(-1e-3, 12e-3, 5)
        Fs = np.zeros(shape = (11, 21, 3))
        for lv1, x in enumerate(xs):
            for lv2, z in enumerate(zs): # hoverheight is 3e-3. z replaces hoverHeight
                penMagnet1.position = (x, 0.00, z + MAGNET_H/2)
                penMagnet2.postion = (x, 0.00, z + 3*MAGNET_H/2)
                F, _ = getFT(c4, penMagnet1) + getFT(c4, penMagnet2)
                Fs[lv2, lv1] = F - np.array([0, 0, penMass*9.81])
        
        fig, axs = plt.subplots(1,3)

        axs[0].imshow(Fs[:,:,2], extent=[xs.min(), xs.max(), zs.min(), zs.max()], origin='lower', cmap='viridis')
        axs[0].set_title('permanent magnets + \nferriteSysOn +\n pen + coil\n Z force')

        axs[1].imshow(Fs[:,:,0], extent=[xs.min(), xs.max(), zs.min(), zs.max()], origin='lower', cmap='viridis')
        axs[1].set_title('permanent magnets + \ferriteSysOn +\n pen + coil\n X force')

        axs[2].streamplot(xs, zs, Fs[:,:,0], Fs[:,:,2], color = np.log(Fs[:,:,0]**2+Fs[:,:,2]**2), density=1.)
        axs[2].set_aspect('equal')
        axs[2].set_title('permanent magnets + \nferriteSysOn +\n pen + coil\n Force Streamlines')
        print('note for the force streamplot, I do not account for varying ferrite magnetization')
        plt.show()

def experiment12():
    # same as exp 11 but update based on more recent test results (outcome of IRL testing from exp11)
    # note: take top of secure EM as datum
    MAGNET_TO_RING_FACE = 5e-3
    POST_TO_SENSOR = -3e-3 - 0.6e-3 # post to top face of sensor cutout + sensing position relative to sensor cutout
    POST_TO_TOP = 2.4e-3
    HOVER_HEIGHT = 5e-3 #5e-3
    MAG_RING_TO_POST = -2e-3 # update from -8e-4
    MAGNET_RING_GAP = 18.4e-3
    FERRITE_H = 12e-3
    FERRITE_D = 8e-3
    TOP_TO_FERRITE = 12.4e-3 + FERRITE_H/2# second value is coilH/2

    MAGNETIZATION = 1.51e6
    FERRITE_MAGNETIZATION_EM_OFF = 1.51e5 # magnetization of ferrite core from permanent magnets

    penMass = 1.28e-2 #kg

    magnetRing1ZPos = - POST_TO_TOP - MAG_RING_TO_POST - MAGNET_TO_RING_FACE - MAGNET_H/2
    magnetRing2ZPos = magnetRing1ZPos - MAGNET_H - MAGNET_RING_GAP
    sensorZPos = - POST_TO_TOP + POST_TO_SENSOR

    # magnetRing1 = magnetRing(0.06, 0, magnetRing1ZPos, 9, MAGNETIZATION)
    magnetRing1 = magnetRing(0.057, 0, magnetRing1ZPos, 9, MAGNETIZATION)
    # magnetRing1 = magnetRing(0.057, 0, magnetRing1ZPos, 9, MAGNETIZATION)
    # magnetRing1 = magnetRing(0.06, 0, magnetRing1ZPos, 10, MAGNETIZATION)
    magnetRing2 = magnetRing(0.054, 0, magnetRing2ZPos, 12, MAGNETIZATION)
    ferriteEMoff = magpy.magnet.Cylinder(
        dimension = (FERRITE_D, FERRITE_H),
        position = (0, 0, -TOP_TO_FERRITE),
        magnetization = (0, 0, -FERRITE_MAGNETIZATION_EM_OFF)
    )
    ferriteSysOn = ferriteEMoff.copy(deep = True)
    ferriteSysOn.magnetization = (0, 0, FERRITE_MAGNETIZATION_EM_OFF * 3.35)

    # add coil
    coil = magpy.Collection()

    coilH = 24e-3
    coilOD = 19.6e-3
    coilID = 8e-3
    wireD = 0.35e-3 # assume wire diameter from https://www.aliexpress.com/item/1005007539263147.html?spm=a2g0o.detail.pcDetailBottomMoreOtherSeller.4.ad14UWzRUWzR8E&gps-id=pcDetailBottomMoreOtherSeller&scm=1007.40050.354490.0&scm_id=1007.40050.354490.0&scm-url=1007.40050.354490.0&pvid=9bdcbb99-2488-4a53-a188-dcab84615b92&_t=gps-id:pcDetailBottomMoreOtherSeller,scm-url:1007.40050.354490.0,pvid:9bdcbb99-2488-4a53-a188-dcab84615b92,tpp_buckets:668%232846%238116%232002&pdp_ext_f=%7B%22order%22%3A%222%22%2C%22eval%22%3A%221%22%2C%22sceneId%22%3A%2230050%22%7D&pdp_npi=4%40dis%21CAD%216.38%214.60%21%21%214.54%213.27%21%402101c5bf17483994196241774eb97f%2112000041207734322%21rec%21CA%212712658390%21X&utparam-url=scene%3ApcDetailBottomMoreOtherSeller%7Cquery_from%3A
    coilCurrent = 0.123 # [A] average. (totalPower - arduinoPower)/voltage = (2.08W-0.6W)/12V = 0.12333...
    coilPosTop = -0.4e-3
    for z in np.arange(coilPosTop - wireD/2 + 1e-6, coilPosTop - coilH + wireD/2 - 1e-6, -wireD): # add -1e-6 from end given arange excludes max values...
        for r in np.arange((coilID + wireD)/2, (coilOD - wireD)/2 + 1e-6, wireD):
            winding = magpy.current.Circle(
                current=coilCurrent,
                diameter=2*r,
                position=(0,0,z),
            )
            coil.add(winding) # ~1k coil windings
    
    penMagnet1 = magpy.magnet.Cylinder(
        magnetization=(0,0,MAGNETIZATION/1.175), dimension=(MAGNET_D, MAGNET_H), position = (0, 0.00, HOVER_HEIGHT + MAGNET_H/2)
        )
        # THIS INACCRATELY CHARACERIZES PEN MAGNET BUT GOOD ENUF SINCE ONLY CARE ABOUT RELATIVE FOR NOW
    penMagnet1.meshing = 15
    penMagnet2 = penMagnet1.copy(deep = True)
    penMagnet2.position = (0, 0.00, HOVER_HEIGHT + 3*MAGNET_H/2)
    
    c = magnetRing1.mCol + magnetRing2.mCol + ferriteSysOn

    # rotate magnet for scanning restoring moment
    penMagnet1.rotate_from_angax(angle = 5, axis = 'y', anchor = (0, 0, HOVER_HEIGHT + MAGNET_H/2), degrees = True)
    penMagnet2.rotate_from_angax(angle = 5, axis = 'y', anchor = (0, 0, HOVER_HEIGHT + MAGNET_H/2), degrees = True)

    # loop thru find optimal placement for extra magnet
    print('loop thru to find optimal placement for extra magnet')
    F, T = getFT(c, penMagnet1) + getFT(c, penMagnet2)
    # print('F', F, 'T', T)
    print('current system as of 2025/09/24. Note 1.1x multiplier on magnetization since had added small magnet under')
    zPos = -33e-3 # -28e-3 update magnet position given it was found to cause noise
    baseMagnet = magpy.magnet.Cylinder(
        magnetization=(0,0,MAGNETIZATION*1.1), dimension=(MAGNET_D, MAGNET_H), position = (0, 0, zPos)
    )
    F2, T2 = getFT(baseMagnet, penMagnet1) + getFT(baseMagnet, penMagnet2)
    Ft = F + F2
    Tt = T + T2
    # ADD SECTION, CALC MAG FIELD AT SENSOR
    B_sensor = magpy.getB(c, [0, 0, sensorZPos]) + magpy.getB(penMagnet1, [0, 0, sensorZPos]) + magpy.getB(penMagnet2, [0, 0, sensorZPos]) + magpy.getB(baseMagnet, [0, 0, sensorZPos])
    print('F', Ft, 'T', Tt, 'B_sensor', B_sensor)

    baseMagnet = magpy.magnet.Cylinder(
        magnetization=(0,0,MAGNETIZATION), dimension=(MAGNET_D, MAGNET_H), position = (0, 0, zPos)
    )
    baseMagnet2 = magpy.magnet.Cylinder(
        magnetization=(0,0,MAGNETIZATION), dimension=(MAGNET_D, MAGNET_H), position = (0, 0, zPos - MAGNET_H)
    )
    baseMagnet3 = magpy.magnet.Cylinder(
        magnetization=(0,0,MAGNETIZATION), dimension=(MAGNET_D, MAGNET_H), position = (0, 0, zPos - MAGNET_H*2)
    )
    F3, T3 = getFT(baseMagnet, penMagnet1) + getFT(baseMagnet, penMagnet2) + getFT(baseMagnet2, penMagnet1) + getFT(baseMagnet2, penMagnet2) + getFT(baseMagnet3, penMagnet1) + getFT(baseMagnet3, penMagnet2)
    Ft = F + F3
    Tt = T + T3
    B_sensor = magpy.getB(c, [0, 0, sensorZPos]) + magpy.getB(penMagnet1, [0, 0, sensorZPos]) + magpy.getB(penMagnet2, [0, 0, sensorZPos]) + magpy.getB(baseMagnet, [0, 0, sensorZPos]) + magpy.getB(baseMagnet2, [0, 0, sensorZPos]) + magpy.getB(baseMagnet3, [0, 0, sensorZPos])
    print('adding magnet: \nF', Ft, 'T', Tt, 'B_sensor', B_sensor)
  
def experiment13():
    # ADD SECTION FOR LOOKING AT TRANSLATIONAL RESTORING FORCE FROM COIL AT DIFFERENT Z HEIGHTS
    # note: take top of secure EM as datum
    MAGNET_TO_RING_FACE = 5e-3
    POST_TO_SENSOR = -3e-3 - 0.6e-3 # post to top face of sensor cutout + sensing position relative to sensor cutout
    POST_TO_TOP = 2.4e-3
    MAG_RING_TO_POST = -2e-3 # update from -8e-4
    MAGNET_RING_GAP = 18.4e-3
    FERRITE_H = 12e-3
    FERRITE_D = 8e-3
    TOP_TO_FERRITE = 12.4e-3 + FERRITE_H/2# second value is coilH/2

    MAGNETIZATION = 1.51e6
    FERRITE_MAGNETIZATION_EM_OFF = 1.51e5 # magnetization of ferrite core from permanent magnets

    penMass = 1.28e-2 #kg

    magnetRing1ZPos = - POST_TO_TOP - MAG_RING_TO_POST - MAGNET_TO_RING_FACE - MAGNET_H/2
    magnetRing2ZPos = magnetRing1ZPos - MAGNET_H - MAGNET_RING_GAP
    sensorZPos = - POST_TO_TOP + POST_TO_SENSOR

    magnetRing1 = magnetRing(0.057, 0, magnetRing1ZPos, 9, MAGNETIZATION)
    magnetRing2 = magnetRing(0.054, 0, magnetRing2ZPos, 12, MAGNETIZATION)
    ferriteEMoff = magpy.magnet.Cylinder(
        dimension = (FERRITE_D, FERRITE_H),
        position = (0, 0, -TOP_TO_FERRITE),
        magnetization = (0, 0, -FERRITE_MAGNETIZATION_EM_OFF)
    )
    ferriteSysOn = ferriteEMoff.copy(deep = True)
    ferriteSysOn.magnetization = (0, 0, FERRITE_MAGNETIZATION_EM_OFF * 3.35)

    # add coil
    coil = magpy.Collection()

    coilH = 24e-3
    coilOD = 19.6e-3
    coilID = 8e-3
    wireD = 0.35e-3 # assume wire diameter from https://www.aliexpress.com/item/1005007539263147.html?spm=a2g0o.detail.pcDetailBottomMoreOtherSeller.4.ad14UWzRUWzR8E&gps-id=pcDetailBottomMoreOtherSeller&scm=1007.40050.354490.0&scm_id=1007.40050.354490.0&scm-url=1007.40050.354490.0&pvid=9bdcbb99-2488-4a53-a188-dcab84615b92&_t=gps-id:pcDetailBottomMoreOtherSeller,scm-url:1007.40050.354490.0,pvid:9bdcbb99-2488-4a53-a188-dcab84615b92,tpp_buckets:668%232846%238116%232002&pdp_ext_f=%7B%22order%22%3A%222%22%2C%22eval%22%3A%221%22%2C%22sceneId%22%3A%2230050%22%7D&pdp_npi=4%40dis%21CAD%216.38%214.60%21%21%214.54%213.27%21%402101c5bf17483994196241774eb97f%2112000041207734322%21rec%21CA%212712658390%21X&utparam-url=scene%3ApcDetailBottomMoreOtherSeller%7Cquery_from%3A
    coilCurrent = 0.123 # [A] average. (totalPower - arduinoPower)/voltage = (2.08W-0.6W)/12V = 0.12333...
    coilPosTop = -0.4e-3
    for z in np.arange(coilPosTop - wireD/2 + 1e-6, coilPosTop - coilH + wireD/2 - 1e-6, -wireD): # add -1e-6 from end given arange excludes max values...
        for r in np.arange((coilID + wireD)/2, (coilOD - wireD)/2 + 1e-6, wireD):
            winding = magpy.current.Circle(
                current=coilCurrent,
                diameter=2*r,
                position=(0,0,z),
            )
            coil.add(winding) # ~1k coil windings
    zPos = -29e-3
    baseMagnet = magpy.magnet.Cylinder(
        magnetization=(0,0,MAGNETIZATION), dimension=(MAGNET_D, MAGNET_H), position = (0, 0, zPos)
    )
    baseMagnet2 = magpy.magnet.Cylinder(
        magnetization=(0,0,MAGNETIZATION), dimension=(MAGNET_D, MAGNET_H), position = (0, 0, zPos - MAGNET_H)
    )
    
    c = magnetRing1.mCol + magnetRing2.mCol + ferriteSysOn + baseMagnet #+ baseMagnet2

    print('hover height, F, Fc, F/Fc, T, Tc, T/Tc')
    for HOVER_HEIGHT in [5e-3, 10e-3, 15e-3]:
        penMagnet1 = magpy.magnet.Cylinder(
        magnetization=(0,0,MAGNETIZATION/1.175), dimension=(MAGNET_D, MAGNET_H), position = (1e-3, 0.00, HOVER_HEIGHT + MAGNET_H/2)
        )
        # THIS INACCRATELY CHARACERIZES PEN MAGNET BUT GOOD ENUF SINCE ONLY CARE ABOUT RELATIVE FOR NOW
        penMagnet1.meshing = 15
        penMagnet2 = penMagnet1.copy(deep = True)
        penMagnet2.position = (1e-3, 0.00, HOVER_HEIGHT + 3*MAGNET_H/2)

        # # rotate magnet for scanning restoring moment
        # penMagnet1.rotate_from_angax(angle = 5, axis = 'y', anchor = (0, 0, HOVER_HEIGHT + MAGNET_H/2), degrees = True)
        # penMagnet2.rotate_from_angax(angle = 5, axis = 'y', anchor = (0, 0, HOVER_HEIGHT + MAGNET_H/2), degrees = True)

        F, T = getFT(c, penMagnet1) + getFT(c, penMagnet2)
        Fc, Tc = getFT(coil, penMagnet1) + getFT(coil, penMagnet2)
        print(HOVER_HEIGHT, F, Fc, F/Fc, T, Tc, T/Tc)

    print('notice coil translational restoring force is minimal and overpowered by permanent magnet attractive force at larger positions')

def ferriteCore(CONSTANTS, EM_state = True):
    d = CONSTANTS['FERRITE_D']
    h = CONSTANTS['FERRITE_H']
    zPos = CONSTANTS['TOP_TO_FERRITE']
    magnetization = CONSTANTS['FERRITE_MAGNETIZATION_EM_ON'] if EM_state else CONSTANTS['FERRITE_MAGNETIZATION_EM_OFF']
    ferriteCore = magpy.magnet.Cylinder(
        dimension = (d, h),
        position = (0, 0, zPos),
        magnetization = (0, 0, magnetization)
    )
    return ferriteCore 

def coil(CONSTANTS):
    diracD = 1e-6
    wireStartZ = CONSTANTS['COIL_POS_TOP'] - CONSTANTS['WIRE_D']/2 + diracD
    wireEndZ = CONSTANTS['COIL_POS_TOP'] + CONSTANTS['WIRE_D']/2 - diracD - CONSTANTS['COIL_H']
    wireStartR = (CONSTANTS['COIL_ID'] + CONSTANTS['WIRE_D'])/2 
    wireEndR = (CONSTANTS['COIL_OD'] - CONSTANTS['WIRE_D'])/2 + diracD
    coilCurrent = CONSTANTS['CURRENT']

    myCoil = magpy.Collection()
    for z in np.arange(wireStartZ, wireEndZ, -CONSTANTS['WIRE_D']): # add -1e-6 from end given arange excludes max values...
        for r in np.arange(wireStartR, wireEndR, CONSTANTS['WIRE_D']):
            winding = magpy.current.Circle(
                current=coilCurrent,
                diameter=2*r,
                position=(0,0,z),
            )
            myCoil.add(winding) # ~1k coil windings
    return myCoil

def penMagnets(CONSTANTS, rotate = 15, combineMagnets = True):
    rotateAnchor = (0, 0, CONSTANTS['HOVER_HEIGHT'] + CONSTANTS['MAGNET_H'])
    if not combineMagnets:
        penMagnet1 = magpy.magnet.Cylinder(
            magnetization = (0, 0, CONSTANTS['MAGNETIZATION']), 
            dimension = (CONSTANTS['MAGNET_D'], CONSTANTS['MAGNET_H']), 
            position = (0, 0, CONSTANTS['HOVER_HEIGHT'] + CONSTANTS['MAGNET_H']/2)
            )
        penMagnet1.meshing = 30
        penMagnet2 = penMagnet1.copy(deep = True)
        penMagnet2.position = (0, 0, CONSTANTS['HOVER_HEIGHT'] + 1.5*CONSTANTS['MAGNET_H'])

        if not rotate: # do not rotate
            return penMagnet1, penMagnet2
        penMagnet1.rotate_from_angax(angle = rotate, axis = 'y', anchor = rotateAnchor, degrees = True)
        penMagnet2.rotate_from_angax(angle = rotate, axis = 'y', anchor = rotateAnchor, degrees = True)
        return penMagnet1, penMagnet2

    # combineMagnets = True
    penMagnets = magpy.magnet.Cylinder(
        magnetization = (0, 0, CONSTANTS['MAGNETIZATION']), 
        dimension = (CONSTANTS['MAGNET_D'], 2*CONSTANTS['MAGNET_H']), 
        position = (0, 0, CONSTANTS['HOVER_HEIGHT'] + CONSTANTS['MAGNET_H'])
        )
    penMagnets.meshing = 20
    if not rotate:
        return penMagnets
    penMagnets.rotate_from_angax(angle = 5, axis = 'y', anchor = rotateAnchor, degrees = True)
    return penMagnets

def baseMagnets(CONSTANTS, combineMagnets = True):
    try:
        if (CONSTANTS['BASE_MAGNET_NUM'] == 1):
            baseMagnet = magpy.magnet.Cylinder(
                magnetization=(0, 0, CONSTANTS['MAGNETIZATION']), 
                dimension=(CONSTANTS['MAGNET_D'], CONSTANTS['MAGNET_H']), 
                position = (0, 0, CONSTANTS['BASE_MAGNET_TOP'] - CONSTANTS['MAGNET_H']/2),
            )
            return baseMagnet

    except:
        pass
    if not combineMagnets:
        baseMagnet1 = magpy.magnet.Cylinder(
            magnetization=(0, 0, CONSTANTS['MAGNETIZATION']), 
            dimension=(CONSTANTS['MAGNET_D'], CONSTANTS['MAGNET_H']), 
            position = (0, 0, CONSTANTS['BASE_MAGNET_TOP'] - CONSTANTS['MAGNET_H']/2),
        )
        baseMagnet2 = baseMagnet1.copy(deep = True)
        baseMagnet2.position = (0, 0, CONSTANTS['BASE_MAGNET_TOP'] - 1.5*CONSTANTS['MAGNET_H'])
        return baseMagnet1, baseMagnet2
    
    baseMagnet = magpy.magnet.Cylinder(
        magnetization=(0, 0, CONSTANTS['MAGNETIZATION']), 
        dimension=(CONSTANTS['MAGNET_D'], 2*CONSTANTS['MAGNET_H']), 
        position = (0, 0, CONSTANTS['BASE_MAGNET_TOP'] - CONSTANTS['MAGNET_H']),
    )
    return baseMagnet

def calcSys(CONSTANTS):
    # re-generate constants with dependencies
    CONSTANTS['TOP_TO_FERRITE'] = -12.4e-3 - CONSTANTS['FERRITE_H']/2 # second value is coilH/2
    CONSTANTS['SENSOR_POS'] =  -CONSTANTS['POST_TO_TOP'] + CONSTANTS['POST_TO_SENSOR']
    CONSTANTS['RING1_Z'] = -CONSTANTS['POST_TO_TOP'] - CONSTANTS['MAG_RING_TO_POST'] - CONSTANTS['MAGNET_TO_RING_FACE'] - CONSTANTS['MAGNET_H']/2
    CONSTANTS['RING2_Z'] = CONSTANTS['RING1_Z'] - CONSTANTS['MAGNET_H'] - CONSTANTS['MAGNET_RING_GAP']
    

    # create system objects
    magnetRing1 = magnetRing(CONSTANTS['RING1_D'], CONSTANTS['RING1_THETA'], CONSTANTS['RING1_Z'], CONSTANTS['RING1_NUM'], CONSTANTS['MAGNETIZATION'])
    magnetRing2 = magnetRing(CONSTANTS['RING2_D'], CONSTANTS['RING2_THETA'], CONSTANTS['RING2_Z'], CONSTANTS['RING2_NUM'], CONSTANTS['MAGNETIZATION'])
    baseMagnet = baseMagnets(CONSTANTS)
    ferriteSysOff = ferriteCore(CONSTANTS, EM_state = False)
    ferriteSysOn = ferriteCore(CONSTANTS)
    myCoil = coil(CONSTANTS)
    penMagnet = penMagnets(CONSTANTS) # penMagnet1, penMagnet2 = penMagnets(CONSTANTS)
    myCol = {
        'magnets' : magnetRing1.mCol + magnetRing2.mCol + baseMagnet,
        # 'EMoff' : ferriteSysOff, # likely can ignore this case...
        'EMon' : ferriteSysOn + myCoil,
        }
    Fs = {}
    Ts = {}
    B_sensor = magpy.getB(penMagnet, [0, 0, CONSTANTS['SENSOR_POS']])
    for key, val in myCol.items():
        Fs[key], Ts[key] = getFT(val, penMagnet)
        B_sensor += magpy.getB(val, [0, 0, CONSTANTS['SENSOR_POS']])

    
    # pl = magpy.show(magnetRing1.mCol, backend='pyvista', return_fig=True)
    # pl.show()

    return Fs, Ts, B_sensor

def scanHoverCalc(CONSTANTS, dHeights = [-1e-3, 0, 1e-3]):
    
    Fs = dict()
    Ts = dict()
    for dHeight in dHeights:
        CONSTANTS_ = copy.deepcopy(CONSTANTS)
        hoverHeight = CONSTANTS['HOVER_HEIGHT'] + dHeight
        CONSTANTS_['HOVER_HEIGHT'] = hoverHeight
        Fs[hoverHeight], Ts[hoverHeight], B_sensor = calcSys(CONSTANTS_)
    return Fs, Ts, B_sensor

import os
import numpy as np
import matplotlib.pyplot as plt

def plotScanResults(variable, variableExplore, CONSTANTS, dHeights=[-1e-3, 0, 1e-3]):
    """
    variableExplore: dict of {variable_value: (Fs_dict, Ts_dict, B_sensor_array)}
    """
    Fg = -9.81 * CONSTANTS['PEN_MASS']
    os.makedirs("background/TheoreticalPlots", exist_ok=True)

    fig, axs = plt.subplots(2, 2, figsize=(12, 10))
    colors = ['tab:blue', 'tab:orange', 'tab:green']

    # --- Step 1: Precompute all ratio data for consistent scaling ---
    all_ratios = []  # Collect all ratio values for scaling
    all_x_vals = []

    for hoverHeight in dHeights:
        x_vals = list(variableExplore.keys())
        y_ratio = []
        for val in x_vals:
            Fs_dict, Ts_dict, B_sensor = variableExplore[val]
            Fs_h = Fs_dict[CONSTANTS['HOVER_HEIGHT'] + hoverHeight]
            Fx_mag = Fs_h["magnets"][0]
            Fx_EMon = Fs_h["EMon"][0]
            ratio = Fx_EMon / Fx_mag if Fx_mag != 0 else np.nan
            y_ratio.append(ratio)
        all_ratios.extend(y_ratio)
        all_x_vals.extend(x_vals)

    # Clean NaNs and determine consistent y-limits
    valid_ratios = np.array([r for r in all_ratios if np.isfinite(r)])
    if len(valid_ratios) > 0:
        ratio_ymin, ratio_ymax = np.nanmin(valid_ratios), np.nanmax(valid_ratios)
        # Add a small margin
        ratio_ymin -= 0.05 * abs(ratio_ymin)
        ratio_ymax += 0.05 * abs(ratio_ymax)
    else:
        ratio_ymin, ratio_ymax = 0, 1

    # --- Step 2: Plot everything ---
    for i, hoverHeight in enumerate(dHeights):
        x_vals = list(variableExplore.keys())
        y_Fz, y_Ty, y_Fx_magnets, y_Fx_EMon, y_Bsensor, y_ratio = [], [], [], [], [], []

        for val in x_vals:
            Fs_dict, Ts_dict, B_sensor = variableExplore[val]
            Fs_h = Fs_dict[CONSTANTS['HOVER_HEIGHT'] + hoverHeight]
            Ts_h = Ts_dict[CONSTANTS['HOVER_HEIGHT'] + hoverHeight]

            Fx_mag = Fs_h["magnets"][0]
            Fx_EMon = Fs_h["EMon"][0]

            y_Fz.append(Fs_h["magnets"][2] + Fs_h["EMon"][2] + Fg)
            y_Ty.append(Ts_h["magnets"][1] + Ts_h["EMon"][1])
            y_Fx_magnets.append(Fx_mag)
            y_Fx_EMon.append(Fx_EMon)
            y_Bsensor.append(B_sensor[2])
            y_ratio.append(Fx_EMon / Fx_mag if Fx_mag != 0 else np.nan)

        label = f"hover = {CONSTANTS['HOVER_HEIGHT'] + hoverHeight:.3e} m"
        color = colors[i % len(colors)]

        # Subplot 1: total vertical force
        axs[0, 0].plot(x_vals, y_Fz, 'o-', color=color, label=label)
        axs[0, 0].set_ylabel("Total Force Z (N)")
        axs[0, 0].set_title(f"{variable} vs Total Restoring Force")

        # Subplot 2: restoring torque
        # flip y axis for intuition (higher better)
        axs[0, 1].plot(x_vals, [-v for v in y_Ty], 'o-', color=color, label=label)
        axs[0, 1].set_ylabel("Total Torque Y (Nm)")
        axs[0, 1].set_title(f"{variable} vs Restoring Torque")

        # Subplot 3: horizontal forces + ratio
        ax_force = axs[1, 0]
        ax_force.plot(x_vals, y_Fx_magnets, '-', color=color, label=f"{label} (magnets)")
        ax_force.plot(x_vals, y_Fx_EMon, '--', color=color, label=f"{label} (EMon)")
        ax_force.set_ylabel("Force X (N)")
        ax_force.set_title(f"{variable} vs Horizontal Forces")

        # Twin axis for ratio — consistent y-scale
        ax_ratio = ax_force.twinx()
        ax_ratio.plot(x_vals, y_ratio, ':', color=color, label=f"{label} (EMon/magnets)")
        ax_ratio.set_ylabel("Fx_EMon / Fx_magnets", color='black')
        ax_ratio.tick_params(axis='y', labelcolor='black')
        ax_ratio.set_ylim(ratio_ymin, ratio_ymax)

        # Combine legends
        lines1, labels1 = ax_force.get_legend_handles_labels()
        lines2, labels2 = ax_ratio.get_legend_handles_labels()
        ax_force.legend(lines1 + lines2, labels1 + labels2, loc='best')

        # Subplot 4: magnetic field
        # flip y axis for intuition (higher better)
        axs[1, 1].plot(x_vals, [-v for v in y_Bsensor], 'o-', color=color, label=label)
        axs[1, 1].set_ylabel("B_sensor Z (T)")
        axs[1, 1].set_title(f"{variable} vs B_sensor")

    # Shared styling
    for ax in axs.flat:
        ax.set_xlabel(variable)
        ax.grid(True)

    plt.suptitle(f"System Behavior vs {variable}")
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    plt.savefig(f"background/TheoreticalPlots/plot_{variable}.png", dpi=300)
    plt.show()


def experiment14():
    # combine exp 12 & 13. Plot.
    # ADD SECTION FOR LOOKING AT TRANSLATIONAL RESTORING FORCE FROM COIL AT DIFFERENT Z HEIGHTS
    # note: take top of secure EM as datum
    CONSTANTS = {
        'MAGNET_D' : 10e-3, # m
        'MAGNET_H' : 5e-3, # m
        'MAGNET_TO_RING_FACE' : 5e-3, # m
        'POST_TO_SENSOR' : -3e-3 - 0.6e-3, # m; post to top face of sensor cutout + sensing position relative to sensor cutout
        'POST_TO_TOP' : 2.4e-3, # m
        'MAG_RING_TO_POST' : -2e-3, # m; update from -8e-4
        'MAGNET_RING_GAP' : 17e-3, #18.4e-3, # m
        'FERRITE_H' : 12e-3, # m
        'FERRITE_D' : 8e-3, # m
        'MAGNETIZATION' : 1.51e6,
        'FERRITE_MAGNETIZATION_EM_OFF' : -1.51e5, # magnetization of ferrite core from permanent magnets
        'FERRITE_MAGNETIZATION_EM_ON' : 1.51e5 * 3.35, # calculated magnetization when control system is ON
        'PEN_MASS' : 1.40e-2, #kg for minimalist pen; # 1.42e-2 # kg for fancy pen
        'HOVER_HEIGHT' : 5e-3, #5e-3
        'COIL_H' : 24e-3,
        'COIL_OD' : 19.6e-3,
        'COIL_ID' : 8e-3,
        'WIRE_D' : 0.35e-3, # assume wire diameter from https://www.aliexpress.com/item/1005007539263147.html?spm=a2g0o.detail.pcDetailBottomMoreOtherSeller.4.ad14UWzRUWzR8E&gps-id=pcDetailBottomMoreOtherSeller&scm=1007.40050.354490.0&scm_id=1007.40050.354490.0&scm-url=1007.40050.354490.0&pvid=9bdcbb99-2488-4a53-a188-dcab84615b92&_t=gps-id:pcDetailBottomMoreOtherSeller,scm-url:1007.40050.354490.0,pvid:9bdcbb99-2488-4a53-a188-dcab84615b92,tpp_buckets:668%232846%238116%232002&pdp_ext_f=%7B%22order%22%3A%222%22%2C%22eval%22%3A%221%22%2C%22sceneId%22%3A%2230050%22%7D&pdp_npi=4%40dis%21CAD%216.38%214.60%21%21%214.54%213.27%21%402101c5bf17483994196241774eb97f%2112000041207734322%21rec%21CA%212712658390%21X&utparam-url=scene%3ApcDetailBottomMoreOtherSeller%7Cquery_from%3A
        'CURRENT' : 0.123, # [A] average. (totalPower - arduinoPower)/voltage = (2.08W-0.6W)/12V = 0.12333...
        'COIL_POS_TOP' : -0.4e-3, # m
        'BASE_MAGNET_TOP' : -31.5e-3, # m
        'RING1_D' : 0.059, # m
        'RING2_D' : 0.045, # m
        'RING1_NUM' : 9, # number of magnets in ring 1
        'RING2_NUM' : 12, # number of magnets in ring 2
        'RING1_THETA' : 0, # deg
        'RING2_THETA' : 0,
    }
    Fg = -9.81*CONSTANTS['PEN_MASS']

    # # base case
    # print('Base Case')
    # print(CONSTANTS)
    # Fs, Ts, B_sensor = calcSys(CONSTANTS)
    # print(f'F_magnet_z {Fs["magnets"][2]:.3f} | F_EMon_z {Fs["EMon"][2]:.3f} | F_g {Fg:.3f} | sum {Fs["magnets"][2] + Fs["EMon"][2] + Fg:.3f}')
    # print(f'restoring moment (care magnitude) {Ts["magnets"][1] + Ts["EMon"][1]:.5f}')
    # print(f'F_destabilize_x {Fs["magnets"][0]:.4f} | F_stabilize_x {Fs["EMon"][0]:.4f} | ratio (small better) {Fs["magnets"][0]/Fs["EMon"][0]:.3f}')
    # print(f'Sensor field Z (closer to 0 best): {B_sensor[2]:.3f}')

    # # scan
    # for variable in ['MAG_RING_TO_POST', 'MAGNET_RING_GAP', 'BASE_MAGNET_TOP', 'RING1_D', 'RING2_D']:
    #     CONSTANTS_ = copy.deepcopy(CONSTANTS)
    #     variableExplore = dict()
    #     for delta in [-4e-3, -2e-3, 0e-3, 2e-3, 4e-3]:
    #         newValue = CONSTANTS[variable] + delta
    #         CONSTANTS_[variable] = newValue
    #         variableExplore[newValue] = scanHoverCalc(CONSTANTS_)

    #     # ADD PLOTTING FUNCTION HERE:
    #     # x-axis is variable being explored, y-axis is variable
    #     # subplot 1: y-axis = Fs["magnets"][2] + Fs["EMon"][2] + Fg. Color code by hover height
    #     # subplot 2: y-axis = Ts["magnets"][1] + Ts["EMon"][1]:.5f. Color code by hover hieght
    #     # subplot 3: y-axis is force. Plot 2 lines: line 1 is Fs["magnets"][0], line 2 is Fs["EMon"][0] (one dashed, one solid). Also color code by hover height
    #     # subplot 4: y-axis is B_sensor[2]
    #     # title each plot with variable being explored
    #     # save plot under name of plot
    #     plotScanResults(variable, variableExplore, CONSTANTS)

    # scan
    CONSTANTS['RING2_D'] = 0.03 # REDUCE FOR EXPERIMENT
    for variable in ['RING1_THETA', 'RING2_THETA', 'RING1_NUM', 'RING2_NUM']:
        CONSTANTS_ = copy.deepcopy(CONSTANTS)
        variableExplore = dict()
        for delta in [-5, -2, -1, 0, 1, 2, 5]:
            newValue = CONSTANTS[variable] + delta
            CONSTANTS_[variable] = newValue
            variableExplore[newValue] = scanHoverCalc(CONSTANTS_)

        plotScanResults(variable, variableExplore, CONSTANTS)
            
            


    # generally smaller ringD for ring2 is better. As ringD reduces, bring slightly higher up.
    return


def experiment15():
    # combine exp 12 & 13. Plot.
    # ADD SECTION FOR LOOKING AT TRANSLATIONAL RESTORING FORCE FROM COIL AT DIFFERENT Z HEIGHTS
    # note: take top of secure EM as datum
    CONSTANTS = {
        'MAGNET_D' : 10e-3, # m
        'MAGNET_H' : 5e-3, # m
        'MAGNET_TO_RING_FACE' : 5e-3, # m
        'POST_TO_SENSOR' : -3e-3 - 0.6e-3, # m; post to top face of sensor cutout + sensing position relative to sensor cutout
        'POST_TO_TOP' : 2.4e-3, # m
        'MAG_RING_TO_POST' : -3.4e-3, # m; update from -8e-4
        'MAGNET_RING_GAP' : 15e-3,#17e-3, #18.4e-3, # m
        'FERRITE_H' : 12e-3, # m
        'FERRITE_D' : 8e-3, # m
        'MAGNETIZATION' : 1.51e6,
        'FERRITE_MAGNETIZATION_EM_OFF' : -1.51e5, # magnetization of ferrite core from permanent magnets
        'FERRITE_MAGNETIZATION_EM_ON' : 1.51e5 * 3.35, # calculated magnetization when control system is ON
        'PEN_MASS' : 1.40e-2, #kg for minimalist pen; # 1.42e-2 # kg for fancy pen
        'HOVER_HEIGHT' : 5e-3, #5e-3 # m
        'COIL_H' : 24e-3, # m
        'COIL_OD' : 19.6e-3, # m
        'COIL_ID' : 8e-3, # m
        'WIRE_D' : 0.35e-3, # m; assume wire diameter from https://www.aliexpress.com/item/1005007539263147.html?spm=a2g0o.detail.pcDetailBottomMoreOtherSeller.4.ad14UWzRUWzR8E&gps-id=pcDetailBottomMoreOtherSeller&scm=1007.40050.354490.0&scm_id=1007.40050.354490.0&scm-url=1007.40050.354490.0&pvid=9bdcbb99-2488-4a53-a188-dcab84615b92&_t=gps-id:pcDetailBottomMoreOtherSeller,scm-url:1007.40050.354490.0,pvid:9bdcbb99-2488-4a53-a188-dcab84615b92,tpp_buckets:668%232846%238116%232002&pdp_ext_f=%7B%22order%22%3A%222%22%2C%22eval%22%3A%221%22%2C%22sceneId%22%3A%2230050%22%7D&pdp_npi=4%40dis%21CAD%216.38%214.60%21%21%214.54%213.27%21%402101c5bf17483994196241774eb97f%2112000041207734322%21rec%21CA%212712658390%21X&utparam-url=scene%3ApcDetailBottomMoreOtherSeller%7Cquery_from%3A
        'CURRENT' : 0.123, # [A] average. (totalPower - arduinoPower)/voltage = (2.08W-0.6W)/12V = 0.12333...
        'COIL_POS_TOP' : -0.4e-3, # m
        'BASE_MAGNET_TOP' : -24e-3, # -31.5e-3, # m
        'BASE_MAGNET_NUM' : 2,
        'RING1_D' : 0.055,#0.06, # m
        'RING2_D' : 0.042,#0.045, # m
        'RING1_NUM' : 9, # number of magnets in ring 1
        'RING2_NUM' : 11,#12, # number of magnets in ring 2
        'RING1_THETA' : 0, # deg
        'RING2_THETA' : 0,
    }
    Fg = -9.81*CONSTANTS['PEN_MASS']

    # # manual iteration
    # print('Base Case')
    # print(CONSTANTS)
    Fs, Ts, B_sensor = calcSys(CONSTANTS)
    # print(f'F_magnet_z {Fs["magnets"][2]:.3f} | F_EMon_z {Fs["EMon"][2]:.3f} | F_g {Fg:.3f} | sum {Fs["magnets"][2] + Fs["EMon"][2] + Fg:.3f}')
    # print(f'restoring moment (care magnitude) {Ts["magnets"][1] + Ts["EMon"][1]:.5f}')
    # print(f'F_destabilize_x {Fs["magnets"][0]:.4f} | F_stabilize_x {Fs["EMon"][0]:.4f} | ratio (small better) {Fs["magnets"][0]/Fs["EMon"][0]:.3f}')
    # print(f'Sensor field Z (closer to 0 best): {B_sensor[2]:.3f}')

    # new_row_data = list(CONSTANTS.keys()) + [
    #     'F_magnet_z [N]', 
    #     'F_EMon_z [N]', 
    #     'F_g_z [N]', 
    #     'F_t_z [N]', 
    #     '-Restoring Moment [Nm]', 
    #     'F_destabilize_x [N]', 
    #     'F_stabilize_x [N]', 
    #     'F_stabilize_x + F_destabilize_x [N]'
    #     ] # for file creation

    new_row_data = list(CONSTANTS.values()) + [
        Fs["magnets"][2], 
        Fs["EMon"][2], 
        Fg, 
        Fs["magnets"][2] + Fs["EMon"][2] + Fg, 
        -(Ts["magnets"][1] + Ts["EMon"][1]),
        Fs["magnets"][0],
        Fs["EMon"][0],
        Fs["EMon"][0] + Fs["magnets"][0],
        ]
    with open('experimentParams.csv', 'a', newline = '') as myFile:
        writer = csv.writer(myFile)
        writer.writerow(new_row_data)

    # # scan for experiment
    # CONSTANTS['RING2_NUM'] = 6
    # for ring2D in [0.03, 0.0325, 0.035]:
    #     CONSTANTS['RING2_D'] = ring2D
    #     variableExplore = dict()
    #     for magnetRingGap in [10e-3, 12e-3, 15e-3, 17.5e-3, 20e-3]: # default is 17e-3
    #         CONSTANTS['MAGNET_RING_GAP'] = magnetRingGap
    #         Fs, Ts, B_sensor = calcSys(CONSTANTS)
    #         variableExplore[magnetRingGap] = scanHoverCalc(CONSTANTS)
    #     plotScanResults(f'Ring2D {ring2D}', variableExplore, CONSTANTS) 
    
    
    # for variable in ['RING1_THETA', 'RING2_THETA', 'RING1_NUM', 'RING2_NUM']:
    #     CONSTANTS_ = copy.deepcopy(CONSTANTS)
    #     variableExplore = dict()
    #     for delta in [-5, -2, -1, 0, 1, 2, 5]:
    #         newValue = CONSTANTS[variable] + delta
    #         CONSTANTS_[variable] = newValue
    #         variableExplore[newValue] = scanHoverCalc(CONSTANTS_)
            
    #     plotScanResults(variable, variableExplore, CONSTANTS)
    return


def experiment16():
    # expand on experiment8 kind of: try and mod exp 8
    # for now keep ferrite magnetization constant. Numbers don't really make sense when considering middle of ferrite 
    # so it's likely that EM is magnetizing ferrite & inductance maintains it and/or magnetization is non-constant through the body

    # search attempt 1
    # for each setup:
    # move pen vertically & find force & torque. Ignore ferrite & EM for now.

    # goal is to find minimum force to lift 9g object with most stabilization

    # loop through setup configs:
        # num magnets in top & bottom ring
        # D of top ring & bottom ring
        # angle of top & bottom ring
        # adding magnet in middle in either orientation (diff strength too)


    pass

    

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
    # experiment8()

    # what is impact of changing coil shape and size
    # experiment9()

    # repeat of experiment8, except also additional magnet under coil
    # experiment11(True)

    # repeat experiment11, updated based on IRL experiments & focused on further optimization
    # experiment12()

    # experiment13()

    # experiment14()
    experiment15()


if __name__ == "__main__":
    main()