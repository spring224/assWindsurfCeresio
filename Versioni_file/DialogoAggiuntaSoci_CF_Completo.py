
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QLabel,
    QPushButton, QFileDialog, QVBoxLayout, QComboBox, QSpinBox, QDateEdit
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import QDate
import os

from codice_fiscale_utils import calcola_codice_fiscale

class DialogoAggiuntaSoci(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nuovo Socio Completo")

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # Campi anagrafici
        self.nome = QLineEdit()
        self.cognome = QLineEdit()
        self.via = QLineEdit()
        self.citta = QLineEdit()
        self.nazione = QLineEdit()
        self.sesso = QComboBox()
        self.sesso.addItems(["M", "F"])

        self.data_nascita = QDateEdit()
        self.data_nascita.setCalendarPopup(True)
        self.data_nascita.setDisplayFormat("dd/MM/yyyy")
        self.data_nascita.setDate(QDate.currentDate())

        self.luogo_nascita = QLineEdit()
        self.telefono = QLineEdit()
        self.email = QLineEdit()

        self.codice_fiscale = QLineEdit()
        self.codice_fiscale.setPlaceholderText("Calcolato se Italia")
        self.btn_calcola_cf = QPushButton("Calcola Codice Fiscale")
        self.btn_calcola_cf.clicked.connect(self.calcola_cf_automaticamente)

        self.anno = QSpinBox()
        self.anno.setRange(2000, 2100)
        self.anno.setValue(2025)

        # Foto
        self.foto_path = ""
        self.foto_label = QLabel("Nessuna foto selezionata")
        self.foto_button = QPushButton("Carica Foto")
        self.foto_button.clicked.connect(self.carica_foto)

        # Aggiunta al form
        form_layout.addRow("Nome:", self.nome)
        form_layout.addRow("Cognome:", self.cognome)
        form_layout.addRow("Sesso:", self.sesso)
        form_layout.addRow("Via:", self.via)
        form_layout.addRow("Città:", self.citta)
        form_layout.addRow("Nazione:", self.nazione)
        form_layout.addRow("Data di nascita:", self.data_nascita)
        form_layout.addRow("Luogo di nascita:", self.luogo_nascita)
        form_layout.addRow("Codice Fiscale:", self.codice_fiscale)
        form_layout.addRow("", self.btn_calcola_cf)
        form_layout.addRow("Telefono:", self.telefono)
        form_layout.addRow("Email:", self.email)
        form_layout.addRow("Anno Attività:", self.anno)
        form_layout.addRow(self.foto_button, self.foto_label)

        layout.addLayout(form_layout)

        # Bottoni OK / Annulla
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def calcola_cf_automaticamente(self):
        if self.nazione.text().strip().lower() != "italia":
            return
        nome = self.nome.text()
        cognome = self.cognome.text()
        sesso = self.sesso.currentText()
        data = self.data_nascita.date().toString("yyyy-MM-dd")
        luogo = self.luogo_nascita.text()
        cf = calcola_codice_fiscale(nome, cognome, sesso, data, luogo)
        if cf:
            self.codice_fiscale.setText(cf)

    def carica_foto(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Seleziona Foto", "", "Immagini (*.png *.jpg *.jpeg *.bmp)")
        if file_name:
            self.foto_path = file_name
            pixmap = QPixmap(file_name).scaledToWidth(100)
            self.foto_label.setPixmap(pixmap)

    def get_dati(self):
        indirizzo = f"{self.via.text()}, {self.citta.text()}, {self.nazione.text()}"
        data_nascita = self.data_nascita.date().toString("yyyy-MM-dd")
        foto_blob = None
        if self.foto_path and os.path.exists(self.foto_path):
            with open(self.foto_path, "rb") as f:
                foto_blob = f.read()

        return {
            "nome": self.nome.text(),
            "cognome": self.cognome.text(),
            "indirizzo": indirizzo,
            "telefono": self.telefono.text(),
            "email": self.email.text(),
            "data_nascita": data_nascita,
            "luogo_nascita": self.luogo_nascita.text(),
            "codice_fiscale": self.codice_fiscale.text(),
            "anno": self.anno.value(),
            "attivo": 1,
            "foto": foto_blob
        }
