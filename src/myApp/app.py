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
import pathlib
import sys
import time
import numpy as np
from functools import partial
from collections import OrderedDict

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QEventLoop
from PyQt5.QtCore import QVariant
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QMessageBox

from mpl4qt.widgets import MatplotlibBaseWidget
from flame_utils import BeamState

from phantasy import MachinePortal
from phantasy_ui import BaseAppForm
from phantasy_ui import delayed_exec
from phantasy_ui import get_save_filename
from phantasy_ui.widgets import BeamStateWidget
from phantasy_ui.widgets import ElementSelectionWidget
from phantasy_ui.widgets import ProbeWidget
from phantasy_ui.widgets import LatticeWidget
from phantasy_ui.widgets import DataAcquisitionThread as DAQT
from phantasy_apps.allison_scanner.data import draw_beam_ellipse_with_params
from phantasy_apps.trajectory_viewer.utils import ElementListModel
from mpl4qt.widgets.utils import MatplotlibCurveWidgetSettings

from .utils import ResultsModel
from .utils import TWISS_KEYS_X
from .utils import TWISS_KEYS_Y
from .ui.ui_app import Ui_MainWindow

DEFAULT_MACHINE, DEFAULT_SEGMENT = "ARIS_VA", "F1"

VALID_ELEMENT_TYPES = ("QUAD", "BEND")
DEFAULT_ELEMENT_TYPE = "QUAD"
DEFAULT_FIELD_NAME = "I" # B2

HTML_TEMPLATE = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li {{ white-space: pre-wrap; }}
</style></head><body style=" font-family:'Cantarell'; font-size:12pt; font-weight:400; font-style:normal;">
<p align="center" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><img src="{0}" /></p></body></html>
"""

DIAG_FLD_MAP = {'envelope': ('sb', 'XRMS', 'YRMS'), 'trajectory': ('sb', 'XCEN', 'YCEN')}
CURPATH = pathlib.Path(__file__)
MPL_CONF_PATH = CURPATH.parent.joinpath("config")
ENVELOPE_MPL_CONF_PATH = MPL_CONF_PATH.joinpath("mpl_settings_envelope.json").resolve()
TRAJECTORY_MPL_CONF_PATH = MPL_CONF_PATH.joinpath("mpl_settings_trajectory.json").resolve()


class MyAppWindow(BaseAppForm, Ui_MainWindow):

    # update ellipse drawing size
    ellipse_size_factor_changed = pyqtSignal()

    # loaded machine/segment changed
    lattice_changed = pyqtSignal(QVariant)

    # update layout drawings
    update_layout = pyqtSignal()

    # show layout drawing (engineer drawings)
    show_layout_drawing = pyqtSignal('QString')

    # data updated 1: (s, x0, y0, rx, ry)
    data_updated1 = pyqtSignal(tuple)
    # data updated 2: dict of Twiss X, dict of Twiss Y
    data_updated2 = pyqtSignal(dict, dict)

    # beam state updated, beamstate
    bs_updated = pyqtSignal(BeamState)

    # selected diag devices changed
    envelope_diags_changed = pyqtSignal(dict)
    trajectory_diags_changed = pyqtSignal(dict)

    # diag data updated
    # s, x0, y0
    diag_data_updated1 = pyqtSignal(tuple)
    # s, rx, ry
    diag_data_updated2 = pyqtSignal(tuple)

    def __init__(self, version, **kws):
        super(self.__class__, self).__init__()

        # app version, title
        self.setAppVersion(version)
        self.setAppTitle("Online Model App")

        # app info in about dialog
        self.app_about_info = """
            <html>
            <h4>About Online Model App</h4>
            <p>This app is an online modeling app with FLAME code for accelerator, developed with
            PHANTASY framework.
            </p>
            <p>Copyright (c) 2021 Facility for Rare Isotope Beams and other contributors.</p>
            </html>
        """.format(self.getAppVersion())

        # UI
        self.setupUi(self)
        self.postInitUi()

        # post init
        self._post_init()

    def _post_init(self):
        """Initialize UI, user customized code put here.
        """
        self.ENG_DRAWING_MAP = {
            'aris': ':/imgs/ARIS-layout.png',
        }
        #
        self.elem_type_cbb.currentTextChanged.connect(self.on_elem_type_changed)
        self.elem_name_cbb.currentTextChanged.connect(self.on_elem_name_changed)
        self.field_name_cbb.currentTextChanged.connect(self.on_fname_changed)
        self.elemlist_cbb.currentTextChanged.connect(self.on_target_element_changed)

        #
        self.data_updated1.connect(self.on_update_data1)
        self.data_updated2.connect(self.on_update_data2)

        #
        self.diag_data_updated1.connect(self.on_update_diag_data1)
        self.diag_data_updated2.connect(self.on_update_diag_data2)

        #
        self._size_factor = self.size_factor_sbox.value()
        self.ellipse_size_factor_changed.connect(self.draw_ellipse)

        # initial vars for FLAME model
        self.fm = None
        self._src_conf = None # initial beam source condition, dict
        self.updater = None # simulator
        self._update_delt = 1.0 # second

        # Dict of ProbeWidget for selected element and target element
        self._probe_widgets_dict = {}

        # element query
        self.elem_probe_btn.clicked.connect(self.on_probe_elem)
        self.target_elem_probe_btn.clicked.connect(self.on_probe_target_elem)

        # lattice load window
        self.lattice_load_window = None
        self.__mp = None
        self.__lat = None
        self._elem_sel_widgets = {}
        self._diag_elems = {'envelope': [], 'trajectory': []} # list of CaElement

        # beam state widget
        self._bs_widget = BeamStateWidget(None, None, None)
        self.bs_updated.connect(self._bs_widget.bs_updated)
        self._bs_widget.beam_source_updated[dict].connect(self.on_beam_source_updated)

        # update layout drawings
        self.update_layout.connect(self.draw_layout)
        self.show_layout_drawing.connect(self.on_show_layout_drawings)
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
        # self.__preload_lattice(DEFAULT_MACHINE, DEFAULT_SEGMENT)

        # diag, envelope
        self.envelope_diag_choose_btn.clicked.connect(partial(self.on_select_devices, 'envelope', ['PM', 'VD']))
        self.envelope_diags_changed.connect(partial(self.on_update_diag_viz, 'envelope'))
        self.envelope_diag_select_all_btn.clicked.connect(partial(self.on_select_all_elems, "envelope"))
        self.envelope_diag_invert_selection_btn.clicked.connect(partial(self.on_inverse_current_elem_selection, "envelope"))

        # diag, trajectory
        self.trajectory_diag_choose_btn.clicked.connect(partial(self.on_select_devices, 'trajectory', ['PM', 'VD', 'BPM']))
        self.trajectory_diags_changed.connect(partial(self.on_update_diag_viz, 'trajectory'))
        self.trajectory_diag_select_all_btn.clicked.connect(partial(self.on_select_all_elems, "trajectory"))
        self.trajectory_diag_invert_selection_btn.clicked.connect(partial(self.on_inverse_current_elem_selection, "trajectory"))

    @pyqtSlot()
    def on_select_all_elems(self, category):
        """Select all diags in *category*_diags_treeView.
        """
        try:
            print("Select All {}s".format(category.upper()))
            model = getattr(self, '{}_diags_treeView'.format(category)).model()
            model.select_all_items()
        except AttributeError:
            QMessageBox.warning(self, "Element Selection",
                                "Selection error, Choose elements first.",
                                QMessageBox.Ok)

    @pyqtSlot()
    def on_inverse_current_elem_selection(self, category):
        """Inverse current diag selection in *category*_diags_treeView.
        """
        try:
            print("Inverse {} selection".format(category.upper()))
            model = getattr(self, '{}_diags_treeView'.format(category)).model()
            model.inverse_current_selection()
        except AttributeError:
            QMessageBox.warning(self, "Element Selection",
                                "Selection error, Choose elements first.",
                                QMessageBox.Ok)

    @pyqtSlot(dict)
    def on_update_diag_viz(self, category, d):
        # update selected diag_elements and dataviz.
        # print("Selected diag devices:")
        if d is not None:
            self._diag_elems[category] = [self.__lat[i] for i in d]

        if len(self._diag_elems[category]) == 0:
            return

        flds = DIAG_FLD_MAP[category]
        diag_data = np.asarray(
                [[getattr(elem, fld) for fld in flds] for elem in self._diag_elems[category]])
        col1 = diag_data[:, 0] + self.__z0 # s
        col2 = diag_data[:, 1] * 1e3 # x0 or rx, m -> mm
        col3 = diag_data[:, 2] * 1e3 # y0 or ry, m -> mm
        if category == 'trajectory':
            self.diag_data_updated1.emit((col1, col2, col3))
        elif category == 'envelope':
            self.diag_data_updated2.emit((col1, col2, col3))

    @pyqtSlot()
    def on_select_devices(self, category, dtype_list):
        """Select devices, category: envelope, trajectory
        """
        if self.__mp is None:
            QMessageBox.warning(self, "Select Element",
                                "Cannot find loaded lattice, load by clicking 'Load Lattice' or Ctrl+Shift+L.",
                                QMessageBox.Ok)
            return
        w = self._elem_sel_widgets.setdefault(category,
                                              ElementSelectionWidget(self, self.__mp, dtypes=dtype_list))
        w.elementsSelected.connect(partial(self.on_update_elems, category))
        w.show()

    @pyqtSlot(OrderedDict)
    def on_elem_selection_updated(self, category, d):
        # mode 'envelope':
        #   selection (envelope_diags_treeView) is updated
        #   * trigger the update of self._diags (trigger data viz update (timeout))
        model = getattr(self, '{}_diags_treeView'.format(category)).model()
        if category == 'envelope':
            #
            print("Diag device selction for envelope is changed...")
            # emit selected monitors
            self.envelope_diags_changed.emit(model._selected_elements)
        elif category == 'trajectory':
            print("Diag device selction for trajectory is changed...")
            # emit selected monitors
            self.trajectory_diags_changed.emit(model._selected_elements)

    @pyqtSlot(list)
    def on_update_elems(self, category, enames):
        """Selected element names list updated, mode: 'envelope'/'trajectory'
        """
        tv = getattr(self, "{}_diags_treeView".format(category))
        model = ElementListModel(tv, self.__mp, enames)
        # list of fields of selected element type
        model.set_model()

        # selection is changed (elementlistmodel)
        m = tv.model()
        m.elementSelected.connect(partial(self.on_elem_selection_updated, category))


    def __preload_lattice(self, mach, segm):
        self.actionLoad_Lattice.triggered.emit()
        self.lattice_load_window.mach_cbb.setCurrentText(mach)
        self.lattice_load_window.seg_cbb.setCurrentText(segm)
        loop = QEventLoop()
        self.lattice_load_window.latticeChanged.connect(loop.exit)
        self.lattice_load_window.load_btn.clicked.emit()
        loop.exec_()
        # auto xyscale (ellipse drawing)
        delayed_exec(self.actionUpdate.triggered.emit, 100)
        delayed_exec(self.auto_limits, 1000)

    def __init_envelope_plot(self):
        """Initialize plot area for beam envelope.
        """
        o = self.envelope_plot
        o.add_curve()
        o.add_curve()
        o.add_curve()
        s = MatplotlibCurveWidgetSettings(str(ENVELOPE_MPL_CONF_PATH))
        o.apply_mpl_settings(s)

    def __init_trajectory_plot(self):
        """Initialize plot area for beam trajectory.
        """
        o = self.trajectory_plot
        o.add_curve()
        o.add_curve()
        o.add_curve()
        s = MatplotlibCurveWidgetSettings(str(TRAJECTORY_MPL_CONF_PATH))
        o.apply_mpl_settings(s)

    @pyqtSlot(dict)
    def on_beam_source_updated(self, src_conf):
        """Initial beam condition is updated.
        """
        # update and run model
        # update dataviz
        self._src_conf = src_conf
        if self.actionAuto_Update.isChecked():
            self.actionAuto_Update.setChecked(False)
        delayed_exec(self.actionUpdate.triggered.emit, 500)

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
                self, "Online Model App",
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

        # update online model (once)
        self.actionUpdate.triggered.emit()

    @pyqtSlot(tuple)
    def on_update_diag_data1(self, t1):
        s, x0, y0 = t1
        for line_id, ucen in zip((2, 3), (x0, y0)):
            self.trajectory_plot.setLineID(line_id)
            self.trajectory_plot.update_curve(s, ucen)

    @pyqtSlot(tuple)
    def on_update_diag_data2(self, t2):
        s, rx, ry = t2
        for line_id, urms in zip((2, 3), (rx, ry)):
            self.envelope_plot.setLineID(line_id)
            self.envelope_plot.update_curve(s, urms)

    @pyqtSlot(tuple)
    def on_update_data1(self, t1):
        s, x0, y0, rx, ry = t1
        self.draw_envelope(s, rx, ry)
        self.draw_trajectory(s, x0, y0)

    @pyqtSlot(dict, dict)
    def on_update_data2(self, d1, d2):
        self.params_x, self.params_y = d1, d2
        self.draw_ellipse()

    def draw_envelope(self, pos, xrms, yrms):
        """Draw beam envelop onto the figure area.
        """
        for line_id, urms in zip((0, 1), (xrms, yrms)):
            self.envelope_plot.setLineID(line_id)
            self.envelope_plot.update_curve(pos, urms)

    def draw_trajectory(self, pos, xcen, ycen):
        """Draw beam centroid trajectory onto the figure area.
        """
        for line_id, ucen in zip((0, 1), (xcen, ycen)):
            self.trajectory_plot.setLineID(line_id)
            self.trajectory_plot.update_curve(pos, ucen)

    @pyqtSlot()
    def draw_ellipse(self):
        """Draw x and y beam ellipse onto the figure area.
        """
        params_x, params_y = self.params_x, self.params_y
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
        delayed_exec(self.actionUpdate.triggered.emit, 1000)

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
        x0, x1 = 0, 0
        for o in self.ellipse_area.findChildren(MatplotlibBaseWidget):
            o.set_autoscale('x')
            x0_, x1_ = o.axes.get_xlim()
            x0 = min(x0_, x0)
            x1 = max(x1_, x1)
        self.xlim_x1_lineEdit.setText(f'{x0:.1f}')
        self.xlim_x2_lineEdit.setText(f'{x1:.1f}')

    @pyqtSlot()
    def on_auto_ylim(self):
        """Auto set ylimit.
        """
        y0, y1 = 0, 0
        for o in self.ellipse_area.findChildren(MatplotlibBaseWidget):
            o.set_autoscale('y')
            y0_, y1_ = o.axes.get_ylim()
            y0 = min(y0_, y0)
            y1 = max(y1_, y1)
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

        #
        if self.__mp.last_machine_name in ('ARIS', 'ARIS_VA',):
            self.show_layout_drawing.emit('aris')

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

        # auto xyscale (ellipse drawing)
        delayed_exec(self.actionUpdate.triggered.emit, 2000)
        delayed_exec(self.auto_limits, 3000)

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

    @pyqtSlot(bool)
    def onAutoUpdateModel(self, toggled):
        """Auto update simulation.
        """
        if toggled:
            self._stop_auto_update = False
            self.start_auto_updater()
        else:
            self.stop_auto_updater()

    def stop_auto_updater(self):
        self._stop_auto_update = True

    def start_auto_updater(self):
        if self._stop_auto_update:
            return
        self.updater_n = DAQT(daq_func=partial(self.update_single,
                              self.__lat, self.elemlist_cbb.currentText(), self._update_delt,
                              self._src_conf),
                              daq_seq=range(1))
        self.updater_n.daqStarted.connect(partial(self.set_widgets_status, "START", True))
        self.updater_n.resultsReady.connect(self.on_updater_results_ready)
        self.updater_n.finished.connect(partial(self.set_widgets_status, "STOP", True))
        self.updater_n.finished.connect(self.start_auto_updater)
        self.updater_n.start()

    @pyqtSlot(float)
    def on_update_rate(self, x):
        self._update_delt = 1.0 / x # second

    def _sim_is_running(self):
        try:
            r = self.updater.isRunning()
        except:
            r = False
        finally:
            return r

    @pyqtSlot()
    def onUpdateModel(self):
        """Update simulation.
        """
        if self._sim_is_running():
            return
        self.updater = DAQT(daq_func=partial(self.update_single,
                            self.__lat, self.elemlist_cbb.currentText(), 0,
                            self._src_conf),
                            daq_seq=range(1))
        self.updater.daqStarted.connect(partial(self.set_widgets_status, "START", False))
        self.updater.resultsReady.connect(self.on_updater_results_ready)
        self.updater.finished.connect(partial(self.set_widgets_status, "STOP", False))
        self.updater.start()

    def update_single(self, lat, target_ename, delt, src_conf, iiter):
        # src_conf: initial beam source configuration.
        t0 = time.time()
        lat.sync_settings()
        _, fm = lat.run(src_conf)
        results, _ = fm.run(monitor='all')
        r, _ = fm.run(monitor=[target_ename])
        if delt > 0:
            dt = time.time() - t0
            if delt - dt > 0:
                time.sleep(delt - dt)
            else:
                print(f"Update rate is: {1.0 / dt:.1f} Hz")
        return results, r, fm

    def on_updater_results_ready(self, res):
        results, r, fm = res[0]
        # pos, xrms, yrms, xcen, ycen, twiss parameters
        self.fm = fm
        # s, x0, y0, rx, ry
        r1_ = fm.collect_data(results, 'pos', 'xcen', 'ycen', 'xrms', 'yrms')
        pos = r1_['pos'] + self.__z0
        xcen, ycen = r1_['xcen'], r1_['ycen']
        xrms, yrms = r1_['xrms'], r1_['yrms']
        self.data_updated1.emit((pos, xcen, ycen, xrms, yrms))
        #
        if r == []:
            QMessageBox.warning(self, "Select Element",
                    "Selected element cannot be located in model, probably for splitable element, select the closest one.",
                    QMessageBox.Ok, QMessageBox.Ok)
        else:
            self.__update_twiss_params(r)
            # update beam state info
            self._bs_widget.ename = self.elemlist_cbb.currentText()
            self.bs_updated.emit(r[0][-1])
        # diag viz
        self.on_update_diag_viz('envelope', None)
        self.on_update_diag_viz('trajectory', None)

    def __update_twiss_params(self, r):
        s = r[0][-1]
        vals_x = (s.xcen, s.xpcen, s.xrms, s.xprms, s.xemittance,
                  s.xnemittance, s.xtwiss_alpha, s.xtwiss_beta,
                  (s.xtwiss_alpha**2 + 1) / s.xtwiss_beta, 1)
        vals_y = (s.ycen, s.ypcen, s.yrms, s.yprms, s.yemittance,
                  s.ynemittance, s.ytwiss_alpha, s.ytwiss_beta,
                  (s.ytwiss_alpha**2 + 1) / s.ytwiss_beta, 1)
        params_x = dict(zip(TWISS_KEYS_X, vals_x))
        params_y = dict(zip(TWISS_KEYS_Y, vals_y))
        self.data_updated2.emit(params_x, params_y)

    def set_widgets_status(self, status, auto_update=False):
        if not auto_update:
            olist1 = (self.actionUpdate, self.actionAuto_Update, )
            olist2 = ()
        else:
            olist1 = (self.actionUpdate, self.update_rate_dsbox, )
            olist2 = ()
        if status != "START":
            [o.setEnabled(True) for o in olist1]
            [o.setEnabled(False) for o in olist2]
        else:
            [o.setEnabled(False) for o in olist1]
            [o.setEnabled(True) for o in olist2]

    @pyqtSlot()
    def on_show_beamstate(self):
        """Show beam state details.
        """
        self._bs_widget.show()

    @pyqtSlot('QString')
    def on_show_layout_drawings(self, name):
        """Show engineering drawing.
        """
        self.eng_drawing_browser.setHtml(HTML_TEMPLATE.format(self.ENG_DRAWING_MAP[name]))



if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys

    version = 0.1
    app = QApplication(sys.argv)
    w = MyAppWindow(version)
    w.show()
    w.setWindowTitle("This is an app from template")
    sys.exit(app.exec_())
