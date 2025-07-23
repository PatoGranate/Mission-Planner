# Initialise virtual machine so that orekit commands work
import orekit
orekit.initVM()

# Allows machine to search for orekit-data.zip within current directory
from orekit.pyhelpers import setup_orekit_curdir
from pathlib import Path

# Point to data folder:
data_dir = Path(__file__).parent.parent.parent / "data" / "orekit-data-master"
setup_orekit_curdir(str(data_dir))

# Import main_window to run gui
from src.gui.main_window import main

# Run gui
if __name__ == "__main__":
    main()

#cd "C:\Users\pelay\OneDrive - University of Bath\Experiences\SuperSharp\Project"
#cd "C:\Users\pelay\OneDrive - University of Bath\Experiences\SuperSharp\Project\src\gui"