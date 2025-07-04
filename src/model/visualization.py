import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from pathlib import Path
from scipy.spatial.transform import Rotation as R
import src.model.satellite_utils as satellite_utils
from cycler import cycler

mpl.rcParams.update({
    'text.color'       : 'white',
    'axes.labelcolor'  : 'white',
    'axes.titlecolor'  : 'white',
    'xtick.color'      : 'white',
    'ytick.color'      : 'white',
    'legend.facecolor' : 'black',
    'legend.edgecolor' : 'white'
})

my_colors = ['#00FEFC', '#FF2603', '#00FF00', '#FFF01F', '#BF00FF']  # e.g. red, blue, green, purple, orange

# Tell Matplotlib to use this cycle for all plots:
plt.rcParams['axes.prop_cycle'] = cycler(color=my_colors)

def plot_ground_tracks(sat_names, times):
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
    
    project_root = Path(__file__).resolve().parents[2]
    img_path = project_root / "imgs" / "earth_outline_gray.png"
    earth_map = plt.imread(str(img_path))
    
    ax.imshow(earth_map, extent=[-180, 180, -90, 90], origin='upper', aspect='equal')
    
    for spine in ax.spines.values():
        spine.set_edgecolor("#E6E6E6")
    
    ax.set_xlim([-180, 180])
    ax.set_ylim([-90, 90])
    ax.set_xticks(np.arange(-180, 181, 60.0))
    ax.set_yticks(np.arange(-90, 91, 30))
    ax.set_xlabel('Longitude (°)')
    ax.set_ylabel('Latitude (°)')
    
    for i, sat in enumerate(sat_names):
        lonlat = sat_names[i].get_gtc(times)
        ax.plot(lonlat[:,0], lonlat[:,1], label = sat.label)
    
    ax.legend()
    
    return fig, ax
    
def plot_orbits(sat_names, times):
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
    
    max_extent = 0
    for i in range(len(sat_names)):
        trajectory = sat_names[i].propagate(times)
        line, = ax.plot(trajectory[:,0], trajectory[:,1], trajectory[:,2], 
                           linewidth=2, label = sat_names[i].label)
        line.set_clip_on(False)
        
        current_max = max(abs(trajectory[:,0]).max(), 
                          abs(trajectory[:,1]).max(), 
                          abs(trajectory[:,2]).max()) * 1.1
        if current_max > max_extent:
            max_extent = current_max
            
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
    ax.axhline(y = tolerance, color = 'r', linestyle = '--')
    
    for i in range(1, len(sat_names)):
        cross_dist = satellite_utils.get_cross_dist(sat_names[0], sat_names[i], times, tolerance)
        ax.plot(times, cross_dist)
    
    ax.set_xlabel('Time elapsed (s)')
    ax.set_ylabel('Cross-sat distance (m)')
    ax.set_xlim([0, max(times)+1])
    ax.set_ylim(bottom = 0)
    
    return fig, ax

def animate_sat_attitude(sat_names, times, tolerance, interval = 100, progress_callback = None):
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
    #quats = satellite_utils.sat_tracker(sat_names[0], sat_names[1], times, tolerance)
    quats = sat_names[0].get_quats(times)
    rots = R.from_quat(quats)
    DCM_body2eci = rots.as_matrix()
    
    fig, ax = plot_orbits(sat_names, times)
    
    trajectories = [sat.propagate(times) for sat in sat_names]
        
    markers = []
    for traj, sat in zip(trajectories, sat_names):
        x0, y0, z0 = traj[0]
        m = ax.scatter(x0, y0, z0, s=200, label=sat.label)
        markers.append(m)
        m.set_clip_on(False)
    
    obs_x0, obs_y0, obs_z0 = trajectories[0][0]
    quiver = ax.quiver([obs_x0]*3, [obs_y0]*3, [obs_z0]*3,    
                       [1,0,0], [0,1,0], [0,0,1], length=1.5e6, 
                       normalize = True, color = ['#E6E6E6', 'w', 'w'])
    quiver.set_clip_on(False)
    
    def update(frame):
        nonlocal quiver
        quiver.remove()
        
        for idx, (m, traj) in enumerate(zip(markers, trajectories)):
            if idx == 0:
                x_obs, y_obs, z_obs = traj[frame]
                m._offsets3d = ([x_obs], [y_obs], [z_obs])
                
                axes_sat = DCM_body2eci[frame]
                U = axes_sat[:,0]
                V = axes_sat[:,1]
                W = axes_sat[:,2]
                
                quiver = ax.quiver(
                    [x_obs]*3,
                    [y_obs]*3,
                    [z_obs]*3,   
                    U, V, W, length=1.5e6, normalize = True, color = ['#E6E6E6', 'w', 'w'])
                quiver.set_clip_on(False)
                
            else:
                x, y, z = traj[frame]
                m._offsets3d = ([x], [y], [z])
                
        ax.set_title(f"Time elapsed: {times[frame]:.0f}s")
        
        if progress_callback is not None:
            progress_callback(frame, len(times))
            
        if frame == len(times) - 1:
            anim.event_source.stop()
            
        return (*markers, quiver)
    
    anim = FuncAnimation(fig, update, frames = len(times),
                         interval = interval, repeat = False, blit = False)
    
    return anim   