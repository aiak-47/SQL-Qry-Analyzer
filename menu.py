# menu.py
from PyQt5.QtWidgets import QMenuBar, QAction, QDialog, QVBoxLayout, QLineEdit, QLabel, QPushButton

class ConnectionStringDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Set Connection Strings')
        self.setGeometry(100, 100, 700, 200)  # Increase the width and height

        layout = QVBoxLayout()

        self.sql_label = QLabel('Enter SQL Connection String:', self)
        layout.addWidget(self.sql_label)
        self.sql_input = QLineEdit(self)
        self.sql_input.setFixedWidth(600)  # Increase the width of the input field
        self.sql_input.setText("mssql+pyodbc://dmatchadmin:IntDon786#@dmdb-srv.database.windows.net,1433/DonMatchDB?driver=ODBC+Driver+18+for+SQL+Server")
        layout.addWidget(self.sql_input)

        self.mongo_label = QLabel('Enter MongoDB Connection String:', self)
        layout.addWidget(self.mongo_label)
        self.mongo_input = QLineEdit(self)
        self.mongo_input.setFixedWidth(600)  # Increase the width of the input field
        layout.addWidget(self.mongo_input)

        self.ok_button = QPushButton('OK', self)
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button)

        self.setLayout(layout)

    def get_connection_strings(self):
        return self.sql_input.text(), self.mongo_input.text()

class MenuComponent(QMenuBar):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.initMenu()

    def initMenu(self):
        # Add "Settings" menu
        settings_menu = self.addMenu('Settings')

        # Add "Connection Strings" action
        conn_str_action = QAction('Set Connection Strings', self)
        conn_str_action.triggered.connect(self.set_connection_strings)
        settings_menu.addAction(conn_str_action)

    def set_connection_strings(self):
        dialog = ConnectionStringDialog()
        if dialog.exec_():
            sql_conn_str, mongo_conn_str = dialog.get_connection_strings()
            if sql_conn_str:
                self.parent.sql_connection_string = sql_conn_str
            if mongo_conn_str:
                self.parent.mongo_connection_string = mongo_conn_str
