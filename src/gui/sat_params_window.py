from PyQt5 import QtWidgets
from src.gui.SatParamsUI import Ui_MainWindow
from src.model.satellite import Satellite

class SatParamsWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent = None):
        # Initialize window and set up button actions
        super().__init__(parent)
        self.setupUi(self)
        self.sat_cancel.clicked.connect(self.close)
        self.create_sat.clicked.connect(self.sat_create)
        self.actionReset.triggered.connect(self.reset)
        
    def sat_create(self):
        # Take user inputs
        a_input = self.set_a.text()
        e_input = self.set_e.text()
        i_input = self.set_i.text()
        omega_input = self.set_omega.text()
        raan_input = self.set_raan.text()
        anomaly_input = self.set_anomaly.text()
        anomaly_type = self.set_anomaly_type.currentText()
        sat_name = self.set_sat_name.text()
        
        date = self.parent().date
        
        # Check that values are numerical inputs and convert to floats
        try:
            a = float(a_input) * 1000
            e = float(e_input)
            i = float(i_input)
            omega = float(omega_input)
            raan = float(raan_input)
            anomaly = float(anomaly_input)
            
        except ValueError:
            QtWidgets.QMessageBox.warning(self, 
            "Invalid input", "Keplerian elements are empty or not numerical")
            return
        
        # Check that eccentricity value is between 0 and 1
        if not (0.0 <= e <= 1.0):
            QtWidgets.QMessageBox.warning(self, "Invalid e",
                "Eccentricity must be between 0 and 1")
            return
        
        # Define satellites
        sat_num = self.sat_chooser.currentIndex()
        sat = Satellite(a, e, i, omega, raan, anomaly, date, anomaly_type, sat_name)
        
        if sat_num == 0:
            self.parent().sat0 = sat
        elif sat_num == 1:
            self.parent().sat1 = sat
        elif sat_num == 2:
            self.parent().sat2 = sat
        elif sat_num == 3:
            self.parent().sat3 = sat
        elif sat_num == 4:
            self.parent().sat4 = sat
        
        # Close window
        self.close()
    
    def reset(self):
        # Reset user inputs to default
        self.set_a.clear()
        self.set_e.clear()
        self.set_i.setValue(0)
        self.set_omega.setValue(0)
        self.set_raan.setValue(0)
        self.set_anomaly.setValue(0)
        self.set_anomaly_type.setCurrentIndex(0)
        self.set_sat_name.clear()
        