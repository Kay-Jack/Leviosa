import magpylib as magpy
import numpy as np
import matplotlib.pyplot as plt
import math
from scipy.spatial.transform import Rotation as R

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
    floatingMagnet:bool = False,
    xs:np.array = np.linspace(-0.05, 0.05, 29),
    zs:np.array = np.linspace(-0.05, 0.05, 29),
    ) -> None:
    Bs = np.array([[magnetCollection.getB([x,0,z]) for x in xs] for z in zs])
    X,Z = np.meshgrid(xs,zs)
    U,V = Bs[:,:,0], Bs[:,:,2]

    ax.streamplot(X, Z, U, V, color=np.log(U**2+V**2),density=2)
    

def main():
    magnetRing1 = magnetRing(0.06, 0, 0, 12)
    magnetRing2 = magnetRing(0.04, 30, -0.05, 12)
    # floatingMagnets = 
    c = magnetRing1.mCol + magnetRing2.mCol

    fig, axs = plt.subplots()
    plotSysB(c, axs)
    plt.show()
    # xs = np.linspace(-0.05,0.05,29)
    # zs = np.linspace(-0.05,0.05,29)
    # Bs = np.array([[c.getB([x,0,z]) for x in xs] for z in zs])
    # X,Z = np.meshgrid(xs,zs)
    # U,V = Bs[:,:,0], Bs[:,:,2]
    # plt.streamplot(X, Z, U, V, color=np.log(U**2+V**2),density=2)
    # plt.show()

if __name__ == "__main__":
    main()


# magnetRing1 = []
# numMagnets1 = 12
# magnetRing1_r = 0.03
# for lv1 in range(numMagnets1):
#     theta = lv1*math.pi/6 # angle in radians
#     magnetRing1.append(
#         magpy.magnet.Cylinder(
#             polarization=(0,0,1), dimension=(0.01, 0.005), 
#             position = (magnetRing1_r*np.cos(theta), magnetRing1_r*np.sin(theta), 0)
#         )
#         )
#     print(magnetRing1[-1].position)

# magnetRing2 = []
# numMagnets2 = 12
# magnetRing2_r = 0.03
# for lv1 in range(numMagnets2):
#     theta = lv1*math.pi/6 # angle in radians
#     magnetRing2.append(
#         magpy.magnet.Cylinder(
#             polarization=(0,0,1), dimension=(0.01, 0.005), 
#             position = (magnetRing2_r*np.cos(theta), magnetRing2_r*np.sin(theta), -0.02))
#         )
#     print(magnetRing2[-1].position)

# # floating magnets
# magnet5 = magpy.magnet.Cylinder(polarization=(0,0,1), dimension=(0.01, 0.005), position = (0, 0, 0.02), orientation = R.from_rotvec((0,45,0), degrees = True))
# # magnet6 = magpy.magnet.Cylinder(polarization=(0,0,1), dimension=(0.01, 0.005), position = (0, 0, 0.025))

# c = magpy.Collection(*magnetRing1)#, magnet5, magnet6)
# print('ring1', c.children,'\n')
# c.add(magpy.Collection(*magnetRing2)) # this creates a nested structure (it doesn't unwarap...)
# print('ring1&2', c.children,'\n')
# c.add(magnet5)
# print('ring1&2&floating',c.children,'\n')



# magnet2 = magpy.magnet.Cylinder(polarization=(0,0,1), dimension=(0.01, 0.005), position = (-0.03, 0, 0), orientation = R.from_rotvec((0,45,0), degrees = True))
# magnet1 = magpy.magnet.Cylinder(polarization=(0,0,1), dimension=(0.01, 0.005), position = (-0.03, 0, 0), orientation = R.from_rotvec((0,45,0), degrees = True))
# print(magnet1.position, magnet1.orientation.as_rotvec())
# magnet1.rotate_from_angax(angle = 180, axis = 'z', anchor = (0,0,0))
# print(magnet1.position, magnet1.orientation.as_rotvec())
# c = magpy.Collection(magnet1, magnet2)
# # magnet2 = magpy.magnet.Cylinder(polarization=(0,0,1), dimension=(0.01, 0.005), position = (0.03, 0, 0))
# # magnet3 = magpy.magnet.Cylinder(polarization=(0,0,1), dimension=(0.01, 0.005), position = (-0.03, 0, -0.02))
# # magnet4 = magpy.magnet.Cylinder(polarization=(0,0,1), dimension=(0.01, 0.005), position = (0.03, 0, -0.02))
# # magnet5 = magpy.magnet.Cylinder(polarization=(0,0,1), dimension=(0.01, 0.005), position = (0, 0, 0.02))
# # magnet6 = magpy.magnet.Cylinder(polarization=(0,0,1), dimension=(0.01, 0.005), position = (0, 0, 0.025))
# # c = magpy.Collection(magnet1, magnet2, magnet3, magnet4, magnet5, magnet6)
# # sensor = magpy.Sensor() #unnecessary? seems like an observer but can also just calc at any point...

# # magpy.show(magnet1, sensor, backend='plotly')


# magnetRing3 = magnetRing(0.06, 30, 0, 12)
# c = magnetRing3.mCol
# print(magnetRing3.mCol.children)

# points = [(0,0,-.01), (0,0,0), (0,0,.01)] # in SI Units (m)

# xs = np.linspace(-0.05,0.05,29)
# zs = np.linspace(-0.05,0.05,29)
# Bs = np.array([[c.getB([x,0,z]) for x in xs] for z in zs])
# X,Z = np.meshgrid(xs,zs)
# U,V = Bs[:,:,0], Bs[:,:,2]
# plt.streamplot(X, Z, U, V, color=np.log(U**2+V**2),density=2)
# plt.show()


# # B = magpy.getB(magnet1, points)

# # H = magpy.getH(magnet1, sensor)

# # print(H.round()) # -> [51017. 24210.     0.] # in SI Units (A/m)
# # import magpylib as magpy
# # import numpy as np
# # import plotly.graph_objects as go

# # # Magpylib field computation
# # loop = magpy.current.Circle(current=1, diameter=0.1)
# # sens = magpy.Sensor(position=np.linspace((0, 0, -0.1), (0, 0, 0.1), 100))
# # B = loop.getB(sens)

# # # Create Plotly figure and subplots
# # fig = go.Figure().set_subplots(
# #     rows=1, cols=2, specs=[[{"type": "xy"}, {"type": "scene"}]]
# # )

# # # 2D Plotly plot
# # fig.add_scatter(y=B[:, 2], name="Bz")

# # # Draw 3d model in the existing Plotly figure
# # magpy.show(loop, sens, canvas=fig, col=2, canvas_update=True)

# # # Add 3d scatter trace to main figure model
# # fig.add_scatter3d(x=(-0.1, 0.1), y=(0, 0), z=(0, 0), col=2, row=1)

# # # Render figure
# fig.show()