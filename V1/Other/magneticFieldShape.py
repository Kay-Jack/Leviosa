# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 07:21:12 2024

@author: Daniel
"""
import numpy as np
import math

class magnet:
    def __init__(self, 
                 position:np.array = np.zeros((3,)), 
                 dipole:np.array = np.zeros((3,))):
        self.position = position
        self.dipole = dipole

def magnetFieldApprox(ptPosition:np.array, myMagnet:magnet):
    u0 = 1.26e-6 #[N*A**-2], permeability of free space. 
    # Here as a technicallity (doesn't matter tbh as is constant)
    r = ptPosition - myMagnet.position
    r_mag = np.sqrt(np.dot(r, r)) # magnitude of r; dist. be/en position & magnet
    
    B = u0 / (4*math.pi) * (3*np.dot(myMagnet.dipole, r)*r/r_mag**3 - myMagnet.dipole/r_mag**3)
    return B

def totalMagneticFieldApprox(ptPosition:np.array(), myMagnets:list):
    if len(myMagnets) == 0:
        print('no magnets defined, returning 0')
        return 0
    totalB = np.zeros((3,))
    for myMagnet in myMagnets:
        totalB += magnetFieldApprox(ptPosition, myMagnet)
    return totalB

def main():
    # define magnets
    myMagnets = list()
    for pos in [np.array([1,1]), np.array(1,-1), np.array(-1,1), np.array(-1,-1)]:
        myMagnets.append(magnet(pos, np.array([0,0,1])))
    
    # define field to calculate over
    fieldMap = np.zeros((21, 21, 21, 3)) # x_idx, y_idx, z_idx, (x,y,z,Bx,By,Bz)
    #not efficient given repeated position info but oh well
    x_min = -2
    y_min = -2
    z_min = -2
    x_max = 2
    y_max = 2
    z_max = 2
    
    x_step = (x_max - x_min) / (fieldMap.shape[0]-1)
    y_step = (y_max - y_min) / (fieldMap.shape[0]-1)
    z_step = (z_max - z_min) / (fieldMap.shape[0]-1)
    for i, x_pos in enumerate(np.arange(x_min, x_max + x_step, x_step)):
        for j, y_pos in enumerate(np.arange(y_min, y_max + y_step, y_step)):
            for k, z_pos in enumerate(np.arange(z_min, z_max + z_step, z_step)):
                fieldMap[i, j, k]
    
#%%
if __name__ == '__main__':
    main()