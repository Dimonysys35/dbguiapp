import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QDialog
from PySide6.QtWidgets import QPushButton, QLineEdit, QVBoxLayout, QHBoxLayout, QWidget
import sqlite3
import db
from ui_db import Ui_MainWindow
import config

connection = sqlite3.connect(config.db)
cur = connection.cursor()

class AddingWindow(QMainWindow):
    def __init__(self, title, table, fields):
        super().__init__()
        self.table = table
        self.setWindowTitle(title)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout()
        central_widget.setLayout(layout)
        self.fields = fields[1:]
        self.inputs = []
        for field in fields:
            if field != "id":
                e = QLineEdit()
                e.setObjectName(str(field))
                e.setPlaceholderText(str(field))
                self.inputs.append(e)
                layout.addWidget(e)
        add = QPushButton("Add")
        add.clicked.connect(self.insert)
        self.cancel = QPushButton("Cancel")
        self.cancel.clicked.connect(self.closing)
        layout.addWidget(add)
        layout.addWidget(self.cancel)
        
    def insert(self):
        global cur
        values = [input.text() for input in self.inputs]
        db.insert(cur, self.table, tuple(self.fields), tuple(values))
        connection.commit()
        self.cancel.clicked.emit()
    
    def closing(self):
        global window
        window.update_table()
        self.close()
        
class UpdatingWindow(QMainWindow):
    def __init__(self, title, table, fields, id):
        global cur
        self.curid = id
        super().__init__()
        self.table = table
        self.setWindowTitle(title)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout()
        central_widget.setLayout(layout)
        self.fields = fields
        self.inputs = []
        self.values = db.get_one(cur, self.table, self.curid)
        for i, field in enumerate(fields):
            e = QLineEdit()
            e.setObjectName(str(field))
            e.setText(str(self.values[i]))
            e.setPlaceholderText(str(field))
            self.inputs.append(e)
            layout.addWidget(e)
        add = QPushButton("Update")
        add.clicked.connect(self.update)
        self.cancel = QPushButton("Cancel")
        self.cancel.clicked.connect(self.closing)
        layout.addWidget(add)
        layout.addWidget(self.cancel)
        
    def update(self):
        global cur
        values = [input.text() for input in self.inputs]
        db.update(cur, self.table, tuple(self.fields), tuple(values), self.curid)
        connection.commit()
        self.cancel.clicked.emit()
    
    def closing(self):
        global window
        window.update_table()
        self.close()

class DBToucher(QMainWindow):
    def __init__(self):
        global cur
        super(DBToucher, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.tables = db.get_tables(cur)

        self.ui.changetables.clear()
        for table in self.tables:
            self.ui.changetables.addItem(table)
        self.curtable = self.ui.changetables.currentText()

        self.ids = db.get_id(cur, self.curtable)
        for id in self.ids:
            self.ui.idch.addItem(str(id))
        self.curid = self.ui.idch.currentText()
        self.ui.idch.currentIndexChanged.connect(self.update_changer)
        
        self.ui.changetables.currentIndexChanged.connect(self.update_table)
        self.ui.changetables.currentIndexChanged.emit(self)
        
        self.ui.newrow.clicked.connect(self.insert_button)
        self.ui.upd.clicked.connect(self.update_button)
        self.ui.delete_2.clicked.connect(self.delete_button)
        
    def update_changer(self):
        self.curid = self.ui.idch.currentText()

    def update_table(self):
        global cur
        self.curtable = self.ui.changetables.currentText()
        # getting data from database
        data = db.select(cur, self.curtable)
        headers = db.get_headers(cur, self.curtable)
        # updating id combobox        
        self.ids = db.get_id(cur, self.curtable)
        self.ui.idch.clear()
        for id in self.ids:
            self.ui.idch.addItem(str(id))
        self.update_changer()
        self.curid = self.ui.idch.currentText()
        
        self.curfields = headers
        # clearing tablewidget
        self.ui.table.clear()
        # putting data into tablewidget
        self.ui.table.setRowCount(len(data)) # rows
        self.ui.table.setColumnCount(len(data[0])) # columns
        self.ui.table.setHorizontalHeaderLabels(headers) # headers
        self.ui.table.setVerticalHeaderLabels(['' for i in range(len(data))])
        for i in range(len(data)):
            for j in range(len(data[i])):
                item = QTableWidgetItem(str(data[i][j]))
                self.ui.table.setItem(i , j, item)
    
    def delete_button(self):
        global cur
        db.delete(cur, self.curtable, self.curid)
        self.ui.changetables.currentIndexChanged.emit(self)
        self.update_changer()
        self.update_table()
    
    def update_button(self):
        self.dlg = UpdatingWindow(f"Обновить поля в таблице {self.curtable}", self.curtable, self.curfields, self.curid)    
        self.dlg.show()
        self.ui.changetables.currentIndexChanged.emit(self)
        self.update_table() 
    
    def insert_button(self):
        self.dlg = AddingWindow(f"Добавить данные в таблицу {self.curtable}", self.curtable, self.curfields)    
        self.dlg.show()
        self.ui.changetables.currentIndexChanged.emit(self)
        self.update_table() 

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = DBToucher()
    window.show()
    
    sys.exit(app.exec())
