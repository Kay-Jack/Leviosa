magnetization=(0, 0, MAGNETIZATION/1.175),
        dimension=(MAGNET_D, MAGNET_H),
        position=(x_eq, 0, z_eq + MAGNET_H/2)
    )
    penMagnet1.meshing = 15
    penMagnet2 = penMagnet1.copy(deep=True)
    penMagnet2.position = (posX, 0, posZ + 3*MAGNET_H/2)

    # define COM (before rotation, relative to bottom of lower magnet)
    penCM = np.array([posX, 0, posZ + 28e-3])

    # rotate about anchor at (posX,0,posZ)
    anchor = np.array([posX, 0, posZ])
    penMagnet1.rotate_from_angax(angle=angle_eq, axis='y', anchor=anchor, degrees=True)
    penMagnet2.rotate_from_angax(angle=a