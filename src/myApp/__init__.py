# -*- coding: utf8 -*-

import sys

from phantasy_ui import QApp as QApplication

from .app import MyAppWindow

__version__ = '0.1'
__title__ = 'Beam Ellipse Drawing App'


def run(cli=False):
    app = QApplication(sys.argv)
    w = MyAppWindow(version=__version__)
    w.setWindowTitle(__title__)
    w.show()
    if cli:
        app.exec_()
    else:
        sys.exit(app.exec_())
