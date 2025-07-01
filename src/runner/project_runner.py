# Initialise virtual machine so that orekit commands work
import orekit
orekit.initVM()

# Allows machine to search for orekit-data.zip within current directory
from orekit.pyhelpers import setup_orekit_curdir
from pathlib import Path

# point to your data folder:
data_dir = Path(__file__).parent.parent.parent / "data" / "orekit-data-master"
setup_orekit_curdir(str(data_dir))

# Imports
import numpy as np

from src.model.satellite import Satellite
import src.model.satellite_utils as satellite_utils
import src.model.visualization as visualization

# Define a common epoch and time range

year = 2020
month = 1
day = 1
hour = 0
minute = 0
second = 0.0

date = [year, month, day, hour, minute, second]


duration = 140000
timestep = 60
times = satellite_utils.get_times(duration, timestep)
# Satellite(s) params
a1 = 7e6
e1 = float(0.00)
i1 = float(60)
omega1 = float(10)
raan1 = float(40)
anomaly1 = float(160)
anomaly_type1 = "TRUE"

a2 = 7.5e6
e2 = float(0.05)
i2 = float(60)
omega2 = float(30)
raan2 = float(60)
anomaly2 = float(175)
anomaly_type2 = "TRUE"

a3 = 7.5e6
e3 = float(0.05)
i3 = float(30)
omega3 = float(45)
raan3 = float(90)
anomaly3 = float(15)
anomaly_type3 = "TRUE"

# Build Sat(s) and find trajectory(/ies) and gtc(s)
sat1 = Satellite(a1, e1, i1, omega1, raan1, anomaly1, date, anomaly_type1, label = "Sat 1")
sat2 = Satellite(a2, e2, i2, omega2, raan2, anomaly2, date, anomaly_type2, label = "Sat 2")
sat3 = Satellite(a3, e3, i3, omega3, raan3, anomaly3, date, anomaly_type3, label = "Sat 3")

# Plot variation in cross distance between satellites
global_tolerance = 3000000

visualization.plot_ground_tracks([sat1, sat2], times)
#visualization.plot_orbits([sat1, sat2], times)
visualization.plot_cross_sat([sat1, sat2, sat3], times, global_tolerance)

#quats = Satellite.get_quats(sat1, times)
#satellite_utils.target_pointer(sat1, sat2, times, global_tolerance)
anim = visualization.animate_sat_attitude([sat1, sat2, sat3], times, global_tolerance)