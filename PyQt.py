import sys
import csv, codecs 
import os
import io
import re
import pandas as pd
import numpy as np
import csv
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

class HashingWindow(QtWidgets.QWidget):
    hashRegEx = QtCore.pyqtSignal()
    hashPy = QtCore.pyqtSignal()

    def __init__(self):
        super(HashingWindow, self).__init__()

        # self.values = QtWidgets.QComboBox(self)
        # self.mainwindow.col_val.connect(self.print_val)

        RegExp_btn = QtWidgets.QPushButton("Hash RegExp")
        PyHash_btn = QtWidgets.QPushButton("Use Python Hashing")

        RegExp_btn.clicked.connect(self.RegExHashing)
        PyHash_btn.clicked.connect(self.PyHashing)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(RegExp_btn)
        layout.addWidget(PyHash_btn)

        self.setLayout(layout)
        self.setWindowTitle("Hashing Options")
        self.setMinimumWidth(350)
    def print_val(self):
        print(col_val)

    def RegExHashing(self):
        self.hashRegEx.emit()
    
    def PyHashing(self):
        self.hashPy.emit()

    
class Window(QtWidgets.QWidget):
    col_val = QtCore.pyqtSignal(list)
    def __init__(self):
        super(Window, self).__init__()

        self.initUI()

    def initUI(self):

        ##Load and Save Buttons##
        self.fileName = ""
        self.fname = "List"
        self.model =  QtGui.QStandardItemModel(self)

        self.tableView = QtWidgets.QTableView(self)
        self.tableView.setStyleSheet(stylesheet(self))
        self.tableView.setModel(self.model)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.setShowGrid(True)
        self.tableView.setGeometry(10, 50, 780, 645)        
        
        self.pushButtonLoad = QtWidgets.QPushButton(self)
        self.pushButtonLoad.setText('Load File')
        self.pushButtonLoad.clicked.connect(self.loadCSV)
        self.pushButtonLoad.setFixedWidth(80)
        self.pushButtonLoad.move(10,10)
        self.pushButtonLoad.setStyleSheet(stylesheet(self))
        
        self.pushButtonSave = QtWidgets.QPushButton(self)
        self.pushButtonSave.setText('Save File')
        self.pushButtonSave.clicked.connect(self.saveCSV)
        self.pushButtonSave.setFixedWidth(80)
        self.pushButtonSave.move(100,10)
        self.pushButtonSave.setStyleSheet(stylesheet(self))

        self.emptybox = QtWidgets.QComboBox(self)
        self.emptybox.move(10,700)

        ##Create Button for Hashing Window##
        self.hashopt = HashingWindow()
        self.hashopt.hashRegEx.connect(self.hash_RegEx)
        self.hashopt.hashPy.connect(self.print_hashpy)

        self.hashBtn = QtWidgets.QPushButton(self)
        self.hashBtn.setText("Hash Selected Data")
        self.hashBtn.clicked.connect(self.get_options)
        self.hashBtn.setFixedWidth(120)
        self.hashBtn.move(100,700)
        self.hashBtn.setStyleSheet(stylesheet(self))

        self.setMinimumSize(820,820)
        self.setWindowTitle('PyQt Hash')    
        self.show()

    def loadCSV(self, filename):
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
        self.printColumns()
 
    
    def saveCSV(self, fileName):
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

    def printColumns(self):
        model = self.model
        col_list = []
        for column in range(model.columnCount()):
            index = model.index(0, column)
            i = index.data()
            print(i)
            col_list.append(i)
            self.emptybox.addItem(i)
        self.emptybox.addItem("All Columns")
        self.col_val.emit(col_list) #created a signal to emit in the future (create new window)

    def get_options(self, index):
        selected_col = self.emptybox.itemText(self.emptybox.currentIndex())
        print("You have chosen", selected_col)
        self.hashopt.show()

    def hash_RegEx(self):
        model = self.model
        self.tableWidget = QtWidgets.QTableWidget()
        selected_col = self.emptybox.itemText(self.emptybox.currentIndex())
        pattern = '[a-zA-Z0-9]+'
        if (selected_col == "All Columns"):
            print("Hashing All Columns")
        # numRows = self.tableWidget.rowCount()
        # self.tableWidget.insertRow(numRows)
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
                            i = re.sub(pattern, str(hash(i)), i)
                        new_i.append(i)
                        new = ' '.join(new_i)
                    #new = QtWidgets.QTableWidgetItem(new)
                    #print(index.row(), index.column(), new)
                    self.model.item(int(index.row()), int(index.column())).setText(new)
                    #self.tableWidget.setItem(int(index.row()), int(index.column()), new)
                self.tableView.resizeColumnsToContents()
            print("Hashed All Columns")
        else:
            print("Hashing column:", selected_col)
            for column in range(model.columnCount()):
                index = model.index(0, column)
                i = index.data()
                if (i == selected_col):
                    col_num = index.column()

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
                                i = re.sub(pattern, str(hash(i)), i)
                            new_i.append(i)
                            new = ' '.join(new_i)
                        #new = QtWidgets.QTableWidgetItem(new)
                        #print(index.row(), index.column(), new)
                        self.model.item(int(index.row()), int(index.column())).setText(new)
                        #self.tableWidget.setItem(int(index.row()), int(index.column()), new)
                    self.tableView.resizeColumnsToContents()
            print("Hashed Selected Column")

    def print_hashpy(self):
        model = self.model
        self.tableWidget = QtWidgets.QTableWidget()
        selected_col = self.emptybox.itemText(self.emptybox.currentIndex())
        pattern = '[a-zA-Z0-9]+'
        if (selected_col == "All Columns"):
            print("Hashing All Columns")
        # numRows = self.tableWidget.rowCount()
        # self.tableWidget.insertRow(numRows)
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
                            i = re.sub(pattern, str(hash(i)), i)
                        new_i.append(i)
                        new = ' '.join(new_i)
                    #new = QtWidgets.QTableWidgetItem(new)
                    #print(index.row(), index.column(), new)
                    self.model.item(int(index.row()), int(index.column())).setText(new)
                    #self.tableWidget.setItem(int(index.row()), int(index.column()), new)
                self.tableView.resizeColumnsToContents()
            print("Hashed All Columns")
        else:
            print("Hashing column:", selected_col)
            for column in range(model.columnCount()):
                index = model.index(0, column)
                i = index.data()
                if (i == selected_col):
                    col_num = index.column()

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
                                i = re.sub(pattern, str(hash(i)), i)
                            new_i.append(i)
                            new = ' '.join(new_i)
                        #new = QtWidgets.QTableWidgetItem(new)
                        #print(index.row(), index.column(), new)
                        self.model.item(int(index.row()), int(index.column())).setText(new)
                        #self.tableWidget.setItem(int(index.row()), int(index.column()), new)
                    self.tableView.resizeColumnsToContents()
            print("Hashed Selected Column")
    

def stylesheet(self):
       return
    
if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())