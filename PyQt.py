import sys
import csv, codecs 
import os
import io
import re
import pandas as pd
from PyQt5 import QtPrintSupport

from PyQt5 import QtCore, QtGui, QtWidgets, QtPrintSupport
from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtCore import QFile
from PyQt5.QtCore import pyqtSlot

from PyQt5.QtGui import (QImage, QPainter, QIcon, QKeySequence, QIcon, QTextCursor, QPalette,
                                          QCursor, QDropEvent, QTextDocument, QTextTableFormat, QColor, QBrush)
from PyQt5.QtCore import (QFile, QSettings, Qt, QFileInfo, QItemSelectionModel, QDir, 
                                            QMetaObject, QAbstractTableModel, QModelIndex, QVariant)
from PyQt5.QtWidgets import (QMainWindow , QAction, QWidget, QLineEdit, QMessageBox, QAbstractItemView, QApplication, 
                                                            QTableWidget, QTableWidgetItem, QGridLayout, QFileDialog, QMenu, QInputDialog, QPushButton)

class Example(QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        self.initUI()
        
        
    def initUI(self): 

        self.fileName = ""
        self.fname = "List"
        self.model =  QtGui.QStandardItemModel(self)

        self.tableView = QtWidgets.QTableView(self)
        self.tableView.setStyleSheet(stylesheet(self))
        self.tableView.setModel(self.model)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.setShowGrid(True)
        self.tableView.setGeometry(10, 50, 780, 645)        
        
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&File')
        load_csv = QtWidgets.QAction('Load', self)
        save_csv = QtWidgets.QAction('Save', self)
        fileMenu.addAction(load_csv)
        fileMenu.addAction(save_csv)

        load_csv.triggered.connect(self.loadCsv)
        save_csv.triggered.connect(self.writeCsv)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('Hash')
        
        hashReg = QtWidgets.QMenu('Regular Expression', self)
        hashAll = QtWidgets.QAction('Hash All', self) 
        hashCol = QtWidgets.QAction('Hash Selected Column', self)
        hashReg.addAction(hashAll)     
        hashReg.addAction(hashCol)

        hashAll.triggered.connect(self.hashAllData)
        hashCol.triggered.connect(self.hashColumn)
        
        fileMenu.addMenu(hashReg)

        self.setMinimumSize(820,820)
        self.setWindowTitle('PyQy Hash')    
        self.show()
    
    
    def loadCsv(self, fileName):
       fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open CSV",
               (QtCore.QDir.homePath()), "CSV (*.csv)")
 
       if fileName:
           print(fileName)
           ff = open(fileName, 'r')
           mytext = ff.read()
           ff.close()
           f = open(fileName, 'r')
           with f:
               self.fname = os.path.splitext(str(fileName))[0].split("/")[-1]
               self.setWindowTitle(self.fname)
               if mytext.count(';') <= mytext.count('\t'):
                   reader = csv.reader(f, delimiter = ',')
                   self.model.clear()
                   for row in reader:    
                       items = [QtGui.QStandardItem(field) for field in row]
                       self.model.appendRow(items)
                   self.tableView.resizeColumnsToContents()
                   self.tableView.resizeRowsToContents()
                   print("File Loaded")

    def writeCsv(self, fileName):
       # find empty cells
       for row in range(self.model.rowCount()):
           for column in range(self.model.columnCount()):
               myitem = self.model.item(row,column)
               if myitem is None:
                   item = QtGui.QStandardItem("")
                   self.model.setItem(row, column, item)
       fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save File", 
                       (QtCore.QDir.homePath() + "/" + self.fname + ".csv"),"CSV Files (*.csv)")
       if fileName:
           print(fileName)
           f = open(fileName, 'w', newline = '')
           with f:
               writer = csv.writer(f, delimiter = ',')
               for rowNumber in range(self.model.rowCount()):
                   fields = [self.model.data(self.model.index(rowNumber, columnNumber),
                                        QtCore.Qt.DisplayRole)
                    for columnNumber in range(self.model.columnCount())]
                   writer.writerow(fields)
               self.fname = os.path.splitext(str(fileName))[0].split("/")[-1]
               self.setWindowTitle(self.fname)

    def hashAllData(self):
        model = self.model
        self.tableWidget = QtWidgets.QTableWidget()
        # numRows = self.tableWidget.rowCount()
        # self.tableWidget.insertRow(numRows)
        pattern = '[a-zA-Z0-9]+'
        for row in range(model.rowCount()):
            data = []
            for column in range(model.columnCount()):
                to_list = []
                index = model.index(row, column)
                i = index.data()
                new_i = []
                n = i.split(' ')
                for i in n:
                    if any((len(i)>5) and char.isdigit() for char in i):
                        i = re.sub(pattern, 'xxxxx', i)
                    new_i.append(i)
                    new = ' '.join(new_i)
                #new = QtWidgets.QTableWidgetItem(new)
                print(index.row(), index.column(), new)
                self.model.item(int(index.row()), int(index.column())).setText(new)
                #self.tableWidget.setItem(int(index.row()), int(index.column()), new)
            self.tableView.resizeColumnsToContents()

    def hashColumn(self):
        model = self.model
        #model = QtGui.QStandardItemModel()
        # self.listwidget = QtWidgets.QListWidget()
        pattern = '[a-zA-Z0-9]+'
        column = self.tableView.selectionModel().selectedColumns()
        for index in column:
            col_num = index.column()
            print(col_num)

        for row in range(model.rowCount()):
            data = []
            for column in range(model.columnCount()):
                to_list = []
                index = model.index(row, column)
                i = index.data()
                new_i = []
                n = i.split(' ')
                if index.column() == col_num:
                    for i in n:
                        if any((len(i)>5) and char.isdigit() for char in i):
                            i = re.sub(pattern, 'xxxxx', i)
                        new_i.append(i)
                        new = ' '.join(new_i)
                    #new = QtWidgets.QTableWidgetItem(new)
                    print(index.row(), index.column(), new)
                    self.model.item(int(index.row()), int(index.column())).setText(new)
                    #self.tableWidget.setItem(int(index.row()), int(index.column()), new)
                self.tableView.resizeColumnsToContents()

def stylesheet(self):
       return
        
        
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())