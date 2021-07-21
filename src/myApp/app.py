#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Template Python module generated based on 'app_template', 'phantasy-ui'
is required to make it executable as a PyQt5 app.

Created by: makeBasePyQtApp.

An example to create an app template:

>>> makeBasePyQtApp --app my_great_app --template AppWindow

Show the available templates:

>>> makeBasePyQtApp -l
"""

from phantasy_apps.allison_scanner.data import draw_beam_ellipse_with_params
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMainWindow

from phantasy import MachinePortal
from phantasy_ui import BaseAppForm

from .ui.ui_app import Ui_MainWindow

MACH, SEGM = "ARIS", "F1"
ARIS_MP = MachinePortal(MACH, SEGM)
ARIS_LAT = ARIS_MP.work_lattice_conf


class MyAppWindow(BaseAppForm, Ui_MainWindow):
    def __init__(self, version, **kws):
        super(self.__class__, self).__init__()

        # app version, title
        self.setAppVersion(version)
        self.setAppTitle("My App")

        # app info in about dialog
        # self.app_about_info = "About info of My App."

        # UI
        self.setupUi(self)
        self.postInitUi()

        # post init
        self._post_init()

    def _post_init(self):
        """Initialize UI, user customized code put here.
        """
        # Fill comboBox quad1_name_cbb with all quad names.
        quad_name_list = [i.name for i in ARIS_MP.get_elements(type='QUAD')]
        self.quad1_name_cbb.addItems(quad_name_list)
        # connect currentTextChanged signal to slot: on_quad1_name_changed()
        self.quad1_name_cbb.currentTextChanged.connect(
            self.on_quad1_name_changed)
        # connect valueChanged signal of quad1_grad_dsbox to on_quad1_grad_changed()
        self.quad1_grad_dsbox.valueChanged.connect(self.on_quad1_grad_changed)
        # initialize quad1_name_cbb
        self.quad1_name_cbb.currentTextChanged.emit(quad_name_list[0])

    @pyqtSlot('QString')
    def on_quad1_name_changed(self, name: str) -> None:
        """When the current selected quad name is changed, do:
        show the current setting of the selected quad on quad1_grad_dsbox.
        when set value to quad1_grad_dsbox, disconnect valueChanged and
        reconnect, to avoid unnecessary trigging.
        """
        self.quad_selected = ARIS_MP.get_elements(name=name)[0]
        self.quad1_grad_dsbox.valueChanged.disconnect()
        self.quad1_grad_dsbox.setValue(
            self.quad_selected.current_setting('B2'))
        self.quad1_grad_dsbox.valueChanged.connect(self.on_quad1_grad_changed)

    @pyqtSlot(float)
    def on_quad1_grad_changed(self, grad: float) -> None:
        """When the setting of the selected quad is changed, do:
        1. print the setting of selected quad
        2. update drawing with online simulated results
        """
        q = self.quad_selected.name
        print(f"'{q}' setting is: {grad} T/m")
        # draw ellipse
        self.update_drawing()

    def update_drawing(self):
        """This is the routine to update the figure with the updated drawing.
        Here I'm drawing the beam envelop along the entire beamline, try to
        replace with your routine for beam ellipse drawing.
        """
        try:
            self.draw_ellipse
        except NotImplementedError:
            self.draw_envelope()

    def draw_envelope(self):
        """Draw beam envelop onto the figure area.
        """
        # online simulation
        ARIS_LAT.sync_settings()
        _, fm = ARIS_LAT.run()
        r, _ = fm.run(monitor='all')
        results_dict = fm.collect_data(r, 'pos', 'xrms', 'yrms')
        pos = results_dict['pos']
        xrms = results_dict['xrms']
        yrms = results_dict['yrms']
        # update drawing
        # Note: matplotlibbaseWidget is used here for generic drawing,
        # for curve visualization, matplotlibCurveWidget is a better choice.
        self.matplotlibbaseWidget.clear_figure()
        self.matplotlibbaseWidget.axes.plot(
            pos,
            xrms,
            'b-',
            pos,
            yrms,
            'r-',
        )
        self.matplotlibbaseWidget.update_figure()

    def draw_ellipse(self):
        #raise NotImplementedError

        """Draw x and y beam ellipse onto the figure area.
        """
        ARIS_LAT.sync_settings()
        _, fm = ARIS_LAT.run()
        r, s = fm.run(monitor='all')
        keys_x = [i.format(u='x') for i in ('{u}_cen', '{u}p_cen', '{u}_rms', '{u}p_rms', 'emit_{u}', 'emitn_{u}','alpha_{u}', 'beta_{u}', 'gamma_{u}', 'total_intensity')]
        vals_x = (s.xcen, s.xpcen, s.xrms, s.xprms, s.xemittance, s.xnemittance,
        s.xtwiss_alpha, s.xtwiss_beta, (s.xtwiss_alpha**2+1)/s.xtwiss_beta, 1)
        params_x = dict(zip(keys_x, vals_x))
        self.matplotlibbaseWidget.clear_figure()
        draw_beam_ellipse_with_params(params_x, color='b', factor=4, ax=self.matplotlibbaseWidget.axes, xoy='x', fill='g', anote=False)
        self.matplotlibbaseWidget.update_figure()

        keys_y = [i.format(u='y') for i in ('{u}_cen', '{u}p_cen', '{u}_rms', '{u}p_rms', 'emit_{u}', 'emitn_{u}','alpha_{u}', 'beta_{u}', 'gamma_{u}', 'total_intensity')]
        vals_y = (s.ycen, s.ypcen, s.yrms, s.yprms, s.yemittance, s.ynemittance,
        s.ytwiss_alpha, s.ytwiss_beta, (s.ytwiss_alpha**2+1)/s.ytwiss_beta, 1)
        params_y = dict(zip(keys_y, vals_y))
        self.matplotlibbaseWidget_1.clear_figure()
        draw_beam_ellipse_with_params(params_y, color='b', factor=4, ax=self.matplotlibbaseWidget_1.axes, xoy='y', fill='g', anote=True)
        self.matplotlibbaseWidget_1.update_figure()

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys

    version = 0.1
    app = QApplication(sys.argv)
    w = MyAppWindow(version)
    w.show()
    w.setWindowTitle("This is an app from template")
    sys.exit(app.exec_())
