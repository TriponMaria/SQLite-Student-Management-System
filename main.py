from PyQt6.QtWidgets import QToolBar
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QGridLayout, QLabel, QWidget, \
    QMainWindow, QTableWidget, QTableWidgetItem, QDialog, QVBoxLayout, \
    QLineEdit, QComboBox, QPushButton, QToolBar, QStatusBar, QMessageBox
from PySide6.QtGui import  QAction, QIcon
import sys
import sqlite3

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Student Management System")
        self.setFixedSize(500, 500)

        # Add elements to menuBar
        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        search_menu_item = self.menuBar().addMenu("&Edit")

        add_student_action = QAction(QIcon("icons/add.png"), "Add Student", self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)

        search_action = QAction(QIcon("icons/search.png"), "Search", self)
        search_action.triggered.connect(self.search)
        search_menu_item.addAction(search_action)

        # Create table
        self.tabel =  QTableWidget()
        self.tabel.setColumnCount(4)
        self.tabel.setHorizontalHeaderLabels(("Id", "Name", "Course", "Phone Number"))
        self.tabel.verticalHeader().setVisible(False)
        self.setCentralWidget(self.tabel)

        # Create toolbar and add elements
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)
        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)

        # Create status bar and add status bar elements
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Detect a cell clicked
        self.tabel.cellClicked.connect(self.cell_clicked)


    def cell_clicked(self):
        # Create buttons for statusbar
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        # Clean status bar
        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)

        # Add buttons for statusbar
        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)

    def load_data(self):
        connection = sqlite3.connect("database.db")
        result = connection.execute("SELECT * FROM students")
        # reset the table - used to not duplicate the data
        self.tabel.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.tabel.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.tabel.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        connection.close()

    def insert(self):
        dialog = InsertDialog()
        dialog.exec()

    def search(self):
        dialog = SearchDialog()
        dialog.exec()

    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()



class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert Student Data")

        # Dimensions of dialog window
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Add student name widget
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Add combo box of courses
        self.course_name = QComboBox()
        courses = ["Math", "Astronomy", "Biology", "Physics"]
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        # Add phone number widget
        self.phone_number = QLineEdit()
        self.phone_number.setPlaceholderText("Phone Number")
        layout.addWidget(self.phone_number)

        # Add a submit button
        button = QPushButton("Add Student")
        button.clicked.connect(self.add_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def add_student(self):
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.phone_number.text()
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, course, mobile) VALUES (?, ?, ?)",
                       (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Search Student")

        layout = QVBoxLayout()

        # Add student name widget
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Create button
        button = QPushButton("Search")
        button.clicked.connect(self.search)
        layout.addWidget(button)

        self.setLayout(layout)

    def search(self):
        name = self.student_name.text()

        items = main_window.tabel.findItems(name, Qt.MatchFlag.MatchContains)
        for item in items:
            main_window.tabel.item(item.row(), 1).setSelected(True)


class EditDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Update Student Data")

        # Dimensions of Edit window
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Get data from selected row
        index = main_window.tabel.currentRow()
        student_name = main_window.tabel.item(index, 1).text()
        course = main_window.tabel.item(index, 2).text()
        phone_number = main_window.tabel.item(index, 3).text()

        # Get student_id
        self.student_id = main_window.tabel.item(index, 0).text()

        # Add widgets
        self.student_name = QLineEdit(student_name)
        layout.addWidget(self.student_name)

        self.course = QComboBox()
        courses = ["Math", "Astronomy", "Biology", "Physics"]
        self.course.addItems(courses)
        self.course.setCurrentText(course)
        layout.addWidget(self.course)

        self.phone_number = QLineEdit(phone_number)
        layout.addWidget(self.phone_number)

        button = QPushButton("Update")
        button.clicked.connect(self.update_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def update_student(self):
        name = self.student_name.text()
        course = self.course.itemText(self.course.currentIndex())
        mobile = self.phone_number.text()

        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = ?, course = ?, mobile = ? WHERE id = ?",
                       (name, course, mobile, self.student_id))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Delete Student Data")

        # Dimensions of Delete window
        self.setFixedSize(200, 100)

        layout = QGridLayout()

        # Add widgets
        confirmation = QLabel("Are you sure you want to delete?")
        layout.addWidget(confirmation, 0, 0, 1, 2)

        yes = QPushButton("Yes")
        yes.clicked.connect(self.delete_record)
        layout.addWidget(yes, 1, 0)

        no = QPushButton("No")
        no.clicked.connect(self.close)
        layout.addWidget(no, 1, 1)

        self.setLayout(layout)

    def delete_record(self):
        # Get the selected row and student id
        index = main_window.tabel.currentRow()
        student_id = main_window.tabel.item(index, 0).text()
        print(student_id)

        # Remove student from database
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("DELETE FROM students WHERE id = ?", (student_id, ))
        connection.commit()
        cursor.close()
        connection.close()

        # Refresh data from tabel
        main_window.load_data()
        self.close()

        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("The record was deleted successfully")
        confirmation_widget.exec()


app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
main_window.load_data()
sys.exit(app.exec())