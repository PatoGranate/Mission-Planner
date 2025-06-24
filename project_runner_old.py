import matplotlib.pyplot as plt
import orekit
# Initialise virtual machine so that orekit commands work
orekit.initVM()

from orekit.pyhelpers import setup_orekit_curdir
# Allows machine to search for orekit-data.zip within current directory
setup_orekit_curdir()

# Import the Satellite class from satellite.py and libraries for epoch
from satellite import Satellite
from org.orekit.time import AbsoluteDate, TimeScalesFactory

"""
Define a common Epoch for all of the satellites. This will need to be changed 
so that this is a user input
"""
utc = TimeScalesFactory.getUTC()
common_epoch = AbsoluteDate(2020, 1, 1, 0, 0, 0.0, utc)

"""
The following lines determine the time over which the simulation is going to
be run. This will change depending on user inputs, so requires adapting to the
GUI when this is implemented.
"""
import numpy as np
duration = 7000
timestep = 60
times = np.arange(0, duration, timestep)


# Lets define a first, test satellite:
a1 = 7e6
e1 = float(0.0)
i1 = float(np.deg2rad(60))
omega1 = float(np.deg2rad(0))
raan1 = float(np.deg2rad(0))
anomaly1 = float(np.deg2rad(0))
anomaly_type1 = "TRUE" # This has to be either TRUE, MEAN, or ECCENTRIC

# Build a Satellite for the parameters above
sat1 = Satellite(a1, e1, i1, omega1, raan1, anomaly1, common_epoch, anomaly_type1)

# Find its trajectory
trajectory1 = sat1.propagate(times)

xs1, ys1, zs1 = trajectory1[:, 0], trajectory1[:, 1], trajectory1[:, 2]

R_earth = 6.378e6
n_lon = 60
n_lat = 30

longitudes = np.linspace(0, 2*np.pi, n_lon)
latitudes = np.linspace(0, np.pi, n_lat)

lon_grid, lat_grid = np.meshgrid(longitudes, latitudes)

X = R_earth * np.sin(lat_grid) * np.cos(lon_grid)
Y = R_earth * np.sin(lat_grid) * np.sin(lon_grid)
Z = R_earth * np.cos(lat_grid)

fig = plt.figure()

ax1 = fig.add_subplot(111, projection='3d')
ax1.plot_wireframe(X, Y, Z, color='blue', alpha=0.5, linewidth=0.5)
ax1.plot(xs1, ys1, zs1, color='red', linewidth=2)
ax1.set_box_aspect([1, 1, 1])
# Get the maximum extent in any direction
max_extent = max(abs(xs1).max(), abs(ys1).max(), abs(zs1).max()) * 1.1

ax1.set_xlim([-max_extent, max_extent])
ax1.set_ylim([-max_extent, max_extent])
ax1.set_zlim([-max_extent, max_extent])
"""
ax1.plot_surface(X, Y, Z, color = 'lightgray', linewidth = 0, 
                rstride = 1, cstride = 1, shade = True)


ax1.scatter(xs1, ys1, zs1, marker = 'o', color = 'red', s = 2, 
           depthshade = True, label = 'sat1')
"""
plt.show()
