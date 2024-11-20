# app.py
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QMessageBox
)
from PyQt5.QtCore import Qt
import pyodbc
import time
import pandas as pd
from menu import MenuComponent

class SqlApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('SQL Query Executor')
        self.setGeometry(100, 100, 1000, 600)

        # Create a menu bar
        self.menu = MenuComponent(self)
        self.setMenuBar(self.menu)

        # Initial connection strings
        self.sql_connection_string = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=your_server_name;DATABASE=your_database_name;UID=your_username;PWD=your_password'
        self.mongo_connection_string = 'your_mongo_connection_string'

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        # Input query text box
        self.query_input = QTextEdit(self)
        self.query_input.setPlaceholderText('Enter your SQL query here')
        layout.addWidget(self.query_input)

        # Execute button
        execute_button = QPushButton('Execute', self)
        execute_button.clicked.connect(self.execute_query)
        layout.addWidget(execute_button)

        # Result display
        self.result_display = QTextEdit(self)
        self.result_display.setReadOnly(True)
        layout.addWidget(self.result_display)

        # Statistics display
        stats_layout = QHBoxLayout()
        self.exec_time_label = QLabel('Execution Time: N/A', self)
        self.record_count_label = QLabel('Records Returned: N/A', self)
        stats_layout.addWidget(self.exec_time_label)
        stats_layout.addWidget(self.record_count_label)
        layout.addLayout(stats_layout)

        # Analysis display
        self.analysis_display = QTextEdit(self)
        self.analysis_display.setReadOnly(True)
        layout.addWidget(self.analysis_display)

        central_widget.setLayout(layout)

    def execute_query(self):
        query = self.query_input.toPlainText()

        try:
            conn = pyodbc.connect(self.sql_connection_string)
            start_time = time.time()
            df1 = pd.read_sql_query(query, conn)
            exec_time = (time.time() - start_time) * 1000  # Convert to milliseconds

            self.result_display.setText(df1.to_string())
            self.exec_time_label.setText(f'Execution Time: {exec_time:.2f} ms')
            self.record_count_label.setText(f'Records Returned: {len(df1)}')

            # Assume we have a previous result stored in self.previous_df for comparison
            if hasattr(self, 'previous_df'):
                df2 = self.previous_df
                analysis = self.compare_dataframes(df1, df2)
                self.analysis_display.setText(analysis)
            else:
                self.analysis_display.setText('No previous result to compare.')

            # Store the current result for future comparisons
            self.previous_df = df1

        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An error occurred: {e}', QMessageBox.Ok)

    def compare_dataframes(self, df1, df2):
        differences = []

        # Compare shapes
        if df1.shape != df2.shape:
            differences.append(f'Different shapes: {df1.shape} vs {df2.shape}')

        # Compare data
        diff = df1.compare(df2, keep_shape=True, keep_equal=True)
        if not diff.empty:
            differences.append('Differences found in row/column values:\n' + diff.to_string())

        return '\n'.join(differences) if differences else 'No differences found.'

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SqlApp()
    ex.show()
    sys.exit(app.exec_())
