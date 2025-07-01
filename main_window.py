import sys
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5 import QtWidgets
import matplotlib.pyplot as plt
from MainUI import Ui_MainWindow
from sat_params_window import SatParamsWindow
from times_window import TimesWindow

import visualization

plt.ioff()

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        # Initiate window
        super().__init__()
        self.setupUi(self)
        
        # Creating canvas inside frame to plot graphs
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.graph_frame)
        self.horizontalLayout.setObjectName("horizontalLayout")
        
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        
        self.horizontalLayout.addWidget(self.canvas)
        # End of canvas
        
        # Set up button functionality
        self.new_sat.clicked.connect(self.open_sat)
        self.sim_timer.clicked.connect(self.open_times)
        self.run.clicked.connect(self.run_project)
    def open_sat(self):
        # Check that an epoch has been created before opening the sat window
        try:
            date = self.date
        except AttributeError:
            QtWidgets.QMessageBox().warning(self, "Missing Epoch", 
                    "Please set simulation times first")
            return
        
        # Open sat window
        self.satWin = SatParamsWindow(self)
        self.satWin.show()
        
    def open_times(self):
        # Open times window
        self.timesWin = TimesWindow(self)
        self.timesWin.show()
        
    def update_canvas(self, fig):
        self.horizontalLayout.removeWidget(self.canvas)
        self.canvas.setParent(None)
        
        self.canvas = FigureCanvas(fig)
        self.horizontalLayout.addWidget(self.canvas)
        self.canvas.draw()
        
    def run_project(self):
        # Check that a satellite has been defined, then run
        try:
            date = self.sat1
        except AttributeError:
            QtWidgets.QMessageBox().warning(self, "Missing Satellite", 
                    "Please define one or more satellites first")
            return
        
        if self.vis_ops.currentIndex() == 0:
            fig, _ = visualization.plot_ground_tracks([self.sat1], self.times)
            self.update_canvas(fig)
        elif self.vis_ops.currentIndex() == 1:
            fig, _ = visualization.plot_orbits([self.sat1], self.times)
            self.update_canvas(fig)

if __name__ == "__main__":
    # If script is rund irectly open the main window
    app = QtWidgets.QApplication([])
    w = MainWindow()
    w.show()
    app.exec_()

