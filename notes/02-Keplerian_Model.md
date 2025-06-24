The Keplerian Model uses Kepler's laws of motion and their Keplerian elements to propagate a satellite's orbit through time and space. 

When programming Keplerian orbits in python, the following command is used: 
```python
from org.orekit.orbits import KeplerianOrbit, PositionAngleType
from org.orekit.frames import FramesFactory
from org.orekit.time   import AbsoluteDate, TimeScalesFactory
from org.orekit.utils  import Constants

utc = TimeScalesFactory.getUTC()
date = AbsoluteDate(2020, 6, 20, 12, 12, 12.0, utc)

orbit = KeplerianOrbit(
    7000000.0,                  # 1. a: semi-major axis [m]
    0.001,                      # 2. e: eccentricity
    0.1,                        # 3. i: inclination [rad]
    0.5,                        # 4. ω: argument of perigee [rad]
    1.0,                        # 5. Ω: RAAN [rad]
    0.0,                        # 6. ν: true anomaly [rad]
    PositionAngleType.TRUE,     # 7. Type of anomaly
    FramesFactory.getEME2000(), # 8. Inertial frame
    date,                       # 9. Epoch (today, in UTC)
    Constants.WGS84_EARTH_MU    # 10. Gravitational parameter
)
``` 

The 7th argument determines the type of anomaly that is being given in the 6th (TRUE, ECCENTRIC, or MEAN). The 8th argument gives the inertial frame used, which essentially describes the 3D space that the orbit is being propagated within. 
Take the example of a satellite orbiting earth. EME2000 is one type of inertial frame, that takes the earth as the centre of reference, and does not include rotation in the 3D space. i.e. if you wanted to animate it, you would have to manually animate the earth's rotation, and the satellite's track would be closed and repeating periodically. On the other hand, an alternative ITRF frame could be used, which keeps the earth still (no rotation) and makes the orbit be open and non-repeating (i.e. the orbit goes through different points in the 3D space in each rotation, since the space is rotating with time). Typically, for animation purposes we want to use EME2000, since it's more intuitive to visualize, and we can manually convert to ITRF if needed for things like plotting ground tracks.

The 9th argument takes the epoch to be the exact moment in time in which the simulation is being run, and the 10th argument takes the value of mu (= MG) directly from WGS84.

In order to do anything useful with this model, we want to [[03-Propagation and Transformations|propagate the orbit over time]]
.