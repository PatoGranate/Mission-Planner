### Pre-requisites
Have Spyder and Orekit installed within the correct environment

### Starting
Orekit can be used in Python using a wrapper but is really a Javascript program, so a Javascript machine must be initialized at the beginning of every script in order for Orekit to run.

``` python
import orekit
orekit.initVM()
```

Many Orekit classes require specific data to run. This data is stored inside "orekit-data.zip", and must be configured to be used. 

```python
from orekit.pyhelpers import setup_orekit_curdir
setup_orekit_curdir()
```

The above code loads the Orekit data files from the current directory - assumes that your script is in the same place as the data. The second line automatically searches for this data in the current directory and configures Orekit to use it. It is important to note that the zip folder must be saved exactly as orekit-data.zip, as setup_orekit_curdir() looks for this name and won't recognize anything else.

Generally, we want to use the [[02-Keplerian_Model|Keplerian model]] to propagate orbits, although others can be used.




