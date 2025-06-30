from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel

class GestioneNoleggi(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestione Noleggi")

        layout = QVBoxLayout()

        self.btn_listino = QPushButton("📋 Gestione Listino Noleggio")
        self.btn_resoconto = QPushButton("📈 Resoconto Noleggi")

        self.btn_listino.clicked.connect(self.apri_listino)
        self.btn_resoconto.clicked.connect(self.apri_resoconto)

        layout.addWidget(QLabel("Scegli un'operazione:"))
        layout.addWidget(self.btn_listino)
        layout.addWidget(self.btn_resoconto)

        self.setLayout(layout)

    def apri_listino(self):
        from Listino_noleggi import FinestraListino
        self.finestra_listino = FinestraListino()
        self.finestra_listino.show()

    def apri_resoconto(self):
        from resoconto_noleggi import FinestraResoconto
        self.finestra_resoconto = FinestraResoconto()
        self.finestra_resoconto.show()