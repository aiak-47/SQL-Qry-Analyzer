# progress_dialog.py
import sys
from PyQt5.QtWidgets import QApplication,QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import Qt

class Progress(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('work in progress')
        self.setFixedSize(300, 300)  # Adjust the size to fit both label and GIF

        layout = QVBoxLayout()

        # Label to display the status message
        self.status_label = QLabel('Initializing...', self)
        self.status_label.width = 300
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # Label to display the GIF
        self.gif_label = QLabel(self)
        self.gif_label.width = 200
        self.gif_label.setAlignment(Qt.AlignCenter)
        self.gif_label.setScaledContents(True)
        layout.addWidget(self.gif_label)

        # Load the GIF
        self.movie = QMovie('Gears.gif')
        self.gif_label.setMovie(self.movie)
        self.movie.start()

        # Set the layout
        self.setLayout(layout)
        # Remove the title bar and frame 
        self.setWindowFlags(Qt.FramelessWindowHint)

    def update_status(self, message):
        self.status_label.setText(message)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Create and show the progress dialog
    progress_dialog = Progress()
    progress_dialog.show()

    # Update the status message (for testing purposes)
    progress_dialog.update_status('Loading data...')

    sys.exit(app.exec_())
