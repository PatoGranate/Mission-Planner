import numpy as np
from org.orekit.orbits import KeplerianOrbit, PositionAngleType
from org.orekit.frames import FramesFactory
from org.orekit.utils import Constants, IERSConventions
from org.orekit.propagation.analytical import KeplerianPropagator
from org.orekit.bodies import OneAxisEllipsoid
from org.hipparchus.geometry.euclidean.threed import Vector3D

"""
Define frames of reference for the coordinate systems, and generate an
elliptical model for the Earth
"""
inertial = FramesFactory.getEME2000()
earth_fixed = FramesFactory.getITRF(IERSConventions.IERS_2010, True)

earth_ellipsoid = OneAxisEllipsoid(Constants.WGS84_EARTH_EQUATORIAL_RADIUS,
                                   Constants.WGS84_EARTH_FLATTENING,
                                   earth_fixed)
"""
Define a Satellite class, in which we can create satellites and run their
orbits and propagators.
"""
class Satellite:
    def __init__(self, a, e, i, omega, raan, anomaly, epoch, anomaly_type):
        self.a, self.e, self.i = a, e, i
        self.omega, self.raan, self.anomaly = omega, raan, anomaly
        self.anomaly_type = anomaly_type
        self.epoch = epoch
        
        # KeplarianOrbit is defined once per satellite class and then re-used
        self.orbit = KeplerianOrbit(self.a, self.e, self.i, 
                                    self.omega, self.raan, self.anomaly, 
                                    PositionAngleType.valueOf(self.anomaly_type),
                                    inertial, self.epoch, 
                                    Constants.WGS84_EARTH_MU)
        
        # The same is done for KeplerianPropagator
        self.propagator = KeplerianPropagator(self.orbit)
        
        # Find initial position and velocity for orientation
        state_init = self.orbit.getPVCoordinates(epoch, inertial)
        self.pos_init = state_init.getPosition()
        self.vel_init = state_init.getVelocity()

        
        # Initialize caches to empty
        self._cache_times = None
        self._cache_poses = None
        self._cache_ecef = None
        self._cache_lla = None
        self._cache_gtc = None
        
        # This will be changed later if updated, useful for keys
        self._version = 0
       
    # Update changes in orbital parameters
    def update_orbit(self, *, a = None, e = None, i = None, omega = None, 
                     raan = None, anomaly = None, anomaly_type = None):
        changed = False
        # Check if any parameters have been updated
        if a is not None and a != self.a:
            self.a = a
            changed = True
        if e is not None and e != self.e:
            self.e = e
            changed = True
        if i is not None and i != self.i:
            self.i = i
            changed = True
        if omega is not None and omega != self.omega:
            self.omega = omega
            changed = True
        if raan is not None and raan != self.raan:
            self.raan = raan
            changed = True
        if anomaly is not None and anomaly != self.anomaly:
            self.anomaly = anomaly
            changed = True
        if anomaly_type is not None and anomaly_type != self.anomaly_type:
            self.anomaly_type = anomaly_type
            changed = True
            
        if not changed:
            return
           
        # Re-define self.orbit
        self.orbit = KeplerianOrbit(self.a, self.e, self.i, 
                                    self.omega, self.raan, self.anomaly, 
                                    PositionAngleType.valueOf(self.anomaly_type),
                                    inertial, self.epoch, 
                                    Constants.WGS84_EARTH_MU)
        
        # The same is done for KeplerianPropagator
        self.propagator = KeplerianPropagator(self.orbit)
        
        # Change caches to empty
        self._cache_times = None
        self._cache_poses = None
        self._cache_ecef = None
        self._cache_lla = None
        self._cache_gtc = None
        
        self._version += 1
        
    # Define a method that will propagate over time
    def propagate(self, times):
        # If we have not yet run propagate or the time input has changed:
        if (self._cache_times is None 
            or not np.array_equal(times, self._cache_times)):
            
            # Cache the new times input
            self._cache_times = times.copy()
        
            # Generate an empty matrix to store positions over time
            poses = np.zeros((len(times), 3))
            
            for idx, elapsed in enumerate(times):
                # Find the positions of the satellite at each timestep and add
                # each position vector as an entry in the poses matrix
                current_state = self.propagator.propagate(self.epoch.shiftedBy(float(elapsed)))
                current_pos = current_state.getPVCoordinates().getPosition()
                poses[idx, :] = current_pos.getX(), current_pos.getY(), current_pos.getZ()
              
            # Cache poses and invalidate down-the-line previously cached vars
            self._cache_poses = poses
            self._cache_ecef = None
            self._cache_lla = None
            self._cache_gtc = None
        
        return self._cache_poses

    def glob_to_cart(self, poses, times):
        # Generate an empty matrix to store positions over time
        ecef_poses = np.zeros((len(times), 3))
        lla_poses = np.zeros((len(times), 3))
        
        for idx, (time_offset, inertial_xyz) in enumerate(zip(times, poses)):
            # Change from EME2000() to ECEF positions which consider Earth's
            # rotation, so that ground tracks can be extracted
            current_date = self.epoch.shiftedBy(float(time_offset))
            transformation = inertial.getTransformTo(earth_fixed, current_date)
            inertial_vector = Vector3D(float(inertial_xyz[0]), 
                                       float(inertial_xyz[1]), 
                                       float(inertial_xyz[2]))
            rotation = transformation.getRotation()
            ecef_vector = rotation.applyTo(inertial_vector)
            ecef_poses[idx, :] = ecef_vector.getX(), ecef_vector.getY(), ecef_vector.getZ()
            
            # With Earth Centered coordinates, cartesian coordinates can be
            # computed for each Satellite.
            geo_transformation = earth_ellipsoid.transform(ecef_vector,
                                                           earth_fixed,
                                                           self.epoch.shiftedBy(float(time_offset)))
            lla_poses[idx,:] = (np.rad2deg(geo_transformation.getLatitude()),
                                np.rad2deg(geo_transformation.getLongitude()),
                                geo_transformation.getAltitude())
        return ecef_poses, lla_poses
   
    def _ensure_converted(self, times):
        poses = self.propagate(times)
        # If no cache for ecef or lla, compute new ones
        if self._cache_ecef is None or self._cache_lla is None:
            ecef, lla = self.glob_to_cart(poses, times)
            self._cache_ecef = ecef
            self._cache_lla = lla
            self._cache_gtc = None
   
    def get_ecef(self, times):
        self._ensure_converted(times)
        return self._cache_ecef
         
    def get_lla(self, times):
        self._ensure_converted(times)
        return self._cache_lla
        
    def get_gtc(self, times):
        _ = self.get_lla(times)
        
        # If gtc has not been previously computed, find gtc
        if self._cache_gtc is None:
            lla = self.get_lla(times)
            lon_dif = np.diff(lla[:,1])
            breaks = np.where(np.abs(lon_dif) > 180)[0] + 1
            
            lon_plot = lla[:,1].copy()
            lat_plot = lla[:,0].copy()
            
            # Make a new array of positions with the ground track positions
            # which add breaks between large steps in longitudes to avoid
            # horizontal lines in the ground tracks
            for idx in reversed(breaks):
                lon_plot = np.insert(lon_plot, idx, np.nan)
                lat_plot = np.insert(lat_plot, idx, np.nan)
                
            gtc =  np.column_stack([lon_plot, lat_plot])
            
            self._cache_gtc = gtc
        
        return self._cache_gtc
            
    # Define initial pointing for Satellite based on trajectory and anomaly
    def initial_pointing(self):
        # Calculate the unit vector nadir pointing at t = 0
        r0 = self.pos_init
        r0_mag = r0.getNorm()
        b3_unit = r0.scalarMultiply(1/r0_mag)
        
        # Calculate the unit vector pointing in direction of motion
        v0 = self.vel_init
        b1 = v0.subtract(b3_unit.scalarMultiply(v0.dotProduct(b3_unit)))
        b1_unit = b1.scalarMultiply(1/b1.getNorm())
        
        # Calculate remaining third vector
        b2_unit = b3_unit.crossProduct(b1_unit)
        
        print(b2_unit)
        
#%cd "C:/Users/pelay/OneDrive - University of Bath/Experiences/SuperSharp/Project"