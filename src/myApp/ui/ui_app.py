# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_app.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1337, 692)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/default.png"),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.tab)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_3 = QtWidgets.QLabel(self.tab)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_2.addWidget(self.label_3)
        self.elemlist_cbb = QtWidgets.QComboBox(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.elemlist_cbb.sizePolicy().hasHeightForWidth())
        self.elemlist_cbb.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Monospace")
        self.elemlist_cbb.setFont(font)
        self.elemlist_cbb.setObjectName("elemlist_cbb")
        self.horizontalLayout_2.addWidget(self.elemlist_cbb)
        self.elem_info_btn = QtWidgets.QToolButton(self.tab)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/info.png"), QtGui.QIcon.Normal,
                        QtGui.QIcon.Off)
        self.elem_info_btn.setIcon(icon1)
        self.elem_info_btn.setIconSize(QtCore.QSize(30, 30))
        self.elem_info_btn.setAutoRaise(True)
        self.elem_info_btn.setObjectName("elem_info_btn")
        self.horizontalLayout_2.addWidget(self.elem_info_btn)
        self.pos_lineEdit = QtWidgets.QLineEdit(self.tab)
        self.pos_lineEdit.setReadOnly(True)
        self.pos_lineEdit.setObjectName("pos_lineEdit")
        self.horizontalLayout_2.addWidget(self.pos_lineEdit)
        self.family_lineEdit = QtWidgets.QLineEdit(self.tab)
        self.family_lineEdit.setReadOnly(True)
        self.family_lineEdit.setObjectName("family_lineEdit")
        self.horizontalLayout_2.addWidget(self.family_lineEdit)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.x_ellipse_plot = MatplotlibBaseWidget(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                           QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.x_ellipse_plot.sizePolicy().hasHeightForWidth())
        self.x_ellipse_plot.setSizePolicy(sizePolicy)
        self.x_ellipse_plot.setFigureTitle("")
        font = QtGui.QFont()
        font.setFamily("sans-serif")
        font.setPointSize(14)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.x_ellipse_plot.setFigureXYlabelFont(font)
        font = QtGui.QFont()
        font.setFamily("sans-serif")
        font.setPointSize(16)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.x_ellipse_plot.setFigureTitleFont(font)
        font = QtGui.QFont()
        font.setFamily("sans-serif")
        font.setPointSize(12)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.x_ellipse_plot.setFigureXYticksFont(font)
        self.x_ellipse_plot.setProperty("figureToolbarToggle", False)
        self.x_ellipse_plot.setObjectName("x_ellipse_plot")
        self.horizontalLayout_4.addWidget(self.x_ellipse_plot)
        self.y_ellipse_plot = MatplotlibBaseWidget(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                           QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.y_ellipse_plot.sizePolicy().hasHeightForWidth())
        self.y_ellipse_plot.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("sans-serif")
        font.setPointSize(14)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.y_ellipse_plot.setFigureXYlabelFont(font)
        font = QtGui.QFont()
        font.setFamily("sans-serif")
        font.setPointSize(16)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.y_ellipse_plot.setFigureTitleFont(font)
        font = QtGui.QFont()
        font.setFamily("sans-serif")
        font.setPointSize(12)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.y_ellipse_plot.setFigureXYticksFont(font)
        self.y_ellipse_plot.setProperty("figureToolbarToggle", False)
        self.y_ellipse_plot.setObjectName("y_ellipse_plot")
        self.horizontalLayout_4.addWidget(self.y_ellipse_plot)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.tab_2)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.envelope_plot = MatplotlibCurveWidget(self.tab_2)
        self.envelope_plot.setFigureAutoScale(True)
        font = QtGui.QFont()
        font.setFamily("sans-serif")
        font.setPointSize(14)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.envelope_plot.setFigureXYlabelFont(font)
        self.envelope_plot.setProperty("figureLegendToggle", True)
        self.envelope_plot.setObjectName("envelope_plot")
        self.horizontalLayout_3.addWidget(self.envelope_plot)
        self.tabWidget.addTab(self.tab_2, "")
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                           QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.quad1_name_cbb = QtWidgets.QComboBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.quad1_name_cbb.sizePolicy().hasHeightForWidth())
        self.quad1_name_cbb.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Monospace")
        self.quad1_name_cbb.setFont(font)
        self.quad1_name_cbb.setObjectName("quad1_name_cbb")
        self.horizontalLayout.addWidget(self.quad1_name_cbb)
        self.quad_info_btn = QtWidgets.QToolButton(self.centralwidget)
        self.quad_info_btn.setIcon(icon1)
        self.quad_info_btn.setIconSize(QtCore.QSize(30, 30))
        self.quad_info_btn.setAutoRaise(True)
        self.quad_info_btn.setObjectName("quad_info_btn")
        self.horizontalLayout.addWidget(self.quad_info_btn)
        spacerItem = QtWidgets.QSpacerItem(40, 20,
                                           QtWidgets.QSizePolicy.Expanding,
                                           QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                           QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.quad1_grad_dsbox = QtWidgets.QDoubleSpinBox(self.centralwidget)
        self.quad1_grad_dsbox.setDecimals(3)
        self.quad1_grad_dsbox.setMinimum(-100.0)
        self.quad1_grad_dsbox.setMaximum(100.0)
        self.quad1_grad_dsbox.setSingleStep(0.1)
        self.quad1_grad_dsbox.setObjectName("quad1_grad_dsbox")
        self.horizontalLayout.addWidget(self.quad1_grad_dsbox)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1337, 30))
        self.menubar.setObjectName("menubar")
        self.menu_File = QtWidgets.QMenu(self.menubar)
        self.menu_File.setObjectName("menu_File")
        self.menu_Help = QtWidgets.QMenu(self.menubar)
        self.menu_Help.setObjectName("menu_Help")
        MainWindow.setMenuBar(self.menubar)
        self.action_About = QtWidgets.QAction(MainWindow)
        self.action_About.setObjectName("action_About")
        self.actionAbout_Qt = QtWidgets.QAction(MainWindow)
        self.actionAbout_Qt.setObjectName("actionAbout_Qt")
        self.actionE_xit = QtWidgets.QAction(MainWindow)
        self.actionE_xit.setObjectName("actionE_xit")
        self.actionContents = QtWidgets.QAction(MainWindow)
        self.actionContents.setObjectName("actionContents")
        self.menu_File.addAction(self.actionE_xit)
        self.menu_Help.addAction(self.actionContents)
        self.menu_Help.addSeparator()
        self.menu_Help.addAction(self.action_About)
        self.menu_Help.addAction(self.actionAbout_Qt)
        self.menubar.addAction(self.menu_File.menuAction())
        self.menubar.addAction(self.menu_Help.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        self.actionAbout_Qt.triggered.connect(MainWindow.onAboutQt)
        self.actionE_xit.triggered.connect(MainWindow.close)
        self.action_About.triggered.connect(MainWindow.onAbout)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label_3.setText(_translate("MainWindow", "Show results after"))
        self.elem_info_btn.setToolTip(
            _translate("MainWindow",
                       "Click to see the details of selected device."))
        self.elem_info_btn.setText(_translate("MainWindow", "info"))
        self.x_ellipse_plot.setFigureXlabel(_translate("MainWindow", "X (mm)"))
        self.x_ellipse_plot.setFigureYlabel(
            _translate("MainWindow", "X\' (mrad)"))
        self.y_ellipse_plot.setFigureXlabel(_translate("MainWindow", "Y (mm)"))
        self.y_ellipse_plot.setFigureYlabel(
            _translate("MainWindow", "Y\' (mrad)"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab),
                                  _translate("MainWindow", "Beam Ellipse"))
        self.envelope_plot.setFigureXlabel(_translate("MainWindow", "s [m]"))
        self.envelope_plot.setFigureYlabel(
            _translate("MainWindow", "Envelop [mm]"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2),
                                  _translate("MainWindow", "Beam Envelope"))
        self.label.setText(_translate("MainWindow", "Select quadrupole"))
        self.quad_info_btn.setToolTip(
            _translate("MainWindow",
                       "Click to see the details of selected device."))
        self.quad_info_btn.setText(_translate("MainWindow", "info"))
        self.label_2.setText(_translate("MainWindow", "Gradient Setting"))
        self.quad1_grad_dsbox.setSuffix(_translate("MainWindow", " T/m"))
        self.menu_File.setTitle(_translate("MainWindow", "&File"))
        self.menu_Help.setTitle(_translate("MainWindow", "&Help"))
        self.action_About.setText(_translate("MainWindow", "&About"))
        self.action_About.setShortcut(_translate("MainWindow", "Ctrl+A"))
        self.actionAbout_Qt.setText(_translate("MainWindow", "About Qt"))
        self.actionE_xit.setText(_translate("MainWindow", "E&xit"))
        self.actionE_xit.setShortcut(_translate("MainWindow", "Ctrl+W"))
        self.actionContents.setText(_translate("MainWindow", "Contents"))
        self.actionContents.setShortcut(_translate("MainWindow", "F1"))


from mpl4qt.widgets.mplbasewidget import MatplotlibBaseWidget
from mpl4qt.widgets.mplcurvewidget import MatplotlibCurveWidget
from . import resources_rc

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
