# Initialise virtual machine so that orekit commands work
import orekit
orekit.initVM()

# Allows machine to search for orekit-data.zip within current directory
from orekit.pyhelpers import setup_orekit_curdir
setup_orekit_curdir()

# Imports
import numpy as np
import matplotlib.pyplot as plt
from org.orekit.time import AbsoluteDate, TimeScalesFactory
from satellite import Satellite
from satellite_utils import cross_sat, get_cross_dist, get_runs, target_pointer

# Define a common epoch and time range
utc = TimeScalesFactory.getUTC()
common_epoch = AbsoluteDate(2020, 1, 1, 0, 0, 0.0, utc)
duration = 140000
timestep = 60
times = np.arange(0, duration, timestep)


# Satellite(s) params
a1 = 7e6
e1 = float(0.00)
i1 = float(np.deg2rad(60))
omega1 = float(np.deg2rad(10))
raan1 = float(np.deg2rad(40))
anomaly1 = float(np.deg2rad(85))
anomaly_type1 = "TRUE"

a2 = 7.5e6
e2 = float(0.05)
i2 = float(np.deg2rad(60))
omega2 = float(np.deg2rad(30))
raan2 = float(np.deg2rad(60))
anomaly2 = float(np.deg2rad(175))
anomaly_type2 = "TRUE"


# Build Sat(s) and find trajectory(/ies) and gtc(s)
sat1 = Satellite(a1, e1, i1, omega1, raan1, anomaly1, common_epoch, anomaly_type1)
sat2 = Satellite(a2, e2, i2, omega2, raan2, anomaly2, common_epoch, anomaly_type2)

trajectory1 = sat1.propagate(times)
trajectory2 = sat2.propagate(times)

lonlat1 = sat1.get_gtc(times)
lonlat2 = sat2.get_gtc(times)

# Generate sphere to represent Earth
R_earth = 6.378e6
n_lon = 60
n_lat = 30

longitudes = np.linspace(0, 2*np.pi, n_lon)
latitudes = np.linspace(0, np.pi, n_lat)
lon_grid, lat_grid = np.meshgrid(longitudes, latitudes)

X = R_earth * np.sin(lat_grid) * np.cos(lon_grid)
Y = R_earth * np.sin(lat_grid) * np.sin(lon_grid)
Z = R_earth * np.cos(lat_grid)


# Create figure and plot Earth + Satellites in 3D
fig1 = plt.figure()
grid = fig1.add_gridspec(1, 2, width_ratios = [1, 2])

ax1_1 = fig1.add_subplot(grid[0], projection='3d')
ax1_1.plot_wireframe(X, Y, Z, color='black', alpha=0.5, linewidth=0.5)

ax1_1.plot(trajectory1[:,0], trajectory1[:,1], trajectory1[:,2], color='red', linewidth=2, label = 'Sat1')
ax1_1.plot(trajectory2[:,0], trajectory2[:,1], trajectory2[:,2], color='blue', linewidth=2, label = 'Sat2')

"""ESTO HABRÁ QUE CAMBIARLO POR QUE AHORA MISMO SI TIENES UN SAT2
CON UN SEMI MAJOR AXIS MUCHO MÁS GRANDE QUE SAT1, ACABAS CON SAT2 FUERA
DEL FIGURE POR QUE ESTÁS FITTING LAS DIMS DE LOS EJES CON LAS DIMENSIONES
DE LA TRAYECTORIA DE SAT1. HABRÍA QUE HACER ALGÚN CHEQUEO DE CUAL ES EL MÁS
GRANDE Y EN BASE A ESO DEFINIR LOS LIMITES DEL FIGURE"""
# Formatting
ax1_1.set_box_aspect([1, 1, 1])
max_extent = max(abs(trajectory1[:,0]).max(), abs(trajectory1[:,1]).max(), abs(trajectory1[:,2]).max()) * 1.1
ax1_1.set_xlim([-max_extent, max_extent])
ax1_1.set_ylim([-max_extent, max_extent])
ax1_1.set_zlim([-max_extent, max_extent])
ax1_1.legend()
ax1_1.set_xlabel('x-Pos (m)')
ax1_1.set_ylabel('y-Pos (m)')
ax1_1.set_zlabel('z-Pos (m)')
# Plot ground tracks
ax1_2 = fig1.add_subplot(grid[1])
earth_map = plt.imread('earth_outline.png')
ax1_2.imshow(earth_map, extent=[-180, 180, -90, 90], origin='upper', aspect='equal')

ax1_2.plot(lonlat1[:,0], lonlat1[:,1], color = 'red')
ax1_2.plot(lonlat2[:,0], lonlat2[:,1], color = 'blue')

ax1_2.set_xlim([-180, 180])
ax1_2.set_ylim([-90, 90])
ax1_2.set_xticks(np.arange(-180, 181, 60.0))
ax1_2.set_yticks(np.arange(-90, 91, 30))
ax1_2.set_xlabel('Longitude (°)')
ax1_2.set_ylabel('Latitude (°)')

# Plot variation in cross distance between satellites
global_tolerance = 3000000
cross_dist = get_cross_dist(sat1, sat2, times, global_tolerance)

fig2 = plt.figure()
ax2_1 = fig2.add_subplot(111)
ax2_1.plot(times, cross_dist)
ax2_1.axhline(y = global_tolerance, color = 'r', linestyle = '--')
ax2_1.set_xlabel('Time elapsed (s)')
ax2_1.set_ylabel('Cross-sat distance (m)')
ax2_1.set_xlim([0, max(times)+1])
ax2_1.set_ylim(bottom = 0)



quats = Satellite.get_quats(sat1, times)
target_pointer(sat1, sat2, times, global_tolerance)
