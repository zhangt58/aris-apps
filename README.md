# ARIS-VA-Ellipse

This is a high-level physics application (HLA) built upon ``phantasy`` framework.
The EPICS controls environment is provided by ARIS virtual accelerator (VA)
(pre-separator), the UI skeleton is provided by ``phantasy-ui``, and
the device controls is provided by ``phantasy``.

This repository keeps the generated project files as the start point of the
development of a HLA to visualize the beam ellipse drawing with the simulation
results from FLAME model. This HLA also works with the real machine.

## Initialize App Skeleton

Be sure to update the required packages, do ``sudo apt update && sudo apt upgrade`` in the
Terminal.

```shell
# the working directory is /tmp
$ makeBasePyQtApp --app aris-va-ellipse --template AppWindow
What's the name of this package? (default: mypkg) aris_apps
What's the name of the app, also the command to run it? (default: myApp) online_model
Generating aris-va-ellipse with template AppWindow...
Successfully made an base app at '/tmp/aris-va-ellipse'.
What to do next:
> Install package: cd /tmp/aris-va-ellipse; make deploy
> Run app by executing online_model
> Edit .ui file with 'frib_designer', and the .py files.
> Update the package: cd /tmp/aris-va-ellipse; make redeploy
> Happy Coding!
```

## Start ARIS VA
Set environmental variable ``PHANTASY_CONFIG_DIR`` in your ``~/.bashrc`` file persistently to point to the location where keeps the VA configuration files, e.g.:
```shell
export PHANTASY_CONFIG_DIR=$HOME/phantasy-machines
```
Start VA from Terminal:
```shell
phytool flame-vastart --mach ARIS_VA --subm F1
```

## Communicate with ARIS VA
Use ``phantasy`` to control the VA in an interactively way in Python terminal.
```python
from phantasy import MachinePortal

# Instantiate the portal of the machine
mp = MachinePortal("ARIS_VA", "F1")

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
2. Convert .ui files to .py files by executing `make` in the ui folder;
3. In the project root folder, type `make redeploy` to update the package and execute the command
   (i.e. ``online_model``) to run the app, or just type `make run`;
4. Uninstall the package by: ``pip uninstall <pkg_name>`` (for this case, pkg_name is `aris_apps`),
   or type `make uninstall`.

## Note
If the command ``online_model`` cannot be found, you'll have to update ``PATH`` env, i.e.
```shell
echo 'export PATH=$HOME/.local/bin:$PATH' >> ~/.bashrc
```
