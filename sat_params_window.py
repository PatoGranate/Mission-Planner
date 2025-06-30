from PyQt5 import QtWidgets
from SatParamsUI import Ui_MainWindow
from satellite import Satellite

class SatParamsWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setupUi(self)
        self.sat_cancel.clicked.connect(self.close)
        self.create_sat.clicked.connect(self.sat_create)
        
    def sat_create(self):
        a_input = self.set_a.text()
        e_input = self.set_e.text()
        i_input = self.set_i.text()
        omega_input = self.set_omega.text()
        raan_input = self.set_raan.text()
        anomaly_input = self.set_anomaly.text()
        anomaly_type = self.set_anomaly_type.currentText()
        sat_name = self.set_sat_name.text()
        
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
        
        sat1 = Satellite(a, e, i, raan, omega, anomaly, epoch, anomaly_type, label = sat_name)
        
        return sat1
    
    """
    QUEDA PENDIENTE PARA MAÑANA AVERIGUAR COMO PASAR EL EPOCH DE UN LADO A OTRO
    Y ASÍ PODER CREAR EL OBJETO DE LA CLASE SATELITE. TAMBIÉN HACE FALTA ENTENDER BIEN
    DONDE HAY QUE IMPORTAR CADA COSA POR QUE AHORA MISMO TIENES UNOS IMPORTS
    QUE IGUAL NO ESTAN EN EL DOCU CORRECTO
    """