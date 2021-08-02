#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem
from PyQt5.QtGui import QStandardItemModel

DELTA = '\N{GREEK CAPITAL LETTER DELTA}'
ALPHA = '\N{GREEK SMALL LETTER ALPHA}'
BETA = '\N{GREEK SMALL LETTER BETA}'
GAMMA = '\N{GREEK SMALL LETTER GAMMA}'
EPSILON = '\N{GREEK SMALL LETTER EPSILON}'
SIGMA = '\N{GREEK SMALL LETTER SIGMA}'
DOT = '\N{WORD SEPARATOR MIDDLE DOT}'

NAME_MAP = {
    'alpha_x': (f'{ALPHA}(x)', '-'),
    'beta_x': (f'{BETA}(x)', 'm'),
    'gamma_x': (f'{GAMMA}(x)', '1/m'),
    'emit_x': (f'{EPSILON}(x)', f'mm{DOT}mrad'),

    'alpha_y': (f'{ALPHA}(y)', '-'),
    'beta_y': (f'{BETA}(y)', 'm'),
    'gamma_y': (f'{GAMMA}(y)', '1/m'),
    'emit_y': (f'{EPSILON}(y)', f'mm{DOT}mrad'),

    'x_cen': ("Center(x)", 'mm'),
    'xp_cen': ("Center(x')", 'mrad'),
    'x_rms': (f'{SIGMA}(x)', 'mm'),
    'xp_rms': (f"{SIGMA}(x')", 'mrad'),

    'y_cen': ('Center(y)', 'mm'),
    'yp_cen': ("Center(y')", 'mrad'),
    'y_rms': (f'{SIGMA}(y)', 'mm'),
    'yp_rms': (f"{SIGMA}(y')", 'mrad'),
}

# key strings for Twiss X,Y parameters
TWISS_KEYS_X = [
    i.format(u='x') for i in ('{u}_cen', '{u}p_cen', '{u}_rms', '{u}p_rms',
                              'emit_{u}', 'emitn_{u}', 'alpha_{u}', 'beta_{u}',
                              'gamma_{u}', 'total_intensity')
]
TWISS_KEYS_Y = [
    i.format(u='y') for i in ('{u}_cen', '{u}p_cen', '{u}_rms', '{u}p_rms',
                              'emit_{u}', 'emitn_{u}', 'alpha_{u}', 'beta_{u}',
                              'gamma_{u}', 'total_intensity')
]



class ResultsModel(QStandardItemModel):
    """Data model for Twiss parameters.

    data : list of values (list), [parameter, value, value1]
    """
    def __init__(self, parent, data, **kws):
        super(self.__class__, self).__init__(parent)
        self._v = parent
        self._data = data
        self._fmt = "{0:>.3f}"

        #
        self.header = self.h_param, self.h_unit, self.h_value, \
                      self.h_value1, self.h_diff \
                    = "Parameter", "Unit", "Model (v0)", "Measured (v1)", f"{DELTA}(v0, v1)"
        self.ids = self.i_param, self.i_unit, self.i_value, self._i_value1, self.i_diff \
                 = range(len(self.header))

    def set_data(self):
        for name, v0, v1 in self._data:
            name_tuple = NAME_MAP.get(name, None)
            if name_tuple is None:
                continue
            name, unit = name_tuple
            it_param = QStandardItem(name)
            it_unit = QStandardItem(unit)
            it_v0 = QStandardItem(self._fmt.format(v0))
            if v1 == '-':
                it_v1 = QStandardItem('-')
                it_dv = QStandardItem('-')
            else:
                it_v1 = QStandardItem(self._fmt.format(v1))
                it_dv = QStandardItem(self._fmt.format(v0 - v1))
            row = [it_param, it_unit, it_v0, it_v1, it_dv]
            for o in (it_param, it_unit, it_v0):
                o.setEditable(False)
            self.appendRow(row)

    def set_model(self):
        self.set_data()
        self._v.setModel(self)
        self.__post_init_ui()

    def __post_init_ui(self):
        # set headers
        v = self._v
        v.setSortingEnabled(True)
        for i, s in zip(self.ids, self.header):
            self.setHeaderData(i, Qt.Horizontal, s)
        v.model().sort(self.i_param)
        v.header().setStyleSheet("""
            QHeaderView {
                font-weight: bold;
            }""")
        #
        v.setStyleSheet("""
            QTreeView {
                font-family: monospace;
                show-decoration-selected: 1;
                alternate-background-color: #D3D7CF;
            }

            QTreeView::item {
                /*color: black;*/
                border: 1px solid #D9D9D9;
                border-top-color: transparent;
                border-bottom-color: transparent;
            }

            QTreeView::item:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #e7effd, stop: 1 #cbdaf1);
                border: 1px solid #bfcde4;
            }

            QTreeView::item:selected {
                border: 1px solid #567DBC;
                background-color: #D3D7CF;
            }

            QTreeView::item:selected:active{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #6ea1f1, stop: 1 #567dbc);
            }""")
        self.fit_view()

    def fit_view(self):
        v = self._v
        #v.expandAll()
        for i in self.ids:
            v.resizeColumnToContents(i)
        #v.collapseAll()
