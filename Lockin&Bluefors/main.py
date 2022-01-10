# -*- coding: utf-8 -*-
"""
Created on Thu May 13 21:43:17 2021

@author: SOC
"""

# -*- coding: utf-8 -*-
"""
Created on Thu May 13 16:49:12 2021

@author: SOC
"""


# Record frequency (ms)
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QMessageBox
import pyqtgraph as pg
from BF_Temp_1_LK import Ui_MainWindow
import sys
from datetime import datetime
from pymeasure.instruments.srs.sr830 import SR830
from bluefors_origin import BlueFors
import os
acq_period = 100


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        global s_time, x, y
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Timer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_label)
        self.timer.timeout.connect(self.onNewData)

        # Buttons
        self.ui.pushButton.clicked.connect(self.timeGo)
        self.ui.pushButton_2.clicked.connect(self.timeStop)

        # LK Connection
        '''
        Adjust the GPIB number here for the lockin connection
        '''
        self.Ins = SR830("GPIB::1")

        '''
        BF Connection
        Adjust folder path for the BF connection
        '''
        # Triton folder path
        TRITON_FRIDGE_FOLDER_PATH = "E:\\DATA\\Bluefors_log\\192.168.0.116"
        TRITON_PROBE_FOLDER_PATH = "E:\\DATA\\Bluefors_log\\192.168.0.115"

        # RF folder path
        RF_FRIDGE_FOLDER_PATH = "C:\\DATA\\Bluefors_log\\192.168.0.116"
        RF_PROBE_FOLDER_PATH = "C:\\DATA\\Bluefors_log\\192.168.0.115"

        fridge_folder_path = RF_FRIDGE_FOLDER_PATH
        probe_folder_path = RF_PROBE_FOLDER_PATH

        if not os.path.isdir(fridge_folder_path) and os.path.isdir(probe_folder_path):
            print("Failed to find the file. Please check the file address.")
        else:
            self.bf_fridge = BlueFors('bf_fridge',
                                      folder_path=fridge_folder_path,
                                      channel_vacuum_can=1,
                                      channel_pumping_line=2,
                                      channel_compressor_outlet=3,
                                      channel_compressor_inlet=4,
                                      channel_mixture_tank=5,
                                      channel_venting_line=6,
                                      channel_50k_plate=1,
                                      channel_4k_plate=2,
                                      channel_magnet=3,
                                      channel_still=5,
                                      channel_mixing_chamber=8)

            self.bf_probe = BlueFors('bf_probe',
                                     folder_path=probe_folder_path,
                                     channel_vacuum_can=1,
                                     channel_pumping_line=2,
                                     channel_compressor_outlet=3,
                                     channel_compressor_inlet=4,
                                     channel_mixture_tank=5,
                                     channel_venting_line=6,
                                     channel_50k_plate=1,
                                     channel_4k_plate=2,
                                     channel_magnet=3,
                                     channel_still=5,
                                     channel_mixing_chamber=8)
        # Initialization

        # Menu
        self.ui.retranslateUi(self)
        self.ui.actionQuit.setShortcut('Ctrl+Q')
        self.ui.actionQuit.triggered.connect(app.exit)
        self.ui.actionQuit.triggered.connect(self.timer.stop)
        # self.ui.actionQuit.triggered.connect(self.Ins.shut_down)
        self.ui.actionQuit.triggered.connect(self.close)
        self.ui.actionQuit.triggered.connect(self.bf_fridge.close_all)
        self.ui.actionQuit.triggered.connect(self.bf_probe.close_all)

        # plot setting
        # get the plotDataItem as data_line (reference)
        self.plt = self.ui.graphWidget
        self.plt.setLabel('bottom', 'Tempertaute(K)')
        self.plt.setLabel('left', 'LK Magnitude R (V)')
        self.data_line = self.ui.graphWidget.plot([])
        x = []
        y = []

        s_time = datetime.now()

    def setData(self, x, y):
        self.data_line.setData(x, y, pen=pg.mkPen(pg.intColor(2), width=1))

    def onNewData(self):
        global d_sec, x, y
        x.append(float(self.probe))
        y.append(float(self.R))
        self.setData(x, y)

    def update_label(self):
        global current_time, c_time, d_time, activate, d_sec
        # Get the necessary info

        # Sample info
        self.R = self.Ins.magnitude
        self.phase = self.Ins.theta

        # Temp
        self.MXC = self.bf_fridge.get_temperature(8)
        self.probe = self.bf_probe.get_temperature(1)

        # Update the lakeshore part
        label_6 = round(self.R*1000, 3)
        self.ui.label_6.setText(str(label_6))
        self.ui.label_7.setText(str(self.phase))

        # Update the thermometer part
        label_35 = round(float(self.MXC) * 1000, 4)
        label_34 = round(float(self.probe) * 1000, 4)
        self.ui.label_35.setText(str(label_35))
        self.ui.label_34.setText(str(label_34))

        # Update the date time part
        c_time = datetime.now()
        d_time = c_time - s_time
        d_sec = str(d_time.total_seconds())
        difference_time = str(d_time)[:-3]
        current_time = c_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

        self.ui.label_16.setText(current_time)
        self.ui.label_18.setText(difference_time)

        # Save the datas
        with open(name + '.txt', 'a') as f:
            f.write(current_time)
            f.write(',')
            f.write(d_sec)
            f.write(',')
            f.write(str(self.R))
            f.write(',')
            f.write(str(self.phase))
            f.write(',')
            f.write(str(self.MXC))
            f.write(',')
            f.write(str(self.probe))
            f.write('\n')

    def timeGo(self):
        global name, full_name, s_time, x, y
        name = self.ui.lineEdit.text()
        if name == '':
            QMessageBox.information(
                self, "Wrong!.", "Please type the file name.")
        else:
            full_name = name + '.txt'
            List = os.listdir()
            if full_name in List:
                reply = QMessageBox.information(
                    self, "Wrong!.", "The file has existed. Do you want to overwrite it?", QMessageBox.Ok | QMessageBox.Close, QMessageBox.Close)
                if reply == QMessageBox.Close:
                    QMessageBox.information(
                        self, "Wrong!.", "Please adjust the file name.")
                elif reply == QMessageBox.Ok:
                    self.txt_creat()
                    self.timer.start(acq_period)
                    self.ui.graphWidget.clear()
                    s_time = datetime.now()
                    x = []
                    y = []
                    self.data_line = self.ui.graphWidget.plot([])
            else:
                self.txt_creat()
                self.timer.start(acq_period)
                self.ui.graphWidget.clear()
                s_time = datetime.now()
                x = []
                y = []
                self.data_line = self.ui.graphWidget.plot([])

    def timeStop(self):
        self.timer.stop()

    def txt_creat(self):
        global name, full_name
        title = [
            'Date time, Elasped time (s), R (V), Phase, BF_MXC(K), BF_probe(K)']
        f = open(full_name, 'w')
        f.writelines(title)
        f.write('\n')
        f.close()


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
