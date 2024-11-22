import sys
import time
import re
import os
import logging

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QMessageBox, QTableWidget, QTableWidgetItem, QDialog
)
from ydata_profiling import ProfileReport
from PyQt5.QtCore import Qt,QThread, pyqtSignal
from PyQt5.QtGui import QColor,QIcon
from sqlalchemy import create_engine, event
import pandas as pd
from menu import MenuComponent

logging.basicConfig(filename='app.log', level=logging.ERROR, format='%(asctime)s:%(levelname)s:%(message)s')

def log_unhandled_exceptions(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        # Let the KeyboardInterrupt exception propagate normally
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return 
    # Log the unhandled exception 
    logging.error("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))
# Set the global exception handler 
sys.excepthook = log_unhandled_exceptions    
class QueryWorker(QThread):
    update_status = pyqtSignal(str)
    finished = pyqtSignal(object, object, object, object)  # Dataframes and execution times

    def __init__(self, query1, query2, execute_query_func, profile_results_func):
        super().__init__()
        self.query1 = query1
        self.query2 = query2
        self.execute_query = execute_query_func
        self.profile_results = profile_results_func

    def run(self):
        try:
            self.update_status.emit('Executing left query...')
            df1, exec_time_left = self.execute_query(self.query1)
            self.update_status.emit('Left query executed. Profiling results...')
            profile_left = self.profile_results(df1, 'left')

            self.update_status.emit('Executing right query...')
            df2, exec_time_right = self.execute_query(self.query2)
            self.update_status.emit('Right query executed. Profiling results...')
            profile_right = self.profile_results(df2, 'right')

            self.finished.emit(df1, exec_time_left, df2, exec_time_right)
        except Exception as e:
            self.update_status.emit(f'Error: {e}')
            self.finished.emit(None, None, None, None)
  

class MainApp(QMainWindow):
    # Initial connection strings
    sql_connection_string = "mssql+pyodbc://dmatchadmin:IntDon786#@dmdb-srv.database.windows.net,1433/DonMatchDB?driver=ODBC+Driver+18+for+SQL+Server"
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('SQL Query Analyzer')
        self.setGeometry(100, 100, 1000, 600)
        # Set the window icon 
        self.setWindowIcon(QIcon('analysis.png'))

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
        # Clear previous results
        self.reset_ui()
        self.clean_reports_folder()
        
        # Disable UI elements
        self.enable_ui_elements(False)
        
        # Set initial button text
        self.execute_button.setText('Executing queries...')
        
        # Get queries from text inputs
        query1 = self.query_input1.toPlainText()
        query2 = self.query_input2.toPlainText()
        
        # Create and start the worker thread
        self.worker = QueryWorker(query1, query2, self.execute_query, self.profile_results)
        self.worker.update_status.connect(self.update_button_text)
        self.worker.finished.connect(self.handle_query_results)
        self.worker.start()

    def update_button_text(self, message):
        self.execute_button.setText(message)
        self.execute_button.repaint()  # Force repaint to update the text immediately

    def handle_query_results(self, df1, exec_time_left, df2, exec_time_right):
        if df1 is not None and df2 is not None:
            self.display_results(self.result_table1, df1)
            self.display_results(self.result_table2, df2)
            self.qry_stats_label_left.setText(f'Rows: {len(df1)} in {exec_time_left:.2f} ms')
            self.qry_stats_label_right.setText(f'Rows: {len(df2)} in {exec_time_right:.2f} ms')
            self.update_button_text('Validating results...')

        # Perform comparison if both results are available
        if not df1.empty and not df2.empty:
            self.update_button_text('Starting comparison...')
            comp_pass, message = self.compare_dataframes(df1, df2)
            if not comp_pass:
                message_type = 'error'
                self.write_to_analysis_display(message, message_type)
                self.enable_ui_elements(True)
                return
            else:
                message = 'Results are similar in shape, column names, data types, and index.'
                message_type = 'info'
                self.write_to_analysis_display(message, message_type)
        else:
            self.write_to_analysis_display('No results to compare.', 'warning')
    
    # Re-enable UI elements
        self.enable_ui_elements(True)
        self.update_button_text('Analyze')

    def enable_ui_elements(self,enable=True):
        self.execute_button.setEnabled(enable)
        self.query_input1.setEnabled(enable)
        self.query_input2.setEnabled(enable)
        if(enable):
            # self.progress_dialog.close()
            self.execute_button.setText('Analyze')
            QApplication.restoreOverrideCursor()
        else:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            
    def reset_ui(self):
        self.result_table1.clear()
        self.result_table2.clear()
        self.analysis_display.clear()
        self.qry_stats_label_left.setText('Rows: N/A in N/A ms')
        self.qry_stats_label_right.setText('Rows: N/A in N/A ms')
        self.execute_button.text = 'Analyze'

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

    def profile_results(self, df,type):
        root_dir = os.path.dirname(os.path.abspath(__file__)) 
        reports_folder = os.path.join(root_dir, 'reports')
        
        if not os.path.exists(reports_folder): 
            os.makedirs(reports_folder)
        
        report_path = os.path.join(reports_folder, f'{type}_profile.html')
        profile = ProfileReport(df,title=f'{type}_Results Profile')
        profile.to_file(report_path)
        return profile
    
    def clean_reports_folder(self):
        root_dir = os.path.dirname(os.path.abspath(__file__)) 
        reports_folder = os.path.join(root_dir, 'reports')
        
        if os.path.exists(reports_folder):
            for filename in os.listdir(reports_folder):
                file_path = os.path.join(reports_folder, filename) 
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.remove(file_path) 
                    # elif os.path.isdir(file_path):
                        # shutil.rmtree(file_path) 
                except Exception as e: print(f'Failed to delete {file_path}. Reason: {e}')
    # Function to compare DataFrames and return a boolean and message if there are discrepancies
    def compare_dataframes(self,df1, df2):
        # Sort DataFrames 
        df1 = df1.sort_values(by=df1.columns.tolist()).reset_index(drop=True) 
        df2 = df2.sort_values(by=df2.columns.tolist()).reset_index(drop=True)
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

        differences = df1.compare(df2,result_names=('Left','Right'))
        if not differences.empty:
            # self.profile_results(differences,'Differences')
            self.profile_diff = self.profile_left.compare(self.profile_right)
            self.profile_diff.to_file('reports/differences_profile.html')
            diff = df1.ne(df2) 
            differing_cells = diff.stack()[diff.stack()]
            Message = f"Differences found in {len(differing_cells)} cells. /n/nSee profile reports for details."
            return False, Message
        else:
            return True, "Results are similar in shape, column names, data types, and index."    
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('analysis.png'))
    ex = MainApp()
    ex.show()
    sys.exit(app.exec_())
