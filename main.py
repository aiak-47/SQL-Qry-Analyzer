import sys
import time

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QMessageBox, QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import Qt
from sqlalchemy import create_engine
import pandas as pd
from menu import MenuComponent

class SqlApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('SQL Query Executor')
        self.setGeometry(100, 100, 1000, 600)

        # Maximize the window
        self.showMaximized()

        # Create a menu bar
        self.menu = MenuComponent(self)
        self.setMenuBar(self.menu)

        # Initial connection strings
        # self.sql_connection_string = 'mssql+pyodbc://username:password@server/database?driver=ODBC+Driver+18+for+SQL+Server'
        # self.mongo_connection_string = 'your_mongo_connection_string'

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        # Create a horizontal layout for query inputs
        query_layout = QHBoxLayout()

        # Input query text box 1
        self.query_input1 = QTextEdit(self)
        self.query_input1.setPlaceholderText('Enter your first SQL query here')
        query_layout.addWidget(self.query_input1)

        # Input query text box 2
        self.query_input2 = QTextEdit(self)
        self.query_input2.setPlaceholderText('Enter your second SQL query here')
        query_layout.addWidget(self.query_input2)

        # Add the query layout to the main layout
        layout.addLayout(query_layout)

        # Execute button
        execute_button = QPushButton('Execute', self)
        execute_button.clicked.connect(self.execute_query)
        layout.addWidget(execute_button)

        # Create a horizontal layout for result displays
        result_layout = QHBoxLayout()

        # Result table 1
        self.result_table1 = QTableWidget(self)
        result_layout.addWidget(self.result_table1)

        # Result table 2
        self.result_table2 = QTableWidget(self)
        result_layout.addWidget(self.result_table2)

        # Add the result layout to the main layout
        layout.addLayout(result_layout)

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
        query1 = self.query_input1.toPlainText()
        query2 = self.query_input2.toPlainText()

        try:
            # Create the SQLAlchemy engine
            engine = create_engine(self.sql_connection_string)

            # Execute the first query
            start_time = time.time()
            df1 = pd.read_sql_query(query1, engine)
            exec_time1 = (time.time() - start_time) * 1000  # Convert to milliseconds

            # Execute the second query
            start_time = time.time()
            df2 = pd.read_sql_query(query2, engine)
            exec_time2 = (time.time() - start_time) * 1000  # Convert to milliseconds

            self.display_results(self.result_table1, df1)
            self.display_results(self.result_table2, df2)
            self.exec_time_label.setText(f'Execution Time: Query 1 - {exec_time1:.2f} ms, Query 2 - {exec_time2:.2f} ms')
            self.record_count_label.setText(f'Records Returned: Query 1 - {len(df1)}, Query 2 - {len(df2)}')

            # Perform comparison if both results are available
            if not df1.empty and not df2.empty:
                analysis = self.compare_dataframes(df1, df2)
                self.analysis_display.setText(analysis)
            else:
                self.analysis_display.setText('No result to compare.')

        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An error occurred: {e}', QMessageBox.Ok)

    def display_results(self, table_widget, df):
        table_widget.setRowCount(df.shape[0])
        table_widget.setColumnCount(df.shape[1])
        table_widget.setHorizontalHeaderLabels(df.columns)

        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                table_widget.setItem(i, j, QTableWidgetItem(str(df.iloc[i, j])))

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
