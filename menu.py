# menu.py
from PyQt5.QtWidgets import QMenuBar, QAction, QInputDialog

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
        # Prompt the user to enter the SQL connection string
        sql_conn_str, ok = QInputDialog.getText(self.parent, 'Set SQL Connection String', 'Enter SQL Connection String:')
        if ok and sql_conn_str:
            self.parent.sql_connection_string = sql_conn_str

        # Prompt the user to enter the MongoDB connection string
        mongo_conn_str, ok = QInputDialog.getText(self.parent, 'Set MongoDB Connection String', 'Enter MongoDB Connection String:')
        if ok and mongo_conn_str:
            self.parent.mongo_connection_string = mongo_conn_str
