import sys
import src.gui.icons_rc
sys.modules['icons_rc'] = src.gui.icons_rc

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as BaseCanvas
from PyQt5 import QtWidgets, QtCore
import matplotlib.pyplot as plt
from src.gui.MainUI import Ui_MainWindow
from src.gui.sat_params_window import SatParamsWindow
from src.gui.times_window import TimesWindow
from src.gui.sat_info_window import SatInfoWindow
from PyQt5.QtWidgets import QSizePolicy
import src.model.visualization as visualization


plt.ioff()

class TransparentCanvas(BaseCanvas):
    def __init__(self, figure):
        super().__init__(figure)
        self.setAutoFillBackground(False)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setStyleSheet("background: transparent;")


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        # Initiate window
        super().__init__()
        self.setupUi(self)
        
        # Creating canvas inside frame to plot graphs
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.graph_frame)
        self.horizontalLayout.setObjectName("horizontalLayout")
        
        self.figure = Figure(facecolor = "None")
        self.figure.patch.set_alpha(0)
        self.canvas = TransparentCanvas(self.figure)
        self.horizontalLayout.addWidget(self.canvas)
        # End of canvas
        
        # Set up button functionality
        self.new_sat.clicked.connect(self.open_sat)
        self.sim_timer.clicked.connect(self.open_times)
        self.run.clicked.connect(self.run_project)
        self.sat_info.clicked.connect(self.open_info)
        
                
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
        
    def open_info(self):
        # Open satellite information window
        self.sat_infoWin = SatInfoWindow(self)
        self.sat_infoWin.show()
        
    def update_canvas(self, fig):
        fig.patch.set_facecolor("none")
        fig.patch.set_alpha(0)
        
        for ax in fig.axes:
            ax.patch.set_facecolor("none")
            ax.patch.set_alpha(0)
           
        new_canvas = TransparentCanvas(fig)
        self.horizontalLayout.replaceWidget(self.canvas, new_canvas)
        self.canvas.setParent(None)
        self.canvas = new_canvas
        
        self.canvas.draw()
        
    def run_project(self):
        # Check that a satellite has been defined, then run
        sat0 = getattr(self, 'sat0', None)
        sat1 = getattr(self, 'sat1', None)
        sat2 = getattr(self, 'sat2', None)
        sat3 = getattr(self, 'sat3', None)
        sat4 = getattr(self, 'sat4', None)
        
        self.sats = [s for s in [sat0, sat1, sat2, sat3, sat4] if s is not None]
        if len(self.sats) == 0:
            QtWidgets.QMessageBox().warning(self, "Missing Satellite", 
                    "Please define one or more satellites first")
            return
        
        if self.vis_ops.currentIndex() == 0:
            fig, _ = visualization.plot_ground_tracks(self.sats, self.times)
            fig.patch.set_facecolor('none')
            self.update_canvas(fig)
            
        elif self.vis_ops.currentIndex() == 1:
            fig, _ = visualization.plot_orbits(self.sats, self.times)
            for ax in fig.axes:
                ax.set_facecolor('none')
            fig.patch.set_facecolor('none')
            self.update_canvas(fig)
        
        elif self.vis_ops.currentIndex() == 2:
            if len(self.sats) == 1:
                QtWidgets.QMessageBox().warning(self, "Missing Satellite", 
                        "More than one satellite is required for this plot")
                return
            tolerance = 3000000
            fig, _ = visualization.plot_cross_sat(self.sats, self.times, tolerance)
            fig.patch.set_facecolor('none')
            self.update_canvas(fig)

from qt_material import apply_stylesheet
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    
    # 1) load the material theme
    apply_stylesheet(app, theme="dark_blue.xml")
    
    # 2) grab the theme’s QSS
    base_qss = app.styleSheet()

    override = override = r"""
    /* GENERAL EDITS */
    * {
      font-size: 16pt !important;
    }
    
    
    /* BUTTON EDITS */
    /* change button font sizes to be bigger */
    QPushButton{
        font-size:20pt !important;
        background-color: transparent !important;
    }
    
    /* add hover effects to buttons */
    QPushButton:hover, QPushButton:focus {
        background-color: rgba(0, 0, 255, 0.2) !important;
        font-size: 21pt !important;
    }
    
    /* only run button goes green */
    QPushButton#run {
      color: rgb(0, 170, 0) !important;
      border: 2px solid rgb(0, 170, 0) !important;
      background-color: transparent !important;
    }
    
    QPushButton#run:hover, QPushButton#run:focus {
        background-color: rgba(0, 170, 0, 0.2) !important;
    }
    
    /* Change cancel buttons to be red */
    QPushButton#sat_cancel {
        color: rgb(255, 0, 0) !important;
        border: 2px solid rgb(255, 0, 0) !important;
        background-color: transparent !important;
    }
    
    QPushButton#sat_cancel:hover, QPushButton#sat_cancel:focus {
        background-color: rgba(255, 0, 0, 0.2) !important;
    }
    
    /* Change cancel buttons to be red */
    QPushButton#times_cancel {
        color: rgb(255, 0, 0) !important;
        border: 2px solid rgb(255, 0, 0) !important;
        background-color: transparent !important;
    }
    
    QPushButton#times_cancel:hover, QPushButton#times_cancel:focus {
        background-color: rgba(255, 0, 0, 0.2) !important;
    }
    
    
    /* LABEL EDITS*/
    /* set label font size to 20pt */
    QLabel{
        font-size: 20pt !important
    }
    
    
    /* MISC EDITS */
    /* make sure icons actually draw at a reasonable size */
    QPushButton, QToolButton {
      qproperty-iconSize: 60px 60px !important;
    }
    
    /* style all combo‐boxes with transparent bg, blue rounded border, centered & blue text */
    QComboBox {
        background-color: transparent !important;
        font-size: 20pt !important
    }
    
    /* hide all QFrame/QGroupBox borders */
    QFrame, QGroupBox {
      border: none !important;
      background-color: transparent !important;
    }
    
    
    
    QWidget#centralwidget {
        background-image: url(:/icons/stars.png) !important;
        background-repeat: no-repeat !important;
        background-position: center !important;
        background-attachment: fixed !important;
        border-image: url(:/icons/stars.png) 0 0 0 0 stretch stretch;
    }
    """
    
    app.setStyleSheet(base_qss + override)
    #app.setStyleSheet("")
    w = MainWindow()
    w.show()
    app.exec_()
    
    """

    
    
    QUEDA PENDIENTE AÑADIR FUNCIONALIDAD DE SIMULACIÓN, SOLUCIONAR LO DEL BACKGROUND
    QUIZÁS CAMBIAR LOS COLORES DE LOS SATELITES PARA QUE SEAN MÁS CLAROS Y QUE 
    ASÍ SE VEAN MEJOR EN CONTRASTE CON EL BACKGROUND OSCURO
    """
