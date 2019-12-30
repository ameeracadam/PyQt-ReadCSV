from PyQt5 import QtCore, QtGui, QtWidgets
import os
import csv


class Ui_MainWindow(object):
   
    def setupUi(self, MainWindow):
        self.model = QtGui.QStandardItemModel(None)
        MainWindow.setObjectName("Data Engineering Tool")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.verticalLayout_4.addWidget(self.label)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")

        self.tableView = QtWidgets.QTableView(self.centralwidget)
        self.tableView.setObjectName("tableView")
        self.tableView.setModel(self.model)

        self.verticalLayout.addWidget(self.tableView)
        
        # load data button
        self.loadDataButton = QtWidgets.QPushButton(self.centralwidget)
        self.loadDataButton.setObjectName("loadDataButton")
        self.loadDataButton.clicked.connect(self.loadCSV)

        self.verticalLayout.addWidget(self.loadDataButton)
        self.verticalLayout_4.addLayout(self.verticalLayout)

        # hash data button
        self.hashDataButton = QtWidgets.QPushButton(self.centralwidget)
        self.hashDataButton.setObjectName("hashDataButton")
        self.verticalLayout_4.addWidget(self.hashDataButton)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\"><span style=\" font-size:36pt; font-weight:600;\">Data Engineering Tool</span></p></body></html>"))
        self.loadDataButton.setText(_translate("MainWindow", "Load Data"))
        self.hashDataButton.setText(_translate("MainWindow", "Hash"))
    
    def loadCSV(self, fileName):
        fileName, _  = QtWidgets.QFileDialog.getOpenFileName(None, "Open CSV",
            (QtCore.QDir.homePath()), "CSV (*.csv)")
        if fileName:
            print(fileName)
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


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
