import sys
import time
import re
from pandas_profiling import ProfileReport

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QMessageBox, QTableWidget, QTableWidgetItem, QProgressDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from sqlalchemy import create_engine, event
import pandas as pd
from menu import MenuComponent

class SqlApp(QMainWindow):
    # Initial connection strings
    sql_connection_string = "mssql+pyodbc://dmatchadmin:IntDon786#@dmdb-srv.database.windows.net,1433/DonMatchDB?driver=ODBC+Driver+18+for+SQL+Server"
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('SQL Query Analyzer')
        self.setGeometry(100, 100, 1000, 600)

        # Maximize the window
        self.showMaximized()

        # Create a menu bar
        self.menu = MenuComponent(self)
        self.setMenuBar(self.menu)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        # Create a horizontal layout for query inputs
        query_layout = QHBoxLayout()

        # Input query text box 1
        self.query_input1 = QTextEdit(self)
        self.query_input1.setPlaceholderText('Enter your first query here')
        query_layout.addWidget(self.query_input1)

        # Input query text box 2
        self.query_input2 = QTextEdit(self)
        self.query_input2.setPlaceholderText('Enter your second query here')
        query_layout.addWidget(self.query_input2)

        # Add the query layout to the main layout
        layout.addLayout(query_layout)

        # Execute button
        self.execute_button = QPushButton('Analyze', self)
        self.execute_button.setStyleSheet("background-color: lightblue;")
        self.execute_button.clicked.connect(self.execute_queries)
        layout.addWidget(self.execute_button)

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
        self.qry_stats_label_left = QLabel('Rows: N/A in N/A ms', self)
        self.qry_stats_label_left.setAutoFillBackground(True)
        self.qry_stats_label_left.setStyleSheet("background-color: lightgrey;color: Blue;font-weight: bold;")
        self.qry_stats_label_right = QLabel('Rows: N/A in N/A ms', self)
        self.qry_stats_label_right.setAutoFillBackground(True)
        self.qry_stats_label_right.setStyleSheet("background-color: lightgrey;color: Blue;font-weight: bold;")
        self.qry_stats_label_left.setAlignment(Qt.AlignRight)
        self.qry_stats_label_right.setAlignment(Qt.AlignRight)
        stats_layout.addWidget(self.qry_stats_label_left)
        stats_layout.addWidget(self.qry_stats_label_right)
        layout.addLayout(stats_layout)

        # Analysis display
        self.analysis_display = QTextEdit(self)
        self.analysis_display.setReadOnly(True)
        self.analysis_display.setStyleSheet("background-color: lightgrey;")
        layout.addWidget(self.analysis_display)


        central_widget.setLayout(layout)
    def write_to_analysis_display(self, message, message_type): 
        if message_type == 'info': 
            color = "black" 
        elif message_type == 'warning':
            color = "orange"
        elif message_type == 'error':
            color = "red" 
        else: 
            color = "black"
        self.analysis_display.setTextColor(QColor(color)) 
        self.analysis_display.append(message)

    def execute_queries(self):
        #clear previous results
        self.reset_ui()
        # Disable UI elements 
        self.enable_ui_elements(False)
        
        # Show progress dialog 
        self.progress_dialog = QProgressDialog("Executing queries...", "Cancel", 0, 100, self) 
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setWindowTitle("Please wait")
        self.progress_dialog.setRange(0, 0)
        self.progress_dialog.setMinimumWidth(400)
        self.progress_dialog.show()
        QApplication.processEvents()
        
        self.progress_dialog.setValue(10)
        
        query1 = self.query_input1.toPlainText()
        query2 = self.query_input2.toPlainText()
        
        df1,exec_time_left = self.execute_query(query1)
        self.progress_dialog.setValue(30)
        QApplication.processEvents()
        self.profile_query(df1,'left')
        df2,exec_time_right = self.execute_query(query2)
        self.progress_dialog.setValue(50)
        self.profile_query(df2,'right')
        self.display_results(self.result_table1, df1)
        self.progress_dialog.setValue(60)
        QApplication.processEvents()
        self.display_results(self.result_table2, df2)
        self.progress_dialog.setValue(70)
        self.qry_stats_label_left.setText(f'Rows:{len(df1)} in {exec_time_left:.2f} ms')
        self.progress_dialog.setValue(80)
        QApplication.processEvents()
        self.qry_stats_label_right.setText(f'Rows:{len(df2)} in {exec_time_right:.2f} ms')

        # Perform comparison if both results are available
        if not df1.empty and not df2.empty:
            comp_pass, message = compare_dataframes(df1, df2)
            if not comp_pass:
                message_type = 'error'
                self.write_to_analysis_display(message, message_type)
                self.enable_ui_elements(True)
                return
            else:
                message_type = 'info'
                self.write_to_analysis_display(message, message_type)
            self.progress_dialog.setValue(90)
            analysis = self.summarize_differences(df1, df2)
            self.analysis_display.setText(analysis)
        else:
            self.write_to_analysis_display('No results to compare.', 'warning')
            self.enable_ui_elements(True)
            
        self.enable_ui_elements(True)
        # except Exception as e:
        #     QMessageBox.critical(self, 'Error', f'An error occurred: {e}', QMessageBox.Ok)
    def enable_ui_elements(self,enable=True):
        self.execute_button.setEnabled(enable)
        self.query_input1.setEnabled(enable)
        self.query_input2.setEnabled(enable)
        if(enable):
            self.progress_dialog.setValue(100)
            self.progress_dialog.close()
            
    def reset_ui(self):
        self.result_table1.clear()
        self.result_table2.clear()
        self.analysis_display.clear()
        self.qry_stats_label_left.setText('Rows: N/A in N/A ms')
        self.qry_stats_label_right.setText('Rows: N/A in N/A ms')

    def execute_query(self, qry):
        try:
            # Create the SQLAlchemy engine
            engine = create_engine(self.sql_connection_string)

            # Capture the execution time
            with engine.connect() as conn:
                start_time = time.time()
                df = pd.read_sql_query(qry, conn)
                end_time = time.time()
                
            # Calculate execution time in milliseconds
            exec_time = (end_time - start_time) * 1000  # in milliseconds

            return df, exec_time
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An error occurred: {e}', QMessageBox.Ok)
            self.enable_ui_elements(True)
            
            return None, "N/A"
          

    def display_results(self, table_widget, df):
        table_widget.setRowCount(df.shape[0])
        table_widget.setColumnCount(df.shape[1])
        table_widget.setHorizontalHeaderLabels(df.columns)

        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                table_widget.setItem(i, j, QTableWidgetItem(str(df.iloc[i, j])))

    def profile_query(self, df,type):
        profile = df.profile_report(title='Query Profile')
        profile.to_file(f'{type}_profile.html')
        return profile
        
    def summarize_differences(self, df1, df2):
        differences = []
    
        # Numeric differences
        numeric_diff = self.calculate_numeric_differences(df1, df2)
        if numeric_diff:
            differences.append(numeric_diff)

        # Boolean differences
        bool_diff = self.calculate_bool_differences(df1, df2)
        if bool_diff:
            differences.append(bool_diff)

        # String differences
        string_diff = self.calculate_string_differences(df1, df2)
        if string_diff:
            differences.append(string_diff)

        # Datetime differences
        datetime_diff = self.calculate_datetime_differences(df1, df2)
        if datetime_diff:
            differences.append(datetime_diff)
    # High-level summary
        high_level_summary = self.generate_high_level_summary(differences)
        differences.insert(0, high_level_summary)
        
        return '\n\n'.join(differences) if differences else 'No differences found.'
    def calculate_numeric_differences(self, df1, df2):
        numeric_cols = df1.select_dtypes(include='number').columns
        if numeric_cols.empty:
            return ''

        var1 = df1[numeric_cols].var()
        var2 = df2[numeric_cols].var()
        var_diff = var1 - var2

        return f'Numeric Differences:\n{var_diff.to_string()}'
    
    
    def calculate_bool_differences(self, df1, df2):
        bool_cols = df1.select_dtypes(include='bool').columns
        if bool_cols.empty:
            return ''

        bool_diff = df1[bool_cols].astype(int).sum() - df2[bool_cols].astype(int).sum()
        return f'Boolean Differences:\n{bool_diff.to_string()}'

    def calculate_string_differences(self, df1, df2):
        string_cols = df1.select_dtypes(include='object').columns
        if string_cols.empty:
            return ''

        string_diff = (df1[string_cols] != df2[string_cols]).sum()
        if(string_diff.any()):
            return f'String Differences (number of differing rows):\n{string_diff.to_string()}'
        else:
            return ''

    def calculate_datetime_differences(self, df1, df2):
        datetime_cols = df1.select_dtypes(include='datetime').columns
        if datetime_cols.empty:
            return ''

        datetime_diff = (df1[datetime_cols] != df2[datetime_cols]).sum()
        return f'Datetime Differences (number of differing rows):\n{datetime_diff.to_string()}'

    def generate_high_level_summary(self, differences):
        numeric_count = sum(1 for diff in differences if 'Numeric Differences' in diff)-1
        bool_count = sum(1 for diff in differences if 'Boolean Differences' in diff)-1
        string_count = sum(1 for diff in differences if 'String Differences' in diff)
        datetime_count = sum(1 for diff in differences if 'Datetime Differences' in diff)-1

        return (
            f'High-Level Summary:\n'
            f'- Numeric Differences: {numeric_count}\n'
            f'- Boolean Differences: {bool_count}\n'
            f'- String Differences: {string_count}\n'
            f'- Datetime Differences: {datetime_count}'
        )
        
    # Function to compare DataFrames and return a boolean and message if there are discrepancies
def compare_dataframes(df1, df2):
    # Check shapes
    if df1.shape != df2.shape:
        if df1.shape[0] != df2.shape[0]:
            return False, f"Row count mismatch: Left query has {df1.shape[0]} rows, Right has {df2.shape[0]} rows. Queries return differing number of rows."
        if df1.shape[1] != df2.shape[1]:
            return False, f"Column count mismatch: Left query has {df1.shape[1]} columns, Right has {df2.shape[1]} columns. Queries return differing number of columns."

    # Check column names
    if list(df1.columns) != list(df2.columns):
        return False, f"Column names mismatch: Left query columns are {list(df1.columns)}, Right query columns are {list(df2.columns)}"
    
    # Check data types
    if list(df1.dtypes) != list(df2.dtypes):
        return False, f"Data types mismatch: Left query types are {list(df1.dtypes)}, Right query types are {list(df2.dtypes)}"
    
    # Check indexes
    if not df1.index.equals(df2.index):
        return False, f"Index mismatch: Left query index is {df1.index}, Right query index is {df2.index}"

    return True, "Results are similar in shape, column names, data types, and index."    
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SqlApp()
    ex.show()
    sys.exit(app.exec_())
