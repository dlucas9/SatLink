import numpy as np
from numpy import log as ln
from models.spec_att import specific_attenuation
from sat import satellite
from GrStat import ground_station


# INPUT VARIABLES

site_lat = -3.7
site_long = -45.9
sat_long = -70
f = 3.5
tau = 90 #H=0, V = 90, circ = 45
hS = 0.447 #ground station height
ant_diam = 1.2
p = 0.01

station = ground_station(site_lat, site_long, ant_diam)
# first step - determine R0,01

R001 = station.get_R001()

# second step - calculate the effective rain height hR

hR = station.get_hR()

# third step - calculate the slant path in rain LS
# hs - ground station height
# E - elevation angle

sat = satellite(sat_long, f)
E = sat.get_elevation(site_lat, site_long)
LS = (hR - hS) / np.sin(np.radians(E))

# fourth step - calculate the horizontal projection (LG) of the slant path

LG = LS * np.cos(np.radians(E))

# fifth step - calculate the specific attenuation gamaR
# this is done through the specific_attenuation class (ref. ITU P.838-3)

gamaR = specific_attenuation().get_gamaR(R001, f, E, tau)

# sixth step - calculate the horizontal reduction factor r001

r001 = (1 + 0.078 * np.sqrt(LG * gamaR / f) - 0.38 * (1 - np.exp(-2 * LG))) ** (-1)

# seventh step - calculate the vertical adjustment factor v001
# to obtain v001, it is necessary to calculate other variables - zeta, LR and chi

# zeta (degrees)
zeta = np.tan(np.radians((hR - hS) / (LG * r001))) ** (-1)

# LR (km)
if zeta > E:
    LR = LG * r001 / np.cos(np.radians(E))
else:
    LR = (hR - hS) / np.sin(np.radians(E))
# chi
if abs(site_lat) < 36:
    chi = 36 - abs(site_lat)
else:
    chi = 0

v001 = (1 + np.sqrt(np.sin(np.radians(E))) * (
            31 * (1 - np.exp(-E / (1 + chi))) * (np.sqrt(LR * gamaR) / f ** 2) - 0.45)) ** (-1)

# eighth step - calculate the path distance LE (km)

LE = LR * v001

# ninth step - finally, the attenuation exceeded for 0.01% of the annual average A001

A001 = gamaR * LE

# CONVERSION TO OTHER RAIN PROBABILITY VALUES p BEYOND 0.01% (less than 5%)

if p > 0.0001:
    # determination of beta

    if p >= 0.01 or abs(site_lat) > 36:
        beta = 0
    elif p <= 0.01 and abs(site_lat) < 36 and E > 25:
        beta = -0.005 * (abs(site_lat) - 36)
    else:
        beta = -0.005 * (abs(site_lat) - 36) + 1.8 - 4.25 * np.sin(np.radians(E))

    # converting the A001 value to the Ap value for a different p

    Ap = A001 * (p / 0.01) ** -(0.655 + 0.033 * ln(p) - 0.045 * ln(A001) - beta * (1 - p) * np.sin(np.radians(E)))

else:

    Ap = A001
print('E ', E)
print('hR ', hR)
print('LS ', LS)
print('LG ', LG)
print('zeta ', zeta)
print('chi ', chi)
print('gamaR ', gamaR)
print('r001 ', r001)
print('vv001 ', v001)
print('LE ', LE)
print('AP ', Ap)
print('A001 ', A001)

