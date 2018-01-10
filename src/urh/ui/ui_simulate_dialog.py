# -*- coding: utf-8 -*-

#
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SimulateDialog(object):
    def setupUi(self, SimulateDialog):
        SimulateDialog.setObjectName("SimulateDialog")
        SimulateDialog.resize(1032, 698)
        SimulateDialog.setSizeGripEnabled(False)
        SimulateDialog.setModal(True)
        self.gridLayout = QtWidgets.QGridLayout(SimulateDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.splitter = QtWidgets.QSplitter(SimulateDialog)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.frame_2 = QtWidgets.QFrame(self.splitter)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame_2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_7 = QtWidgets.QLabel(self.frame_2)
        self.label_7.setObjectName("label_7")
        self.verticalLayout_2.addWidget(self.label_7)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tableDeviceProfiles = QtWidgets.QTableWidget(self.frame_2)
        self.tableDeviceProfiles.setObjectName("tableDeviceProfiles")
        self.tableDeviceProfiles.setColumnCount(3)
        self.tableDeviceProfiles.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableDeviceProfiles.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableDeviceProfiles.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableDeviceProfiles.setHorizontalHeaderItem(2, item)
        self.horizontalLayout.addWidget(self.tableDeviceProfiles)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.toolButton = QtWidgets.QToolButton(self.frame_2)
        icon = QtGui.QIcon.fromTheme("list-add")
        self.toolButton.setIcon(icon)
        self.toolButton.setObjectName("toolButton")
        self.verticalLayout.addWidget(self.toolButton)
        self.toolButton_2 = QtWidgets.QToolButton(self.frame_2)
        icon = QtGui.QIcon.fromTheme("list-remove")
        self.toolButton_2.setIcon(icon)
        self.toolButton_2.setObjectName("toolButton_2")
        self.verticalLayout.addWidget(self.toolButton_2)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.label = QtWidgets.QLabel(self.frame_2)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.tableViewSimulate = QtWidgets.QTableView(self.frame_2)
        self.tableViewSimulate.setAlternatingRowColors(True)
        self.tableViewSimulate.setShowGrid(False)
        self.tableViewSimulate.setObjectName("tableViewSimulate")
        self.tableViewSimulate.horizontalHeader().setDefaultSectionSize(150)
        self.tableViewSimulate.horizontalHeader().setStretchLastSection(True)
        self.tableViewSimulate.verticalHeader().setVisible(False)
        self.verticalLayout_2.addWidget(self.tableViewSimulate)
        self.label_2 = QtWidgets.QLabel(self.frame_2)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_2.addWidget(self.label_2)
        self.spinBoxNRepeat = QtWidgets.QSpinBox(self.frame_2)
        self.spinBoxNRepeat.setObjectName("spinBoxNRepeat")
        self.verticalLayout_2.addWidget(self.spinBoxNRepeat)
        self.label_3 = QtWidgets.QLabel(self.frame_2)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_2.addWidget(self.label_3)
        self.spinBoxTimeout = QtWidgets.QSpinBox(self.frame_2)
        self.spinBoxTimeout.setObjectName("spinBoxTimeout")
        self.verticalLayout_2.addWidget(self.spinBoxTimeout)
        self.label_4 = QtWidgets.QLabel(self.frame_2)
        self.label_4.setObjectName("label_4")
        self.verticalLayout_2.addWidget(self.label_4)
        self.comboBoxError = QtWidgets.QComboBox(self.frame_2)
        self.comboBoxError.setObjectName("comboBoxError")
        self.comboBoxError.addItem("")
        self.comboBoxError.addItem("")
        self.comboBoxError.addItem("")
        self.verticalLayout_2.addWidget(self.comboBoxError)
        self.label_6 = QtWidgets.QLabel(self.frame_2)
        self.label_6.setObjectName("label_6")
        self.verticalLayout_2.addWidget(self.label_6)
        self.spinBoxRetries = QtWidgets.QSpinBox(self.frame_2)
        self.spinBoxRetries.setMinimum(1)
        self.spinBoxRetries.setProperty("value", 10)
        self.spinBoxRetries.setObjectName("spinBoxRetries")
        self.verticalLayout_2.addWidget(self.spinBoxRetries)
        self.frame = QtWidgets.QFrame(self.splitter)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.frame)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.btnLogAll = QtWidgets.QPushButton(self.frame)
        self.btnLogAll.setObjectName("btnLogAll")
        self.gridLayout_2.addWidget(self.btnLogAll, 2, 1, 1, 1)
        self.btnLogNone = QtWidgets.QPushButton(self.frame)
        self.btnLogNone.setObjectName("btnLogNone")
        self.gridLayout_2.addWidget(self.btnLogNone, 2, 2, 1, 1)
        self.btnLog = QtWidgets.QPushButton(self.frame)
        self.btnLog.setObjectName("btnLog")
        self.gridLayout_2.addWidget(self.btnLog, 2, 0, 1, 1)
        self.gvSimulator = LoggingGraphicsView(self.frame)
        self.gvSimulator.setObjectName("gvSimulator")
        self.gridLayout_2.addWidget(self.gvSimulator, 1, 0, 1, 3)
        self.label_5 = QtWidgets.QLabel(self.frame)
        self.label_5.setObjectName("label_5")
        self.gridLayout_2.addWidget(self.label_5, 0, 0, 1, 3)
        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 1)
        self.btnSimulate = QtWidgets.QPushButton(SimulateDialog)
        self.btnSimulate.setObjectName("btnSimulate")
        self.gridLayout.addWidget(self.btnSimulate, 1, 0, 1, 1)

        self.retranslateUi(SimulateDialog)
        QtCore.QMetaObject.connectSlotsByName(SimulateDialog)

    def retranslateUi(self, SimulateDialog):
        _translate = QtCore.QCoreApplication.translate
        SimulateDialog.setWindowTitle(_translate("SimulateDialog", "Simulation settings"))
        self.label_7.setText(_translate("SimulateDialog", "Device Profiles:"))
        item = self.tableDeviceProfiles.horizontalHeaderItem(0)
        item.setText(_translate("SimulateDialog", "Name"))
        item = self.tableDeviceProfiles.horizontalHeaderItem(1)
        item.setText(_translate("SimulateDialog", "Receive"))
        item = self.tableDeviceProfiles.horizontalHeaderItem(2)
        item.setText(_translate("SimulateDialog", "Send"))
        self.toolButton.setText(_translate("SimulateDialog", "..."))
        self.toolButton_2.setText(_translate("SimulateDialog", "..."))
        self.label.setText(_translate("SimulateDialog", "Simulate:"))
        self.label_2.setText(_translate("SimulateDialog", "Repeat:"))
        self.spinBoxNRepeat.setSpecialValueText(_translate("SimulateDialog", "Infinite"))
        self.label_3.setText(_translate("SimulateDialog", "Timeout (in seconds):"))
        self.label_4.setText(_translate("SimulateDialog", "In case of an overdue response:"))
        self.comboBoxError.setItemText(0, _translate("SimulateDialog", "Resend last message"))
        self.comboBoxError.setItemText(1, _translate("SimulateDialog", "Stop simulation"))
        self.comboBoxError.setItemText(2, _translate("SimulateDialog", "Restart simulation"))
        self.label_6.setText(_translate("SimulateDialog", "Max retries:"))
        self.btnLogAll.setText(_translate("SimulateDialog", "Log all"))
        self.btnLogNone.setText(_translate("SimulateDialog", "Log none"))
        self.btnLog.setText(_translate("SimulateDialog", "Toggle selected"))
        self.label_5.setText(_translate("SimulateDialog", "Log settings:"))
        self.btnSimulate.setText(_translate("SimulateDialog", "Confirm"))

from urh.ui.views.LoggingGraphicsView import LoggingGraphicsView
