import sys
import csv, codecs 
import os
import io
import re
import pandas as pd
import numpy as np
import csv
import hashlib
import random
from PyQt5 import QtPrintSupport

from PyQt5 import QtCore, QtGui, QtWidgets, QtPrintSupport
from PyQt5.QtCore import QFile
from PyQt5.QtCore import pyqtSlot

from PyQt5.QtGui import (QImage, QPainter, QIcon, QKeySequence, QIcon, QTextCursor, QPalette,
                                          QCursor, QDropEvent, QTextDocument, QTextTableFormat, QColor, QBrush)
from PyQt5.QtCore import (QFile, QSettings, Qt, QFileInfo, QItemSelectionModel, QDir, 
                                            QMetaObject, QAbstractTableModel, QModelIndex, QVariant)
from PyQt5.QtWidgets import (QMainWindow , QAction, QWidget, QLineEdit, QMessageBox, QAbstractItemView, QApplication, 
                                                            QTableWidget, QTableWidgetItem, QGridLayout, QFileDialog, QMenu, QInputDialog, QPushButton,
                                                            QLabel)
from faker import Faker

from sklearn import preprocessing
from nltk.tokenize import word_tokenize


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

        self.hash_headers = QtWidgets.QCheckBox(self)
        self.containsHeaders = False
        self.hash_headers.setText('Dataset Contains Headers')
        self.hash_headers.stateChanged.connect(self.haveHeaders)
        self.hash_headers.setFixedWidth(150)
        self.hash_headers.move(190,10)

        self.hashOpt = QtWidgets.QPushButton(self)
        self.hashOpt.setText('Hash Columns')
        self.hashOpt.clicked.connect(self.showChildForm)
        self.hashOpt.setFixedWidth(80)
        self.hashOpt.move(10, 700)
        self.hashOpt.setStyle(stylesheet(self))

        self.partData = QtWidgets.QPushButton(self)
        self.partData.setText('Partition Data')
        self.partData.clicked.connect(self.datasetPartition)
        self.partData.setFixedWidth(80)
        self.partData.move(100, 700)
        self.partData.setStyleSheet(stylesheet(self))

        self.partData = QtWidgets.QPushButton(self)
        self.partData.setText('Obfuscate Data')
        self.partData.clicked.connect(self.datasetObfuscation)
        self.partData.setFixedWidth(100)
        self.partData.move(190, 700)
        self.partData.setStyleSheet(stylesheet(self))

        self.tokenizeData = QtWidgets.QPushButton(self)
        self.tokenizeData.setText('Tokenize Data')
        self.tokenizeData.clicked.connect(self.tokenData)
        self.tokenizeData.setFixedWidth(80)
        self.tokenizeData.move(300, 700)
        self.tokenizeData.setStyleSheet(stylesheet(self))

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
    

    def haveHeaders(self, state):
        self.containsHeaders is False
        if state == QtCore.Qt.Checked:
            print('Dataset contains headers')
            self.containsHeaders = True
        else:
            print('Dataset contains no headers')
            self.containsHeaders = False

    def showChildForm(self):
        model = self.model
        self.child_win = childForm(model, self.containsHeaders)      
        self.child_win.show()
        self.child_win.new_mod.connect(self.updateModel)

    def datasetPartition(self):
        model = self.model
        
        self.new_partition_window = datasetPartWin(model, self.containsHeaders)
        self.new_partition_window.show() 


    def datasetObfuscation(self):
        model = self.model

        self.new_obfuscation_window = datasetObfuscate(model)
        self.new_obfuscation_window.show()   
        self.new_obfuscation_window.new_mod.connect(self.updateModel)

    def tokenData(self):
        model = self.model
        
        self.token_win = tokenizeWindow(model, self.containsHeaders)
        self.token_win.show()
        self.token_win.new_mod.connect(self.updateModel)
    
    def updateModel(self, new_mod):
        print('Model updating')
        self.model.clear()
        model = self.model
        self.new_model = new_mod
        new_model = self.new_model
        self.tableWidget = QtWidgets.QTableWidget()

        row_num = new_model.rowCount()
        col_num = new_model.columnCount()
        self.model.setRowCount(row_num)
        self.model.setColumnCount(col_num)

        for row in range(model.rowCount()):
            for column in range(model.columnCount()):
                index = new_model.index(row, column)
                i = index.data()
                n_row = int(row)
                n_col = int(column)
                self.model.setItem(n_row,n_col,QtGui.QStandardItem(str(i)))
        
        self.tableView.resizeColumnsToContents()
        self.tableView.resizeRowsToContents()
        print('Model Updated')



class childForm(QtWidgets.QMainWindow, QtWidgets.QWidget):

    new_mod = QtCore.pyqtSignal('QStandardItemModel')


    def __init__(self, main_mod, headers, parent=None):
        QtWidgets.QMainWindow.__init__(self)
        self.main_mod = main_mod
        self.containsHeaders = headers
        self.subUI()
    
    def subUI(self):

        self.hashingModel = QtGui.QStandardItemModel(self)
        self.previewModel = QtGui.QStandardItemModel(self)

        ##populate hasingModel and previewModel

        n_row = self.main_mod.rowCount()
        n_col = self.main_mod.columnCount()

        self.hashingModel.setRowCount(n_row)
        self.hashingModel.setColumnCount(n_col)

        self.previewModel.setRowCount(n_row)
        self.previewModel.setColumnCount(n_col)

        for row in range(self.main_mod.rowCount()):
            for column in range(self.main_mod.columnCount()):
                index = self.main_mod.index(row, column)
                idx = index.data()
                self.hashingModel.setItem(row, column, QtGui.QStandardItem(str(idx)))
                self.previewModel.setItem(row, column, QtGui.QStandardItem(str(idx)))
        

        self.colModel = QtGui.QStandardItemModel()
        self.CollistView = QtWidgets.QListView()

        self.ColtableView = QtWidgets.QTableView(self)
        self.ColtableView.setStyleSheet(stylesheet(self))
        self.ColtableView.setModel(self.colModel)
        self.ColtableView.horizontalHeader().setStretchLastSection(True)
        self.ColtableView.setShowGrid(True)
        self.ColtableView.setGeometry(10, 30, 300, 150) 

        checked = False

        self.col_val = []
        for col in range(self.main_mod.columnCount()):
            index = self.main_mod.index(0, col)
            idx = index.data()
            self.col_val.append(idx)

        for string in self.col_val:
            item = QtGui.QStandardItem(string)
            item.setCheckable(True)
            check = \
                (QtCore.Qt.Checked if checked else QtCore.Qt.Unchecked)
            item.setCheckState(check)
            self.colModel.appendRow(item)

        self.CollistView.setModel(self.colModel)

        self.select_col = QtWidgets.QLabel(self)
        self.select_col.setText('Select colunms to hash')
        self.select_col.setFixedWidth(200)
        self.select_col.move(10,5)
        self.select_col.setStyleSheet(stylesheet(self))

        self.preview_mod = QtWidgets.QLabel(self)
        self.preview_mod.setText('Preview Model')
        self.preview_mod.setFixedWidth(200)
        self.preview_mod.move(10,350)
        self.preview_mod.setStyleSheet(stylesheet(self))        

        self.select_all = QtWidgets.QPushButton(self)
        self.select_all.setText('Select All')
        self.select_all.clicked.connect(self.select)
        self.select_all.setFixedWidth(80)
        self.select_all.move(320,50)
        self.select_all.setStyleSheet(stylesheet(self))

        self.cancel_all = QtWidgets.QPushButton(self)
        self.cancel_all.setText('Unselect All')
        self.cancel_all.clicked.connect(self.unselect)
        self.cancel_all.setFixedWidth(80)
        self.cancel_all.move(320,100)
        self.cancel_all.setStyleSheet(stylesheet(self))

        self.hash_mtd = QtWidgets.QLabel(self)
        self.hash_mtd.setText('Hash Method')
        self.hash_mtd.setFixedWidth(80)
        self.hash_mtd.move(10,200)
        self.hash_mtd.setStyleSheet(stylesheet(self))

        self.hash_box = QtWidgets.QComboBox(self)
        self.hash_box.addItem('sha1')
        self.hash_box.addItem('sha256')
        self.hash_box.addItem('sha224')
        self.hash_box.addItem('blake2b')
        self.hash_box.move(90, 200)

        self.set_salt = QtWidgets.QLineEdit(self)
        self.haveSalt = False
        self.set_salt.setEchoMode(QLineEdit.Password)
        self.set_salt.setFixedWidth(100)
        self.set_salt.move(90,250)
        self.set_salt.setStyleSheet(stylesheet(self))

        self.salt_line = QtWidgets.QLabel(self)
        self.salt_line.setText('Set a salt')
        self.salt_line.setFixedWidth(80)
        self.salt_line.move(10,250)
        self.salt_line.setStyleSheet(stylesheet(self))
        
        self.confirm_salt = QtWidgets.QPushButton(self)
        self.saltConfirmed = False
        self.confirm_salt.setText('Confirm Salt')
        self.confirm_salt.clicked.connect(self.new_salt_window)
        self.confirm_salt.setFixedWidth(80)
        self.confirm_salt.move(200, 250)
        self.confirm_salt.setStyleSheet(stylesheet(self))

        self.to_hash = QtWidgets.QPushButton(self)
        self.to_hash.setText("Hash!")
        self.to_hash.clicked.connect(self.hash_this)
        self.setFixedWidth(100)
        self.to_hash.move(10,310)
        self.to_hash.setStyleSheet(stylesheet(self))

        self.save_salt = QtWidgets.QPushButton(self)
        self.save_salt.setText('Save Salt')
        self.save_salt.clicked.connect(self.saveSalt)
        self.setFixedWidth(100)
        self.save_salt.move(140,310)
        self.save_salt.setStyleSheet(stylesheet(self))

        self.modelListView = QtWidgets.QListView()

        self.modelTableView = QtWidgets.QTableView(self)
        self.modelTableView.setStyleSheet(stylesheet(self))
        self.modelTableView.setModel(self.previewModel)
        self.modelTableView.horizontalHeader().setStretchLastSection(True)
        self.modelTableView.setShowGrid(True)
        self.modelTableView.setGeometry(10, 380, 480, 250)
        self.modelTableView.resizeColumnsToContents()
        self.modelTableView.resizeRowsToContents()

        self.confirmModelBtn = QtWidgets.QPushButton(self)
        self.confirmModelBtn.setText('Confirm Model')
        self.confirmModelBtn.setStyleSheet(stylesheet(self))
        self.confirmModelBtn.clicked.connect(self.confirmModel)
        self.confirmModelBtn.setFixedWidth(150)
        self.confirmModelBtn.move(160, 640)

        self.setWindowTitle('Hashing Options')
        self.setMinimumSize(500,680)
        self.show()


    def onAccepted(self):
        self.choices = []
        self.choices = [self.colModel.item(i).text() for i in
                        range(self.colModel.rowCount())
                        if self.colModel.item(i).checkState()
                        == QtCore.Qt.Checked]

        print(self.choices)

    def select(self):
        for i in range(self.colModel.rowCount()):
            item = self.colModel.item(i)
            item.setCheckState(QtCore.Qt.Checked)

    def unselect(self):
        for i in range(self.colModel.rowCount()):
            item = self.colModel.item(i)
            item.setCheckState(QtCore.Qt.Unchecked)

        self.show()

    def new_salt_window(self):
        salt = self.set_salt.text()
        self.salt_window = newSaltWindow(salt)
        self.salt_window.show()
        self.salt_window.message.connect(self.confirmSalt)
    
    def confirmSalt(self, message):
        msg = message
        # print(msg)
        if msg == 'clicked!':
            self.saltConfirmed = True
        
    def hash_this(self):
        self.choices = [self.colModel.item(i).text() for i in
                        range(self.colModel.rowCount())
                        if self.colModel.item(i).checkState()
                        == QtCore.Qt.Checked]
        if self.choices == '':
            print('Confirm Choices')
        else:
        
            model = self.hashingModel
            values = []
            columns = self.choices

            values.append(columns)

            print('You have chosen:')
            for i in columns:
                print(i)

            selected_hash = self.hash_box.itemText(self.hash_box.currentIndex())
            values.append(selected_hash)

            print('Hashing Method:', selected_hash)

            hashing_salt = self.set_salt.text()
            if hashing_salt == '':
                print('No salt used')
                values.append(hashing_salt)
                self.hashPara(values)
            else:
                if self.saltConfirmed is True:
                    print('Salt to use', hashing_salt)
                    values.append(hashing_salt)
                    self.hashPara(values)
                else:
                    print('Please confirm salt')
        
    def saveSalt(self):
        salt = self.set_salt.text()
        new_file, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save File", 
                        (QtCore.QDir.homePath() + "/" + "salt"+ ".txt"), 'txt files (*.txt)')
        
        if new_file:
            # print(new_file)
            f = open(new_file, 'w')
            f.write(salt)
            f.close()

    def hashPara(self, value):
        if value[1] == 'sha1':
            self.sha1_col(value)
        if value[1] == 'sha256':
            self.sha256_col(value)
        if value[1] == 'sha224':
            self.sha224_col(value)
        if value[1] == 'sha384':
            self.sha384_col(value)
        if value[1] == 'sha512':
            self.sha512_col(value)
        if value[1] == 'blake2b':
            self.blake2b_col(value)
        
    def sha1_col(self, value):
        m = hashlib.sha1()
        self.sha_hashing_col(m, value) 
    
    
    def sha256_col(self, value):
        m = hashlib.sha256()
        self.sha_hashing_col(m, value)

    
    def sha224_col(self, value):
        m = hashlib.sha224()
        self.sha_hashing_col(m, value)

    
    def sha384_col(self,value):
        m = hashlib.sha384()
        self.sha_hashing_col(m, value)


    
    def sha512_col(self,value):
        m = hashlib.sha512()
        self.sha_hashing_col(m, value)


    
    def blake2b_col(self, value):
        m = hashlib.blake2b()
        self.sha_hashing_col(m, value)


    def sha_hashing_col(self, m, value):
        model = self.hashingModel
        self.tableWidget = QtWidgets.QTableWidget()
        columns = value[0]
        salt = str(value[2])
        for selected_col in columns:
            if salt == '':
                print('Hashing without salt')
            else:
                print('With salt', salt)
            print('Hashing', selected_col)
            for column in range(model.columnCount()):
                index = model.index(0, column)
                i = index.data()
                if (i == selected_col):
                    col_num = index.column()
                    hash_col = col_num
                    self.start_hash(m, hash_col, salt)

    
    def start_hash(self, m, hash_col, salt):
        model = self.hashingModel
        self.tableWidget = QtWidgets.QTableWidget()
        row_range = range(model.rowCount())

        if self.containsHeaders == True:
            row_range = range(1, model.rowCount())

        for row in row_range:
            data = []
            for column in range(model.columnCount()):
                to_list = []
                index = model.index(row, column)
                i = index.data()
                new_i = []
                n = i.split(' ')
                if index.column() == hash_col:
                    for i in n:
                        i = i + salt
                        encoded = i.encode()
                        m.update(encoded)
                        hashed = m.hexdigest()
                        i = hashed
                        new_i.append(i)
                        new = ' '.join(new_i)

                    self.previewModel.item(int(index.row()), int(index.column())).setText(new)

        print("Hashed Selected Column")

        self.modelTableView.resizeColumnsToContents()

    def confirmModel(self):
        self.new_mod.emit(self.previewModel)
        print('Model has been hashed. Emitting Model.')
        self.close()


class newSaltWindow(QtWidgets.QMainWindow, QtWidgets.QWidget):

    message = QtCore.pyqtSignal(str)
    
    def __init__(self, salt, parent=None):
        QtWidgets.QMainWindow.__init__(self)
        self.salt = salt
        self.subUI()
    
    def subUI(self):

        self.model =  QtGui.QStandardItemModel(self)
        
        self.salt_text = QtWidgets.QLabel(self)
        self.salt_text.setText('Type in salt')
        self.salt_text.setFixedWidth(150)
        self.salt_text.move(10,10)
        self.salt_text.setStyleSheet(stylesheet(self))

        self.salt_line = QtWidgets.QLineEdit(self)
        self.salt_line.setEchoMode(QLineEdit.Password)
        self.salt_line.setFixedWidth(100)
        self.salt_line.move(50,40)
        self.salt_line.setStyleSheet(stylesheet(self))

        self.confirm_salt = QtWidgets.QPushButton(self)
        self.confirm_salt.setText('Re-confirm Salt')
        self.confirm_salt.clicked.connect(self.match_salt)
        self.confirm_salt.setFixedWidth(150)
        self.confirm_salt.move(25, 80)
        self.confirm_salt.setStyleSheet(stylesheet(self))

        self.setWindowTitle('Confirm Salt')
        self.setMinimumSize(150,150)
        self.show()
    
    def match_salt(self):
        msg = 'notclicked:('
        model = self.model
        new_salt = self.salt_line.text()
        initial_salt = self.salt

        # print(new_salt, initial_salt)

        if (new_salt == initial_salt):
            print('Salts match!')
            msg = 'clicked!'
            self.message.emit(msg)
            self.close()
        else:
            print("Salts don't match. Try again.")

class datasetPartWin(QtWidgets.QMainWindow, QtWidgets.QWidget):

    new_mod = QtCore.pyqtSignal('QStandardItemModel')
    
    def __init__(self, main_mod, headers, parent=None):
        QtWidgets.QMainWindow.__init__(self)
        self.main_model = main_mod
        self.model = QtGui.QStandardItemModel(self)
        self.containsHeaders = headers
        print(self.containsHeaders)
        self.subUI()
    
    def subUI(self):
        
        ##Create working model based off main model (ie don't touch main model)
        self.workingModel = QtGui.QStandardItemModel(self)
        main_model = self.main_model
        self.tableWidget = QtWidgets.QTableWidget()

        row_num = main_model.rowCount()
        col_num = main_model.columnCount()
        self.workingModel.setRowCount(row_num)
        self.workingModel.setColumnCount(col_num)

        for row in range(self.workingModel.rowCount()):
            for column in range(self.workingModel.columnCount()):
                index = main_model.index(row, column)
                i = index.data()
                n_row = int(row)
                n_col = int(column)
                self.workingModel.setItem(n_row,n_col,QtGui.QStandardItem(str(i)))

        ##Set a preview model to display
        self.previewModel = QtGui.QStandardItemModel(self)
        row_num = self.workingModel.rowCount()
        col_num = self.workingModel.columnCount()
        self.previewModel.setRowCount(row_num)
        self.previewModel.setColumnCount(col_num)

        for row in range(self.previewModel.rowCount()):
            for column in range(self.previewModel.columnCount()):
                index = self.workingModel.index(row, column)
                i = index.data()
                n_row = int(row)
                n_col = int(column)
                self.previewModel.setItem(n_row,n_col,QtGui.QStandardItem(str(i)))

        self.listView = QtWidgets.QListView()

        self.tableView = QtWidgets.QTableView(self)
        self.tableView.setStyleSheet(stylesheet(self))
        self.tableView.setModel(self.previewModel)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.setShowGrid(True)
        self.tableView.setGeometry(10, 50, 650, 600) 

        self.tableView.resizeColumnsToContents()
        self.tableView.resizeRowsToContents()

        self.part_opt = QtWidgets.QComboBox(self)

        self.part_opt.addItem('N-Fold')
        self.part_opt.move(10,680)

        self.header = QtWidgets.QLabel(self)
        self.header.setText('Current Dataset:')
        self.header.move(10,10)
        self.header.setStyleSheet(stylesheet(self))

        self.pushButtonLoad = QtWidgets.QPushButton(self)
        self.pushButtonLoad.setText('Load Options')
        self.pushButtonLoad.clicked.connect(self.loadOptions)
        self.pushButtonLoad.setFixedWidth(80)
        self.pushButtonLoad.move(120,680)
        self.pushButtonLoad.setStyleSheet(stylesheet(self))

        self.previewDataset = QtWidgets.QPushButton(self)
        self.previewDataset.setText('Preview Folded Dataset')
        self.previewDataset.clicked.connect(self.preview)
        self.previewDataset.setFixedWidth(180)
        self.previewDataset.move(10, 720)
        self.previewDataset.setStyleSheet(stylesheet(self))

        self.previewSelection = QtWidgets.QComboBox(self)
        self.previewSelection.setFixedWidth(80)
        self.previewSelection.move(200, 720)
        self.previewSelection.setStyleSheet(stylesheet(self))

        self.confirm_model = QtWidgets.QPushButton(self)
        self.confirm_model.setText('Confirm and Save Datasets')
        self.confirm_model.clicked.connect(self.confirmModel)
        self.confirm_model.setFixedWidth(180)
        self.confirm_model.move(10,760)
        self.confirm_model.setStyleSheet(stylesheet(self))

        self.setWindowTitle('Partioning Options')
        self.setMinimumSize(700,800)
        self.show()

    def confirmModel(self):

        chunk_no = 0
        g = globals()
        for chunk in self.chunks:
            save_model = g['foldedModel_{}'.format(chunk_no)]
            for row in range(save_model.rowCount()):
                for column in range(save_model.columnCount()):
                    myitem = save_model.item(row, column)
                    if myitem is None:
                        item = QtGui.QStandardItem("")
                        save_model.setItem(row, column, item)
            fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save File", 
                            (QtCore.QDir.homePath() + "/" + 'foldNo' + str(chunk_no) + ".csv"),"CSV Files (*.csv)")
            
            if fileName:
                print(fileName)
                f = open(fileName, 'w', newline = '')
                with f:
                    writer = csv.writer(f, delimiter = ',')
                    for rowNumber in range(save_model.rowCount()):
                        fields = [save_model.data(save_model.index(rowNumber, columnNumber),
                                            QtCore.Qt.DisplayRole)
                        for columnNumber in range(save_model.columnCount())]
                        writer.writerow(fields)
                    self.fname = os.path.splitext(str(fileName))[0].split("/")[-1]
            
            chunk_no = chunk_no + 1
        

    
    def loadOptions(self):
        option = self.part_opt.itemText(self.part_opt.currentIndex())

        
        if option == 'N-Fold':
            self.para_window = KFoldGetParameters()
            self.para_window.show()
            self.para_window.parameters.connect(self.nFold_split)
    
    def nFold_split(self, parameters):
        split = parameters[0]
        to_shuffle = parameters[1]
        lst = []

        if self.containsHeaders == True:
            row_start = 1 ##Contains Headers
        else:
            row_start = 0 ##Don't contain headers

        ##To shuffle the working model
        shuffle_lst = []
        if to_shuffle == 1:
            print('Shuffle Dataset')
            col_num = self.workingModel.columnCount()
            self.workingModel.setColumnCount(col_num+1)
            for row in range(int(row_start), self.workingModel.rowCount()):
                n = np.random.rand()
                shuffle_lst.append(n)
                self.workingModel.setItem(int(row), int(col_num), QtGui.QStandardItem(str(n)))
                # print(n)
        
            random.shuffle(shuffle_lst)
            ##Create a new model to input shuffled parts
            self.shuffledModel = QtGui.QStandardItemModel(self)
            self.shuffledModel.setColumnCount(col_num)
            self.shuffledModel.setRowCount(self.workingModel.rowCount())
            if row_start == 1:
                for col in range(self.shuffledModel.columnCount()):
                    index = self.workingModel.index(0, col)
                    i = index.data()
                    self.shuffledModel.setItem(0, int(col), QtGui.QStandardItem(str(i)))

            shuffle_row = row_start
            for num in shuffle_lst:
                for row in range(int(row_start), self.workingModel.rowCount()):
                    number = self.workingModel.index(row, col_num)
                    n = number.data()
                    if str(num) == str(n):
                        for col in range(self.shuffledModel.columnCount()):
                            index = self.workingModel.index(row, col)
                            idx = index.data()
                            # print(idx)
                            self.shuffledModel.setItem(int(shuffle_row), int(col), QtGui.QStandardItem(str(idx)))
                shuffle_row = shuffle_row + 1
            
            # for row in range(self.shuffledModel.rowCount()):
            #     for col in range(self.shuffledModel.columnCount()):
            #         index = self.shuffledModel.index(row, col)
            #         print(index.data())
                        
            
            self.workingModel = self.shuffledModel


        for r in range(int(row_start), self.workingModel.rowCount()):
            lst.append(r) 
        fold = int(len(lst)) // int(split)
        self.chunks = [lst[i:i + fold] for i in range(0, len(lst), fold)]

        g = globals()
        col_num = self.workingModel.columnCount()
        chunk_no = 0
        for chunk in self.chunks:
            g['foldedModel_{}'.format(chunk_no)] = QtGui.QStandardItemModel(self)
            if self.containsHeaders == True:
                g['foldedModel_{}'.format(chunk_no)].setRowCount(len(chunk)+1)
            else:
                g['foldedModel_{}'.format(chunk_no)].setRowCount(len(chunk))

            g['foldedModel_{}'.format(chunk_no)].setColumnCount(col_num)
            # print(g['foldedModel_{}'.format(chunk_no)].rowCount(), g['foldedModel_{}'.format(chunk_no)].columnCount())
            
            if self.containsHeaders == True:
                foldedModel_row = 1
                for column in range(self.workingModel.columnCount()):
                    index = self.workingModel.index(0, column)
                    i = index.data()
                    g['foldedModel_{}'.format(chunk_no)].setItem(0, int(column), QtGui.QStandardItem(str(i)))
                for row_num in chunk:
                    for row in range(1, self.workingModel.rowCount()):
                        for column in range(self.workingModel.columnCount()):
                            if int(row) == row_num:
                                index = self.workingModel.index(row, column)
                                i = index.data()
                                g['foldedModel_{}'.format(chunk_no)].setItem(foldedModel_row, int(column), QtGui.QStandardItem(str(i)))
                    foldedModel_row = foldedModel_row+1
                
            else:
                foldedModel_row = 0
                for row_num in chunk:
                    for row in range(0, self.workingModel.rowCount()):
                        for column in range(self.workingModel.columnCount()):
                            if int(row) == row_num:
                                index = self.workingModel.index(row, column)
                                i = index.data()
                                g['foldedModel_{}'.format(chunk_no)].setItem(foldedModel_row, int(column), QtGui.QStandardItem(str(i)))
                    foldedModel_row = foldedModel_row+1

            
            chunk_no = chunk_no + 1

        self.model_0 = foldedModel_0
           
        self.previewModel.clear()
        
        ##Preview First chunk
        print('Setting to preview first fold')
        self.previewModel.setRowCount(self.model_0.rowCount())
        self.previewModel.setColumnCount(self.model_0.columnCount())
        for row in range(self.previewModel.rowCount()):
            for column in range(self.previewModel.columnCount()):
                index = self.model_0.index(row,column)
                i = index.data()
                self.previewModel.setItem(int(row), int(column), QtGui.QStandardItem(str(i)))
        self.tableView.resizeColumnsToContents()
        self.tableView.resizeRowsToContents()   

        ##Populate ComboBox
        self.previewSelection.clear()
        chunk_no = 0
        for chunk in self.chunks:
            self.previewSelection.addItem(str(chunk_no))
            chunk_no = chunk_no + 1
    
    def preview(self):
        g = globals()
        preview_fold = self.previewSelection.itemText(self.previewSelection.currentIndex())
        print('Previewing fold', preview_fold)
        self.fold_model = g['foldedModel_{}'.format(preview_fold)]
        self.previewModel.clear()
        self.previewModel.setRowCount(self.fold_model.rowCount())
        self.previewModel.setColumnCount(self.fold_model.columnCount())
        for row in range(self.previewModel.rowCount()):
            for column in range(self.previewModel.columnCount()):
                index = self.fold_model.index(row,column)
                i = index.data()
                self.previewModel.setItem(int(row), int(column), QtGui.QStandardItem(str(i)))
        self.tableView.resizeColumnsToContents()
        self.tableView.resizeRowsToContents()  
    


class KFoldGetParameters(QtWidgets.QMainWindow, QtWidgets.QWidget):

    parameters = QtCore.pyqtSignal(list)
    
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self)
        self.subUI()

    def subUI(self):
        
        self.fold_lbl = QtWidgets.QLabel(self)
        self.fold_lbl.setText('Number of Folds')
        self.fold_lbl.setFixedWidth(80)
        self.fold_lbl.move(10,10)
        self.fold_lbl.setStyleSheet(stylesheet(self))

        self.n_fold = QtWidgets.QLineEdit(self)
        self.n_fold.setFixedWidth(40)
        self.n_fold.move(120,10)
        self.n_fold.setStyleSheet(stylesheet(self))

        self.shuffleBtn = QtWidgets.QCheckBox(self)
        self.shuffleBtn.setText('Shuffle Dataset')
        self.shuffleDataset = False
        self.shuffleBtn.stateChanged.connect(self.shuffleData)
        self.shuffleBtn.move(50, 40)

        self.confirm_para = QtWidgets.QPushButton(self)
        self.confirm_para.setText('Get Parameters')
        self.confirm_para.clicked.connect(self.get_parameters)
        self.confirm_para.setFixedWidth(100)
        self.confirm_para.move(50, 70)
        self.confirm_para.setStyleSheet(stylesheet(self))

        self.setWindowTitle('Parameters')
        self.setMinimumSize(140,120)
        self.show()

    def get_parameters(self):
        para = []

        size = self.n_fold.text()
        para.append(size)

        if self.shuffleDataset == True:
            para.append(int(1))
        else:
            para.append(int(0))

        self.parameters.emit(para)

        self.close()

    def shuffleData(self, state):
        self.shuffleDataset is False
        if state == QtCore.Qt.Checked:
            print('Dataset will be shuffled')
            self.shuffleDataset = True
            
        else:
            print('Dataset will not be shuffled')
            self.shuffleDataset = False

class datasetObfuscate(QtWidgets.QMainWindow, QtWidgets.QWidget):

    new_mod = QtCore.pyqtSignal('QStandardItemModel')
    
    def __init__(self, main_mod, parent=None):
        QtWidgets.QMainWindow.__init__(self)
        self.main_model = main_mod
        self.model = QtGui.QStandardItemModel(self)
        self.subUI()
    
    def subUI(self):

        self.PreviewModel = QtGui.QStandardItemModel(self)
        self.tableWidget = QtWidgets.QTableWidget()

        row_num = self.main_model.rowCount()
        col_num = self.main_model.columnCount()
        self.PreviewModel.setRowCount(row_num)
        self.PreviewModel.setColumnCount(col_num)

        for row in range(self.PreviewModel.rowCount()):
            for column in range(self.PreviewModel.columnCount()):
                index = self.main_model.index(row, column)
                i = index.data()
                n_row = int(row)
                n_col = int(column)
                self.PreviewModel.setItem(n_row,n_col,QtGui.QStandardItem(str(i)))

        self.listView = QtWidgets.QListView()

        self.tableView = QtWidgets.QTableView(self)
        self.tableView.setStyleSheet(stylesheet(self))
        self.tableView.setModel(self.PreviewModel)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.setShowGrid(True)
        self.tableView.setGeometry(10, 50, 680, 390) 

        self.tableView.resizeColumnsToContents()
        self.tableView.resizeRowsToContents()

        self.preview_lbl = QtWidgets.QLabel(self)
        self.preview_lbl.setText('Preview Model')
        self.preview_lbl.move(10, 10)

        self.obfuscationOpt = QtWidgets.QComboBox(self)
        self.obfuscationOpt.addItem('Fake Data')
        self.obfuscationOpt.addItem('Encode Labels')
        self.obfuscationOpt.setFixedWidth(100)
        self.obfuscationOpt.move(130, 470)

        self.obfuscationOpt_lbl = QtWidgets.QLabel(self)
        self.obfuscationOpt_lbl.setText('Select Masking Method')
        self.obfuscationOpt_lbl.setFixedWidth(150)
        self.obfuscationOpt_lbl.move(10, 470)

        self.loadOpt = QtWidgets.QPushButton(self)
        self.loadOpt.setText('Load Options')
        self.loadOpt.clicked.connect(self.loadOptions)
        self.loadOpt.setFixedWidth(100)
        self.loadOpt.move(250, 470)

        self.setColumns = QtWidgets.QPushButton(self)
        self.setColumns.setText('Confirm Model')
        self.setColumns.clicked.connect(self.loadModel)
        self.setColumns.setFixedWidth(250)
        self.setColumns.move(220,700)
        self.setColumns.setStyleSheet(stylesheet(self))

        self.setWindowTitle('Obfuscation Options')
        self.setMinimumSize(700,750)
        self.show()
    
    def onAccepted(self):
        self.choices = [self.col_model.item(i).text() for i in
                        range(self.col_model.rowCount())
                        if self.col_model.item(i).checkState()
                        == QtCore.Qt.Checked]

        print(self.choices)

    def select(self):
        for i in range(self.col_model.rowCount()):
            item = self.col_model.item(i)
            item.setCheckState(QtCore.Qt.Checked)

    def unselect(self):

        for i in range(self.col_model.rowCount()):
            item = self.col_model.item(i)
            item.setCheckState(QtCore.Qt.Unchecked)

        self.show()


    def loadModel(self):
        model = self.PreviewModel
        self.new_mod.emit(model)
        print('Model Emitted')
    
    def loadOptions(self):
        method = self.obfuscationOpt.itemText(self.obfuscationOpt.currentIndex())
        
        if method == 'Fake Data':
            self.fakeWin = FakeWindow(self.PreviewModel)
            self.fakeWin.show()
            self.fakeWin.new_model.connect(self.preview_Model)
        
        if method == 'Encode Labels':
            self.encodeWin = EncodeLblWindow(self.PreviewModel)
            self.encodeWin.show()
            self.encodeWin.new_model.connect(self.preview_Model)
    
    def preview_Model(self, new_mod):

        self.changedModel = new_mod
        for row in range(self.PreviewModel.rowCount()):
            for column in range(self.PreviewModel.columnCount()):
                index = self.changedModel.index(row, column)
                idx = index.data()
                self.PreviewModel.setItem(row, column, QtGui.QStandardItem(str(idx)))

        self.tableView.resizeColumnsToContents()
        self.tableView.resizeRowsToContents()
        

class FakeWindow(QtWidgets.QMainWindow, QtWidgets.QWidget):

    new_model = QtCore.pyqtSignal('QStandardItemModel')

    def __init__(self, main_mod, parent = None):
        QtWidgets.QMainWindow.__init__(self)
        self.main_model = main_mod
        self.subUI()

    def subUI(self):
        
        self.previewMod = QtGui.QStandardItemModel(self)
        self.workingMod = QtGui.QStandardItemModel(self)

        num_row = self.main_model.rowCount()
        num_col = self.main_model.columnCount()
        self.workingMod.setRowCount(num_row)
        self.workingMod.setColumnCount(num_col)

        for row in range(self.main_model.rowCount()):
            for column in range(self.main_model.columnCount()):
                index = self.main_model.index(row, column)
                idx = index.data()
                self.workingMod.setItem(int(row), int(column), QtGui.QStandardItem(str(idx)))

        ##Set columns
        self.col_list = []
        for column in range(self.main_model.columnCount()):
            index = self.main_model.index(0, column)
            i = index.data()
            self.col_list.append(i)

        self.listView = QtWidgets.QListView()

        self.tableView = QtWidgets.QTableView(self)
        self.tableView.setStyleSheet(stylesheet(self))
        self.tableView.setModel(self.workingMod)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.setShowGrid(True)
        self.tableView.setGeometry(10, 250, 480, 250) 
        self.tableView.resizeColumnsToContents()
        self.tableView.resizeRowsToContents()

        self.preview_lbl = QtWidgets.QLabel(self)
        self.preview_lbl.setText('Preview Columns')
        self.preview_lbl.setFixedWidth(150)
        self.preview_lbl.move(10, 220)

        self.selection_lbl = QtWidgets.QLabel(self)
        self.selection_lbl.setText('Select up to 3 columns to fake')
        self.selection_lbl.setFixedWidth(200)
        self.selection_lbl.move(10,5)

        self.col_lbl = QtWidgets.QLabel(self)
        self.col_lbl.setText('Select Columns')
        self.col_lbl.setFixedWidth(100)
        self.col_lbl.move(70, 30)

        self.mtd_lbl = QtWidgets.QLabel(self)
        self.mtd_lbl.setText('Type of data to fake')
        self.mtd_lbl.setFixedWidth(150)
        self.mtd_lbl.move(300, 30)

        self.col1 = QtWidgets.QComboBox(self)
        self.col1.addItem('None')
        for string in self.col_list:
            self.col1.addItem(string)
        self.col1.setFixedWidth(100)
        self.col1.move(50,60)

        self.col2 = QtWidgets.QComboBox(self)
        self.col2.addItem('None')
        for string in self.col_list:
            self.col2.addItem(string)
        self.col2.setFixedWidth(100)
        self.col2.move(50,100)

        self.col3 = QtWidgets.QComboBox(self)
        self.col3.addItem('None')
        for string in self.col_list:
            self.col3.addItem(string)
        self.col3.setFixedWidth(100)
        self.col3.move(50,140)

        self.choice1 = QtWidgets.QComboBox(self)
        self.choice1.addItem('Name')
        self.choice1.addItem('Address')
        self.choice1.addItem('Credit Card')
        self.choice1.addItem('E-Mail')
        self.choice1.addItem('Phone Number')
        self.choice1.setFixedWidth(100)
        self.choice1.move(300,60)

        self.choice2 = QtWidgets.QComboBox(self)
        self.choice2.addItem('Name')
        self.choice2.addItem('Address')
        self.choice2.addItem('Credit Card')
        self.choice2.addItem('E-Mail')
        self.choice2.addItem('Phone Number')
        self.choice2.setFixedWidth(100)
        self.choice2.move(300,100)

        self.choice3 = QtWidgets.QComboBox(self)
        self.choice3.addItem('Name')
        self.choice3.addItem('Address')
        self.choice3.addItem('Credit Card')
        self.choice3.addItem('E-Mail')
        self.choice3.addItem('Phone Number')
        self.choice3.setFixedWidth(100)
        self.choice3.move(300,140)

        self.confirm_btn = QtWidgets.QPushButton(self)
        self.confirm_btn.setText('Confirm Parameters')
        self.confirm_btn.clicked.connect(self.confirmParameters)
        self.confirm_btn.setFixedWidth(150)
        self.confirm_btn.move(160,180)

        self.cnfmModel_btn = QtWidgets.QPushButton(self)
        self.cnfmModel_btn.setText('Confirm Model')
        self.cnfmModel_btn.clicked.connect(self.confirmModel)
        self.cnfmModel_btn.setFixedWidth(150)
        self.cnfmModel_btn.move(180,510)

        self.setWindowTitle('Faking Options')
        self.setMinimumSize(500,550)
        self.show()

    def confirmParameters(self):
        col_1 = self.col1.itemText(self.col1.currentIndex())
        if col_1 != 'None':
            fake1 = self.choice1.itemText(self.choice1.currentIndex())
            self.fakeData(col_1, fake1)

        col_2 = self.col2.itemText(self.col2.currentIndex())
        if col_2 != 'None':
            fake2 = self.choice2.itemText(self.choice2.currentIndex())
            self.fakeData(col_2, fake2)

        col_3 = self.col3.itemText(self.col3.currentIndex())
        if col_3 != 'None':
            fake3 = self.choice3.itemText(self.choice3.currentIndex())
            self.fakeData(col_3, fake3)

    def fakeData(self, col, fake_para):
        
        fake = Faker()
        self.tableWidget = QtWidgets.QTableWidget()
        print('Faking', col, 'with parameter:', fake_para)

        for row in range(1, self.workingMod.rowCount()):
            data = []
            for column in range(self.workingMod.columnCount()):
                index = self.workingMod.index(0, column)
                i = index.data()
                if (i == col):
                    col_num = index.column()

        col_num = col_num
        for row in range(1, self.workingMod.rowCount()):
            data = []
            for column in range(self.workingMod.columnCount()):
                to_list = []
                index = self.workingMod.index(row, column)
                i = index.data()
                if index.column() == col_num:
                    if fake_para == 'Name':
                        i = fake.name()
                    if fake_para == 'Address':
                        i = fake.address()
                    if fake_para == 'Credit Card':
                        i = fake.credit_card_number(card_type=None)
                    if fake_para == 'Phone Number':
                        i = fake.phone_number()
                    if fake_para == 'E-Mail':
                        i = fake.free_email()
                    
                    self.workingMod.item(int(index.row()), int(index.column())).setText(i)
        
        self.tableView.resizeColumnsToContents()
    
    def confirmModel(self):
        self.new_model.emit(self.workingMod)
        print('Model has been faked. Model emitted.')

class EncodeLblWindow(QtWidgets.QMainWindow, QtWidgets.QWidget):

    new_model = QtCore.pyqtSignal('QStandardItemModel')

    def __init__(self, main_model, parent=None):

        QtWidgets.QMainWindow.__init__(self)
        self.main_model = main_model
        self.subUI()

    def subUI(self):

        self.workingMod = QtGui.QStandardItemModel(self)
        
        num_row = self.main_model.rowCount()
        num_col = self.main_model.columnCount()
        self.workingMod.setRowCount(num_row)
        self.workingMod.setColumnCount(num_col)

        for row in range(self.main_model.rowCount()):
            for column in range(self.main_model.columnCount()):
                index = self.main_model.index(row, column)
                idx = index.data()
                self.workingMod.setItem(int(row), int(column), QtGui.QStandardItem(str(idx)))

        col_val = []
        for col in range(self.main_model.columnCount()):
            index = self.main_model.index(0, col)
            idx = index.data()
            col_val.append(str(idx))

        self.listView = QtWidgets.QListView()

        self.tableView = QtWidgets.QTableView(self)
        self.tableView.setStyleSheet(stylesheet(self))
        self.tableView.setModel(self.workingMod)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.setShowGrid(True)
        self.tableView.setGeometry(10, 250, 480, 250) 
        self.tableView.resizeColumnsToContents()
        self.tableView.resizeRowsToContents()  

        self.columnModel = QtGui.QStandardItemModel(self)
        self.columnView = QtWidgets.QTableView(self)
        self.columnView.setStyleSheet(stylesheet(self))
        self.columnView.setModel(self.columnModel)
        self.columnView.horizontalHeader().setStretchLastSection(True)
        self.columnView.setShowGrid(True)
        self.columnView.setGeometry(10, 10, 200, 180) 

        checked = False
        
        for string in col_val:
            item = QtGui.QStandardItem(str(string))
            item.setCheckable(True)
            check = \
                (QtCore.Qt.Checked if checked else QtCore.Qt.Unchecked)
            item.setCheckState(check)
            self.columnModel.appendRow(item)
        
        self.select_col = QtWidgets.QPushButton(self)
        self.choices = ''
        self.select_col.setText('Confirm Selection')
        self.select_col.clicked.connect(self.onAccepted)
        self.select_col.setFixedWidth(100)
        self.select_col.move(220,20)
        self.select_col.setStyleSheet(stylesheet(self))

        self.select_all = QtWidgets.QPushButton(self)
        self.select_all.setText('Select All')
        self.select_all.clicked.connect(self.select)
        self.select_all.setFixedWidth(80)
        self.select_all.move(220,70)
        self.select_all.setStyleSheet(stylesheet(self))

        self.cancel_all = QtWidgets.QPushButton(self)
        self.cancel_all.setText('Unselect All')
        self.cancel_all.clicked.connect(self.unselect)
        self.cancel_all.setFixedWidth(80)
        self.cancel_all.move(220,120)
        self.cancel_all.setStyleSheet(stylesheet(self))

        self.confirmModel_btn = QtWidgets.QPushButton(self)
        self.confirmModel_btn.setText('Confirm Model')
        self.confirmModel_btn.clicked.connect(self.confirmModel)
        self.confirmModel_btn.setFixedWidth(150)
        self.confirmModel_btn.move(180, 510)

        self.preview_lbl = QtWidgets.QLabel(self)
        self.preview_lbl.setText('Preview Model')
        self.preview_lbl.setFixedWidth(150)
        self.preview_lbl.move(10, 220)

        self.setWindowTitle('Encode Labels Options')
        self.setMinimumSize(500,550)
        self.show()  

    def onAccepted(self):
        self.choices = [self.columnModel.item(i).text() for i in
                        range(self.columnModel.rowCount())
                        if self.columnModel.item(i).checkState()
                        == QtCore.Qt.Checked]

        self.encodeChoices()

    def select(self):
        for i in range(self.columnModel.rowCount()):
            item = self.columnModel.item(i)
            item.setCheckState(QtCore.Qt.Checked)

    def unselect(self):
        for i in range(self.columnModel.rowCount()):
            item = self.columnModel.item(i)
            item.setCheckState(QtCore.Qt.Unchecked)
    
    def encodeChoices(self):
        le = preprocessing.LabelEncoder()
        for choice in self.choices:
            labels = []
            for column in range(self.workingMod.columnCount()):
                index = self.workingMod.index(0, column)
                idx = index.data()
                if str(idx) == str(choice):
                    print('Encoding', idx)
                    col = choice
                    col_num = column

                    for row in range(1, self.workingMod.rowCount()):
                        index = self.workingMod.index(row, col_num)
                        i = index.data()
                        labels.append(i)
            
            labels = list(set(labels))
            le.fit(labels)

            for row in range(1, self.workingMod.rowCount()):
                arr = []
                index = self.workingMod.index(row, col_num)
                i = index.data()
                arr.append(i)
                transformed = le.transform(arr)
                for string in transformed:
                    new_i = str(string)
                    self.workingMod.setItem(row, col_num, QtGui.QStandardItem(str(new_i)))
    
    def confirmModel(self):

        self.new_model.emit(self.workingMod)
        print('Encoded Labels. Emitting Model')
    
              
class tokenizeWindow(QtWidgets.QMainWindow, QtWidgets.QWidget):

    new_mod = QtCore.pyqtSignal('QStandardItemModel')

    def __init__(self, main_mod, headers, parent = None):
        QtWidgets.QMainWindow.__init__(self)
        self.main_mod = main_mod
        self.containsHeaders = headers
        self.subUI()

    def subUI(self):

        self.previewModel = QtGui.QStandardItemModel(self)
        self.workingModel = QtGui.QStandardItemModel(self)

        n_row = self.main_mod.rowCount()
        n_col = self.main_mod.columnCount()

        self.workingModel.setRowCount(n_row)
        self.workingModel.setColumnCount(n_col)

        self.previewModel.setRowCount(n_row)
        self.previewModel.setColumnCount(n_col)

        for row in range(self.main_mod.rowCount()):
            for column in range(self.main_mod.columnCount()):
                index = self.main_mod.index(row, column)
                idx = index.data()
                self.workingModel.setItem(row, column, QtGui.QStandardItem(str(idx)))
                self.previewModel.setItem(row, column, QtGui.QStandardItem(str(idx)))
        

        self.colModel = QtGui.QStandardItemModel()
        self.CollistView = QtWidgets.QListView()

        self.ColtableView = QtWidgets.QTableView(self)
        self.ColtableView.setStyleSheet(stylesheet(self))
        self.ColtableView.setModel(self.colModel)
        self.ColtableView.horizontalHeader().setStretchLastSection(True)
        self.ColtableView.setShowGrid(True)
        self.ColtableView.setGeometry(10, 30, 300, 150) 

        checked = False

        self.col_val = []
        for col in range(self.main_mod.columnCount()):
            index = self.main_mod.index(0, col)
            idx = index.data()
            self.col_val.append(idx)

        for string in self.col_val:
            item = QtGui.QStandardItem(string)
            item.setCheckable(True)
            check = \
                (QtCore.Qt.Checked if checked else QtCore.Qt.Unchecked)
            item.setCheckState(check)
            self.colModel.appendRow(item)

        self.CollistView.setModel(self.colModel)

        self.modelListView = QtWidgets.QListView()

        self.modelTableView = QtWidgets.QTableView(self)
        self.modelTableView.setStyleSheet(stylesheet(self))
        self.modelTableView.setModel(self.workingModel)
        self.modelTableView.horizontalHeader().setStretchLastSection(True)
        self.modelTableView.setShowGrid(True)
        self.modelTableView.setGeometry(10, 310, 680, 390)
        self.modelTableView.resizeColumnsToContents()
        self.modelTableView.resizeRowsToContents()

        self.select_col = QtWidgets.QLabel(self)
        self.select_col.setText('Select colunms to tokenize')
        self.select_col.setFixedWidth(200)
        self.select_col.move(10,5)
        self.select_col.setStyleSheet(stylesheet(self))

        self.preview_mod = QtWidgets.QLabel(self)
        self.preview_mod.setText('Preview Model')
        self.preview_mod.setFixedWidth(200)
        self.preview_mod.move(10,280)
        self.preview_mod.setStyleSheet(stylesheet(self))  

        self.select_all = QtWidgets.QPushButton(self)
        self.select_all.setText('Select All')
        self.select_all.clicked.connect(self.select)
        self.select_all.setFixedWidth(80)
        self.select_all.move(320,70)
        self.select_all.setStyleSheet(stylesheet(self))

        self.cancel_all = QtWidgets.QPushButton(self)
        self.cancel_all.setText('Unselect All')
        self.cancel_all.clicked.connect(self.unselect)
        self.cancel_all.setFixedWidth(80)
        self.cancel_all.move(320,120)
        self.cancel_all.setStyleSheet(stylesheet(self))

        self.select_token = QtWidgets.QComboBox(self)
        self.select_token.addItem('NLTK Word Tokenizer')
        self.select_token.setFixedWidth(150)
        self.select_token.move(150, 200)

        self.token_lbl = QtWidgets.QLabel(self)
        self.token_lbl.setText('Select Tokenization Method')
        self.token_lbl.setFixedWidth(200)
        self.token_lbl.move(10,200)

        self.select_opt = QtWidgets.QPushButton(self)
        self.select_opt.setText('Confirm Selections')
        self.select_opt.clicked.connect(self.onAccepted)
        self.select_opt.setFixedWidth(150)
        self.select_opt.move(10,240)
        self.select_opt.setStyleSheet(stylesheet(self))

        self.confirm_model = QtWidgets.QPushButton(self)
        self.confirm_model.setText('Confirm Model')
        self.confirm_model.clicked.connect(self.confirmModel)
        self.confirm_model.setFixedWidth(250)
        self.confirm_model.move(220,710)
        self.confirm_model.setStyleSheet(stylesheet(self))       

        self.setWindowTitle('Tokenization Options')
        self.setMinimumSize(700,750)
        self.show()
    

    def onAccepted(self):
        self.choices = []
        self.choices = [self.colModel.item(i).text() for i in
                        range(self.colModel.rowCount())
                        if self.colModel.item(i).checkState()
                        == QtCore.Qt.Checked]
        if self.choices == []:
            print('Select Columns')
        else:
            self.tokenize()
        

    def select(self):
        for i in range(self.colModel.rowCount()):
            item = self.colModel.item(i)
            item.setCheckState(QtCore.Qt.Checked)

    def unselect(self):
        for i in range(self.colModel.rowCount()):
            item = self.colModel.item(i)
            item.setCheckState(QtCore.Qt.Unchecked)

        self.show()

    def confirmModel(self):
        self.new_mod.emit(self.workingModel)
        print('Model has been tokenized. Emitting Model.')
        self.close()

    def tokenize(self):
        for val in self.choices:
            print('Tokenizing column:', val)
            for column in range(self.workingModel.columnCount()):
                colIndex = self.workingModel.index(0, int(column))
                colHeader = colIndex.data()
                if val == colHeader:
                    col_num = colIndex.column()
                    print(col_num)
                    token_col = col_num
                    self.startToken(token_col)
    
    def startToken(self, token_col):
        self.tableWidget = QtWidgets.QTableWidget()
        row_range = range(self.workingModel.rowCount())

        if self.containsHeaders == True:
            row_range = range(1, self.workingModel.rowCount())
        
        for row in row_range:
            for column in range(self.workingModel.columnCount()):
                index = self.workingModel.index(row, column)
                i = index.data()
                # print(index.column())
                if index.column() == token_col:
                    tokenized = str(word_tokenize(i))
                    print(tokenized)
                    self.workingModel.item(int(index.row()), int(index.column())).setText(tokenized)

class partedWindow(QtWidgets.QMainWindow, QtWidgets.QWidget):
    
    def __init__(self, main_model, parent = None):
        
        QtWidgets.QMainWindow.__init__(self)
        self.main_mod = main_model
        self.subUI()

    def subUI(self):
        self.show()

    

def stylesheet(self):
       return


if __name__ == "__main__":
    app=QtWidgets.QApplication.instance() 
    if not app:  
         app = QtWidgets.QApplication(sys.argv)
    window = MainPage()
    window.show()
    sys.exit(app.exec_())

