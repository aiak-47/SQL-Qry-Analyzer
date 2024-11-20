import sys
import time
import re

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QMessageBox, QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import Qt
from sqlalchemy import create_engine, event
import pandas as pd
from menu import MenuComponent

class SqlApp(QMainWindow):
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

        # Initial connection strings
        self.sql_connection_string = "mssql+pyodbc://dmatchadmin:IntDon786#@dmdb-srv.database.windows.net,1433/DonMatchDB?driver=ODBC+Driver+18+for+SQL+Server"

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
        execute_button.clicked.connect(self.execute_queries)
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
        self.qry_stats_label_left = QLabel('Rows: N/A in N/A ms', self)
        self.qry_stats_label_right = QLabel('Rows: N/A in N/A ms', self)
        self.qry_stats_label_left.setAlignment(Qt.AlignRight)
        self.qry_stats_label_right.setAlignment(Qt.AlignRight)
        stats_layout.addWidget(self.qry_stats_label_left)
        stats_layout.addWidget(self.qry_stats_label_right)
        layout.addLayout(stats_layout)

        # Analysis display
        self.analysis_display = QTextEdit(self)
        self.analysis_display.setReadOnly(True)
        layout.addWidget(self.analysis_display)


        central_widget.setLayout(layout)

    def execute_queries(self):
        query1 = self.query_input1.toPlainText()
        query2 = self.query_input2.toPlainText()
        
        df1,exec_time_left = self.execute_query(query1)
        df2,exec_time_right = self.execute_query(query2)
        
        self.display_results(self.result_table1, df1)
        self.display_results(self.result_table2, df2)
        self.qry_stats_label_left.setText(f'Rows:{len(df1)} in {exec_time_left:.2f} ms')
        self.qry_stats_label_right.setText(f'Rows:{len(df2)} in {exec_time_right:.2f} ms')
        # self.record_count_label.setText(f'Records Returned: Query 1 - {len(df1)}, Query 2 - {len(df2)}')

        # Perform comparison if both results are available
        if not df1.empty and not df2.empty:
            analysis = self.summarize_differences(df1, df2)
            self.analysis_display.setText(analysis)
        else:
            self.analysis_display.setText('No results to compare.')

        # except Exception as e:
        #     QMessageBox.critical(self, 'Error', f'An error occurred: {e}', QMessageBox.Ok)
        
    def execute_query(self, qry):
        try:
            # Create the SQLAlchemy engine
            engine = create_engine(self.sql_connection_string)
            execution_time = []
            with engine.connect() as conn:
                # conn.execute("SET STATISTICS TIME ON;")
                
                # @event.listens_for(engine, "do_execute")
                # def do_execute(conn, cursor, statement, parameters, context):
                #     cursor.execute(statement, parameters)

                # # Capture and parse SQL Server messages
                #     messages = conn.connection.connection.get_messages()
                #     for message in messages:
                #         match = re.search(r'CPU time = (\d+) ms, elapsed time = (\d+) ms.', str(message))
                #         if match:
                #             execution_time.append(f"Elapsed time: {match.group(2)} ms")
                start_time = time.time()
                df = pd.read_sql_query(qry, conn)
                end_time = time.time()

                exec_time = (end_time - start_time) * 1000 # in milliseconds
                # conn.execute("SET STATISTICS TIME OFF")
                # exec_time = execution_time[-1] if execution_time else "N/A"  # Capture the last execution time message
                # Clear execution time
                execution_time.clear()
            return df, exec_time
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An error occurred: {e}', QMessageBox.Ok)
            return None, "N/A"             

    def display_results(self, table_widget, df):
        table_widget.setRowCount(df.shape[0])
        table_widget.setColumnCount(df.shape[1])
        table_widget.setHorizontalHeaderLabels(df.columns)

        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                table_widget.setItem(i, j, QTableWidgetItem(str(df.iloc[i, j])))

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

        # percentage_differences = ((df1[numeric_cols] - df2[numeric_cols]) / df2[numeric_cols].replace(0, pd.NA)) * 100
        # percentage_differences = percentage_differences.mean().dropna()

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
        return f'String Differences (number of differing rows):\n{string_diff.to_string()}'

    def calculate_datetime_differences(self, df1, df2):
        datetime_cols = df1.select_dtypes(include='datetime').columns
        if datetime_cols.empty:
            return ''

        datetime_diff = (df1[datetime_cols] != df2[datetime_cols]).sum()
        return f'Datetime Differences (number of differing rows):\n{datetime_diff.to_string()}'

    def generate_high_level_summary(self, differences):
        numeric_count = sum(1 for diff in differences if 'Numeric Differences' in diff)
        bool_count = sum(1 for diff in differences if 'Boolean Differences' in diff)
        string_count = sum(1 for diff in differences if 'String Differences' in diff)
        datetime_count = sum(1 for diff in differences if 'Datetime Differences' in diff)

        return (
            f'High-Level Summary:\n'
            f'- Numeric Differences: {numeric_count}\n'
            f'- Boolean Differences: {bool_count}\n'
            f'- String Differences: {string_count}\n'
            f'- Datetime Differences: {datetime_count}'
        )
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SqlApp()
    ex.show()
    sys.exit(app.exec_())
