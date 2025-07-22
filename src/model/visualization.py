import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from pathlib import Path
from scipy.spatial.transform import Rotation as R
from cycler import cycler

import src.model.groundstation as groundstation
import src.model.satellite_utils as satellite_utils

# Set preset style for plots
mpl.rcParams.update({
    'text.color'       : 'white',
    'axes.labelcolor'  : 'white',
    'axes.titlecolor'  : 'white',
    'xtick.color'      : 'white',
    'ytick.color'      : 'white',
    'legend.facecolor' : 'black',
    'legend.edgecolor' : 'white'
})

# Change default colors and set them to the cycler
my_colors = ['#00FEFC', '#FF2603', '#00FF00', '#FFF01F', '#BF00FF']

plt.rcParams['axes.prop_cycle'] = cycler(color=my_colors)

def plot_ground_tracks(sat_names, ground_stations, times):
    """
    Plot the ground tracks of a set of satellites
    
    Parameters
    ----------
    sat_names : satellite.Satellite array
        Array of Satellite objects
    times : np.array
        Array of timesteps (s)
        
    Returns
    -------
    fig : figure.Figure
        Ground track figure
    ax : axes._axes.Axes
        2D axes configured for ground track plotting
    """
    fig = plt.figure()
    ax = fig.add_subplot()
    
    # Find Earth map from folder
    project_root = Path(__file__).resolve().parents[2]
    img_path = project_root / "imgs" / "earth_outline_gray.png"
    earth_map = plt.imread(str(img_path))
    
    # Fix axes and edit visuals
    ax.imshow(earth_map, extent=[-180, 180, -90, 90], origin='upper', aspect='equal')
    
    for spine in ax.spines.values():
        spine.set_edgecolor("#E6E6E6")
    
    ax.set_xlim([-180, 180])
    ax.set_ylim([-90, 90])
    ax.set_xticks(np.arange(-180, 181, 60.0))
    ax.set_yticks(np.arange(-90, 91, 30))
    ax.set_xlabel('Longitude (°)')
    ax.set_ylabel('Latitude (°)')
    
    # Plot ground stations
    for g in ground_stations:
        plt.scatter(np.rad2deg(g.lon), np.rad2deg(g.lat), color = '#FC5E31')

    # Plot tracks
    for i, sat in enumerate(sat_names):
        lonlat = sat_names[i].get_gtc(times)
        ax.plot(lonlat[:,0], lonlat[:,1], label = sat.label)
    
    ax.legend()
    
    return fig, ax
    
def plot_orbits(sat_names, ground_stations, times):
    """
    Plot earth and 3D orbital track of satellites
    
    Parameters
    ----------
    sat_names : satellite.Satellite array
        Array of Satellite objects
    times : np.array
        Array of timesteps (s)
        
    Returns
    -------
    fig : figure.Figure
        Ground track figure
    ax : axes._axes.Axes
        3D axes configured for orbit propagation
    """
    # Generate spherical representation of Earth
    R_earth = 6.378e6
    n_lon = 59
    n_lat = 30

    longitudes = np.linspace(0, 2*np.pi, n_lon)
    latitudes = np.linspace(0, np.pi, n_lat)
    lon_grid, lat_grid = np.meshgrid(longitudes, latitudes)

    X = R_earth * np.sin(lat_grid) * np.cos(lon_grid)
    Y = R_earth * np.sin(lat_grid) * np.sin(lon_grid)
    Z = R_earth * np.cos(lat_grid)

    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    eline = ax.plot_wireframe(X, Y, Z, color='#E6E6E6', alpha=0.7, linewidth=0.5)
    eline.set_clip_on(False)
    
    # Define a maximum extent to generate equal axes - avoid distortion
    max_extent = R_earth
    
    # Plot trajectories per sat
    for i in range(len(sat_names)):
        trajectory = sat_names[i].propagate(times)
        line, = ax.plot(trajectory[:,0], trajectory[:,1], trajectory[:,2], 
                           linewidth=2, label = sat_names[i].label)
        line.set_clip_on(False)
        
        current_max = max(abs(trajectory[:,0]).max(), 
                          abs(trajectory[:,1]).max(), 
                          abs(trajectory[:,2]).max()) * 1.1
        
        # Take maximum extent from trajectories
        if current_max > max_extent:
            max_extent = current_max
    
    # Set axes to avoid distortion
    ax.set_box_aspect([1, 1, 1])
    
    ax.set_xlim([-max_extent, max_extent])
    ax.set_ylim([-max_extent, max_extent])
    ax.set_zlim([-max_extent, max_extent])
    ax.legend()
    ax.set_xlabel('x-Pos (m)')
    ax.set_ylabel('y-Pos (m)')
    ax.set_zlabel('z-Pos (m)')
    
    return fig, ax

def plot_cross_sat(sat_names, times, tolerance):
    """
    Plot distances from observer satellite to other satellites
    
    Parameters
    ----------
    sat_names : satellite.Satellite array
        Array of Satellite objects
    times : np.array
        Array of timesteps (s)
    tolerance : int
        Maxmium distance for visibility (m)
        
    Returns
    -------
    fig : figure.Figure
        Ground track figure
    ax : axes._axes.Axes
        2D axes configured for distance visualization
    """
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.axhline(y = tolerance, linestyle = '--')
    
    # Skip first color in cycle
    base_cycle = plt.rcParams['axes.prop_cycle']
    skip_first = base_cycle[1:]
    ax.set_prop_cycle(skip_first)
    
    # Plot distances
    for i in range(1, len(sat_names)):
        cross_dist = satellite_utils.get_cross_dist(sat_names[0], sat_names[i], times, tolerance)
        ax.plot(times, cross_dist, label = sat_names[i].label)
        
    ax.legend()
    ax.set_xlabel('Time elapsed (s)')
    ax.set_ylabel('Cross-sat distance (m)')
    ax.set_xlim([0, max(times)+1])
    ax.set_ylim(bottom = 0)
    
    return fig, ax

def animate_sat_attitude(sat_names, ground_stations, times, tolerance, tolerance2, interval = 100, progress_callback = None):
    """
    Animate satellite objects and attitude frames around orbits
    
    Parameters
    ----------
    sat_names : satellite.Satellite array
        Array of Satellite objects
    times : np.array
        Array of timesteps (s)
    tolerance : int
        Maxmium distance for visibility (m)
    interval = 100 : int
        Interval between frames
        
    Returns
    -------
    anim : animation.FuncAnimation
        Satellite and frame animation
    """
    satlen = len(sat_names)
    gslen = len(ground_stations)
    
    # Take base quaternions 
    quats = sat_names[0].get_quats(times).copy()
    
    # Totruns defines the total runs for all target satellites together
    totruns = []
    
    # If there are target ground stations, connect with them - not priority
    if gslen > 0:
        for i in range(gslen):
            idxs, new_quats, runs, _ = satellite_utils.target_pointer(sat_names[0], ground_stations[i], times, tolerance, tolerance2)
            # If runs for new ground station, save pointing quats and runs
            if len(new_quats) > 0:
                quats[idxs] = new_quats
                totruns.append(runs)
            
            # If there are runs replace old quats with slewed quats
            if len(totruns) > 0:
                quats = satellite_utils.get_slewed_quats(quats, times, totruns)
            
    # If there are target satellites, check their visibility
    if satlen > 1:
        for i in range(1, satlen):
            idxs, new_quats, runs, _ = satellite_utils.target_pointer(sat_names[0], sat_names[i], times, tolerance, tolerance2)
            # If runs for new satellite, save pointing quats and runs
            if len(new_quats) > 0:
                quats[idxs] = new_quats
                totruns.append(runs)
        
        # If there are runs replace old quats with slewed quats
        if len(totruns) > 0:
            quats = satellite_utils.get_slewed_quats(quats, times, totruns)
            
    # Turn quaternions into axes rotations
    rots = R.from_quat(quats)
    DCM_body2eci = rots.as_matrix()
    
    # Plot trajectories without ground stations
    fig, ax = plot_orbits(sat_names, [], times)
    
    # Plot initial position ground station markers
    gsmovement = [gs.get_ecipos(times) for gs in ground_stations]
    gsmarkers = []
    for gstt in ground_stations:
        gsx0, gsy0, gsz0 = gstt.ecef_pos.getX(), gstt.ecef_pos.getY(), gstt.ecef_pos.getZ()
        gm = ax.scatter(gsx0, gsy0, gsz0, s = 150, color = '#FC5E31', label = gstt.label)
        gsmarkers.append(gm)
        gm.set_clip_on(False) 
        
    # Save trajectories and plot them with markers for the satellites
    trajectories = [sat.propagate(times) for sat in sat_names]
    satmarkers = []
    for traj, sat in zip(trajectories, sat_names):
        x0, y0, z0 = traj[0]
        sm = ax.scatter(x0, y0, z0, s=200, label=sat.label)
        satmarkers.append(sm)
        sm.set_clip_on(False)
    
    # Create quiver for observer satellite
    obs_x0, obs_y0, obs_z0 = trajectories[0][0]
    quiver = ax.quiver([obs_x0]*3, [obs_y0]*3, [obs_z0]*3,    
                       [1,0,0], [0,1,0], [0,0,1], length=1.5e6, 
                       normalize = True, color = ['#E6E6E6', 'w', 'w'])
    quiver.set_clip_on(False)
    
    # Update frame to move markers and rotate quiver
    def update(frame):
        nonlocal quiver
        quiver.remove()
        
        for idx, (sm, traj) in enumerate(zip(satmarkers, trajectories)):
            # If idx == 0, we're editing observer so we need to edit quiver
            if idx == 0:
                # Find the observer position at frame and update marker
                x_obs, y_obs, z_obs = traj[frame]
                sm._offsets3d = ([x_obs], [y_obs], [z_obs])
                
                # Extract three vectors for quiver
                axes_sat = DCM_body2eci[frame]
                U = axes_sat[:,0]
                V = axes_sat[:,1]
                W = axes_sat[:,2]
                
                # Update quiver to new position and orientation
                quiver = ax.quiver(
                    [x_obs]*3,
                    [y_obs]*3,
                    [z_obs]*3,   
                    U, V, W, length=1.5e6, normalize = True, color = ['#E6E6E6', 'w', 'w'])
                quiver.set_clip_on(False)
            
            # If idx != 0, satellite is not observer so no quiver updates
            else:
                # Find target position at frame and update marker
                x, y, z = traj[frame]
                sm._offsets3d = ([x], [y], [z])
         
        # Update ground station positions over time as above
        for idx, (gm, mov) in enumerate(zip(gsmarkers, gsmovement)):
            gsx, gsy, gsz = mov[frame]
            gm._offsets3d = ([gsx], [gsy], [gsz])
            
        # Update title with time elapsed
        ax.set_title(f"Time elapsed: {times[frame]:.0f}s")
        
        # Update progress bar
        if progress_callback is not None:
            progress_callback(frame, len(times))
            
        if frame == len(times) - 1:
            anim.event_source.stop()
            
        return
    
    anim = FuncAnimation(fig, update, frames = len(times),
                         interval = interval, repeat = False, blit = False)
    
    return anim