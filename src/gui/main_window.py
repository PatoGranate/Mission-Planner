import sys
import src.gui.icons_rc
sys.modules['icons_rc'] = src.gui.icons_rc

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as BaseCanvas
from PyQt5 import QtWidgets, QtCore
from qt_material import apply_stylesheet
plt.ioff()

import src.model.visualization as visualization
from src.gui.MainUI import Ui_MainWindow
from src.gui.sat_params_window import SatParamsWindow
from src.gui.times_window import TimesWindow
from src.gui.sat_info_window import SatInfoWindow
from src.gui.sim_info_window import SimInfoWindow
from src.gui.gs_params_window import GSParamsWindow

# Canvas is used to plot matplotlib on QFrame
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
        self.tolerance = 3000000
        self.tolerance2 = 1000000
        
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
        self.sat_info.clicked.connect(self.open_sat_info)
        self.sim_info.clicked.connect(self.open_sim_info)
        self.new_location.clicked.connect(self.open_gs)
        
        
    def open_sat(self):
        # Check that an epoch has been created before opening the sat window
        try:
            self.date
        except AttributeError:
            QtWidgets.QMessageBox().warning(self, "Missing Epoch", 
                    "Please set simulation times first")
            return
        
        # Open sat window
        self.satWin = SatParamsWindow(self)
        self.satWin.show()
        
    def open_gs(self):
        # Check that an epoch has been created before opening the gs window
        try:
            self.date
        except AttributeError:
            QtWidgets.QMessageBox().warning(self, "Missing Epoch", 
                    "Please set simulation times first")
            return
        
        # Open gs window
        self.gsWin = GSParamsWindow(self)
        self.gsWin.show()
        
    def open_times(self):
        # Open times window
        self.timesWin = TimesWindow(self)
        self.timesWin.show()
        
    def open_sat_info(self):
        # Open satellite information window
        self.sat_infoWin = SatInfoWindow(self)
        self.sat_infoWin.show()
        
    def open_sim_info(self):
        # Open simulation information window
        self.sim_infoWin = SimInfoWindow(self)
        self.sim_infoWin.show()
        
    def update_canvas(self, fig):
        # When called, change the current canvas to display a new figure
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
        
    # Compute and plot selected information
    def run_project(self):
        # Check which satellites have been defined
        sat0 = getattr(self, 'sat0', None)
        sat1 = getattr(self, 'sat1', None)
        sat2 = getattr(self, 'sat2', None)
        sat3 = getattr(self, 'sat3', None)
        sat4 = getattr(self, 'sat4', None)
        
        # Create a list of existing satellites
        self.sats = [s for s in [sat0, sat1, sat2, sat3, sat4] if s is not None]
        
        # Repeat for ground stations
        gs0 = getattr(self, 'gs0', None)
        gs1 = getattr(self, 'gs1', None)
        gs2 = getattr(self, 'gs2', None)
        gs3 = getattr(self, 'gs3', None)
        gs4 = getattr(self, 'gs4', None)
        
        self.gss = [g for g in [gs0, gs1, gs2, gs3, gs4] if g is not None]
        
        # If no satellites warning
        if len(self.sats) == 0:
            QtWidgets.QMessageBox().warning(self, "Missing Satellite", 
                    "Please define one or more satellites first")
            return
        
        # Reset progress bar when changing from simulation to another plot
        if getattr(self, "anim", None):
            try:
                self.anim.event_source.stop()
            except Exception:
                pass
            self.simulation_progress.reset()
        
        # Ground tracks option
        if self.vis_ops.currentIndex() == 0:
            fig, _ = visualization.plot_ground_tracks(self.sats, self.gss, self.times)
            self.update_canvas(fig)
            
        # 3D orbit
        elif self.vis_ops.currentIndex() == 1:
            fig, _ = visualization.plot_orbits(self.sats, self.gss, self.times)
            for ax in fig.axes:
                ax.set_facecolor('none')
                ax.set_axis_off()
                
            fig.patch.set_facecolor('none')
            self.update_canvas(fig)
        
        # Satellite distances
        elif self.vis_ops.currentIndex() == 2:
            if len(self.sats) == 1:
                QtWidgets.QMessageBox().warning(self, "Missing Satellite", 
                        "More than one satellite is required for this plot")
                return
            
            fig, _ = visualization.plot_cross_sat(self.sats, self.times, self.tolerance)
            fig.patch.set_facecolor('none')
            self.update_canvas(fig)
         
        # Orbit + viewing animation
        elif self.vis_ops.currentIndex() == 3:
            self.sim_info.setEnabled(True)
            self.anim = visualization.animate_sat_attitude(self.sats, self.gss,
                self.times, self.tolerance, self.tolerance2, progress_callback = self.progress_callback)
            fig = self.anim._fig
            fig.patch.set_color('none')
            
            for ax in fig.axes:
                ax.set_facecolor('none')
                ax.set_axis_off()
                
            fig.patch.set_facecolor('none')

            self.update_canvas(fig)
            
            self.anim._init_draw()
            old_timer = self.anim.event_source
            new_timer = self.canvas.new_timer(interval = old_timer.interval)
            new_timer.add_callback(self.anim._step)
            self.anim.event_source = new_timer
            
            new_timer.start()
    
    # Progress bar def
    def progress_callback(self, i, N):
        self.simulation_progress.setMaximum(N-1)
        self.simulation_progress.setValue(i)

# When run apply:
def main():
    app = QtWidgets.QApplication([])
    
    # Load and apply stylesheet
    apply_stylesheet(app, theme="dark_blue.xml")
    base_qss = app.styleSheet()

    # Apply overriding edits
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
    QPushButton#sat_cancel, QPushButton#gs_cancel{
        color: rgb(255, 0, 0) !important;
        border: 2px solid rgb(255, 0, 0) !important;
        background-color: transparent !important;
    }
    
    
    QPushButton#sat_cancel:hover, QPushButton#sat_cancel:focus, QPushButton#gs_cancel:hover, QPushButton#gs_cancel:focus {
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
    /* set label font size to 16pt */
    QLabel{
        font-size: 16pt !important
    }
    
    
    /* MISC EDITS */
    /* make sure icons actually draw at a reasonable size */
    QPushButton, QToolButton {
      qproperty-iconSize: 80px 80px !important;
    }
    
    /* style all combo‐boxes with transparent bg, blue rounded border, centered & blue text */
    QComboBox {
        background-color: transparent !important;
        font-size: 20pt !important
    }
    
    /* resize combo boxes in sat_params*/
    QComboBox#sat_chooser, QComboBox#set_anomaly_type{
        font-size: 16pt !important
    }
    
    
    /* hide all QFrame/QGroupBox borders */
    QFrame, QGroupBox {
      border: none !important;
      background-color: transparent !important;
    }
    
    /* progress bar visual edits */
    QProgressBar#simulation_progress {
    background-color: rgba(255, 255, 255, 20);
    border: none;
    border-radius: 5px;
    text-align: center;
    }
    
    
    /* BACKGROUND EDITS */
    QWidget#centralwidget {
        background-image: url(:/icons/stars.png) !important;
        background-repeat: no-repeat !important;
        background-position: center !important;
        background-attachment: fixed !important;
        border-image: url(:/icons/stars.png) 0 0 0 0 stretch stretch;
    }
    
    QTextEdit, QPlainTextEdit {
        color: #E6E6E6 !important;
        }
    """
    plt.close()
    app.setStyleSheet(base_qss + override)
    w = MainWindow()
    w.show()
    app.exec_()
    plt.close('all')