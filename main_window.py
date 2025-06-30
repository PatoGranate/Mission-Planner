import sys
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5 import QtWidgets

from MainUI import Ui_MainWindow
from sat_params_window import SatParamsWindow
from times_window import TimesWindow




import orekit
orekit.initVM()

# Allows machine to search for orekit-data.zip within current directory
from orekit.pyhelpers import setup_orekit_curdir
setup_orekit_curdir()





class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        # Creating canvas inside frame to plot graphs
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.fGraph)
        self.horizontalLayout.setObjectName("horizontalLayout")
        
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        
        self.horizontalLayout.addWidget(self.canvas)
        # End of canvas
        
        self.new_sat.clicked.connect(self.open_sat)
        self.sim_timer.clicked.connect(self.open_times)
        
    def open_sat(self):
        self.satWin = SatParamsWindow(self)
        self.satWin.show()
        
    def open_times(self):
        self.timesWin = TimesWindow(self)
        self.timesWin.show()
    

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    w = MainWindow()
    w.show()
    app.exec_()

