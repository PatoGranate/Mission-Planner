import numpy as np
import itertools
from org.hipparchus.geometry.euclidean.threed import Vector3D
from scipy.spatial.transform import Rotation as R

_cross_cache = {}

# Compute distance between two points
def cross_sat(satA, satB, times, tolerance):
    # Find the key for the specific satellites and times being called
    key_parts = sorted([(id(satA), satA._version),
                        (id(satB), satB._version)])
    key = (key_parts[0], key_parts[1], times.tobytes())
    
    # If the key already exists 
    if key not in _cross_cache:
        ecefA = satA.get_ecef(times)
        ecefB = satB.get_ecef(times)
        
        difference = ecefB - ecefA
        cross_dist = np.linalg.norm(difference, axis = 1, keepdims = True)
    
        approach_times = np.where(cross_dist[:,0] < tolerance)[0]
    
        splits = np.where(np.diff(approach_times) > 1)[0] + 1
        blocks = np.split(approach_times, splits)
        
        runs = [(int(b[0]), int(b[-1]), len(b)) for b in blocks if b.size]
        _cross_cache[key] = (cross_dist, runs)
        
        
def get_cross_dist(satA, satB, times, tolerance):
    cross_sat(satA, satB, times, tolerance)
    key_parts = sorted([(id(satA), satA._version),
                        (id(satB), satB._version)])
    key = (key_parts[0], key_parts[1], times.tobytes())
    cross_sat(satA, satB, times, tolerance)
    return _cross_cache[key][0]

def get_runs(satA, satB, times, tolerance):
    cross_sat(satA, satB, times, tolerance)
    key_parts = sorted([(id(satA), satA._version),
                        (id(satB), satB._version)])
    key = (key_parts[0], key_parts[1], times.tobytes())
    cross_sat(satA, satB, times, tolerance)
    return _cross_cache[key][1]

def target_pointer(satA, satB, times, tolerance):
    runs = get_runs(satA, satB, times, tolerance)
    cross_dist = get_cross_dist(satA, satB, times, tolerance)
    
    closest_approach_dist = tolerance
    if len(runs) != 0:
        print(runs)
        closest_approach_time = runs[0][0]
        for i in range(runs[0][2]):
            current_dist = cross_dist[runs[0][0]+i]
            if current_dist < closest_approach_dist:
                closest_approach_dist = current_dist
                closest_approach_time = runs[0][0] + i
                
        eciA = satA.propagate(times)
        eciB = satB.propagate(times)
        
        observer_pos = eciA[closest_approach_time]
        target_pos = eciB[closest_approach_time]
        
        target_vector = Vector3D(float(target_pos[0] - observer_pos[0]),
                                 float(target_pos[1] - observer_pos[1]),
                                 float(target_pos[2] - observer_pos[2]))
        
        target_vector_mag = target_vector.getNorm()
        b3_unit = target_vector.scalarMultiply(1/target_vector_mag)
        
        vel = satA.get_vels(times)
        vec_vel = Vector3D(float(vel[closest_approach_time,0]),
                           float(vel[closest_approach_time,1]),
                           float(vel[closest_approach_time,2]))
        
        b1 = vec_vel.subtract(b3_unit.scalarMultiply(vec_vel.dotProduct(b3_unit)))
        b1_unit = b1.scalarMultiply(1/b1.getNorm())
        
        b2_unit = b3_unit.crossProduct(b1_unit)
        
        DCM_b2e = np.array([(b1_unit.x, b1_unit.y, b1_unit.z), 
                            (b2_unit.x, b2_unit.y, b2_unit.z), 
                            (b3_unit.x, b3_unit.y, b3_unit.z)])
        
        quat = R.from_matrix(DCM_b2e).as_quat()
        
        return quat