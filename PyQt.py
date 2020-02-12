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
                                                            QTableWidget, QTableWidgetItem, QGridLayout, QFileDialog, QMenu, QInputDialog, QPushButton,
                                                            QLabel)

from sklearn.model_selection import train_test_split, KFold

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

        self.partData = QtWidgets.QPushButton(self)
        self.partData.setText('Partition Data')
        self.partData.clicked.connect(self.datasetPartition)
        self.partData.setFixedWidth(80)
        self.partData.move(100, 700)
        self.partData.setStyleSheet(stylesheet(self))

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
        model = self.model
        self.tableWidget = QtWidgets.QTableWidget()
        columns = value[0]
        salt = str(value[2])
        for selected_col in columns:
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
        model = self.model
        self.tableWidget = QtWidgets.QTableWidget()
        for row in range(model.rowCount()):
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

                    self.model.item(int(index.row()), int(index.column())).setText(new)

        print("Hashed Selected Column")

        self.tableView.resizeColumnsToContents()
        self.child_win.close()   

    def datasetPartition(self):
        model = self.model
        
        self.new_partition_window = datasetPartWin(model)
        self.new_partition_window.show() 
        self.new_partition_window.new_mod.connect(self.updateModel)   
    
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

    value = QtCore.pyqtSignal(list)

    def __init__(self, myList, parent=None):
        QtWidgets.QMainWindow.__init__(self)
        self.col_val = myList
        self.subUI()
    
    def subUI(self):

        self.model = QtGui.QStandardItemModel()
        self.listView = QtWidgets.QListView()

        self.tableView = QtWidgets.QTableView(self)
        self.tableView.setStyleSheet(stylesheet(self))
        self.tableView.setModel(self.model)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.setShowGrid(True)
        self.tableView.setGeometry(10, 10, 200, 150) 

        checked = False

        for string in self.col_val:
            item = QtGui.QStandardItem(string)
            item.setCheckable(True)
            check = \
                (QtCore.Qt.Checked if checked else QtCore.Qt.Unchecked)
            item.setCheckState(check)
            self.model.appendRow(item)

        self.listView.setModel(self.model)

        self.select_col = QtWidgets.QPushButton(self)
        self.select_col.setText('Select Columns')
        self.select_col.clicked.connect(self.onAccepted)
        self.select_col.setFixedWidth(80)
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

        self.hash_mtd = QtWidgets.QLabel(self)
        self.hash_mtd.setText('Hash Method')
        self.hash_mtd.setFixedWidth(80)
        self.hash_mtd.move(10,180)
        self.hash_mtd.setStyleSheet(stylesheet(self))

        self.hash_box = QtWidgets.QComboBox(self)
        self.hash_box.addItem('sha1')
        self.hash_box.addItem('sha256')
        self.hash_box.addItem('sha224')
        self.hash_box.addItem('blake2b')
        self.hash_box.move(90, 180)

        self.set_salt = QtWidgets.QLineEdit(self)
        self.set_salt.setEchoMode(QLineEdit.Password)
        self.set_salt.setFixedWidth(100)
        self.set_salt.move(90,230)
        self.set_salt.setStyleSheet(stylesheet(self))

        self.salt_line = QtWidgets.QLabel(self)
        self.salt_line.setText('Set a salt')
        self.salt_line.setFixedWidth(80)
        self.salt_line.move(10,230)
        self.salt_line.setStyleSheet(stylesheet(self))
        
        self.confirm_salt = QtWidgets.QPushButton(self)
        self.confirm_salt.setText('Confirm Salt')
        self.confirm_salt.clicked.connect(self.new_salt_window)
        self.confirm_salt.setFixedWidth(80)
        self.confirm_salt.move(200, 230)
        self.confirm_salt.setStyleSheet(stylesheet(self))

        self.to_hash = QtWidgets.QPushButton(self)
        self.to_hash.setText("Hash!")
        self.to_hash.clicked.connect(self.hash_this)
        self.setFixedWidth(200)
        self.to_hash.move(10,280)
        self.to_hash.setStyleSheet(stylesheet(self))

        self.can_hash = True

        self.setWindowTitle('Hashing Options')
        self.setMinimumSize(320,350)
        self.show()


    def onAccepted(self):
        self.choices = [self.model.item(i).text() for i in
                        range(self.model.rowCount())
                        if self.model.item(i).checkState()
                        == QtCore.Qt.Checked]

        print(self.choices)

    def select(self):
        for i in range(self.model.rowCount()):
            item = self.model.item(i)
            item.setCheckState(QtCore.Qt.Checked)

    def unselect(self):
        for i in range(self.model.rowCount()):
            item = self.model.item(i)
            item.setCheckState(QtCore.Qt.Unchecked)

        self.show()

    def new_salt_window(self):
        model = self.model
        salt = self.set_salt.text()
        self.salt_window = newSaltWindow(salt)
        self.salt_window.show()
        self.can_hash = True

    # def confirm_hash(self, message):
    #     model = self.model
    #     self.can_hash = True
        
    def hash_this(self):
        model = self.model
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
        print('Salt to use', hashing_salt)
        values.append(hashing_salt)
        self.value.emit(values)


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
        model = self.model
        new_salt = self.salt_line.text()
        initial_salt = self.salt

        print(new_salt, initial_salt)

        if (new_salt == initial_salt):
            print('Salts match!')
            msg = 'clicked!'
            self.message.emit(msg)
            self.close()
        else:
            print("Salts don't match. Try again.")

class datasetPartWin(QtWidgets.QMainWindow, QtWidgets.QWidget):

    new_mod = QtCore.pyqtSignal('QStandardItemModel')
    
    def __init__(self, main_mod, parent=None):
        QtWidgets.QMainWindow.__init__(self)
        self.main_model = main_mod
        self.model = QtGui.QStandardItemModel(self)
        self.subUI()
    
    def subUI(self):

        model = self.model
        main_model = self.main_model
        self.tableWidget = QtWidgets.QTableWidget()

        row_num = main_model.rowCount()
        col_num = main_model.columnCount()
        self.model.setRowCount(row_num)
        self.model.setColumnCount(col_num)

        for row in range(model.rowCount()):
            for column in range(model.columnCount()):
                index = main_model.index(row, column)
                i = index.data()
                n_row = int(row)
                n_col = int(column)
                self.model.setItem(n_row,n_col,QtGui.QStandardItem(str(i)))

        self.listView = QtWidgets.QListView()

        self.tableView = QtWidgets.QTableView(self)
        self.tableView.setStyleSheet(stylesheet(self))
        self.tableView.setModel(self.model)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.setShowGrid(True)
        self.tableView.setGeometry(10, 10, 600, 600) 

        self.tableView.resizeColumnsToContents()
        self.tableView.resizeRowsToContents()

        self.part_opt = QtWidgets.QComboBox(self)
        self.part_opt.addItem('Random Split')
        self.part_opt.addItem('Train Test Split')
        self.part_opt.addItem('K-Fold')
        self.part_opt.move(10,630)

        self.pushButtonLoad = QtWidgets.QPushButton(self)
        self.pushButtonLoad.setText('Load Options')
        self.pushButtonLoad.clicked.connect(self.loadOptions)
        self.pushButtonLoad.setFixedWidth(80)
        self.pushButtonLoad.move(120,630)
        self.pushButtonLoad.setStyleSheet(stylesheet(self))

        self.confirm_model = QtWidgets.QPushButton(self)
        self.confirm_model.setText('Confirm')
        self.confirm_model.clicked.connect(self.confirmModel)
        self.confirm_model.setFixedWidth(80)
        self.confirm_model.move(120,670)
        self.confirm_model.setStyleSheet(stylesheet(self))

        self.setWindowTitle('Partioning Options')
        self.setMinimumSize(700,750)
        self.show()

    def confirmModel(self):
        model = self.model
        self.new_mod.emit(model)
        print('Model Emitted')

    
    def loadOptions(self):
        model = self.model
        option = self.part_opt.itemText(self.part_opt.currentIndex())

        if option == 'Random Split':
            #Create a random number generator and deletes rows whose greater than 0
            for row in range(1, model.rowCount()):
                random_n = np.random.randn()
                if random_n <= 0.0 :
                    model.removeRow(row)
        
        if option == 'Train Test Split':
            #Set test_size and random state
            self.para_window = TrainTestGetParameters()
            self.para_window.show()
            self.para_window.parameters.connect(self.traintest_split)
        
        if option == 'K-Fold':
            self.para_window = KFoldGetParameters()
            self.para_window.show()
            self.para_window.parameters.connect(self.kFold_split)
    
    def kFold_split(self, parameters):
        split = parameters[0]
        kf = KFold(n_splits=int(split))
        model = self.model
        numbers = []
        col_count = model.columnCount()
        model.setColumnCount(col_count+1)
        new_col = col_count
        for row in range(1, model.rowCount()):
            rand_num = np.random.rand()
            self.model.setItem(int(row), int(new_col),QtGui.QStandardItem(str(rand_num)))
            numbers.append(rand_num)

        df = pd.DataFrame(numbers)
        print(type(df))
        for fold, x_fold in kf.split(df):
            fold_df = pd.DataFrame(df.loc[fold])
            foldx_df = pd.DataFrame(df.loc[x_fold])

        x = []
        x2_num = []
        x.append(foldx_df.values.tolist())
        for arr in x:
           for lis in arr:
                for num in lis:
                    x2_num.append(num)
        
        for row in range(1, model.rowCount()):
            index = model.index(row, col_count)
            i = index.data()
            for val in x2_num:
                if str(i) == str(val):
                    model.removeRow(row)
        model.removeColumn(col_count)
        self.para_window.close()
            

    def traintest_split(self,parameters):
        size = float(parameters[0])
        state = int(parameters[1])
        # print(size,state)
        model = self.model
        numbers = []
        col_count = model.columnCount()
        model.setColumnCount(col_count+1)
        new_col = col_count
        for row in range(1, model.rowCount()):
            rand_num = np.random.rand()
            self.model.setItem(int(row), int(new_col),QtGui.QStandardItem(str(rand_num)))
            numbers.append(rand_num)
        x_numbers, x2_numbers = train_test_split(numbers, test_size=size, random_state=state)

        for row in range(1, model.rowCount()):
            index = model.index(row, col_count)
            i = index.data()
            for val in x2_numbers:
                if str(i) == str(val):
                    model.removeRow(row)
        model.removeColumn(col_count)
        self.para_window.close()

class TrainTestGetParameters(QtWidgets.QMainWindow, QtWidgets.QWidget):

    parameters = QtCore.pyqtSignal(list)
    
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self)
        self.subUI()

    def subUI(self):
        
        self.test_lbl = QtWidgets.QLabel(self)
        self.test_lbl.setText('Set Size')
        self.test_lbl.setFixedWidth(80)
        self.test_lbl.move(10,30)
        self.test_lbl.setStyleSheet(stylesheet(self))

        self.test_size = QtWidgets.QLineEdit(self)
        self.test_size.setFixedWidth(40)
        self.test_size.move(120,30)
        self.test_size.setStyleSheet(stylesheet(self))

        self.rand_lbl = QtWidgets.QLabel(self)
        self.rand_lbl.setText('Set Random State')
        self.rand_lbl.setFixedWidth(100)
        self.rand_lbl.move(10,70)
        self.rand_lbl.setStyleSheet(stylesheet(self))

        self.rand_state = QtWidgets.QLineEdit(self)
        self.rand_state.setFixedWidth(40)
        self.rand_state.move(120,70)
        self.rand_state.setStyleSheet(stylesheet(self))

        self.confirm_para = QtWidgets.QPushButton(self)
        self.confirm_para.setText('Get Parameters')
        self.confirm_para.clicked.connect(self.get_parameters)
        self.confirm_para.setFixedWidth(100)
        self.confirm_para.move(50, 110)
        self.confirm_para.setStyleSheet(stylesheet(self))

        self.setWindowTitle('Parameters')
        self.setMinimumSize(150,200)
        self.show()

    def get_parameters(self):

        para = []
        size = self.test_size.text()
        state = self.rand_state.text()
        para.append(size)
        para.append(state)

        self.parameters.emit(para)

class KFoldGetParameters(QtWidgets.QMainWindow, QtWidgets.QWidget):

    parameters = QtCore.pyqtSignal(list)
    
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self)
        self.subUI()

    def subUI(self):
        
        self.fold_lbl = QtWidgets.QLabel(self)
        self.fold_lbl.setText('Number of Folds')
        self.fold_lbl.setFixedWidth(80)
        self.fold_lbl.move(10,30)
        self.fold_lbl.setStyleSheet(stylesheet(self))

        self.n_fold = QtWidgets.QLineEdit(self)
        self.n_fold.setFixedWidth(40)
        self.n_fold.move(120,30)
        self.n_fold.setStyleSheet(stylesheet(self))

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

        self.parameters.emit(para)


            


    

def stylesheet(self):
       return


if __name__ == "__main__":
    app=QtWidgets.QApplication.instance() 
    if not app:  
         app = QtWidgets.QApplication(sys.argv)
    window = MainPage()
    window.show()
    sys.exit(app.exec_())