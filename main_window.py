import sys
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5 import QtWidgets

from MainUI import Ui_MainWindow
from sat_params_window import SatParamsWindow
from times_window import TimesWindow

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        # Creating canvas inside frame to plot graphs
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.graph_frame)
        self.horizontalLayout.setObjectName("horizontalLayout")
        
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        
        self.horizontalLayout.addWidget(self.canvas)
        # End of canvas
        
        self.new_sat.clicked.connect(self.open_sat)
        self.sim_timer.clicked.connect(self.open_times)

        
    def open_sat(self):
        try:
            date = self.date
        except AttributeError:
            QtWidgets.QMessageBox().warning(self, "Missing Epoch", 
                    "Please set simulation times first")
            return
        
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

