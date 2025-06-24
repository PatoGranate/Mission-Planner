To propagate a model over time, a propagator needs to be defined. For instance:
```python
from org.orekit.propagation.analytical import KeplerianPropagator
testpropagator = KeplerianPropagator(orbit)
```
This essentially takes the orbit defined previously and allows you to solve it for any given point in time after the initialized state. 
We can then take different points in time by doing:
```python
t0 = date
t1 = t0.shiftedBy(60.0)
```
For taking the current time/date you can do
```python
from datetime import datetime, timezone
today = datetime.now(timezone.utc)
```
And after this do:
```python
state = testpropagator.propagate(t1)
pv = state.getPVCoordinates()
pos = pv.getPosition()
```
Which gives the position of the satellite at t1 in global (x, y, z) coordinates, which are by default in EME2000. If we want ITRF, we can do:
```python
pv_itrf = state.getPVCoordinates(FramesFactory.getITRF(
    IERSConventions.IERS_2010, True))
```

These global coordinates can be changed into geodetic coordinates by changing the reference frame, which can be done using Orekit as follows (where inertial vector is a position vector using Vector3D from hipparchus):
```python

inertial = FramesFactory.getEME2000()
earth_fixed = FramesFactory.getITRF(IERSConventions.IERS_2010, True)
transformation = inertial.getTransformTo(earth_fixed, current_date)

rotation = transformation.getRotation()
ecef_vector = rotation.applyTo(inertial_vector)
ecef_poses[idx, :] = ecef_vector.getX(), 
					 ecef_vector.getY(), 
			         ecef_vector.getZ()
```
