# ARIS-VA-Ellipse

This is a high-level physics application built upon ``phantasy`` framework.
The EPICS controls environment is provided by ARIS virtual accelerator (VA)
(pre-separator), the UI skeleton is provided by ``phantasy-ui``, and
the device controls is provided by ``phantasy``.

## Initialize App Skeleton

```shell
makeBasePyQtApp --app myApp --template AppWindow
```

## Start ARIS VA
Set environmental variable ``PHANTASY_CONFIG_DIR`` in your ``~/.bashrc`` file persistently to point to the location where keeps the VA configuration files, e.g.:
```shell
export PHANTASY_CONFIG_DIR=$HOME/phantasy-machines
```
Start VA from Terminal:
```shell
phytool flame-vastart --mach ARIS --subm F1
```

## Communicate with ARIS VA
Use ``phantasy`` to control the VA in an interactively way in Python terminal.
```python
from phantasy import MachinePortal

# Instantiate the portal of the machine
mp = MachinePortal("ARIS", "F1")

# Find the device by type, see the doc of mp.get_elements()
# first quad could be found by:
quad0 = mp.get_elements(type='QUAD')[0]

# Explore the attributes of quad0 through dot syntax
# e.g. the current gradient value could be got by .B2
quad0.B2

# Set the B2 field by assigning with a new value, e.g.
quad0.B2 = 10
```

## Development Workflow
1. Edit .ui file in ``frib_designer``, which is a command tool from package ``phantasy_ui``;
2. Convert .ui file to .py file with ``pyuic5``: ``pyuic5 ui_app.ui -o ui_app.py -x``;
3. Run app by ``python3 app.py``.
