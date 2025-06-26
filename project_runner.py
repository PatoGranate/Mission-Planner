# Initialise virtual machine so that orekit commands work
import orekit
orekit.initVM()

# Allows machine to search for orekit-data.zip within current directory
from orekit.pyhelpers import setup_orekit_curdir
setup_orekit_curdir()

# Imports
import numpy as np
from org.orekit.time import AbsoluteDate, TimeScalesFactory
from satellite import Satellite
import satellite_utils
import visualization

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
anomaly1 = float(np.deg2rad(160))
anomaly_type1 = "TRUE"

a2 = 7.5e6
e2 = float(0.05)
i2 = float(np.deg2rad(60))
omega2 = float(np.deg2rad(30))
raan2 = float(np.deg2rad(60))
anomaly2 = float(np.deg2rad(175))
anomaly_type2 = "TRUE"

a3 = 7.5e6
e3 = float(0.05)
i3 = float(np.deg2rad(30))
omega3 = float(np.deg2rad(30))
raan3 = float(np.deg2rad(60))
anomaly3 = float(np.deg2rad(175))
anomaly_type3 = "TRUE"

# Build Sat(s) and find trajectory(/ies) and gtc(s)
sat1 = Satellite(a1, e1, i1, omega1, raan1, anomaly1, common_epoch, anomaly_type1, label = "Sat 1")
sat2 = Satellite(a2, e2, i2, omega2, raan2, anomaly2, common_epoch, anomaly_type2, label = "Sat 2")
sat3 = Satellite(a3, e3, i3, omega3, raan3, anomaly3, common_epoch, anomaly_type3, label = "Sat 3")

# Plot variation in cross distance between satellites
global_tolerance = 3000000

#visualization.plot_ground_tracks([sat1, sat2], times)
#visualization.plot_orbits([sat1, sat2], times)
visualization.plot_cross_sat([sat1, sat2, sat3], times, global_tolerance)

#quats = Satellite.get_quats(sat1, times)
#satellite_utils.target_pointer(sat1, sat2, times, global_tolerance)
visualization.animate_sat_attitude([sat1, sat2, sat3], times, global_tolerance)