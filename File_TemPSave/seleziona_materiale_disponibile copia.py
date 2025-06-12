from PySide6.QtWidgets import QDialog, QVBoxLayout, QComboBox, QPushButton
from data_access import get_materiali_disponibili

class SelezionaMaterialeDisponibile(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Seleziona Materiale Disponibile per il Noleggio")
        self.materiale_scelto = None

        layout = QVBoxLayout()
        self.combo = QComboBox()
        
        self.materiali = get_materiali_disponibili()
        for materiale in self.materiali:
            # materiale = (id, codice, nome, produttore)
            descrizione = f"{materiale[1]} - {materiale[2]} ({materiale[3]})"
            self.combo.addItem(descrizione, materiale)

        layout.addWidget(self.combo)

        btn_ok = QPushButton("Seleziona")
        btn_ok.clicked.connect(self.seleziona)
        layout.addWidget(btn_ok)

        self.setLayout(layout)

    def seleziona(self):
        self.materiale_scelto = self.combo.currentData()
        self.accept()
