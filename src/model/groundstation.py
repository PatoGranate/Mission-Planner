import numpy as np
from org.orekit.time import AbsoluteDate, TimeScalesFactory
from org.orekit.frames import FramesFactory
from org.orekit.utils import IERSConventions, Constants
from org.orekit.bodies import OneAxisEllipsoid, GeodeticPoint
from org.hipparchus.geometry.euclidean.threed import Vector3D
from org.orekit.utils import PVCoordinates

"""
Define frames of reference for the coordinate systems, and generate an
elliptical model for the Earth
"""
inertial = FramesFactory.getEME2000()
earth_fixed = FramesFactory.getITRF(IERSConventions.IERS_2010, True)

earth_ellipsoid = OneAxisEllipsoid(Constants.WGS84_EARTH_EQUATORIAL_RADIUS,
                                   Constants.WGS84_EARTH_FLATTENING,
                                   earth_fixed)

class GroundStation:
    def __init__(self, lat, lon, date, alt = 0, label = "no label"):
        """
        Initialization function for the GroundStation class

        Parameters
        ----------
        lat : int
            Latitude of ground station (deg)
        lon : int
            Longitude of ground station (deg)
        date : array
            [year, month, day, hour, minute, second]
        alt = 0 : int
            Altitude of ground station (default 0 - on Earth surface, km)
        label = "(no label)" : str
            Name of ground station
            
        Returns
        -------
        """
        self.lat = float(np.deg2rad(lat))
        self.lon = float(np.deg2rad(lon))
        self.alt = alt
        
        geo = GeodeticPoint(self.lat, self.lon, self.alt)
        pos_ecef = earth_ellipsoid.transform(geo)
        self.pv_ecef = PVCoordinates(pos_ecef, Vector3D.ZERO)
        self.ecef_pos = self.pv_ecef.getPosition()
        
        self.date = date
        utc = TimeScalesFactory.getUTC()
        epoch = AbsoluteDate(date[0], date[1], date[2], date[3], date[4], date[5], utc)
        self.epoch = epoch
        
        self.label = label
        
        self._cache_times = None
        self._cache_ecimov = None
    
    def update_gs(self, lat = None, lon = None, date = None, alt = None, label = None):
        """
        Updates ground station parameters

        Parameters
        ----------
        lat = None : int
            Latitude of ground station (deg)
        lon = None : int
            Longitude of ground station (deg)
        date = None : array
            [year, month, day, hour, minute, second]
        alt = None : int
            Altitude of ground station (default 0 - on Earth surface, km)
        label = None : str
            Name of ground station
            
        Returns
        -------
        """
        changed = False
        # Check if any parameters have been updated
        if lat is not None and lat != self.lat:
            self.lat = lat
            changed = True
        if lon is not None and lon != self.lon:
            self.lon = lon
            changed = True
        if alt is not None and alt != self.alt:
            self.alt = alt
            changed = True
        if date is not None and date != self.date:
            self.date = date
            changed = True
        if label is not None and label != self.label:
            self.label = label
            
        if not changed:
            return
           
        # Re-define self.orbit
        self.__init__(self.lat, self.lon, self.date, self.alt, self.label)
        
    def eci_at_epoch(self):
        """
        Computes earth centered inertial frame of reference position of gs
        
        Parameters
        ----------
        
        Returns
        -------
        pv_eci.getPosition() : Vector3D
            3-dimensional position vector
        """
        # Create a geodetic point in orekit
        tf = earth_fixed.getTransformTo(inertial, self.epoch)
        pv_eci = tf.transformPVCoordinates(self.pv_ecef)
        
        return pv_eci.getPosition()
        
    def _update_pos(self, times):
        """
        Computes ECI position of ground station over time

        Parameters
        ----------
        times : np.array
            Array of timesteps (s)
            
        Returns
        -------
        None.
        """
        if (self._cache_ecimov is None 
        or not np.array_equal(times, self._cache_times)):
            
            self._cache_times = times.copy()
            eci_movement = np.zeros((len(times), 3))
            for idx, time_offset in enumerate(times):
                current_date = self.epoch.shiftedBy(float(time_offset))
                tf = earth_fixed.getTransformTo(inertial, current_date)
                pv_eci = tf.transformPVCoordinates(self.pv_ecef).getPosition()
                eci_movement[idx, :] = pv_eci.getX(), pv_eci.getY(), pv_eci.getZ()
            self._cache_ecimov = eci_movement
    
    def get_ecipos(self, times):
        """
        Retrieves positions over time for ground station from cache

        Parameters
        ----------
        times : np.array
            Array of timesteps (s)

        Returns
        -------
        self._cache_ecimov : np.array
            Array of 3D position vectors over time
        """
        self._update_pos(times)
        return self._cache_ecimov