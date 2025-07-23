from PyQt5 import QtWidgets

from src.gui.GroundStationUI import Ui_MainWindow
from src.model.groundstation import GroundStation

class GSParamsWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent = None):
        # Initialize window and set up button actions
        super().__init__(parent)
        self.setupUi(self)
        
        self.gs_cancel.clicked.connect(self.close)
        self.create_gs.clicked.connect(self.gs_create)
        
        # Try finding existing gss, change dropdown preset to inexisting gs
        try: 
            self.parent().gs0
            self.gs_chooser.setCurrentIndex(1)
            try:
                self.parent().gs1
                self.gs_chooser.setCurrentIndex(2)
                try:
                    self.parent().gs2
                    self.gs_chooser.setCurrentIndex(3)
                    try:
                        self.parent().gs3
                        self.gs_chooser.setCurrentIndex(4)
                    except AttributeError:
                        pass
                except AttributeError:
                    pass
            except AttributeError:
                pass
        except AttributeError:
            pass
        
    def gs_create(self):
        # Take user inputs
        lat_input = self.set_lat.text()
        lon_input = self.set_lon.text()
        alt_input = self.set_alt.text()
        label_input = self.set_gs_name.text()
        
        date = self.parent().date

        # Ensure lat and lon are in correct format, else raise exception warning
        try:
            latnum, latlet = (i for i in lat_input.split())
            lonnum, lonlet = (i for i in lon_input.split())
            
            if float(latnum) > 90 or float(latnum) < 0:
                raise ValueError("Invalid latitude")
                
            if float(lonnum) > 180 or float(lonnum) < 0:
                raise ValueError("Invalid longitude")
                
            if str(latlet) != "N" and str(latlet) != "S":
                raise ValueError("Invalid Latitude")
            if str(lonlet) != "W" and str(lonlet) != "E":
                raise ValueError("Invalid Longitude")
            
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Invalid input", 
            "Latitude and Longitude inputs must be: <number_letter>. Lat value <= 90 N/S, lon value <= 180 E/W.")
            return
        
        # If South or East, deg in negative
        if latlet == "S":
            latnum = float(latnum) * (-1)
        if lonlet == "W":
            lonnum = float(lonnum) * (-1)
            
        # Ensure altitude is numerical and above 0
        try:
            alt = float(alt_input) * 1000
            if alt < 0:
                raise ValueError("Invalid altitude negative")
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Invalid input", 
            "Altitude input must be numerical and positive")
            return
        
        # If no label set to gs number
        if label_input == "":
            label = self.gs_chooser.currentText()
        else:
            label = label_input
        
        # Create ground station
        gs = GroundStation(float(latnum), float(lonnum), date, float(alt), label)
        
        gs_num = self.gs_chooser.currentIndex()
        
        # Depending on dropdown select, create or update ground station
        if gs_num == 0:
            gs0 = getattr(self.parent(), 'gs0', None)
            if gs0 == None:
                self.parent().gs0 = gs
            else:
                self.parent().gs0.update_gs(lat = float(latnum), 
                                            lon = float(lonnum), alt = alt, 
                                            label = label)
        elif gs_num == 1:
            gs1 = getattr(self.parent(), 'gs1', None)
            if gs1 == None:
                self.parent().gs1 = gs
            else:
                self.parent().gs1.update_gs(lat = float(latnum), 
                                            lon = float(lonnum), alt = alt, 
                                            label = label)
        elif gs_num == 2:
            gs2 = getattr(self.parent(), 'gs2', None)
            if gs2 == None:
                self.parent().gs2 = gs
            else:
                self.parent().gs2.update_gs(lat = float(latnum), 
                                            lon = float(lonnum), alt = alt, 
                                            label = label)
        elif gs_num == 3:
            gs3 = getattr(self.parent(), 'gs3', None)
            if gs3 == None:
                self.parent().gs3 = gs
            else:
                self.parent().gs3.update_gs(lat = float(latnum), 
                                            lon = float(lonnum), alt = alt, 
                                            label = label)
        elif gs_num == 4:
            gs4 = getattr(self.parent(), 'gs4', None)
            if gs4 == None:
                self.parent().gs4 = gs
            else:
                self.parent().gs4.update_gs(lat = float(latnum), 
                                            lon = float(lonnum), alt = alt, 
                                            label = label)
        
        # Close window
        self.close()