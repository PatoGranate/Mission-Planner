from PyQt5 import QtWidgets
from SatParamsUI import Ui_MainWindow
from satellite import Satellite

class SatParamsWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setupUi(self)
        self.sat_cancel.clicked.connect(self.close)
        self.create_sat.clicked.connect(self.sat_create)
        self.actionReset.triggered.connect(self.reset)
        
    def sat_create(self):
        a_input = self.set_a.text()
        e_input = self.set_e.text()
        i_input = self.set_i.text()
        omega_input = self.set_omega.text()
        raan_input = self.set_raan.text()
        anomaly_input = self.set_anomaly.text()
        anomaly_type = self.set_anomaly_type.currentText()
        sat_name = self.set_sat_name.text()
        
        date = self.parent().date
        
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
    
        if not (0.0 <= e <= 1.0):
            QtWidgets.QMessageBox.warning(self, "Invalid e",
                "Eccentricity must be between 0 and 1")
            return
        
        sat1 = Satellite(a, e, i, raan, omega, anomaly, date, 
                         anomaly_type, label = sat_name)
        
        self.parent().sat1 = sat1
        self.close()
    
    def reset(self):
        self.set_a.clear()
        self.set_e.clear()
        self.set_i.setValue(0)
        self.set_omega.setValue(0)
        self.set_raan.setValue(0)
        self.set_anomaly.setValue(0)
        self.set_anomaly_type.setCurrentIndex(0)
        self.set_sat_name.clear()
        