import sys
import csv, codecs 
import os
import io
import re
import pandas as pd
import numpy as np
import csv
import hashlib
from PyQt5 import QtPrintSupport

from PyQt5 import QtCore, QtGui, QtWidgets, QtPrintSupport
from PyQt5.QtCore import QFile
from PyQt5.QtCore import pyqtSlot

from PyQt5.QtGui import (QImage, QPainter, QIcon, QKeySequence, QIcon, QTextCursor, QPalette,
                                          QCursor, QDropEvent, QTextDocument, QTextTableFormat, QColor, QBrush)
from PyQt5.QtCore import (QFile, QSettings, Qt, QFileInfo, QItemSelectionModel, QDir, 
                                            QMetaObject, QAbstractTableModel, QModelIndex, QVariant)
from PyQt5.QtWidgets import (QMainWindow , QAction, QWidget, QLineEdit, QMessageBox, QAbstractItemView, QApplication, 
                                                            QTableWidget, QTableWidgetItem, QGridLayout, QFileDialog, QMenu, QInputDialog, QPushButton)

class MainPage(QtWidgets.QMainWindow, QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        super(MainPage, self).__init__()

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

        self.hashOpt = QtWidgets.QPushButton(self)
        self.hashOpt.setText('Hash Columns')
        self.hashOpt.clicked.connect(self.showChildForm)
        self.hashOpt.setFixedWidth(80)
        self.hashOpt.move(10, 700)
        self.hashOpt.setStyle(stylesheet(self))

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

    def showChildForm(self):
        model = self.model
        col_list = []
        for column in range(model.columnCount()):
            index = model.index(0, column)
            i = index.data()
            col_list.append(i)
        self.child_win = childForm(col_list)      
        self.child_win.show()
        self.child_win.value.connect(self.hash_para)
    
    def hash_para(self,value):
        print('You have chosen to hash', value[0], "using method", value[1])

        if value[0] == 'All Columns':
            if value[1] == 'Python Hashing':
                self.pyHash_all()
            if value[1] == 'sha1':
                self.sha1_all()
            if value[1] == 'sha256':
                self.sha256_all()
        
        else:
            if value[1] == 'Python Hashing':
                self.pyHash_col(value)
            if value[1] == 'sha1':
                self.sha1_col(value)
            if value[1] == 'sha256':
                self.sha256_col(value)
    
    def pyHash_all(self):
        model = self.model
        self.tableWidget = QtWidgets.QTableWidget()
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
                        i = re.sub(pattern, str(hash(i)), i)
                    new_i.append(i)
                    new = ' '.join(new_i)
                #new = QtWidgets.QTableWidgetItem(new)
                #print(index.row(), index.column(), new)
                self.model.item(int(index.row()), int(index.column())).setText(new)
                #self.tableWidget.setItem(int(index.row()), int(index.column()), new)
            self.tableView.resizeColumnsToContents()
        print("Hashed All Columns")
    
    def pyHash_col(self, value):
        model = self.model
        selected_col = value[0]
        pattern = '[a-zA-Z0-9]+'
        print('Hashing', selected_col)
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

    
    def sha1_all(self):
        m = hashlib.sha1()
        self.sha_hashing_all(m)
        
    def sha1_col(self, value):
        m = hashlib.sha1()
        selected_col = value[0]
        self.sha_hashing_col(m, selected_col) 
    
    def sha256_all(self):
        m = hashlib.sha256()
        self.sha_hashing_all(m)
    
    def sha256_col(self, value):
        m = hashlib.sha256()
        selected_col = value[0]
        self.sha_hashing_col(m, selected_col)

##sha Hashing
    
    def sha_hashing_all(self,m):
        model = self.model
        self.tableWidget = QtWidgets.QTableWidget()
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
                            encoded = i.encode()
                            m.update(encoded)
                            hashed = m.hexdigest()
                            i = re.sub(pattern, hashed, i)
                        new_i.append(i)
                        new = ' '.join(new_i)
                    #new = QtWidgets.QTableWidgetItem(new)
                    #prints(index.row(), index.column(), new)
                    self.model.item(int(index.row()), int(index.column())).setText(new)
                    #self.tableWidget.setItem(int(index.row()), int(index.column()), new)
                self.tableView.resizeColumnsToContents()
        print("Hashed All Columns")
    
    def sha_hashing_col(self, m, selected_col):
        model = self.model
        self.tableWidget = QtWidgets.QTableWidget()
        pattern = '[a-zA-Z0-9]+'
        print('Hashing', selected_col)
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
                            encoded = i.encode()
                            m.update(encoded)
                            hashed = m.hexdigest()
                            i = re.sub(pattern, hashed, i)
                        new_i.append(i)
                        new = ' '.join(new_i)
                    #new = QtWidgets.QTableWidgetItem(new)
                    #print(index.row(), index.column(), new)
                    self.model.item(int(index.row()), int(index.column())).setText(new)
                    #self.tableWidget.setItem(int(index.row()), int(index.column()), new)
                self.tableView.resizeColumnsToContents()
        print("Hashed Selected Column")




class childForm(QtWidgets.QMainWindow, QtWidgets.QWidget):

    value = QtCore.pyqtSignal(list)

    def __init__(self, myList, parent=None):
        QtWidgets.QMainWindow.__init__(self)
        self.col_val = myList

        self.subUI()
    
    def subUI(self):

        self.col_box = QtWidgets.QComboBox(self)
        for val in self.col_val:
            self.col_box.addItem(val)
        self.col_box.addItem('All Columns')
        self.col_box.move(10,10)

        self.hash_box = QtWidgets.QComboBox(self)
        self.hash_box.addItem('Python Hashing')
        self.hash_box.addItem('sha1')
        self.hash_box.addItem('sha256')
        self.hash_box.move(150, 10)

        self.to_hash = QtWidgets.QPushButton(self)
        self.to_hash.setText("Confirm Options")
        self.to_hash.clicked.connect(self.hash_this)
        self.setFixedWidth(120)
        self.to_hash.move(70,50)
        self.to_hash.setStyleSheet(stylesheet(self))

        self.setWindowTitle('Hashing Options')
        self.setMinimumSize(300,200)
        self.show()
        
    def hash_this(self):
        values = []
        selected_col = self.col_box.itemText(self.col_box.currentIndex())
        values.append(selected_col)
        selected_hash = self.hash_box.itemText(self.hash_box.currentIndex())
        values.append(selected_hash)
        # print('You have chosen:', selected_col)
        # print('Hashing Method:', selected_hash)
        self.value.emit(values)
    


def stylesheet(self):
       return


if __name__ == "__main__":
    app=QtWidgets.QApplication.instance() 
    if not app:  
         app = QtWidgets.QApplication(sys.argv)
    window = MainPage()
    window.show()
    sys.exit(app.exec_())