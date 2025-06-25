import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.spatial.transform import Rotation as R
import satellite_utils

def plot_ground_tracks(sat_names, times):
    fig1 = plt.figure()
    ax1 = fig1.add_subplot()
    earth_map = plt.imread('earth_outline.png')
    ax1.imshow(earth_map, extent=[-180, 180, -90, 90], origin='upper', aspect='equal')
    
    ax1.set_xlim([-180, 180])
    ax1.set_ylim([-90, 90])
    ax1.set_xticks(np.arange(-180, 181, 60.0))
    ax1.set_yticks(np.arange(-90, 91, 30))
    ax1.set_xlabel('Longitude (°)')
    ax1.set_ylabel('Latitude (°)')
    
    for i in range(len(sat_names)):
        lonlat = sat_names[i].get_gtc(times)
        ax1.plot(lonlat[:,0], lonlat[:,1])
    
    return fig1
    
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

    fig2 = plt.figure()
    ax2 = fig2.add_subplot(projection='3d')
    ax2.plot_wireframe(X, Y, Z, color='black', alpha=0.5, linewidth=0.5)
    
    max_extent = 0
    for i in range(len(sat_names)):
        trajectory = sat_names[i].propagate(times)
        ax2.plot(trajectory[:,0], trajectory[:,1], trajectory[:,2], 
                 linewidth=2, label = sat_names[i].label)
        
        current_max = max(abs(trajectory[:,0]).max(), 
                          abs(trajectory[:,1]).max(), 
                          abs(trajectory[:,2]).max()) * 1.1
        if current_max > max_extent:
            max_extent = current_max
            
    ax2.set_box_aspect([1, 1, 1])
    
    ax2.set_xlim([-max_extent, max_extent])
    ax2.set_ylim([-max_extent, max_extent])
    ax2.set_zlim([-max_extent, max_extent])
    ax2.legend()
    ax2.set_xlabel('x-Pos (m)')
    ax2.set_ylabel('y-Pos (m)')
    ax2.set_zlabel('z-Pos (m)')

def plot_cross_sat(satA, satB, times, tolerance):
    cross_dist = satellite_utils.get_cross_dist(satA, satB, times, tolerance)

    fig3 = plt.figure()
    ax3 = fig3.add_subplot(111)
    ax3.plot(times, cross_dist)
    ax3.axhline(y = tolerance, color = 'r', linestyle = '--')
    ax3.set_xlabel('Time elapsed (s)')
    ax3.set_ylabel('Cross-sat distance (m)')
    ax3.set_xlim([0, max(times)+1])
    ax3.set_ylim(bottom = 0)




def animate_sat_attitude(satA, times, interval = 100):
    quats = satA.get_quats(times)
    rots = R.from_quat(quats)
    DCM_eci2body = rots.as_matrix()
    DCM_body2eci = DCM_eci2body.transpose(0, 2, 1)
    
    fig = plt.figure()
    ax = fig.add_subplot(111, projection = '3d')
    ax.set_xlim(-1, 1), ax.set_ylim(-1, 1), ax.set_zlim(-1, 1)
    ax.set_xlabel('X'), ax.set_ylabel('Y'), ax.set_zlabel('Z')
    
    quiver = ax.quiver(
    [0,0,0], [0,0,0], [0,0,0],    
    [1,0,0], [0,1,0], [0,0,1], # initial directions = body-axes aligned with ECI
    length=1)
    
    def update(i):
        nonlocal quiver
        quiver.remove()
        
        axes_sat = DCM_body2eci[i]
        U = axes_sat[:,0]
        V = axes_sat[:,1]
        W = axes_sat[:,2]
        
        quiver = ax.quiver(
        [0,0,0], [0,0,0], [0,0,0],    
        U, V, W, # initial directions = body-axes aligned with ECI
        length=1)
        
        return quiver,
    
    anim = FuncAnimation(fig, update, frames = len(times),
                         interval = interval, blit = False)
    
    return anim   