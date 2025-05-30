
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout, QComboBox, QFileDialog, QDateEdit
from PySide6.QtGui import QPixmap
from PySide6.QtCore import QDate
import os
from pathlib import Path

class DialogoModificaSoci(QDialog):
    def __init__(self, socio=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Modifica Socio")
        self.resize(400, 400)
        self.foto_path = None

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.nome = QLineEdit()
        self.cognome = QLineEdit()
        self.via = QLineEdit()
        self.citta = QLineEdit()
        self.nazione = QComboBox()
        self.nazione.addItems(["Italia", "Svizzera", "Francia", "Germania", "Austria", "Spagna"])
        self.telefono = QLineEdit()
        self.email = QLineEdit()
        self.data_nascita = QDateEdit()
        self.data_nascita.setCalendarPopup(True)
        self.data_nascita.setDisplayFormat("yyyy-MM-dd")
        self.luogo_nascita = QLineEdit()
        self.codice_fiscale = QLineEdit()
        self.anno = QLineEdit()
        self.foto_label = QLabel("Nessuna foto selezionata")
        self.btn_foto = QPushButton("Carica Foto")
        self.btn_foto.clicked.connect(self.carica_foto)

        form_layout.addRow("Nome", self.nome)
        form_layout.addRow("Cognome", self.cognome)
        form_layout.addRow("Via", self.via)
        form_layout.addRow("Città", self.citta)
        form_layout.addRow("Nazione", self.nazione)
        form_layout.addRow("Telefono", self.telefono)
        form_layout.addRow("Email", self.email)
        form_layout.addRow("Data di nascita", self.data_nascita)
        form_layout.addRow("Luogo di nascita", self.luogo_nascita)
        form_layout.addRow("Codice Fiscale", self.codice_fiscale)
        form_layout.addRow("Anno", self.anno)
        form_layout.addRow("Foto", self.btn_foto)
        form_layout.addRow("", self.foto_label)

        layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        self.btn_ok = QPushButton("Salva")
        self.btn_annulla = QPushButton("Annulla")
        self.btn_ok.clicked.connect(self.accept)
        self.btn_annulla.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_ok)
        btn_layout.addWidget(self.btn_annulla)

        layout.addLayout(btn_layout)

        if socio:
            self.set_dati(socio)

    def set_dati(self, dati):
        self.nome.setText(dati["nome"])
        self.cognome.setText(dati["cognome"])
        indirizzo = dati["indirizzo"].split(",")
        if len(indirizzo) >= 3:
            self.via.setText(indirizzo[0].strip())
            self.citta.setText(indirizzo[1].strip())
            self.nazione.setCurrentText(indirizzo[2].strip())
        self.telefono.setText(dati["telefono"])
        self.email.setText(dati["email"])
        self.data_nascita.setDate(QDate.fromString(dati["data_nascita"], "yyyy-MM-dd"))
        self.luogo_nascita.setText(str(dati["luogo_nascita"]))

        self.codice_fiscale.setText(dati["codice_fiscale"])
        self.anno.setText(str(dati["anno"]))

    def get_dati(self):
        indirizzo = f"{self.via.text()}, {self.citta.text()}, {self.nazione.currentText()}"
        data_nascita = self.data_nascita.date().toString("yyyy-MM-dd")
        foto_blob = None
        if self.foto_path and os.path.exists(self.foto_path):
            with open(Path(self.foto_path), "rb") as f:
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
            "anno": int(self.anno.text()),
            "foto": foto_blob
        }

    def carica_foto(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Seleziona foto", "", "Immagini (*.png *.jpg *.bmp)")
        if file_name:
            self.foto_path = file_name
            self.foto_label.setText(os.path.basename(file_name))
