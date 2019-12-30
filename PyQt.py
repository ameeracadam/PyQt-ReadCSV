import sys
import csv, codecs
import os

from PyQt5 import QtCore, QtGui, QtWidgets, QtPrintSupport
from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtCore import QFile

class Window(QtWidgets.QWidget):
    def __init__(self, fileName, parent = None):
        super(Window, self).__init__(parent)
        self.fileName = ""
        self.model = QtGui.QStandardItemModel(self)

        #Create View
        self.tableView = QtWidgets.QTableView(self)
        self.tableView.setStyleSheet(stylesheet(self))
        self.tableView.setModel(self.model)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.setGeometry(10, 50, 780, 645)

        ##Load CSV
        self.pushButtonLoad = QtWidgets.QPushButton(self)
        self.pushButtonLoad.setText("Load CSV")
        self.pushButtonLoad.clicked.connect(self.loadCSV)
        self.pushButtonLoad.setFixedWidth(80)
        self.pushButtonLoad.setStyleSheet(stylesheet(self))


    def loadCSV(self, fileName):
        fileName, _  = QtWidgets.QFileDialog.getOpenFileName(self, "Open CSV",
            (QtCore.QDir.homePath()), "CSV (*.csv)")
        if fileName:
            print(fileName)
            ff = open(fileName, 'r')
            text = ff.read()
            ff.close()
            f = open(fileName, 'r')
            with f:
                self.fname = os.path.splitext(str(fileName))[0].split("/")[-1]
                self.setWindowTitle(self.fname)
                if text.count(';') <= text.count(','):
                    reader = csv.reader(f, delimiter = ',')
                    self.model.clear()
                    for row in reader:
                        items = [QtGui.QStandardItem(field) for field in row]
                        self.model.appendRow(items)
                    self.tableView.resizeColumnsToContents()
    
def stylesheet(self):
    return


if __name__ == "__main__":
    
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName('Window')
    main = Window('')
    main.setMinimumSize(820, 300)
    main.setGeometry(0,0,820,700)
    main.setWindowTitle("CSV Viewer")
    main.show()
    

sys.exit(app.exec_())