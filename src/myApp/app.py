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
import sys

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QEventLoop
from PyQt5.QtCore import QVariant
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QMessageBox

from mpl4qt.widgets import MatplotlibBaseWidget

from phantasy import MachinePortal
from phantasy_ui import BaseAppForm
from phantasy_ui import milli_sleep
from phantasy_ui import get_save_filename
from phantasy_ui.widgets import ProbeWidget
from phantasy_ui.widgets import LatticeWidget
from phantasy_apps.allison_scanner.data import draw_beam_ellipse_with_params

from .utils import ResultsModel
from .utils import TWISS_KEYS_X
from .utils import TWISS_KEYS_Y
from .ui.ui_app import Ui_MainWindow

DEFAULT_MACHINE, DEFAULT_SEGMENT = "ARIS_VA", "F1"

VALID_ELEMENT_TYPES = ("QUAD", "BEND")
DEFAULT_ELEMENT_TYPE = "QUAD"
DEFAULT_FIELD_NAME = "I" # B2


class MyAppWindow(BaseAppForm, Ui_MainWindow):

    # update ellipse drawing size
    ellipse_size_factor_changed = pyqtSignal()

    # loaded machine/segment changed
    lattice_changed = pyqtSignal(QVariant)

    # update layout drawings
    update_layout = pyqtSignal()

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
        #
        self.elem_type_cbb.currentTextChanged.connect(self.on_elem_type_changed)
        self.elem_name_cbb.currentTextChanged.connect(self.on_elem_name_changed)
        self.field_name_cbb.currentTextChanged.connect(self.on_fname_changed)
        self.elemlist_cbb.currentTextChanged.connect(self.on_target_element_changed)

        #
        self._size_factor = self.size_factor_sbox.value()
        self.ellipse_size_factor_changed.connect(self.draw_ellipse)

        # initial vars for FLAME model
        self.results = None
        self.last_bs = None
        self.fm = None

        # Dict of ProbeWidget for selected element and target element
        self._probe_widgets_dict = {}

        # element query
        self.elem_probe_btn.clicked.connect(self.on_probe_elem)
        self.target_elem_probe_btn.clicked.connect(self.on_probe_target_elem)

        # lattice load window
        self.lattice_load_window = None
        self.__mp = None
        self.__lat = None

        # update layout drawings
        self.update_layout.connect(self.draw_layout)
        # lattice changed
        self.lattice_changed.connect(self.on_lattice_changed)

        # connect valueChanged signal of new_cset_dsbox to on_new_cset_changed()
        self.new_cset_dsbox.valueChanged.connect(self.on_new_cset_changed)

        # envelope and trajectory
        self.__init_envelope_plot()
        self.__init_trajectory_plot()

        # ellipse drawing figure configuration
        for o in (self.xlim_x1_lineEdit, self.xlim_x2_lineEdit, ):
            o.setValidator(QDoubleValidator())
            o.textChanged.connect(self.on_xlimit_changed)

        for o in (self.ylim_y1_lineEdit, self.ylim_y2_lineEdit, ):
            o.setValidator(QDoubleValidator())
            o.textChanged.connect(self.on_ylimit_changed)

        self.grid_on_chkbox.toggled.connect(self.on_grid_enabled)
        self.mticks_on_chkbox.toggled.connect(self.on_mticks_enabled)
        self.tight_layout_on_chkbox.toggled.connect(self.on_tightlayout_enabled)

        # preload default machine/segment
        self.__preload_lattice(DEFAULT_MACHINE, DEFAULT_SEGMENT)

    def __preload_lattice(self, mach, segm):
        self.actionLoad_Lattice.triggered.emit()
        self.lattice_load_window.mach_cbb.setCurrentText(mach)
        self.lattice_load_window.seg_cbb.setCurrentText(segm)
        loop = QEventLoop()
        self.lattice_load_window.latticeChanged.connect(loop.exit)
        self.lattice_load_window.load_btn.clicked.emit()
        loop.exec_()
        # auto xyscale (ellipse drawing)
        self.auto_limits()

    def __init_envelope_plot(self):
        """Initialize plot area for beam envelope.
        """
        o = self.envelope_plot
        o.add_curve()
        o.setLineID(0)  # X
        o.setLineColor(QColor('#0000FF'))
        o.setLineLabel("$\sigma_x$")
        o.setLineID(1)  # Y
        o.setLineColor(QColor('#FF0000'))
        o.setLineLabel("$\sigma_y$")

    def __init_trajectory_plot(self):
        """Initialize plot area for beam trajectory.
        """
        o = self.trajectory_plot
        o.add_curve()
        o.setLineID(0)  # X
        o.setLineColor(QColor('#0000FF'))
        o.setLineLabel("$x_0$")
        o.setLineID(1)  # Y
        o.setLineColor(QColor('#FF0000'))
        o.setLineLabel("$y_0$")

    @pyqtSlot('QString')
    def on_fname_changed(self, fname: str) -> None:
        """Selected field name is changed.
        """
        # 1. Update current cset and rd values, initialize new cset.
        self.fld_selected = self.elem_selected.get_field(fname)
        cset = self.fld_selected.current_setting()
        self.new_cset_dsbox.valueChanged.disconnect()
        try:
            self.new_cset_dsbox.setValue(cset)
        except TypeError:
            # current_settings('B2') is None --> most likely VA is not running
            QMessageBox.critical(
                self, "ARIS Beam Ellipse",
                "Cannot reach process variables, please either start virtual accelerator or ensure Channel Access is permittable.",
                QMessageBox.Ok, QMessageBox.Ok)
            sys.exit(1)
        self.new_cset_dsbox.valueChanged.connect(self.on_new_cset_changed)

    @pyqtSlot('QString')
    def on_elem_name_changed(self, name: str) -> None:
        """When the current selected element name is changed."""
        # 1. refresh the field name list combobox
        # 2. set field name cbb with the first item

        self.elem_selected = self.__mp.get_elements(name=name)[0]
        # milli_sleep(500)
        self.field_name_cbb.currentTextChanged.disconnect()
        self.field_name_cbb.clear()
        self.field_name_cbb.addItems(self.elem_selected.fields)
        #
        self.field_name_cbb.setCurrentIndex(0)
        self.field_name_cbb.currentTextChanged.connect(self.on_fname_changed)
        self.field_name_cbb.currentTextChanged.emit(self.field_name_cbb.currentText())

    @pyqtSlot(float)
    def on_new_cset_changed(self, val: float) -> None:
        """When the setting of the selected element/field is changed, do:
        1. print the setting of selected element/field
        2. update drawing with online simulated results
        """
        self.fld_selected.value = val

        # update simulation
        self.__lat.sync_settings()
        _, fm = self.__lat.run()
        self.fm = fm
        self.results, _ = fm.run(monitor='all')
        r, _ = fm.run(monitor=[self.elemlist_cbb.currentText()])
        if r != []:
            self.last_bs = r[0][-1]

        # update drawing
        self.update_drawing()

    def update_drawing(self):
        """This is the routine to update the figure with the updated drawing.
        Here I'm drawing the beam envelop along the entire beamline, try to
        replace with your routine for beam ellipse drawing.
        """
        self.draw_ellipse()
        self.draw_envelope()
        self.draw_trajectory()

    def draw_envelope(self):
        """Draw beam envelop onto the figure area.
        """
        results_dict = self.fm.collect_data(self.results, 'pos', 'xrms', 'yrms')
        pos = results_dict['pos'] + self.__z0
        xrms = results_dict['xrms']
        yrms = results_dict['yrms']
        for line_id, urms in zip((0, 1), (xrms, yrms)):
            self.envelope_plot.setLineID(line_id)
            self.envelope_plot.update_curve(pos, urms)

    def draw_trajectory(self):
        """Draw beam centroid trajectory onto the figure area.
        """
        results_dict = self.fm.collect_data(self.results, 'pos', 'xcen', 'ycen')
        pos = results_dict['pos'] + self.__z0
        xcen = results_dict['xcen']
        ycen = results_dict['ycen']
        for line_id, ucen in zip((0, 1), (xcen, ycen)):
            self.trajectory_plot.setLineID(line_id)
            self.trajectory_plot.update_curve(pos, ucen)

    @pyqtSlot()
    def draw_ellipse(self):
        """Draw x and y beam ellipse onto the figure area.
        """
        #
        s = self.last_bs
        #
        vals_x = (s.xcen, s.xpcen, s.xrms, s.xprms, s.xemittance,
                  s.xnemittance, s.xtwiss_alpha, s.xtwiss_beta,
                  (s.xtwiss_alpha**2 + 1) / s.xtwiss_beta, 1)
        vals_y = (s.ycen, s.ypcen, s.yrms, s.yprms, s.yemittance,
                  s.ynemittance, s.ytwiss_alpha, s.ytwiss_beta,
                  (s.ytwiss_alpha**2 + 1) / s.ytwiss_beta, 1)
        params_x = dict(zip(TWISS_KEYS_X, vals_x))
        params_y = dict(zip(TWISS_KEYS_Y, vals_y))

        self._plot_ellipse(self.x_ellipse_plot,
                           params_x,
                           color='b',
                           factor=self._size_factor,
                           xoy='x',
                           fill='g',
                           anote=False)
        self._plot_ellipse(self.y_ellipse_plot,
                           params_y,
                           color='r',
                           factor=self._size_factor,
                           xoy='y',
                           fill='m',
                           anote=False)
        #
        params = {k: v for k, v in params_x.items()}
        params.update(params_y)
        data = [(k, v, '-') for k, v in params.items()]
        self._show_results(data)


    def _plot_ellipse(self, figure_obj, params, **kws):
        xoy = kws.get('xoy', 'x')
        xlbl = f"{xoy} [mm]"
        ylbl = f"{xoy}' [mrad]"
        figure_obj.clear_figure()
        draw_beam_ellipse_with_params(params,
                                      ax=figure_obj.axes,
                                      color=kws.get('color', 'b'),
                                      factor=kws.get('factor', 4),
                                      xoy=xoy,
                                      fill=kws.get('fill', 'g'),
                                      anote=kws.get('anote', False))
        figure_obj.setFigureXlabel(xlbl)
        figure_obj.setFigureYlabel(ylbl)
        figure_obj.update_figure()
        self.on_xlimit_changed('')
        self.on_ylimit_changed('')
        self.grid_on_chkbox.toggled.emit(self.grid_on_chkbox.isChecked())
        self.mticks_on_chkbox.toggled.emit(self.mticks_on_chkbox.isChecked())
        self.tight_layout_on_chkbox.toggled.emit(self.tight_layout_on_chkbox.isChecked())

    def draw_layout(self):
        for o in (self.layout_plot, self.envelope_layout_plot, self.trajectory_layout_plot):
            o.clear_figure()
            _, ax = self.__lat.layout.draw(ax=o.axes, fig=o.figure,
                                           span=(1.05, 1.1),
                                           fig_opt={'figsize': (20, 8), 'dpi': 130})
        self.envelope_plot_splitter.setStretchFactor(0, 4)
        self.envelope_plot_splitter.setStretchFactor(1, 1)
        self.trajectory_plot_splitter.setStretchFactor(0, 4)
        self.trajectory_plot_splitter.setStretchFactor(1, 1)

    @pyqtSlot('QString')
    def on_target_element_changed(self, ename: str):
        """Get beam state result after the selected element from FLAME model.
        """
        elem = self.__lat[ename]
        self.family_lineEdit.setText(elem.family)
        self.pos_lineEdit.setText(f"{elem.sb + self.__z0:.3f} m")
        r, _ = self.fm.run(monitor=[ename])
        if r == []:
            QMessageBox.warning(self, "Select Element",
                    "Selected element cannot be located in model, probably for splitable element, select the closest one.",
                    QMessageBox.Ok, QMessageBox.Ok)
            return
        self.last_bs = r[0][-1]
        self.draw_ellipse()

    def _show_results(self, data):
        m = ResultsModel(self.twiss_results_treeView, data)
        m.set_model()

    @pyqtSlot()
    def on_probe_elem(self):
        """Pop up dialog for selected element for info query.
        """
        elem = self.elem_selected
        fname = self.fld_selected.name
        self.__probe_element(elem, fname)

    @pyqtSlot()
    def on_probe_target_elem(self):
        """Pop up dialog for selected target element for info query.
        """
        elem = self.__lat[self.elemlist_cbb.currentText()]
        self.__probe_element(elem)

    def __probe_element(self, elem, fname=None):
        ename = elem.name
        if ename not in self._probe_widgets_dict:
            w = ProbeWidget(element=elem, detached=False)
            self._probe_widgets_dict[ename] = w
        w = self._probe_widgets_dict[ename]
        if fname is not None:
            w.set_field(fname)
        w.show()
        w.raise_()

    @pyqtSlot('QString')
    def on_xlimit_changed(self, s):
        """xlimit to be updated.
        """
        try:
            x1 = float(self.xlim_x1_lineEdit.text())
            x2 = float(self.xlim_x2_lineEdit.text())
        except ValueError:
            pass
        else:
            for o in self.ellipse_area.findChildren(MatplotlibBaseWidget):
                o.set_xlimit(x1, x2)

    @pyqtSlot('QString')
    def on_ylimit_changed(self, s):
        """ylimit to be updated.
        """
        try:
            y1 = float(self.ylim_y1_lineEdit.text())
            y2 = float(self.ylim_y2_lineEdit.text())
        except ValueError:
            pass
        else:
            for o in self.ellipse_area.findChildren(MatplotlibBaseWidget):
                o.set_ylimit(y1, y2)

    @pyqtSlot(bool)
    def on_grid_enabled(self, enabled):
        for o in self.ellipse_area.findChildren(MatplotlibBaseWidget):
            o.setFigureGridToggle(enabled)

    @pyqtSlot(bool)
    def on_mticks_enabled(self, enabled):
        for o in self.ellipse_area.findChildren(MatplotlibBaseWidget):
            o.setFigureMTicksToggle(enabled)

    @pyqtSlot(bool)
    def on_tightlayout_enabled(self, enabled):
        for o in self.ellipse_area.findChildren(MatplotlibBaseWidget):
            o.setTightLayoutToggle(enabled)

    def auto_limits(self):
        self.on_auto_xlim()
        self.on_auto_ylim()

    @pyqtSlot()
    def on_auto_xlim(self):
        """Auto set xlimit.
        """
        x0, x1 = 0, 1
        for o in self.ellipse_area.findChildren(MatplotlibBaseWidget):
            o.set_autoscale('x')
            x0_, x1_ = o.axes.get_xlim()
            if x0_ < x0:
                x0 = x0_
            if x1_ > x1:
                x1 = x1_
        self.xlim_x1_lineEdit.setText(f'{x0:.1f}')
        self.xlim_x2_lineEdit.setText(f'{x1:.1f}')

    @pyqtSlot()
    def on_auto_ylim(self):
        """Auto set ylimit.
        """
        y0, y1 = 0, 1
        for o in self.ellipse_area.findChildren(MatplotlibBaseWidget):
            o.set_autoscale('y')
            y0_, y1_ = o.axes.get_ylim()
            if y0_ < y0:
                y0 = y0_
            if y1_ > y1:
                y1 = y1_
        self.ylim_y1_lineEdit.setText(f'{y0:.1f}')
        self.ylim_y2_lineEdit.setText(f'{y1:.1f}')

    @pyqtSlot(int)
    def on_ellipse_size_changed(self, i: int) -> None:
        """Ellipse size factor changed.
        """
        self._size_factor = i
        self.ellipse_size_factor_changed.emit()

    @pyqtSlot()
    def onLoadLattice(self):
        """Load machine/segment.
        """
        if self.lattice_load_window is None:
            self.lattice_load_window = LatticeWidget()
            self.lattice_load_window.latticeChanged.connect(self.lattice_changed)
            self.lattice_load_window.latticeChanged.connect(
                    self.lattice_load_window.close)
        self.lattice_load_window.show()

    @pyqtSlot(QVariant)
    def on_lattice_changed(self, mp):
        """A new machine/segment is loaded.
        """
        self.__mp = mp
        self.__lat = mp.work_lattice_conf
        self.__z0 = self.__lat.layout.z

        # update layout drawings
        self.update_layout.emit()

        # update element type cbb,
        self.elem_type_cbb.currentTextChanged.disconnect()
        self.elem_type_cbb.clear()
        dtype_list = list(set([i.family for i in self.__lat if i.family in VALID_ELEMENT_TYPES]))
        self.elem_type_cbb.addItems(dtype_list)
        if DEFAULT_ELEMENT_TYPE in dtype_list:
            self.elem_type_cbb.setCurrentText(DEFAULT_ELEMENT_TYPE)
        else:
            self.elem_type_cbb.setCurrentIndex(0)
        self.elem_type_cbb.currentTextChanged.connect(self.on_elem_type_changed)
        self.elem_type_cbb.currentTextChanged.emit(self.elem_type_cbb.currentText())

        # update element list (at which view results)
        ename_list = [i.name for i in self.__lat]
        self.elemlist_cbb.currentTextChanged.disconnect()
        self.elemlist_cbb.addItems(ename_list)
        self.elemlist_cbb.currentTextChanged.connect(self.on_target_element_changed)

        # update selected field and its settings
        self.field_name_cbb.currentTextChanged.emit(self.field_name_cbb.currentText())

        # update plots
        self.new_cset_dsbox.valueChanged.emit(self.new_cset_dsbox.value())
        # reset current selected element with the last element
        self.elemlist_cbb.setCurrentIndex(self.elemlist_cbb.count() - 1)
        self.elemlist_cbb.currentTextChanged.emit(self.elemlist_cbb.currentText())

    @pyqtSlot()
    def onExportLatfile(self):
        """Export FLAME lattice file from the model.
        """
        filename, ext = get_save_filename(self,
                                          caption="Choose a file to save",
                                          cdir='.',
                                          type_filter="Lattice File (*.lat)")
        if filename is None:
            return
        try:
            self.fm.generate_latfile(latfile=filename)
        except:
            QMessageBox.warning(self, "Export Lattice File",
                    "Failed to export model as a FLAME lattice file.",
                    QMessageBox.Ok, QMessageBox.Ok)
        else:
            QMessageBox.information(self, "Export Lattice File",
                    f"Export FLAME lattice file to {filename}.",
                    QMessageBox.Ok, QMessageBox.Ok)

    @pyqtSlot('QString')
    def on_elem_type_changed(self, dtype: str) -> None:
        """Element type selection is changed.
        """
        # 1. Refresh element name list combobox
        # 2. Set element list combobox with the first item
        self.elem_name_cbb.currentTextChanged.disconnect()
        self.elem_name_cbb.clear()
        self.elem_name_cbb.addItems([i.name for i in self.__mp.get_elements(type=dtype)])
        self.elem_name_cbb.setCurrentIndex(0)
        self.elem_name_cbb.currentTextChanged.connect(self.on_elem_name_changed)
        self.elem_name_cbb.currentTextChanged.emit(self.elem_name_cbb.currentText())


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys

    version = 0.1
    app = QApplication(sys.argv)
    w = MyAppWindow(version)
    w.show()
    w.setWindowTitle("This is an app from template")
    sys.exit(app.exec_())
