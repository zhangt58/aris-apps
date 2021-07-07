"""Template arguments:

- pkg_name: Python package name, default if mypkg
- exe_name: Executable name for the GUI app, default is myApp

"""
from setuptools import setup


PKG_NAME = "aris"
EXE_NAME = "beam_ellipse"


install_requires = []
def set_entry_points():
    r = {}
    r['gui_scripts'] = [
        f'{EXE_NAME}={PKG_NAME}.myapp:run',
    ]
    return r

def readme():
    with open('README.md', 'r') as f:
        return f.read()

def read_license():
    with open('LICENSE') as f:
        return f.read()

setup(
    name=f'{PKG_NAME}',
    version='0.1.0',
    description='My app created with phantasy framework',
    long_description=readme(),
    license=read_license(),
    packages=[f'{PKG_NAME}.myapp',
              f'{PKG_NAME}.myapp.ui',
              f'{PKG_NAME}'
    ],
    package_dir={
        f'{PKG_NAME}.myapp': 'src/myApp',
        f'{PKG_NAME}.myapp.ui': 'src/myApp/ui',
        f'{PKG_NAME}': 'src',
    },
    entry_points=set_entry_points(),
    install_requires=install_requires,
)