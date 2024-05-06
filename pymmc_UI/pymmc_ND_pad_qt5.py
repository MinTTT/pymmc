# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'pymmc_ND_pad.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(519, 781)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayoutWidget = QWidget(self.centralwidget)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(200, 50, 77, 131))
        self.move_region = QVBoxLayout(self.verticalLayoutWidget)
        self.move_region.setObjectName(u"move_region")
        self.move_region.setContentsMargins(0, 0, 0, 0)
        self.move_up = QPushButton(self.verticalLayoutWidget)
        self.move_up.setObjectName(u"move_up")

        self.move_region.addWidget(self.move_up)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.move_region.addItem(self.verticalSpacer_2)

        self.move_down = QPushButton(self.verticalLayoutWidget)
        self.move_down.setObjectName(u"move_down")

        self.move_region.addWidget(self.move_down)

        self.verticalLayoutWidget_2 = QWidget(self.centralwidget)
        self.verticalLayoutWidget_2.setObjectName(u"verticalLayoutWidget_2")
        self.verticalLayoutWidget_2.setGeometry(QRect(20, 260, 461, 421))
        self.ND_table_region = QVBoxLayout(self.verticalLayoutWidget_2)
        self.ND_table_region.setObjectName(u"ND_table_region")
        self.ND_table_region.setContentsMargins(0, 0, 0, 0)
        self.ND_table = QTableWidget(self.verticalLayoutWidget_2)
        if (self.ND_table.columnCount() < 5):
            self.ND_table.setColumnCount(5)
        __qtablewidgetitem = QTableWidgetItem()
        self.ND_table.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.ND_table.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.ND_table.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.ND_table.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.ND_table.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        self.ND_table.setObjectName(u"ND_table")
        self.ND_table.horizontalHeader().setDefaultSectionSize(80)

        self.ND_table_region.addWidget(self.ND_table)

        self.horizontalLayoutWidget = QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setObjectName(u"horizontalLayoutWidget")
        self.horizontalLayoutWidget.setGeometry(QRect(20, 220, 461, 31))
        self.function_region = QHBoxLayout(self.horizontalLayoutWidget)
        self.function_region.setObjectName(u"function_region")
        self.function_region.setContentsMargins(0, 0, 0, 0)
        self.checkBox_2 = QCheckBox(self.horizontalLayoutWidget)
        self.checkBox_2.setObjectName(u"checkBox_2")

        self.function_region.addWidget(self.checkBox_2)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.function_region.addItem(self.horizontalSpacer)

        self.delete_pos = QPushButton(self.horizontalLayoutWidget)
        self.delete_pos.setObjectName(u"delete_pos")

        self.function_region.addWidget(self.delete_pos)

        self.horizontalLayoutWidget_2 = QWidget(self.centralwidget)
        self.horizontalLayoutWidget_2.setObjectName(u"horizontalLayoutWidget_2")
        self.horizontalLayoutWidget_2.setGeometry(QRect(400, 690, 77, 31))
        self.horizontalLayout = QHBoxLayout(self.horizontalLayoutWidget_2)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.record_position = QPushButton(self.horizontalLayoutWidget_2)
        self.record_position.setObjectName(u"record_position")
        self.record_position.setEnabled(True)

        self.horizontalLayout.addWidget(self.record_position)

        self.horizontalLayoutWidget_3 = QWidget(self.centralwidget)
        self.horizontalLayoutWidget_3.setObjectName(u"horizontalLayoutWidget_3")
        self.horizontalLayoutWidget_3.setGeometry(QRect(310, 690, 77, 31))
        self.update_layout = QHBoxLayout(self.horizontalLayoutWidget_3)
        self.update_layout.setObjectName(u"update_layout")
        self.update_layout.setContentsMargins(0, 0, 0, 0)
        self.update = QPushButton(self.horizontalLayoutWidget_3)
        self.update.setObjectName(u"update")
        self.update.setEnabled(True)

        self.update_layout.addWidget(self.update)

        self.horizontalLayoutWidget_4 = QWidget(self.centralwidget)
        self.horizontalLayoutWidget_4.setObjectName(u"horizontalLayoutWidget_4")
        self.horizontalLayoutWidget_4.setGeometry(QRect(130, 70, 211, 81))
        self.horizontalLayout_2 = QHBoxLayout(self.horizontalLayoutWidget_4)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.move_left = QPushButton(self.horizontalLayoutWidget_4)
        self.move_left.setObjectName(u"move_left")

        self.horizontalLayout_2.addWidget(self.move_left)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_3)

        self.move_right = QPushButton(self.horizontalLayoutWidget_4)
        self.move_right.setObjectName(u"move_right")

        self.horizontalLayout_2.addWidget(self.move_right)

        self.left_step = QDoubleSpinBox(self.centralwidget)
        self.left_step.setObjectName(u"left_step")
        self.left_step.setGeometry(QRect(40, 100, 81, 22))
        self.left_step.setMaximum(9999.000000000000000)
        self.right_step = QDoubleSpinBox(self.centralwidget)
        self.right_step.setObjectName(u"right_step")
        self.right_step.setGeometry(QRect(360, 100, 91, 22))
        self.right_step.setMaximum(9999.000000000000000)
        self.down_step = QDoubleSpinBox(self.centralwidget)
        self.down_step.setObjectName(u"down_step")
        self.down_step.setGeometry(QRect(191, 190, 91, 22))
        self.down_step.setMaximum(9999.000000000000000)
        self.down_step.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.up_step = QDoubleSpinBox(self.centralwidget)
        self.up_step.setObjectName(u"up_step")
        self.up_step.setGeometry(QRect(210, 20, 81, 22))
        self.up_step.setMaximum(9999.000000000000000)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 519, 22))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.move_up.setText(QCoreApplication.translate("MainWindow", u"UP", None))
        self.move_down.setText(QCoreApplication.translate("MainWindow", u"DOWN", None))
        ___qtablewidgetitem = self.ND_table.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"x_pos", None));
        ___qtablewidgetitem1 = self.ND_table.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", u"y_pos", None));
        ___qtablewidgetitem2 = self.ND_table.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MainWindow", u"z_pos", None));
        ___qtablewidgetitem3 = self.ND_table.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("MainWindow", u"pfs", None));
        ___qtablewidgetitem4 = self.ND_table.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("MainWindow", u"select", None));
        self.checkBox_2.setText(QCoreApplication.translate("MainWindow", u"goto selected", None))
        self.delete_pos.setText(QCoreApplication.translate("MainWindow", u"Delete", None))
        self.record_position.setText(QCoreApplication.translate("MainWindow", u"Record", None))
        self.update.setText(QCoreApplication.translate("MainWindow", u"Update", None))
        self.move_left.setText(QCoreApplication.translate("MainWindow", u"LEFT", None))
        self.move_right.setText(QCoreApplication.translate("MainWindow", u"RIGHT", None))
    # retranslateUi

