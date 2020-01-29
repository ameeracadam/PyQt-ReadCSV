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


class TableWidgetDragRows(QTableWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)
        self.setDragDropOverwriteMode(False)
        self.setDropIndicatorShown(True)

        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.setDragDropMode(QAbstractItemView.InternalMove)

    def dropEvent(self, event: QDropEvent):
        if not event.isAccepted() and event.source() == self:
            drop_row = self.drop_on(event)

            rows = sorted(set(item.row() for item in self.selectedItems()))
            rows_to_move = [[QTableWidgetItem(self.item(row_index, column_index)) for column_index in range(self.columnCount())]
                            for row_index in rows]
            for row_index in reversed(rows):
                self.removeRow(row_index)
                if row_index < drop_row:
                    drop_row -= 1

            for row_index, data in enumerate(rows_to_move):
                row_index += drop_row
                self.insertRow(row_index)
                for column_index, column_data in enumerate(data):
                    self.setItem(row_index, column_index, column_data)
            event.accept()
            for row_index in range(len(rows_to_move)):
                self.item(drop_row + row_index, 0).setSelected(True)
                self.item(drop_row + row_index, 1).setSelected(True)
        super().dropEvent(event)

    def drop_on(self, event):
        index = self.indexAt(event.pos())
        if not index.isValid():
            return self.rowCount()

        return index.row() + 1 if self.is_below(event.pos(), index) else index.row()

    def is_below(self, pos, index):
        rect = self.visualRect(index)
        margin = 2
        if pos.y() - rect.top() < margin:
            return False
        elif rect.bottom() - pos.y() < margin:
            return True
        # noinspection PyTypeChecker
        return rect.contains(pos, True) and not (int(self.model().flags(index)) & Qt.ItemIsDropEnabled) and pos.y() >= rect.center().y()

class MyWindow(QtWidgets.QMainWindow):
    def __init__(self, aPath, parent=None):
        super(MyWindow, self).__init__()

        self.tableView = TableWidgetDragRows()
        self.fileName = ""
        self.fname = "List"
        self.model = QtGui.QStandardItemModel(self)
        
        self.tableView = QtWidgets.QTableView(self)
        self.tableView.setStyleSheet(stylesheet(self))
        self.tableView.setModel(self.model)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.setShowGrid(True)
        self.tableView.setGeometry(10, 50, 780, 645)
        self.model.dataChanged.connect(self.finishedEdit)

        self.pushButtonLoad = QtWidgets.QPushButton(self)
        self.pushButtonLoad.setText("Load CSV")
        self.pushButtonLoad.clicked.connect(self.loadCsv)
        self.pushButtonLoad.setFixedWidth(80)
        self.pushButtonLoad.setStyleSheet(stylesheet(self))

        self.pushButtonWrite = QtWidgets.QPushButton(self)
        self.pushButtonWrite.setText("Save CSV")
        self.pushButtonWrite.clicked.connect(self.writeCsv)
        self.pushButtonWrite.setFixedWidth(80)
        self.pushButtonWrite.move(90,0)
        self.pushButtonWrite.setStyleSheet(stylesheet(self))

        self.pushButtonPreview = QtWidgets.QPushButton(self)
        self.pushButtonPreview.setText("Hash Data")
        self.pushButtonPreview.clicked.connect(self.hashData)
        self.pushButtonPreview.setFixedWidth(80)
        self.pushButtonPreview.move(180,0)
        self.pushButtonPreview.setStyleSheet(stylesheet(self))

        self.pushButtonPreview = QtWidgets.QPushButton(self)
        self.pushButtonPreview.setText("Try This")
        self.pushButtonPreview.clicked.connect(self.tryThis)
        self.pushButtonPreview.setFixedWidth(80)
        self.pushButtonPreview.move(270,0)
        self.pushButtonPreview.setStyleSheet(stylesheet(self))
 
        item = QtGui.QStandardItem()
        self.model.appendRow(item)
        self.model.setData(self.model.index(0, 0), "", 0)
        self.tableView.resizeColumnsToContents()


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
                   #self.setCurrentFile(fileName)
    
    def setCurrentFile(self, fileName):
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, MyWindow):
                widget.updateRecentFileActions()

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
    
    def hashData(self):
        model = self.model
        self.tableWidget = QtWidgets.QTableWidget()
        numRows = self.tableWidget.rowCount()
        self.tableWidget.insertRow(numRows)
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
        self.isChanged = True

    def tryThis(self):
        self.model.item(1,1).setText("henlo")


    def finishedEdit(self):
        self.tableView = TableWidgetDragRows()
        self.tableView.resizeColumnsToContents()


def stylesheet(self):
       return

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    app.setApplicationName('MyWindow')
    main = MyWindow('')
    main.setMinimumSize(820, 820)
    main.setWindowTitle("CSV Viewer")
    main.show()

sys.exit(app.exec_())