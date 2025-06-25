import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.spatial.transform import Rotation as R
import satellite_utils

def plot_ground_tracks(sat_names, times):
    fig = plt.figure()
    ax = fig.add_subplot()
    earth_map = plt.imread('earth_outline.png')
    ax.imshow(earth_map, extent=[-180, 180, -90, 90], origin='upper', aspect='equal')
    
    ax.set_xlim([-180, 180])
    ax.set_ylim([-90, 90])
    ax.set_xticks(np.arange(-180, 181, 60.0))
    ax.set_yticks(np.arange(-90, 91, 30))
    ax.set_xlabel('Longitude (°)')
    ax.set_ylabel('Latitude (°)')
    
    for i in range(len(sat_names)):
        lonlat = sat_names[i].get_gtc(times)
        ax.plot(lonlat[:,0], lonlat[:,1])
    
    return fig, ax
    
def plot_orbits(sat_names, times):
    R_earth = 6.378e6
    n_lon = 60
    n_lat = 30

    longitudes = np.linspace(0, 2*np.pi, n_lon)
    latitudes = np.linspace(0, np.pi, n_lat)
    lon_grid, lat_grid = np.meshgrid(longitudes, latitudes)

    X = R_earth * np.sin(lat_grid) * np.cos(lon_grid)
    Y = R_earth * np.sin(lat_grid) * np.sin(lon_grid)
    Z = R_earth * np.cos(lat_grid)

    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    ax.plot_wireframe(X, Y, Z, color='black', alpha=0.5, linewidth=0.5)
    
    max_extent = 0
    for i in range(len(sat_names)):
        trajectory = sat_names[i].propagate(times)
        ax.plot(trajectory[:,0], trajectory[:,1], trajectory[:,2], 
                 linewidth=2, label = sat_names[i].label)
        
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

def plot_cross_sat(satA, satB, times, tolerance):
    cross_dist = satellite_utils.get_cross_dist(satA, satB, times, tolerance)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(times, cross_dist)
    ax.axhline(y = tolerance, color = 'r', linestyle = '--')
    ax.set_xlabel('Time elapsed (s)')
    ax.set_ylabel('Cross-sat distance (m)')
    ax.set_xlim([0, max(times)+1])
    ax.set_ylim(bottom = 0)
    
    return fig, ax




def animate_sat_attitude(sat_names, times, interval = 100):
    quats = sat_names[0].get_quats(times)
    rots = R.from_quat(quats)
    DCM_eci2body = rots.as_matrix()
    DCM_body2eci = rots.as_matrix()
    
    fig, ax = plot_orbits(sat_names, times)
    
    obs_traj = sat_names[0].propagate(times)
    obs_marker = ax.scatter(obs_traj[0,0], obs_traj[0,1], obs_traj[0,2], 
                            s = 50, label = sat_names[0].label)

    
    quiver = ax.quiver(
    [0,0,0], [0,0,0], [0,0,0],    
    [1,0,0], [0,1,0], [0,0,1], # initial directions = body-axes aligned with ECI
    length=1)
    
    def update(i):
        nonlocal quiver
        
        obs_x, obs_y, obs_z = obs_traj[i]
        obs_marker._offsets3d = ([obs_x], [obs_y], [obs_z])
        
        quiver.remove()
        
        
        axes_sat = DCM_body2eci[i]
        U = axes_sat[:,0]
        V = axes_sat[:,1]
        W = axes_sat[:,2]
        
        quiver = ax.quiver(
            [obs_x, obs_x, obs_x],
            [obs_y, obs_y, obs_y],
            [obs_z, obs_z, obs_z],   
            U, V, W, length=1e6, normalize = True, color = ['r', 'g', 'b'])
        
        
        return quiver, obs_marker,
    
    anim = FuncAnimation(fig, update, frames = len(times),
                         interval = interval, blit = False)
    
    return anim   