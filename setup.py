"""Template arguments:

- pkg_name: Python package name, default if mypkg
- exe_name: Executable name for the GUI app, default is myApp

"""
from setuptools import setup


PKG_NAME = "aris_apps"
EXE_NAME = "online_model"


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


setup(
    name=f'{PKG_NAME}',
    version='1.0.0',
    description='Physics online simulator with FRIB built upon PHANTASY framework',
    long_description=readme(),
    long_description_content_type='text/markdown',
    license="GPL-2+",
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
