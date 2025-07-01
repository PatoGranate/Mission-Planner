from PyQt5 import QtWidgets
from SimTimesUI import Ui_MainWindow
from PyQt5.QtCore import QDate, QTime, QDateTime

class TimesWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setupUi(self)
        self.times_cancel.clicked.connect(self.close)
        self.times_confirm.clicked.connect(self.times_create)
        self.actionReset.triggered.connect(self.reset)
        
    def times_create(self):
        duration_input = self.set_duration.text()
        timestep_input = self.set_timestep.text()
        datetime_input = self.set_epoch.dateTime()
        
        year   = datetime_input.date().year()
        month  = datetime_input.date().month()
        day    = datetime_input.date().day()
        hour   = datetime_input.time().hour()
        minute = datetime_input.time().minute()
        second = float(datetime_input.time().second())
        
        try:
            duration = int(duration_input)
            timestep = int(timestep_input)
        except ValueError:
            QtWidgets.QMessageBox.warning(self, 
            "Invalid input", "Duration or Timestep are empty or not numerical")
            return
        
        parent = self.parent()
        if hasattr(parent, "date"):
            reply = QtWidgets.QMessageBox.question(
                self,
                "New Epoch?",
                "Defining a new epoch will delete the existing satellites. Continue?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            if reply != QtWidgets.QMessageBox.Yes:
                return
        
        date = [year, month, day, hour, minute, second]
        
        parent.date = date
        self.close()
        
    def reset(self):
        dt = QDateTime(QDate(2000, 1, 1), QTime(0, 0, 0))
        self.set_epoch.setDateTime(dt)
        self.set_duration.clear()
        self.set_timestep.clear()