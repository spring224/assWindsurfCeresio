from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout, QStackedWidget
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Windsurf Ceresio")

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        layout = QHBoxLayout(main_widget)

        # Menu laterale
        menu_layout = QVBoxLayout()
        menu_layout.setSpacing(10)

        btn_logo = QPushButton("Home")
        btn_tesserati = QPushButton("Gestione Tesserati")
        btn_materiali = QPushButton("Gestione Materiali")
        btn_noleggi = QPushButton("Gestione Noleggi")
        btn_gestione_corsi = QPushButton("Gestione Corsi")
        btn_gestione_applicazione = QPushButton("Gestione Applicazione")

        btn_logo.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        btn_tesserati.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        btn_materiali.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        btn_noleggi.clicked.connect(lambda: self.stack.setCurrentIndex(3))
        btn_gestione_corsi.clicked.connect(lambda: self.stack.setCurrentIndex(4))
        btn_gestione_applicazione.clicked.connect(lambda: self.stack.setCurrentIndex(5))

        for btn in [btn_logo, btn_tesserati, btn_materiali, btn_noleggi, btn_gestione_corsi, btn_gestione_applicazione]:
            menu_layout.addWidget(btn)

        layout.addLayout(menu_layout, 1)

        # Area principale a destra
        self.stack = QStackedWidget()

        # Pagina 0: logo
        logo_label = QLabel()
        pixmap = QPixmap("logo_windsurf_resized.jpg")
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignCenter)

        self.stack.addWidget(logo_label)  # Index 0

        # Placeholder per i moduli
        self.stack.addWidget(QLabel("Modulo Gestione Tesserati"))  # Index 1
        self.stack.addWidget(QLabel("Modulo Gestione Materiali"))  # Index 2
        self.stack.addWidget(QLabel("Modulo Gestione Noleggi"))    # Index 3
        self.stack.addWidget(QLabel("Modulo Gestione Corsi"))       # Index 4
        self.stack.addWidget(QLabel("Modulo Gestione Applicazione")) # Index 5

        layout.addWidget(self.stack, 4)

app = QApplication(sys.argv)
window = MainWindow()
window.resize(800, 500)
window.show()
app.exec()