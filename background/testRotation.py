import numpy as np
import magpylib as magpy
from scipy.spatial.transform import Rotation as R

# Parameters
MAGNET_D = 10  # mm
MAGNET_H = 5   # mm

magnetization = 1.6e6
nominal_angle = 20          # degrees
angular_std = 3             # degrees

# Monte Carlo orientation
tilt = np.random.normal(0, angular_std)
phi = np.random.uniform(0, 2*np.pi)

var1 = tilt * np.cos(phi)
var2 = 0
var3 = tilt * np.sin(phi)

# orientation = R.from_rotvec(
#     (var1, nominal_angle + var2, var3),
#     degrees=True
# )
orientation = R.from_rotvec(
    (
        0, # rotates about x axis
        45, # rotates about y axis
        90, # rotates about z axis # DO NOT USE THIS ONE. is confusing
    ),
    degrees=True
)

# Create magnet
magnet = magpy.magnet.Cylinder(
    magnetization=(0, 0, magnetization),
    dimension=(MAGNET_D, MAGNET_H),
    position=(0, 0, 0),
    orientation=orientation,
)

# Visualize
magpy.show(magnet, backend="matplotlib")