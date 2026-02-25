import magpylib as magpy
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import pyvista as pv
import math
from scipy.spatial.transform import Rotation as R
import time
from magpylib_force import getFT
from scipy.optimize import minimize

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

def magneticFieldToSensorReading(magField):
    return(511.5 - 3765.2*magField)

def sensorReadingToMagneticField(sensorReading):
    return((-sensorReading + 511.5) / 3765.2)

import numpy as np
import magpylib as magpy
from scipy.optimize import minimize

import numpy as np
import magpylib as magpy
from scipy.optimize import minimize
from scipy.spatial.transform import Rotation as R

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

def findEquilibrium(xi=1e-3, zi=3e-3, initial_angle_deg=-2):
    # --- constants ---
    MAGNET_TO_RING_FACE = 5e-3
    POST_TO_SENSOR = -3e-3 - 0.6e-3
    POST_TO_TOP = 2.1e-3
    MAG_RING_TO_POST = 2e-3 #2e-3
    MAGNET_RING_GAP = 18.4e-3
    FERRITE_H = 12e-3
    FERRITE_D = 8e-3
    TOP_TO_FERRITE = 12.4e-3 + FERRITE_H/2
    MAGNETIZATION = 1.51e6
    FERRITE_MAGNETIZATION_EM_OFF = 1.51e5
    FERRITE_MAGNETIZATION = FERRITE_MAGNETIZATION_EM_OFF * 3.35
    coilH = 24e-3
    coilOD = 19.6e-3
    coilID = 8e-3
    wireD = 0.35e-3
    coilCurrent = 0.123
    Fg = 9.7e-3 * 9.81  # [N] pen weight (positive magnitude)

    # --- build fixed sources ---
    magnetRing1ZPos = - POST_TO_TOP - MAG_RING_TO_POST - MAGNET_TO_RING_FACE - MAGNET_H/2
    magnetRing2ZPos = magnetRing1ZPos - MAGNET_H - MAGNET_RING_GAP

    magnetRing1 = magnetRing(0.06, 0, magnetRing1ZPos, 9, MAGNETIZATION)
    magnetRing2 = magnetRing(0.06, 0, magnetRing2ZPos, 12, MAGNETIZATION)
    ferrite = magpy.magnet.Cylinder(
        dimension=(FERRITE_D, FERRITE_H),
        position=(0, 0, -TOP_TO_FERRITE),
        magnetization=(0, 0, FERRITE_MAGNETIZATION)
    )
    coil = magpy.Collection()
    coilPosTop = -0.4e-3
    for z in np.arange(coilPosTop - wireD/2 + 1e-6,
                       coilPosTop - coilH + wireD/2 - 1e-6, -wireD):
        for r in np.arange((coilID + wireD)/2,
                           (coilOD - wireD)/2 + 1e-6, wireD):
            coil.add(magpy.current.Circle(
                current=coilCurrent,
                diameter=2*r,
                position=(0, 0, z),
            ))
    c = magnetRing1.mCol + magnetRing2.mCol + ferrite + coil

    # --- imbalance function ---
    def imbalance(x):
        posX, posZ, angle_deg = x

        # build magnets
        penMagnet1 = magpy.magnet.Cylinder(
            magnetization=(0, 0, MAGNETIZATION/1.175),
            dimension=(MAGNET_D, MAGNET_H),
            position=(posX, 0, posZ + MAGNET_H/2)
        )
        penMagnet1.meshing = 15
        penMagnet2 = penMagnet1.copy(deep=True)
        penMagnet2.position = (posX, 0, posZ + 3*MAGNET_H/2)

        # define COM (before rotation, relative to bottom of lower magnet)
        penCM = np.array([posX, 0, posZ + 12e-3])

        # rotate about anchor at (posX,0,posZ)
        anchor = np.array([posX, 0, posZ])
        penMagnet1.rotate_from_angax(angle=angle_deg, axis='y', anchor=anchor, degrees=True)
        penMagnet2.rotate_from_angax(angle=angle_deg, axis='y', anchor=anchor, degrees=True)
        rot = R.from_euler('y', angle_deg, degrees=True)
        penCM = anchor + rot.apply(penCM - anchor)
        # print(penCM, penMagnet1.position, penMagnet2.position) # validate rotation is correct

        # get net force + torque about COM
        F1, T1 = getFT(c, penMagnet1, anchor=penCM)
        F2, T2 = getFT(c, penMagnet2, anchor=penCM)
        F = F1 + F2
        T = T1 + T2
        # print(T,F)

        # balance conditions
        Fz_err = F[2] - Fg   # vertical balance
        Fx_err = F[0]        # lateral balance
        Ty_err = T[1]        # restoring torque about y

        cost = Fz_err**2 + Fx_err**2 + (1e5*Ty_err)**2
        print('posX', posX, 'posZ', posZ, 'angle_deg', angle_deg, 'cost', cost, 'force', 'F', 'torque', T)
        print(penCM, penCM-penMagnet1.position, penCM-penMagnet2.position)
        print('magnet1position:', penMagnet1.position, 'F1', F1, 'T1', T1)
        F1_, T1_ = getFT(c, penMagnet1, anchor=penMagnet1.position)
        print('F1', F1_, 'T1', T1_)
        print('comparing where you calculate moment (CofG of pen vs middle of magnet) confirms this calculation is correct')
        print('deviation from IRL is likely magnetic field variance across magnets')
        print('magnet2position:', penMagnet2.position, 'F2', F2, 'T2', T2)
        return cost

    # --- optimize ---
    res = minimize(
        imbalance,
        x0=[xi, zi, initial_angle_deg],
        bounds=[(3e-3, 3e-3), (1e-3, 10e-3), (-20, 20)],
        tol=1e-8
    )

    x_eq, z_eq, angle_eq = res.x
    print(f"Equilibrium found: X = {x_eq*1e3:.2f} mm, Z = {z_eq*1e3:.2f} mm, Angle = {angle_eq:.2f} deg")

    penMagnet1 = magpy.magnet.Cylinder(
        magnetization=(0, 0, MAGNETIZATION/1.175),
        dimension=(MAGNET_D, MAGNET_H),
        position=(x_eq, 0, z_eq + MAGNET_H/2)
    )
    penMagnet1.meshing = 15
    penMagnet2 = penMagnet1.copy(deep=True)
    penMagnet2.position = (x_eq, 0, z_eq + 3*MAGNET_H/2)

    # define COM (before rotation, relative to bottom of lower magnet)
    penCM = np.array([x_eq, 0, z_eq + 12e-3])

    # rotate about anchor at (posX,0,posZ)
    anchor = np.array([x_eq, 0, z_eq])
    penMagnet1.rotate_from_angax(angle=angle_eq, axis='y', anchor=anchor, degrees=True)
    penMagnet2.rotate_from_angax(angle=angle_eq, axis='y', anchor=anchor, degrees=True)

    c2 = magpy.Collection(magnetRing1.mCol, magnetRing2.mCol, ferrite, penMagnet1, penMagnet2, coil, override_parent = True)
    F, T = getFT(c2, penMagnet1) + getFT(c2, penMagnet2)
    
    print(f'with pen & coil: F{F}, T{T}')
    fig, axs = plt.subplots(1,1)
    plotSysB(c2, axs, fig)
    plt.show()

    return x_eq, z_eq, angle_eq, res.fun



def systemFT():
    # gets force and moment 
        # initially tried ignoring coil & ferrite. hover height ~9e-3 as peak moment. Coil and ferrite has big impact so must include

    # note: take top of secure EM as datum
    MAGNET_TO_RING_FACE = 5e-3
    POST_TO_SENSOR = -3e-3 - 0.6e-3 # post to top face of sensor cutout + sensing position relative to sensor cutout
    POST_TO_TOP = 2.1e-3
    # HOVER_HEIGHT = 3e-3
    MAG_RING_TO_POST = 2e-3
    MAGNET_RING_GAP = 18.4e-3
    FERRITE_H = 12e-3
    FERRITE_D = 8e-3
    TOP_TO_FERRITE = 12.4e-3 + FERRITE_H/2# second value is coilH/2

    MAGNETIZATION = 1.51e6
    FERRITE_MAGNETIZATION_EM_OFF = 1.51e5 # magnetization of ferrite core from permanent magnets   
    FERRITE_MAGNETIZATION = FERRITE_MAGNETIZATION_EM_OFF * 3.35 # EM on with pen. Estimate.

    coilH = 24e-3
    coilOD = 19.6e-3
    coilID = 8e-3
    wireD = 0.35e-3 # assume wire diameter from https://www.aliexpress.com/item/1005007539263147.html?spm=a2g0o.detail.pcDetailBottomMoreOtherSeller.4.ad14UWzRUWzR8E&gps-id=pcDetailBottomMoreOtherSeller&scm=1007.40050.354490.0&scm_id=1007.40050.354490.0&scm-url=1007.40050.354490.0&pvid=9bdcbb99-2488-4a53-a188-dcab84615b92&_t=gps-id:pcDetailBottomMoreOtherSeller,scm-url:1007.40050.354490.0,pvid:9bdcbb99-2488-4a53-a188-dcab84615b92,tpp_buckets:668%232846%238116%232002&pdp_ext_f=%7B%22order%22%3A%222%22%2C%22eval%22%3A%221%22%2C%22sceneId%22%3A%2230050%22%7D&pdp_npi=4%40dis%21CAD%216.38%214.60%21%21%214.54%213.27%21%402101c5bf17483994196241774eb97f%2112000041207734322%21rec%21CA%212712658390%21X&utparam-url=scene%3ApcDetailBottomMoreOtherSeller%7Cquery_from%3A
    coilCurrent = 0.123 # (totalPower - arduinoPower)/voltage = (2.08W-0.6W)/12V = 0.12333... average value

    magnetRing1ZPos = - POST_TO_TOP - MAG_RING_TO_POST - MAGNET_TO_RING_FACE - MAGNET_H/2
    magnetRing2ZPos = magnetRing1ZPos - MAGNET_H - MAGNET_RING_GAP
    sensorZPos = - POST_TO_TOP + POST_TO_SENSOR

    magnetRing1 = magnetRing(0.06, 0, magnetRing1ZPos, 9, MAGNETIZATION)
    magnetRing2 = magnetRing(0.06, 0, magnetRing2ZPos, 12, MAGNETIZATION)
    ferrite = magpy.magnet.Cylinder(
        dimension = (FERRITE_D, FERRITE_H),
        position = (0, 0, -TOP_TO_FERRITE),
        magnetization = (0, 0, FERRITE_MAGNETIZATION)
    )
    coil = magpy.Collection()
    coilPosTop = -0.4e-3
    for z in np.arange(coilPosTop - wireD/2 + 1e-6, coilPosTop - coilH + wireD/2 - 1e-6, -wireD): # add -1e-6 from end given arange excludes max values...
        for r in np.arange((coilID + wireD)/2, (coilOD - wireD)/2 + 1e-6, wireD):
            winding = magpy.current.Circle(
                current=coilCurrent,
                diameter=2*r,
                position=(0,0,z),
            )
            coil.add(winding)

    c = magnetRing1.mCol + magnetRing2.mCol + ferrite + coil
    
    Fxs = []
    Fzs = []
    Ts = []
    Fg = 9.7e-3*9.81 # [N] weight of pen
    penCM = [0, 0, 28e-3] # center of mass. Measured from bottom of lower magnet
    hoverHeights = np.linspace(1e-3, 10e-3, 10)
    for HOVER_HEIGHT in hoverHeights:
        penMagnet1 = magpy.magnet.Cylinder(
            magnetization=(0,0,MAGNETIZATION/1.175), dimension=(MAGNET_D, MAGNET_H), position = (0, 0.00, HOVER_HEIGHT + MAGNET_H/2)
            )
        penMagnet1.meshing = 15
        penMagnet2 = penMagnet1.copy(deep = True)
        penMagnet2.position = (0, 0.00, HOVER_HEIGHT + 3*MAGNET_H/2)
        
        # rotate around datum vs about magnets - this results in generally smaller x-force so is more 'accurate' to equilibrium position(s)
        penMagnet1.rotate_from_angax(angle = 5, axis = 'y', anchor = (0, 0, HOVER_HEIGHT + 20e-3), degrees = True)
        penMagnet2.rotate_from_angax(angle = 5, axis = 'y', anchor = (0, 0, HOVER_HEIGHT + 20e-3), degrees = True)
        print(penMagnet1.position)
        print(penMagnet2.position)
        # rotation results in restoring T[1]
        # we care about F[2] since this is vertical force
        # for both we only care about magnitudes, so take abs.
        F, T = getFT(c, penMagnet1) + getFT(c, penMagnet2)
        print('F',F,'T',T)
        Fxs.append(F[0])
        Fzs.append(F[2] - Fg)
        Ts.append(abs(T[1]))

    fig, ax1 = plt.subplots()

    # Plot Fzs vs hoverHeights
    color = 'tab:blue'
    ax1.set_xlabel('Hover Height')
    ax1.set_ylabel('Fz', color=color)
    ax1.plot(hoverHeights, Fzs, color=color, marker='o', label='Fz')
    ax1.plot(hoverHeights, Fxs, color=color, marker='x', label='Fx')
    ax1.tick_params(axis='y', labelcolor=color)

    # Create second y-axis for Ts
    ax2 = ax1.twinx()  
    color = 'tab:red'
    ax2.set_ylabel('T', color=color)
    ax2.plot(hoverHeights, Ts, color=color, marker='s', label='T')
    ax2.tick_params(axis='y', labelcolor=color)

    # Optional: add grid & title
    ax1.grid(True)
    plt.title("Fz and T vs Hover Height")

    plt.show()
        
    # B = magpy.getB(c, (0,0,sensorZPos))
    # B_f = magpy.getB(c, (0,0,-TOP_TO_FERRITE))
    
    return(F,T)


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
    # ^ I think this is incorrectly named FERRITE_MAGNETIZATION_EM_OFF should be FERRITE_MAGNETIZATION_EM_ON
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
    coilPosTop = -0.4e-3
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

def experiment10():
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
    # systemFT()
    print(findEquilibrium())


if __name__ == "__main__":
    main()