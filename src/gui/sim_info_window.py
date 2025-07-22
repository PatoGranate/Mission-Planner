from PyQt5 import QtWidgets
from src.gui.SimInfoUI import Ui_MainWindow
import src.model.satellite_utils as satellite_utils

class SimInfoWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent = None):
        # Initialize window and set up button actions
        super().__init__(parent)
        self.setupUi(self)
        self.update_text(self.parent().sats, self.parent().times, self.parent().tolerance, self.parent().tolerance2)
    
    # Update receipt text based on simulation
    def update_text(self, sat_names, times, tolerance, tolerance2):
        # Get information from cached data
        sat_runs_info, mans_info, col_log = satellite_utils.get_info(sat_names, times, tolerance, tolerance2)
        # If only one satellite exists display this information
        if len(sat_names) == 1:
            self.sim_info_display.append(f"<i>Only {sat_names[0].label} in simulation</i>")
            return
        
        # If collision exists, display information
        if len(col_log) != 0:
            for col in col_log:
                self.sim_info_display.append(f"Collision occurred between {col[0]} and {col[1]} at {col[2]}s!")
            self.sim_info_display.append(f"<i>IF COLLISION OCCURRS, MANOEUVRES ARE NOT CALCULATED</i>")
            return
        
        # Create copy to not have to edit sat_names
        newsats = sat_names.copy()
        
        # Create an array of satellites which are not visible
        no_vis = [0]
        for satidx, sat in enumerate(sat_names):
            if satidx == 0:
                pass
            else:
                curruns = satellite_utils.get_runs(sat_names[0], sat_names[satidx], times, tolerance)
                if len(curruns) == 0:
                    self.sim_info_display.append(f"<i><b>{sat.label}</b> is not visible from observer</i>")
                    self.sim_info_display.append(f"<i> </i>")
                    no_vis.append(satidx)
                
        # Reverse the not-visible satellites and remove them from sat list
        no_vis.reverse()
        for idx in no_vis:
            newsats.pop(idx)
        
        # Reverse the sat list and print the information about the current sat
        newsats.reverse()
        for satidx, sat in enumerate(newsats):
            curvisibility = sat_runs_info[satidx]
            visibility = []
            if curvisibility == []:
                self.sim_info_display.append(f"<i><b>{sat.label}</b> is visible but not a priority")
                self.sim_info_display.append(f"<i> </i>")
            else:
                for cur in curvisibility:
                    visibility.append((int(cur[0]), int(cur[1])))
                visiblestr = "s, ".join(str(vis) for vis in visibility)
                self.sim_info_display.append(f"<i><b>{sat.label}</b> is visible between {visiblestr}s")
                self.sim_info_display.append(f"<i> </i>")
        
        # Sort manoeuvres into chronological order and display information 
        sorted_mans = sorted(mans_info, key = lambda row:row[1])
        for man in sorted_mans:
            manstr, start, end = str(man[0]), int(man[1]), int(man[2])
            
            self.sim_info_display.append(f"<i>Manoeuvre for <b>{manstr}</b> from {start}s to {end}s")
            self.sim_info_display.append(f"<i> </i>")