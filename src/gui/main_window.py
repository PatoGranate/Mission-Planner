import sys
import src.gui.icons_rc
sys.modules['icons_rc'] = src.gui.icons_rc

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5 import QtWidgets
import matplotlib.pyplot as plt
from src.gui.MainUI import Ui_MainWindow
from src.gui.sat_params_window import SatParamsWindow
from src.gui.times_window import TimesWindow
from PyQt5.QtWidgets import QSizePolicy
import src.model.visualization as visualization


plt.ioff()

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        # Initiate window
        super().__init__()
        self.setupUi(self)

        # Creating canvas inside frame to plot graphs
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.graph_frame)
        self.horizontalLayout.setObjectName("horizontalLayout")
        
        self.figure = Figure(facecolor = "None")
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
            fig.patch.set_facecolor('none')
            self.update_canvas(fig)
        elif self.vis_ops.currentIndex() == 1:
            fig, _ = visualization.plot_orbits([self.sat1], self.times)
            for ax in fig.axes:
                ax.set_facecolor('none')
            fig.patch.set_facecolor('none')
            self.update_canvas(fig)

from qt_material import apply_stylesheet
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    
    # 1) load the material theme
    apply_stylesheet(app, theme="light_blue.xml")
    
    # 2) grab the theme’s QSS
    base_qss = app.styleSheet()

    override = override = r"""
    /* force 18pt everywhere */
    * {
      font-size: 18pt !important;
    }
    
    QPushButton:hover, QPushButton:focus {
        background-color: rgba(0, 0, 255, 0.1) !important;
    }
    
    /* hide all QFrame/QGroupBox borders */
    QFrame, QGroupBox {
      border: none !important;
      background-color: transparent !important;
    }
    
    /* make sure icons actually draw at a reasonable size */
    QPushButton, QToolButton {
      qproperty-iconSize: 60px 60px !important;
    }
    
    /* only run button goes green */
    QPushButton#run {
      color: rgb(0, 170, 0) !important;
      border: 2px solid rgb(0, 170, 0) !important;
      background-color: transparent !important;
    }
    
    QPushButton#run:hover, QPushButton#run:focus {
        background-color: rgba(0, 170, 0, 0.1) !important;
    }
    
    /* Change cancel buttons to be red */
    QPushButton#sat_cancel {
        color: rgb(255, 0, 0) !important;
        border: 2px solid rgb(255, 0, 0) !important;
        background-color: transparent !important;
    }
    
    QPushButton#sat_cancel:hover, QPushButton#sat_cancel:focus {
        background-color: rgba(255, 0, 0, 0.1) !important;
    }
    
    /* Change cancel buttons to be red */
    QPushButton#times_cancel {
        color: rgb(255, 0, 0) !important;
        border: 2px solid rgb(255, 0, 0) !important;
        background-color: transparent !important;
    }
    
    QPushButton#times_cancel:hover, QPushButton#times_cancel:focus {
        background-color: rgba(255, 0, 0, 0.1) !important;
    }
    """
    app.setStyleSheet(base_qss + override)
    #app.setStyleSheet("")
    w = MainWindow()
    w.show()
    app.exec_()

