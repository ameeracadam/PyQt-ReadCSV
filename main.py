from PyQt5 import QtWidgets, uic, QtCore, QtGui
import sys
import os
import csv

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('main.ui', self)

        self.fileName = None

        self.loadDataButton = self.findChild(QtWidgets.QPushButton, 'loadDataButton')
        self.loadDataButton.clicked.connect(self.loadCSV)

        self.hashDataButton = self.findChild(QtWidgets.QPushButton, 'hashDataButton')
        self.hashDataButton.clicked.connect(self.hashData)   

        self.tableView = self.findChild(QtWidgets.QTableView, 'tableView')
        self.model = QtGui.QStandardItemModel(None)
        self.tableView.setModel(self.model)     

        self.show()

    def loadCSV(self, fileName):
        fileName, _  = QtWidgets.QFileDialog.getOpenFileName(None, "Open CSV",
            (QtCore.QDir.homePath()), "CSV (*.csv)")
        if fileName:
            self.fileName = fileName
            print(self.fileName)
            ff = open(fileName, 'r')
            text = ff.read()
            ff.close()
            f = open(fileName, 'r')
            with f:
                self.fname = os.path.splitext(str(fileName))[0].split("/")[-1]
                if text.count(';') <= text.count(','):
                    reader = csv.reader(f, delimiter = ',')
                    self.model.clear()
                    for row in reader:
                        items = [QtGui.QStandardItem(field) for field in row]
                        self.model.appendRow(items)
                    self.tableView.resizeColumnsToContents()
    
    def hashData(self):
        if self.fileName is None:
            msg = QtWidgets.QMessageBox()
            msg.setWindowTitle('Warning')
            msg.setText('No data has been loaded!')
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            x = msg.exec_()
        else:
            msg = QtWidgets.QMessageBox()
            msg.setWindowTitle('Hashing data')
            msg.setText('Data is being hashed.')
            msg.setIcon(QtWidgets.QMessageBox.Information)
            x = msg.exec_()
        pass

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    sys.exit(app.exec_())