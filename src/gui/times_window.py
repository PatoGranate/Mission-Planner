from PyQt5 import QtWidgets
from src.gui.SimTimesUI import Ui_MainWindow
from PyQt5.QtCore import QDate, QTime, QDateTime
from src.model.satellite_utils import get_times

class TimesWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent = None):
        # Initialize window and set up button actions
        super().__init__(parent)
        self.setupUi(self)
        self.times_cancel.clicked.connect(self.close)
        self.times_confirm.clicked.connect(self.times_create)
        self.actionReset.triggered.connect(self.reset)
        
        
    def times_create(self):
        # Take user inputs
        duration_input = self.set_duration.text()
        timestep_input = self.set_timestep.text()
        datetime_input = self.set_epoch.dateTime()
        
        year   = datetime_input.date().year()
        month  = datetime_input.date().month()
        day    = datetime_input.date().day()
        hour   = datetime_input.time().hour()
        minute = datetime_input.time().minute()
        second = float(datetime_input.time().second())
        
        # Check that values are numerical inputs
        try:
            duration = int(duration_input)
            timestep = int(timestep_input)
        except ValueError:
            QtWidgets.QMessageBox.warning(self, 
            "Invalid input", "Duration or Timestep are empty or not numerical")
            return
        
        # Check that duration and timestep are positive
        if duration <= 0 or timestep <= 0:
            QtWidgets.QMessageBox.warning(self,
            "Invalid input", "Duration and timestep must not be 0")
            return
        
        # Check that timestep is smaller than duration
        if timestep >= duration:
            QtWidgets.QMessageBox.warning(self,
            "Invalid input", "Duration must be greater than timestep")
            return
        
        # Check whether times are being created or edited
        parent = self.parent()
        if hasattr(parent, "date"):
            reply = QtWidgets.QMessageBox.question(
                self,
                "New times?",
                "Defining a new simualtion time will delete the existing satellites. Continue?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            if reply != QtWidgets.QMessageBox.Yes:
                return
        
        # Save duration, timestep and date for labelling in SatInfo window
        parent.duration = duration
        parent.timestep = timestep
        parent.epoch = datetime_input
        
        # Generate epoch and times
        date = [year, month, day, hour, minute, second]
        times = get_times(duration, timestep)
        
        parent.date = date
        parent.times = times
        
        # Close window when confirmed
        self.close()
        
    def reset(self):
        # Reset user inputs to default
        dt = QDateTime(QDate(2000, 1, 1), QTime(0, 0, 0))
        self.set_epoch.setDateTime(dt)
        self.set_duration.clear()
        self.set_timestep.clear()