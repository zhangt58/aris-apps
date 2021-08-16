# -*- coding: utf8 -*-

import sys

from phantasy_ui import QApp as QApplication

from .app import MyAppWindow

__version__ = '1.0.1'
__title__ = 'A New Online Modeling App'
__authors__ = "Tong Zhang"
__copyright__ = "(c) 2021, Facility for Rare Isotope beams," \
                " Michigan State University"
__contact__ = "Tong Zhang <zhangt@frib.msu.edu>"


def run(cli=False):
    app = QApplication(sys.argv)
    w = MyAppWindow(version=__version__)
    w.setWindowTitle(__title__)
    w.show()
    if cli:
        app.exec_()
    else:
        sys.exit(app.exec_())
