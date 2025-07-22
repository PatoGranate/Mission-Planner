import numpy as np
from org.hipparchus.geometry.euclidean.threed import Vector3D
from scipy.spatial.transform import Rotation as R, Slerp
from src.model.satellite import Satellite

_cross_cache = {}
_slew_cache = {}
_gs_sat_cache = {}

# Generate times array
def get_times(duration, timestep):
    """
    Generate times array
    
    Parameters
    ----------
    duration : int
        Duration in seconds of simulation
    timestep : int
        Difference in numerical integration

    Returns
    -------
    times : np.array
        Numerical array of times
    """
    times = np.arange(0, duration, timestep)
    return times

# Compute distance between two points
def cross_sat(satA, satB, times, tolerance):
    """
    Compute the distance bewteen two satellites as they move through time
    and find the times when they are within direct line of sight of eachother
    
    Parameters
    ----------
    satA : satellite.Satellite
        First satellite considered
    satB : satellite.Satellite 
        Second satellite considered
    times : np.array
        Array of timesteps (s)
    tolerance : int
        Maxmium distance for visibility (m)
    
    Returns
    -------
    """
    # Find the key for the specific satellites and times being called
    key_parts = sorted([(id(satA), satA._version),
                        (id(satB), satB._version)])
    key = (key_parts[0], key_parts[1], times.tobytes())
    
    # If the key already exists 
    if key not in _cross_cache:
        ecefA = satA.get_ecef(times)
        ecefB = satB.get_ecef(times)
        
        # Take the vectors between A and B and find their magnitudes (distance)
        vecAB = ecefB - ecefA
        cross_dist = np.linalg.norm(vecAB, axis = 1)
        
        # Create a boolean mask where True when distance less than tolerance
        mask_prox = (cross_dist <= tolerance)
        
        # Compute the value of t* - see documentation
        rAd = np.sum(ecefA * vecAB, axis = 1)
        dd = np.sum(vecAB * vecAB, axis = 1)
        tstar = -rAd/dd
        
        # Inside the vector if 0 <= t* <= 1, outside else
        inside = (tstar >= 0) & (tstar <= 1)
        outside = ~inside
        
        # Create a Line of Sight boolean mask of the same size as proximity
        mask_los = np.zeros_like(mask_prox)
        
        # If outisde and proximity are both true then LOS = True
        mask_los[outside & mask_prox] = True
        
        # Find the point along the vector for the given t*
        vecAB = ecefA + vecAB * tstar.reshape(-1, 1)
        earth_r = 6371
        
        # If inside and proximity, check whether earth in the way
        mask_los[inside & mask_prox] = (cross_dist[inside & mask_prox] > earth_r)
        
        # idx where LOS is true, generate splits array telling us where to split
        idx = np.where(mask_los)[0]
        splits = np.where(np.diff(idx)>1)[0] + 1
        
        # Split the indexes into blocks
        blocks = np.split(idx, splits)
        
        # Put start and end times into runs
        runs = [(int(b[0]), int(b[-1])) for b in blocks if b.size]
        
        # Insert all into the cache
        _cross_cache[key] = (cross_dist, runs)
        

def get_cross_dist(satA, satB, times, tolerance):
    """
    Retrieve distance array from cross-satellite computations
    
    Parameters
    ----------
    satA : satellite.Satellite
        First satellite considered
    satB : satellite.Satellite 
        Second satellite considered
    times : np.array
        Array of timesteps (s)
    tolerance : int
        Maxmium distance for visibility (m)
    
    Returns
    -------
    _cross_cache[key][0] : array
        Distance between both satellites across time (m)
    """
    cross_sat(satA, satB, times, tolerance)
    key_parts = sorted([(id(satA), satA._version),
                        (id(satB), satB._version)])
    key = (key_parts[0], key_parts[1], times.tobytes())
    cross_sat(satA, satB, times, tolerance)
    return _cross_cache[key][0]

def get_runs(satA, satB, times, tolerance):
    """
    Retrieve runs array from cross-satellite computations
    
    Parameters
    ----------
    satA : satellite.Satellite
        First satellite considered
    satB : satellite.Satellite 
        Second satellite considered
    times : np.array
        Array of timesteps (s)
    tolerance : int
        Maxmium distance for visibility (m)
    
    Returns
    -------
    _cross_cache[key][1] : array
        [(start elapsed time 1, end elapsed time 1, duration 1), ...]
    """

    key_parts = sorted([(id(satA), satA._version),
                        (id(satB), satB._version)])
    key = (key_parts[0], key_parts[1], times.tobytes())
    cross_sat(satA, satB, times, tolerance)
    return _cross_cache[key][1]

def target_pointer(satA, objB, times, tolerance, tolerance2):
    """
    Compute pointing for satA observation of satB
    
    Parameters
    ----------
    satA : satellite.Satellite
        First satellite considered
    satB : satellite.Satellite 
        Second satellite considered
    times : np.array
        Array of timesteps (s)
    tolerance : int
        Maxmium distance for visibility (m)
    
    Returns
    -------
    pointing_idxs : np.array
        Indexes of times at which poiting occurrs
    new_quats : array
        Array of nadir or target pointing quaternions for SatA towards SatB
    runs : np.array
        Satellite runs
    col_log : np.array
        Log of collisions
    """
    sat_gs = True
    if isinstance(objB, Satellite):
        runs = get_runs(satA, objB, times, tolerance)
    else:
        sat_gs = False
        runs = get_runs_gs(satA, objB, times, tolerance2)
    
    pointing_idxs = None
    new_quats = []
    pointing_idxs = []
    starts = []
    col_log = []
    
    # If there is visibilty
    if len(runs) != 0:
        # Take earth centered inertial frames of both sats
        eciA = satA.propagate(times)
        if sat_gs:
            eciB = objB.propagate(times)
        else:
            eciB = objB.get_ecipos(times)

        for start, end in runs:
            current_idxs = np.arange(start, end, 1)
            starts.append(start)
            
            for idx in current_idxs:
                
                # Find the difference in position of satellites
                observer_pos = eciA[idx]
                target_pos = eciB[idx]
                target_vector = Vector3D(float(target_pos[0] - observer_pos[0]),
                                         float(target_pos[1] - observer_pos[1]),
                                         float(target_pos[2] - observer_pos[2]))
                
                # Find if there is collision
                target_vector_mag = target_vector.getNorm()
                if target_vector_mag == 0:
                    collision = collision_logger(satA.label, objB.label, times[idx])
                    col_log.append(collision)
                    break
                
                pointing_idxs.append(idx)
                
                # Pointing vector def
                b3_unit = target_vector.scalarMultiply(1/target_vector_mag)
                
                vel = satA.get_vels(times)
                vec_vel = Vector3D(float(vel[idx,0]),
                                   float(vel[idx,1]),
                                   float(vel[idx,2]))
                
                # Orbit vector ef
                b1 = vec_vel.subtract(b3_unit.scalarMultiply(vec_vel.dotProduct(b3_unit)))
                b1_unit = b1.scalarMultiply(1/b1.getNorm())
                
                # Remaining vector def
                b2_unit = b3_unit.crossProduct(b1_unit)
                
                # Save vectors as DCM
                DCM_b2e = np.array([(b1_unit.x, b1_unit.y, b1_unit.z), 
                                    (b2_unit.x, b2_unit.y, b2_unit.z), 
                                    (b3_unit.x, b3_unit.y, b3_unit.z)])
                
                # Turn into quat and append
                quat = R.from_matrix(DCM_b2e).as_quat()
                new_quats.append(quat)
                
    return pointing_idxs, new_quats, runs, col_log

def collision_logger(labelA, labelB, timestamp):
    """
    Find and log collisions

    Parameters
    ----------
    labelA : str
        Satellite A name/label
    labelB : str
        Satellite B name/label
    timestamp : int
        Time of collision

    Returns
    collision : str
        Collision log
    """
    collision = (labelA, labelB, timestamp)
    return collision
    
def slew_pointer(point_quats, times, tot_runs):
    """
    Identify priorities and determine final list of runs that are going to be
    seen, and generate list of final quaternions for pointing to those targets
    including the slew (transition/manoeuvre) quaternions.

    Parameters
    ----------
    point_quats : np.array
        Array of initial quaternions
    times : np.array
        Array of numerical times
    tot_runs : np.array
        Array of runs for observer

    Returns
    slewed_quats : np.array
        Array of final quaternions
    sat_runs_info : np.array
        Array of information on final runs
    mans_info : np.array
        Array of information on manoeuvres
    """
    tot_runs_key = tuple(tuple(run) for run in tot_runs)
    times_bytes = times.tobytes()
    
    key = (times_bytes, tot_runs_key)
    if key in _slew_cache:

        return _slew_cache[key]
    
    # Reverse the runs list to give priority to the last Sat   
    reversed_runs = list(reversed(tot_runs))
    
    # Generate an empty list of final runs
    master_runs = []
    sat_runs_info = {}
    mans_info = []
    tstep = times[1]
    for sat, sat_runs in enumerate(reversed_runs):
        sat_runs_info[sat] = []
        
        # If Sat priority is max simply append runs, no checking required
        if sat == 0:
            for run in sat_runs:
                master_runs.append(run)
                
                sat_runs_info[sat].append((run[0]*tstep, (run[1]-1)*tstep))
            
        # If Sat priority low, check that there are no conflicts
        else:
            for run in sat_runs:
                # Take the current run and put it into a fragments list
                fragments = [(run[0], run[1])]
                
                # Take the start and end of each run for the masters
                for (a, b) in master_runs:
                    # Define a new empty list
                    new_fragments = []
                    
                    # Take the start and end of the current fragment
                    for u, v in fragments:
                        
                        # If fragment is totally outside master, append fragment
                        # into new_fragments
                        if v < a or u > b:
                            new_fragments.append((u, v))
                        
                        # If conflicts, check what to do:
                        elif u >= a and u <= b:
                            if v <= b:
                                pass
                            elif v > b:
                                new_fragments.append((b, v))
        
                        elif u < a:
                            if v > a and v <= b:
                                new_fragments.append((u, a))
                            elif v > b:
                                new_fragments.append((u, a))
                                new_fragments.append((b, v))
                            elif b == a:
                                pass
                                
                    # Set fragments = new_fragments so that new master considers
                    # new fragments too
                    fragments = new_fragments
                    # If fragments is empty break the array since nothing to add
                    if not fragments:
                        break
                
                # Introduce new fragments into master_runs
                master_runs.extend(fragments)
                if fragments:
                    frags = [x*tstep for x in fragments[0]]
                    sat_runs_info[sat].append(frags)
                
    master_runs.sort()
    slewed_quats = point_quats
    
    # Define max rotational speed and find timestep
    rot_max = 1 / 180 # 2 deg per sec
    
    # Loop for each run we are interested in
    for run in master_runs:
        rstart = run[0]
        
        # If the run is at the beginning of the simulation, no slew
        if rstart == 0 or rstart == 1 or rstart == 2:
            continue
        
        else:
            # The first quat of the run
            start_quat = slewed_quats[rstart]
        
            # Loop to find the start of the manoeuvre
            for i in range(1, rstart - 1):
                # Previous test quat 
                prev_quat = slewed_quats[rstart - i]
                
                # Since both quats are unit length, dot product gives angle
                dot_prod = np.dot(prev_quat, start_quat)
                dot_prod = np.clip(dot_prod, -1.0, 1.0)
                
                # Find theta and time difference to calculate rot speed
                theta = 2*np.arccos(abs(dot_prod))
                dt = (times[rstart] - times[rstart - i])
                rot_speed = theta/dt
                
                # If rot speed acceptable break loop
                if rot_speed <= rot_max:
                    break
             
            dot_final = np.dot(prev_quat, start_quat)
            if dot_final < 0:
                prev_quat = -prev_quat
                start_quat = -start_quat
            # Start and end relative times and quats
            key_times = np.array([0, i*tstep])
            key_quats = np.stack([[*prev_quat[1:], prev_quat[0]],
                                  [*start_quat[1:], start_quat[0]]])
            
            # Start and end rotation objects, create slerp
            key_rots = R.from_quat(key_quats)
            slerp = Slerp(key_times, key_rots)
            
            # Define array of intermediate steps for which we want quats
            inter_times = tstep * np.arange(1, i)
            
            # Find rots for inter_times
            interp_rots = slerp(inter_times)
            
            base_idx = rstart - i
            
            # Loop over interp_rots and convert into quats
            for k, rot in enumerate(interp_rots, start = 1):
                x, y, z, w = rot.as_quat()
                slewed_quats[base_idx + k] = np.array([w, x, y, z])
            
            mans_info.append(["target pointing", 
                              (tstep * base_idx + int(key_times[0])), 
                              (tstep * base_idx + int(key_times[-1]))])
            
    # Loop for each run we are interested in
    for run in master_runs:
        rend = run[-1] - 1
        
        # If the run is at the end of the simulation, no slew
        if rend == len(times) or rend == len(times) - 1:
            continue
        
        else:
            # The last quat of the run
            end_quat = slewed_quats[rend]
            for i in range(1, (len(times) - rend)):
                next_quat = slewed_quats[rend + i]
            
                # Since both quats are unit length, dot product gives angle
                dot_prod = np.dot(end_quat, next_quat)
                dot_prod = np.clip(dot_prod, -1.0, 1.0)
                
                # Find theta and time difference to calculate rot speed
                theta = 2*np.arccos(abs(dot_prod))
                dt = (times[rend + i] - times[rend])
                rot_speed = theta/dt
                
                # If rot speed acceptable break loop
                if rot_speed <= rot_max:
                    break
            
            dot_final = np.dot(end_quat, next_quat)
            if dot_final < 0:
                end_quat = -end_quat
                next_quat = -next_quat
            # Start and end relative times and quats
            key_times = np.array([0, i*tstep])
            key_quats = np.stack([[*end_quat[1:], end_quat[0]],
                                  [*next_quat[1:], next_quat[0]]])
            
            # Start and end rotation objects, create slerp
            key_rots = R.from_quat(key_quats)
            slerp = Slerp(key_times, key_rots)
            
            # Define array of intermediate steps for which we want quats
            inter_times = tstep * np.arange(1, i)
            
            # Find rots for inter_times
            interp_rots = slerp(inter_times)
            
            base_idx = rend 
            
            # Loop over interp_rots and convert into quats
            for k, rot in enumerate(interp_rots, start = 1):
                x, y, z, w = rot.as_quat()
                slewed_quats[base_idx + k] = np.array([w, x, y, z])
            mans_info.append(["nadir pointing", 
                              (tstep * base_idx + int(key_times[0])), 
                              (tstep * base_idx + int(key_times[-1]))])
            
    _slew_cache[key] = slewed_quats, sat_runs_info, mans_info

    return slewed_quats, sat_runs_info, mans_info

def get_slewed_quats(point_quats, times, tot_runs):
    """
    Parameters
    ----------
    point_quats : np.array
        Array of initial quaternions
    times : np.array
        Array of numerical times
    tot_runs : np.array
        Array of runs for observer

    Returns
    -------
    slewed_quats : np.array
        Array of final quaternions
    """
    slewed_quats, _, _ = slew_pointer(point_quats, times, tot_runs)
    return slewed_quats

def _generate_info(point_quats, times, tot_runs):
    """
    Parameters
    ----------
    point_quats : np.array
        Array of initial quaternions
    times : np.array
        Array of numerical times
    tot_runs : np.array
        Array of runs for observer

    Returns
    -------
    sat_runs_info : np.array
        Array of information on final runs
    mans_info : np.array
        Array of information on manoeuvres
    """
    _, sat_runs_info, mans_info = slew_pointer(point_quats, times, tot_runs)
    return sat_runs_info, mans_info

def get_info(target_names, times, tolerance, tolerance2):
    """
    Parameters
    ----------
    sat_names : np.array
        Array of satellite objects
    times : np.array
        Array of numerical times
    tolerance : int
        Maximum distance for visualization of satellites

    Returns
    -------
    sat_runs_info : np.array
        Array of information on final runs
    mans_info : np.array
        Array of information on manoeuvres
    col_log : np.array
        Log of collisions of all satellites
    """
    sats = len(target_names)
    quats = target_names[0].get_quats(times).copy()
    totruns = []
    col_log = []
    
    # If more than one satellite, sum runs, manoeuvres, collisions
    if sats > 1:
        for i in range(1, sats):
            idxs, new_quats, runs, clog = target_pointer(target_names[0], target_names[i], times, tolerance, tolerance2)
            if len(clog) != 0:
                col_log.extend(clog)
            if len(new_quats) > 0:
                quats[idxs] = new_quats
                totruns.append(runs)
        
        if len(totruns) > 0:
            quats = get_slewed_quats(quats, times, totruns)
            
            sat_runs_info, mans_info = _generate_info(quats, times, totruns)
            return sat_runs_info, mans_info, col_log
    # Else return empty
    return [], [], col_log

# cross_sat but for ground stations
def sat_gs_connect(sat, gs, times, tolerance2):
    """
    Compute the distance bewteen a satellite and ground station as they move 
    through time and find the times when they can communicate
    
    Parameters
    ----------
    sat : satellite.Satellite
        Observer
    gs : groundstation.GroundStation
        Ground station considered
    times : np.array
        Array of timesteps (s)
    tolerance2 : int
        Maxmium distance for visibility (m)
    
    Returns
    -------
    """
    # Find the key for the specific satellites and times being called
    key_parts = sorted([(id(sat), int(sat._version)),
                        (int(id(gs)), int(1))])
    key = (key_parts[0], key_parts[1], times.tobytes())
    
    # If the key already exists 
    if key not in _gs_sat_cache:
        ecef_sat = sat.propagate(times)
        ecef_gs = gs.get_ecipos(times)
        
        # Take the vectors between A and B and find their magnitudes (distance)
        vec_sat_gs = ecef_gs - ecef_sat
        sat_gs_dist = np.linalg.norm(vec_sat_gs, axis = 1)
        
        # Create a boolean mask where True when distance less than tolerance
        mask_prox = (sat_gs_dist <= tolerance2)
        
        # Compute the value of t* - see documentation
        rAd = np.sum(ecef_sat * vec_sat_gs, axis = 1)
        dd = np.sum(vec_sat_gs * vec_sat_gs, axis = 1)
        tstar = -rAd/dd
        
        # Inside the vector if 0 <= t* <= 1, outside else
        inside = (tstar >= 0) & (tstar <= 1)
        outside = ~inside
        
        # Create a Line of Sight boolean mask of the same size as proximity
        mask_los = np.zeros_like(mask_prox)
        
        # If outisde and proximity are both true then LOS = True
        mask_los[outside & mask_prox] = True
        
        # Find the point along the vector for the given t*
        vec_sat_gs = ecef_sat + vec_sat_gs * tstar.reshape(-1, 1)
        earth_r = 6371
        
        # If inside and proximity, check whether earth in the way
        mask_los[inside & mask_prox] = (sat_gs_dist[inside & mask_prox] > earth_r)
        
        # idx where LOS is true, generate splits array telling us where to split
        idx = np.where(mask_los)[0]
        splits = np.where(np.diff(idx)>1)[0] + 1
        
        # Split the indexes into blocks
        blocks = np.split(idx, splits)
        
        # Put start and end times into runs
        runs = [(int(b[0]), int(b[-1])) for b in blocks if b.size]
        
        # Insert all into the cache
        _gs_sat_cache[key] = (sat_gs_dist, runs)
        
 
def get_runs_gs(sat, gs, times, tolerance2):
    """
    Retrieve runs array from cross-satellite computations
    
    Parameters
    ----------
    sat : satellite.Satellite
        Observer
    gs : groundstation.GroundStation
        Ground station considered
    times : np.array
        Array of timesteps (s)
    tolerance2 : int
        Maxmium distance for visibility (m)
    
    Returns
    -------
    _gs_sat_cache[key][1] : array
        [(start elapsed time 1, end elapsed time 1, duration 1), ...]
    """
    
    key_parts = sorted([(id(sat), int(sat._version)),
                        (int(id(gs)), int(1))])
    key = (key_parts[0], key_parts[1], times.tobytes())
    sat_gs_connect(sat, gs, times, tolerance2)
    return _gs_sat_cache[key][1]