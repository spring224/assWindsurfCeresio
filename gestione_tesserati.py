from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel

class FinestraSemplice(QWidget):
    def __init__(self, titolo):
        super().__init__()
        self.setWindowTitle(titolo)
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Finestra: {titolo}"))
        self.setLayout(layout)

class GestioneTesseratiWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestione Tesserati")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()

        btn_annuali = QPushButton("Gestione Tesserati Annuali")
        btn_annuali.clicked.connect(lambda: self.apri_sottofinestra("Tesserati Annuali"))
        layout.addWidget(btn_annuali)

        btn_giornalieri = QPushButton("Gestione Tesserati Giornalieri")
        btn_giornalieri.clicked.connect(lambda: self.apri_sottofinestra("Tesserati Giornalieri"))
        layout.addWidget(btn_giornalieri)

        self.setLayout(layout)
        self.finestre_aperte = []

    def apri_sottofinestra(self, titolo):
        finestra = FinestraSemplice(titolo)
        finestra.show()
        self.finestre_aperte.append(finestra)  # tiene in vita la finestra