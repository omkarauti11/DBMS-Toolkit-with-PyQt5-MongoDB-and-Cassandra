from dotenv import load_dotenv
import os

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit, QDateEdit, QTableWidget, QTableWidgetItem, QHeaderView, QVBoxLayout, QWidget, QScrollArea, QMessageBox
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont  

from cassandra.cluster import Cluster
from cassandra.cluster import NoHostAvailable

import re

from datetime import datetime



# Load environment variables from file
load_dotenv('.env') 


headlabelfont = QFont("Noto Sans CJK TC", 15, QFont.Bold)  
labelfont = QFont('Calibri', 13, QFont.Bold) 
entryfont = QFont('Arial', 12) 
buttonfont = QFont('Calibri', 13, QFont.Bold)  



class StudentManagementSystem(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle('Student Management System')
        self.setGeometry(100, 100, 1440, 600)

        # Disable maximize button and window resizing
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)
        self.setFixedSize(1440, 600)  # Set fixed window size
        
        self.initUI()


    def initUI(self):
        # Connect to local Cassandra database instance
        try:
            self.cluster = Cluster(contact_points=['127.0.0.1'], port=9042)
            self.session = self.cluster.connect()
            print("Connected to local Cassandra database")
            self.setup_keyspace()
        except NoHostAvailable as e:
            print("Could not connect to local Cassandra database: %s" % e)
            sys.exit(1)

        self.setup_table()
        
        # Add secondary index on email column
        self.session.execute("CREATE INDEX IF NOT EXISTS email_index ON students (email)")

        self.setupUI()


    def setup_keyspace(self):
        self.session.execute("CREATE KEYSPACE IF NOT EXISTS student_management WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'}")
        self.session.set_keyspace('student_management')


    def setup_table(self):
        self.session.execute("CREATE TABLE IF NOT EXISTS students (id int PRIMARY KEY, name text, email text, phone_no text, gender text, dob date, stream text)")


    def setupUI(self):
        self.head_label = QLabel("STUDENT MANAGEMENT SYSTEM", self)
        head_label_font = QFont("Noto Sans CJK TC", 15, QFont.Bold)
        self.head_label.setFont(head_label_font)
        self.head_label.setStyleSheet("background-color: blue; color: white;")
        self.head_label.setAlignment(Qt.AlignCenter)
        self.head_label.setGeometry(0, 0, 1430, 30)  # Adjusted width to occupy the full header space

        self.left_frame = QWidget(self)
        self.left_frame.setGeometry(0, 30, 250, 545)

        self.center_frame = QWidget(self)
        self.center_frame.setGeometry(250, 30, 250, 545)

        self.right_frame = QScrollArea(self)
        self.right_frame.setGeometry(500, 35, 920, 545)

        self.setup_left_frame()
        self.setup_center_frame()
        self.setup_right_frame()

        self.show()


    def setup_left_frame(self):
        label_name = QLabel("Name", self.left_frame)
        label_name.setFont(labelfont)
        label_name.setGeometry(25, 30, 100, 30)

        self.name_entry = QLineEdit(self.left_frame)
        self.name_entry.setFont(entryfont)
        self.name_entry.setGeometry(25, 65, 230, 30)

        label_contact = QLabel("Contact Number", self.left_frame)
        label_contact.setFont(labelfont)
        label_contact.setGeometry(25, 110, 200, 30)

        self.contact_entry = QLineEdit(self.left_frame)
        self.contact_entry.setFont(entryfont)
        self.contact_entry.setGeometry(25, 145, 230, 30)

        label_email = QLabel("Email Address", self.left_frame)
        label_email.setFont(labelfont)
        label_email.setGeometry(25, 190, 200, 30)

        self.email_entry = QLineEdit(self.left_frame)
        self.email_entry.setFont(entryfont)
        self.email_entry.setGeometry(25, 225, 230, 30)

        label_gender = QLabel("Gender", self.left_frame)
        label_gender.setFont(labelfont)
        label_gender.setGeometry(25, 270, 200, 30)

        self.gender_entry = QComboBox(self.left_frame)
        self.gender_entry.setFont(entryfont)
        self.gender_entry.addItems(["Male", "Female"])
        self.gender_entry.setGeometry(25, 305, 230, 30)

        label_dob = QLabel("Date of Birth (DOB)", self.left_frame)
        label_dob.setFont(labelfont)
        label_dob.setGeometry(25, 350, 200, 30)

        self.dob_entry = QDateEdit(self.left_frame)
        self.dob_entry.setFont(entryfont)
        self.dob_entry.setDisplayFormat("yyyy-MM-dd")
        self.dob_entry.setGeometry(25, 385, 230, 30)

        label_stream = QLabel("Stream", self.left_frame)
        label_stream.setFont(labelfont)
        label_stream.setGeometry(25, 430, 200, 30)

        self.stream_entry = QLineEdit(self.left_frame)
        self.stream_entry.setFont(entryfont)
        self.stream_entry.setGeometry(25, 465, 230, 30)


    def setup_center_frame(self):
        self.button_add_record = QPushButton("Add Record", self.center_frame)
        self.button_add_record.setFont(buttonfont)
        self.button_add_record.clicked.connect(self.add_record)
        self.button_add_record.setGeometry(45, 120, 180, 40)

        self.button_delete_record = QPushButton("Delete Record", self.center_frame)
        self.button_delete_record.setFont(buttonfont)
        self.button_delete_record.clicked.connect(self.remove_record)
        self.button_delete_record.setGeometry(45, 180, 180, 40)

        self.button_view_record = QPushButton("View Record", self.center_frame)
        self.button_view_record.setFont(buttonfont)
        self.button_view_record.clicked.connect(self.view_record)
        self.button_view_record.setGeometry(45, 240, 180, 40)

        self.button_update_record = QPushButton("Update Record", self.center_frame)
        self.button_update_record.setFont(buttonfont)
        self.button_update_record.clicked.connect(self.update_record)
        self.button_update_record.setGeometry(45, 300, 180, 40)

        self.button_reset_fields = QPushButton("Reset Fields", self.center_frame)
        self.button_reset_fields.setFont(buttonfont)
        self.button_reset_fields.clicked.connect(self.reset_fields)
        self.button_reset_fields.setGeometry(45, 360, 180, 40)

        # Set the button colors 
        button_style = "QPushButton { background-color: %s; color: white; font: bold; }"
        self.button_add_record.setStyleSheet(button_style % 'green')
        self.button_delete_record.setStyleSheet(button_style % 'red')
        self.button_view_record.setStyleSheet(button_style % 'blue')
        self.button_update_record.setStyleSheet(button_style % 'orange')
        self.button_reset_fields.setStyleSheet(button_style % 'gray')


    def setup_right_frame(self):
        self.tree = QTableWidget(self.right_frame)
        self.tree.setColumnCount(7)
        self.tree.setHorizontalHeaderLabels(["Student ID", "Name", "Email Address", "Contact Number", "Gender", "Date of Birth", "Stream"])
        
         # Set the font for the header labels to be bold
        header_font = QFont()
        header_font.setBold(True)
        header = self.tree.horizontalHeader()
        for i in range(self.tree.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(i, QHeaderView.Interactive)
            header.setSectionResizeMode(i, QHeaderView.Fixed)
            header.setDefaultAlignment(Qt.AlignCenter)
            header.setFont(header_font)

        # Set the widget that will be displayed inside the right_frame
        self.right_frame.setWidget(self.tree)
        self.right_frame.setWidgetResizable(True)

        # Ensure consistent separation between columns
        self.tree.setColumnWidth(0, 100)
        self.tree.setColumnWidth(1, 170)
        self.tree.setColumnWidth(2, 230)
        self.tree.setColumnWidth(3, 130)
        self.tree.setColumnWidth(4, 82)
        self.tree.setColumnWidth(5, 110)
        self.tree.setColumnWidth(6, 75)

        # Call display_records here to populate the table
        self.display_records()


    def display_records(self):
        self.tree.setRowCount(0)
        rows = self.session.execute("SELECT * FROM students")
        for row in rows:
            rowPosition = self.tree.rowCount()
            self.tree.insertRow(rowPosition)
            self.tree.setItem(rowPosition, 0, QTableWidgetItem(str(row.id)))
            self.tree.setItem(rowPosition, 1, QTableWidgetItem(row.name))
            self.tree.setItem(rowPosition, 2, QTableWidgetItem(row.email))
            self.tree.setItem(rowPosition, 3, QTableWidgetItem(row.phone_no))
            self.tree.setItem(rowPosition, 4, QTableWidgetItem(row.gender))
            # self.tree.setItem(rowPosition, 5, QTableWidgetItem(row.dob.strftime('%Y-%m-%d')))

            # Convert dob to string
            dob_str = str(row.dob)
            
            # Set dob as string
            self.tree.setItem(rowPosition, 5, QTableWidgetItem(dob_str))
    
            self.tree.setItem(rowPosition, 6, QTableWidgetItem(row.stream))
            
            # Align text in each cell to the center
            for col in range(self.tree.columnCount()):
                item = self.tree.item(rowPosition, col)
                if item is not None:
                    item.setTextAlignment(Qt.AlignCenter)


    def reset_fields(self):
        self.name_entry.clear()
        self.email_entry.clear()
        self.contact_entry.clear()
        self.gender_entry.setCurrentIndex(0)
        self.dob_entry.setDate(QDate.currentDate())
        self.stream_entry.clear()


    def confirm_action(self, action):
        confirm = QMessageBox.question(self, "Confirmation", f'Are you sure you want to {action} this record?',
                                        QMessageBox.Yes | QMessageBox.No)
        return confirm == QMessageBox.Yes


    def get_next_id(self):
        rows = self.session.execute("SELECT MAX(id) FROM students")
        last_id = rows.one()[0]
        if last_id:
            return last_id + 1
        else:
            return 1   # Start from 1 if the table is empty
        

    def is_valid_phone_number(self, phone):
        if len(phone) != 10:
            return False
        if not re.match("^[0-9]+$", phone):
            return False
        return True


    def is_valid_email(self, email):
        pattern =  r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(pattern, email) is not None


    def add_record(self):
        name = self.name_entry.text()
        email = self.email_entry.text()
        contact = self.contact_entry.text()
        gender = self.gender_entry.currentText()
        # dob = self.dob_entry.date().toString(Qt.ISODate)

        # Convert QDateEdit to Python datetime.date object
        dob_qdate = self.dob_entry.date().toPyDate()
        dob = dob_qdate.strftime('%Y-%m-%d')
    
        stream = self.stream_entry.text()

        # Check if any field is empty
        if not name or not email or not contact or not gender or not dob or not stream:
            QMessageBox.critical(self, 'Error!', "Please fill all the missing fields!!")
            return

        # Validate email format
        if not self.is_valid_email(email):
            QMessageBox.critical(self, 'Error!', "Please enter a valid email address.")
            return

        # Validate phone number format
        if not self.is_valid_phone_number(contact):
            QMessageBox.critical(self, 'Error!', "Please enter a valid 10-digit phone number.")
            return

        # Check if the email already exists in the database
        existing_record = self.session.execute(f"SELECT * FROM students WHERE email='{email}' ALLOW FILTERING").one()
        if existing_record:
            QMessageBox.critical(self, 'Error!', "Email already exists! Please enter a unique email.")
            return

        # Insert the new record into the collection
        try:
            self.session.execute(
                """
                INSERT INTO students (id, name, email, phone_no, gender, dob, stream) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (self.get_next_id(), name, email, contact, gender, dob, stream)
            )
            QMessageBox.information(self, 'Record added', f"Record of {name} was successfully added")
            self.reset_fields()
            self.display_records()
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An error occurred: {str(e)}')


    def remove_record(self):
        selection = self.tree.selectedItems()
        if not selection:
            QMessageBox.critical(self, 'Error!', 'Please select a record to delete')
        else:
            record_found = False  # Flag to track if any valid record is found
            for item in selection:
                if not record_found:
                    if self.confirm_action('delete'):
                        record_id_text = item.text()  # Get the text of the QTableWidgetItem
                        # Extract only numeric characters from the text using regular expressions
                        record_id_match = re.match(r'\d+', record_id_text)
                        if record_id_match:
                            record_id = int(record_id_match.group())  # Convert the extracted numeric characters to an integer
                            try:
                                self.session.execute(f"DELETE FROM students WHERE id={record_id}")
                                record_found = True  # Set the flag to True if a valid record is found
                                QMessageBox.information(self, 'Done', 'Record Deleted Successfully')
                                self.display_records()  # Refresh the records in the UI
                            except Exception as e:
                                # Don't set record_found here
                                if record_found == False:
                                    QMessageBox.critical(self, 'Error!', 'No record found with the provided ID.')
                                    record_found = True
                                QMessageBox.critical(self, 'Error!', f'An error occurred: {str(e)}')
                        else:
                            QMessageBox.critical(self, 'Error!', 'Invalid record format')
            if not record_found:
                QMessageBox.critical(self, 'Error!', 'No valid record found to delete')



    def view_record(self):
        selection = self.tree.selectedItems()
        if not selection:
            QMessageBox.critical(self, 'Error!', 'Please select a record to view')
        else:
            record_found = False  # Flag to track if any valid record is found
            for item in selection:
                record_id_text = item.text()  # Get the text of the QTableWidgetItem
                # Extract only numeric characters from the text using regular expressions
                record_id_match = re.match(r'\d+', record_id_text)
                if record_id_match:
                    record_id = int(record_id_match.group())  # Convert the extracted numeric characters to an integer
                    try:
                        rows = self.session.execute(f"SELECT * FROM students WHERE id={record_id}")
                        for row in rows:
                            self.name_entry.setText(row.name)
                            self.email_entry.setText(row.email)
                            self.contact_entry.setText(row.phone_no)
                            self.gender_entry.setCurrentText(row.gender)
                            self.dob_entry.setDate(QDate.fromString(str(row.dob), Qt.ISODate))
                            self.stream_entry.setText(row.stream)
                        record_found = True  # Set the flag to True if a valid record is found                           
                    except Exception as e:
                        # Don't set record_found here
                        if record_found == False:
                            QMessageBox.critical(self, 'Error!', 'Record not found')
                            QMessageBox.critical(self, 'Error!', f'An error occurred: {str(e)}')
                            record_found = True
                else:
                    # Skip over items that don't contain a valid numeric record ID
                    continue
            if not record_found:
                QMessageBox.critical(self, 'Error!', 'Record not found')


    def update_record(self):
        selection = self.tree.selectedItems()
        if not selection:
            QMessageBox.critical(self, 'Error!', 'Please select a record to update')
        else:
            record_found = False  # Flag to track if any valid record is found
            for item in selection:
                if not record_found:
                    if self.confirm_action('update'):
                        record_id_text = item.text()  # Get the text of the QTableWidgetItem
                        # Extract only numeric characters from the text using regular expressions
                        record_id_match = re.match(r'\d+', record_id_text)
                        if record_id_match:
                            current_id = int(record_id_match.group())  # Convert the extracted numeric characters to an integer
                            name = self.name_entry.text()
                            email = self.email_entry.text()
                            contact = self.contact_entry.text()
                            gender = self.gender_entry.currentText()
                            # dob = self.dob_entry.date().toString(Qt.ISODate)

                            # Convert QDateEdit to Python datetime.date object
                            dob_qdate = self.dob_entry.date().toPyDate()
                            dob = dob_qdate.strftime('%Y-%m-%d')

                            stream = self.stream_entry.text()

                            if not name or not email or not contact or not gender or not dob or not stream:
                                QMessageBox.critical(self, 'Error!', "Please fill all the missing fields!!")
                                return

                            if not self.is_valid_email(email):
                                QMessageBox.critical(self, 'Error!', "Please enter a valid email address.")
                                return

                            if not self.is_valid_phone_number(contact):
                                QMessageBox.critical(self, 'Error!', "Please enter a valid 10-digit phone number.")
                                return

                            # Check if the email already exists in the database
                            existing_record = self.session.execute(f"SELECT * FROM students WHERE email='{email}' ALLOW FILTERING").one()
                            if existing_record and existing_record.id != current_id:
                                QMessageBox.critical(self, 'Error!', "Email already exists! Please enter a unique email.")
                                return
                            

                            try:
                                self.session.execute(
                                    """
                                    UPDATE students 
                                    SET name=%s, email=%s, phone_no=%s, gender=%s, dob=%s, stream=%s
                                    WHERE id=%s
                                    """,
                                    (name, email, contact, gender, dob, stream, current_id)
                                )
                                record_found = True  # Set the flag to True if a valid record is found
                                QMessageBox.information(self, 'Done', 'Record updated successfully.')
                                self.reset_fields()  # Clear input fields
                                self.display_records()  # Refresh records in the UI
                            except Exception as e:
                                # Don't set record_found here
                                if record_found == False:
                                    QMessageBox.critical(self, 'Error!', 'No record found with the provided ID.')
                                    record_found = True
                                QMessageBox.critical(self, 'Error!', f'An error occurred: {str(e)}')
                        else:
                            QMessageBox.critical(self, 'Error!', 'Invalid record format')
            if not record_found:
                QMessageBox.critical(self, 'Error!', 'No valid record found to update')



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = StudentManagementSystem()
    sys.exit(app.exec_())

