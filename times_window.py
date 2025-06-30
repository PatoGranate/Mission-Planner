from PyQt5 import QtWidgets
from SimTimesUI import Ui_MainWindow
from org.orekit.time import AbsoluteDate, TimeScalesFactory

class TimesWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setupUi(self)
        self.times_cancel.clicked.connect(self.close)
        self.times_confirm.clicked.connect(self.times_create)
        
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
        
        utc = TimeScalesFactory.getUTC()
        common_epoch = AbsoluteDate(year, month, day, hour, minute, second, utc)
        print(common_epoch)
        return common_epoch