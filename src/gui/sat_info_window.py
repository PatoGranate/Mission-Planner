from PyQt5 import QtWidgets
from src.gui.SatInfoUI import Ui_MainWindow

class SatInfoWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent = None):
        # Initialize window and set up button actions
        super().__init__(parent)
        self.setupUi(self)