from PyQt5 import QtWidgets
from src.gui.SatInfoUI import Ui_MainWindow
import numpy as np

class SatInfoWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent = None):
        # Initialize window and set up button actions
        super().__init__(parent)
        self.setupUi(self)
        self.update_info()
        
    def update_info(self):
        try:
            self.info_display_date.setDateTime(self.parent().epoch)
            self.info_display_duration.setText(str(self.parent().duration))
            self.info_display_timestep.setText(str(self.parent().timestep))
            
            try: 
                sat0 = self.parent().sat0
                
                self.info_display_name0.setText(sat0.label)
                self.info_display_a0.setText(str(sat0.a / 1000))
                self.info_display_e0.setText(str(sat0.e))
                self.info_display_i0.setText(str(int(np.rad2deg(sat0.i))))
                self.info_display_omega0.setText(str(int(np.rad2deg(sat0.omega))))
                self.info_display_raan0.setText(str(int(np.rad2deg(sat0.raan))))
                self.info_display_anom0.setText(str(int(np.rad2deg(sat0.anomaly))))
                self.info_display_anom_type0.setText(str(sat0.anomaly_type))
                
            except AttributeError:
                pass
            
            try: 
                sat1 = self.parent().sat1
                
                self.info_display_name1.setText(sat1.label)
                self.info_display_a1.setText(str(sat1.a / 1000))
                self.info_display_e1.setText(str(sat1.e))
                self.info_display_i1.setText(str(int(np.rad2deg(sat1.i))))
                self.info_display_omega1.setText(str(int(np.rad2deg(sat1.omega))))
                self.info_display_raan1.setText(str(int(np.rad2deg(sat1.raan))))
                self.info_display_anom1.setText(str(int(np.rad2deg(sat1.anomaly))))
                self.info_display_anom_type1.setText(str(sat1.anomaly_type))
                
            except AttributeError:
                pass
            
            try: 
                sat2 = self.parent().sat2
                
                self.info_display_name2.setText(sat2.label)
                self.info_display_a2.setText(str(sat2.a / 1000))
                self.info_display_e2.setText(str(sat2.e))
                self.info_display_i2.setText(str(int(np.rad2deg(sat2.i))))
                self.info_display_omega2.setText(str(int(np.rad2deg(sat2.omega))))
                self.info_display_raan2.setText(str(int(np.rad2deg(sat2.raan))))
                self.info_display_anom2.setText(str(int(np.rad2deg(sat2.anomaly))))
                self.info_display_anom_type2.setText(str(sat2.anomaly_type))
                
            except AttributeError:
                pass
            
            try: 
                sat3 = self.parent().sat3
                
                self.info_display_name3.setText(sat0.label)
                self.info_display_a3.setText(str(sat3.a / 1000))
                self.info_display_e3.setText(str(sat3.e))
                self.info_display_i3.setText(str(int(np.rad2deg(sat3.i))))
                self.info_display_omega3.setText(str(int(np.rad2deg(sat3.omega))))
                self.info_display_raan3.setText(str(int(np.rad2deg(sat3.raan))))
                self.info_display_anom3.setText(str(int(np.rad2deg(sat3.anomaly))))
                self.info_display_anom_type3.setText(str(sat3.anomaly_type))
                
            except AttributeError:
                pass
            
            try: 
                sat4 = self.parent().sat4
                
                self.info_display_name4.setText(sat4.label)
                self.info_display_a4.setText(str(sat4.a / 1000))
                self.info_display_e4.setText(str(sat4.e))
                self.info_display_i4.setText(str(int(np.rad2deg(sat4.i))))
                self.info_display_omega4.setText(str(int(np.rad2deg(sat4.omega))))
                self.info_display_raan4.setText(str(int(np.rad2deg(sat4.raan))))
                self.info_display_anom4.setText(str(int(np.rad2deg(sat4.anomaly))))
                self.info_display_anom_type4.setText(str(sat4.anomaly_type))
                
            except AttributeError:
                pass
            
        except AttributeError:
            pass
            
        
        