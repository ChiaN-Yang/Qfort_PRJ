from PyQt5 import QtWidgets, uic
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys
import os
import numpy as np
import math
import csv
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt

data_name = 'tt-2.csv'


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # pointer
        self.data_num = 1
        self.window_length = 51
        self.polyorder = 3
        self.alpha = 30
        self.b = 540
        self.c = 10
        self.d = 500
        self.result = np.zeros((128, 128))

        # Load the UI Page
        uic.loadUi('view.ui', self)

        # Load data
        self.x_data = []
        self.y_data = []
        with open(data_name, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                self.x_data.append(row[0])
                self.y_data.append(row[1])
        del(self.x_data[0])
        del(self.y_data[0])
        self.x_data = list(map(float, self.x_data))
        self.y_data = list(map(float, self.y_data))

        # Plot origin left
        self.left_origin_graph = self.widget.plot(self.x_data, self.y_data)
        self.lr = pg.LinearRegionItem([300, 500])
        self.lr.setZValue(-10)
        self.widget.addItem(self.lr)
        # Plot smooth left
        self.y_smooth = savgol_filter(self.y_data, 51, 3)
        self.left_smooth_graph = self.widget.plot(
            self.x_data, self.y_smooth, pen=(255, 0, 0, 200))

        # Plot smooth right
        self.right_smooth_graph = self.widget_2.plot(
            self.x_data, self.y_smooth, pen=(255, 0, 0, 200))
        self.region_left = self.closest(
            self.x_data, int(self.lr.getRegion()[0]))
        self.region_right = self.closest(
            self.x_data, int(self.lr.getRegion()[1]))
        self.x_region = np.array(
            self.x_data[self.region_left:self.region_right])
        # Plot gaussian right
        self.y_guass = self.gaussian(
            self.x_region, self.alpha, self.b, self.c, self.d)
        self.gaussian_graph = self.widget_2.plot(
            self.x_region, self.y_guass, pen=(0, 0, 255, 200))

        # Plot answer right
        self.y_answer = self.y_data[self.region_left:self.region_right] - \
            self.y_guass + 500
        self.answer_graph = self.widget_2.plot(
            self.x_region, self.y_answer, pen=(0, 255, 0, 200))

        # gaussian change
        self.lineEdit.textChanged[str].connect(self.gaussianChange)
        self.lineEdit_2.textChanged[str].connect(self.gaussianChange)
        self.lineEdit_5.textChanged[str].connect(self.gaussianChange)
        self.lineEdit_6.textChanged[str].connect(self.gaussianChange)
        self.lineEdit_3.textChanged[str].connect(self.smoothChange)
        self.lineEdit_4.textChanged[str].connect(self.smoothChange)
        self.pushButton.clicked.connect(self.previousLine)
        self.pushButton.setEnabled(False)
        self.pushButton_2.clicked.connect(self.nextLine)
        self.pushButton_3.clicked.connect(self.displayResult)

    def previousLine(self):
        self.data_num -= 1
        self.reLoadData()
        if self.data_num == 1:
            self.pushButton.setEnabled(False)

    def nextLine(self):
        self.data_num += 1
        self.reLoadData()
        if self.data_num != 1:
            self.pushButton.setEnabled(True)

    def reLoadData(self):
        y_data = []
        with open(data_name, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                y_data.append(row[self.data_num])
        del(y_data[0])
        y_data = list(map(float, y_data))
        self.y_data = y_data
        self.renewGraph()

    def closest(self, list, Number):
        aux = []
        for valor in list:
            aux.append(abs(Number-valor))
        return aux.index(min(aux))

    def updatePlot(self):
        self.widget_2.setXRange(*self.lr.getRegion(), padding=0)
        self.renewGraph()

    def updateRegion(self):
        self.lr.setRegion(self.widget_2.getViewBox().viewRange()[0])

    def gaussian(self, x, alpha, b, c, d):
        return alpha*np.exp(-np.power((x - b), 2.)/2/c/c)+d

    def gaussianChange(self):
        try:
            self.alpha = float(self.lineEdit.text())
            self.b = float(self.lineEdit_2.text())
            self.c = float(self.lineEdit_5.text())
            self.d = float(self.lineEdit_6.text())
            self.renewGraph()
        except ValueError:
            pass

    def smoothChange(self):
        try:
            self.window_length = int(self.lineEdit_3.text())
            self.polyorder = int(self.lineEdit_4.text())
            self.renewGraph()
        except ValueError:
            pass

    def renewGraph(self):
        # Plot origin left
        self.left_origin_graph.setData(self.x_data, self.y_data)
        # Plot smooth left
        self.y_smooth = savgol_filter(
            self.y_data, self.window_length, self.polyorder)
        self.left_smooth_graph.setData(
            self.x_data, self.y_smooth, pen=(255, 0, 0, 200))
        # Plot smooth right
        self.right_smooth_graph.setData(
            self.x_data, self.y_smooth, pen=(255, 0, 0, 200))
        self.region_left = self.closest(
            self.x_data, int(self.lr.getRegion()[0])+1)
        self.region_right = self.closest(
            self.x_data, int(self.lr.getRegion()[1])+1)
        self.x_region = np.array(
            self.x_data[self.region_left:self.region_right])
        self.y_guass = self.gaussian(
            self.x_region, self.alpha, self.b, self.c, self.d)
        # Plot gaussian right
        self.gaussian_graph.setData(
            self.x_region, self.y_guass, pen=(0, 0, 255, 200))
        # Plot answer right
        self.y_answer = self.y_smooth[self.region_left:self.region_right] - \
            self.y_guass + 500
        self.answer_graph.setData(
            self.x_region, self.y_answer, pen=(0, 255, 0, 200))
        self.label_4.setText(f'{max(self.y_answer):.3f}')
        list_y = self.y_answer.tolist()
        index_max = list_y.index(max(list_y))
        self.answer_x = self.x_region[index_max]
        self.label_10.setText(f'{self.answer_x:.3f}')

    def displayResult(self):
        try:
            self.data_num = 1
            for i in range(128):
                for j in range(128):
                    self.data_num += 1
                    self.reLoadData()
                    self.result[i][j] = self.answer_x
                    app.processEvents()
                    print(f'progress: {i*128+j} / {128*128}')

            self.showResult()

        except:
            self.showResult()

    def showResult(self):
        with open('output.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(self.result)

        fig = plt.figure(figsize=(8, 6))
        plt.pcolormesh(self.result)
        plt.title("Plot 2D array")
        plt.colorbar()
        plt.show()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    main.lr.sigRegionChanged.connect(main.updatePlot)
    main.widget_2.sigXRangeChanged.connect(main.updateRegion)
    main.updatePlot()
    sys.exit(app.exec_())
