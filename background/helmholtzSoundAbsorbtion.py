import math

# f=2/πc*sqrt(​A/ (VL) ​)

# Constants
c = 343  # speed of sound in m/s
f = 5000  # target frequency in Hz
A = math.pi * (1e-3)**2 # mm, area of opening
V = (1e-2)**3  # volume of the cavity in m^3

# Calculate neck length (L)
L = (c / (2 * math.pi)) * math.sqrt(A / (V * f**2))
print("Neck length (L):", L, "m")
print("Neck length (L):", L/1000, "mm")

# to absrob over range of freq, use tapered neck & use longer neck or larger opening