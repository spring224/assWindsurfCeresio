
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox,
    QFormLayout, QDialogButtonBox, QDialog,QComboBox, QSpinBox, QDateEdit,QInputDialog)
from PySide6.QtCore import Qt
from PySide6.QtCore import QDate
from data_access import get_all_soci, insert_socio
from codice_fiscale_utils import calcola_codice_fiscale
from data_access import insert_socio_esteso
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QInputDialog
import os

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

       # self.nazione.currentText() == QComboBox()
        self.nazione = QComboBox()
        nazioni_europee = ["Italia", "Francia", "Germania", "Svizzera", "Spagna", "Austria", "Belgio", "Paesi Bassi", "Portogallo", "Regno Unito"]
        self.nazione.addItems(nazioni_europee)

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

        # Caricamento foto
        self.foto_path = ""
        self.foto_label = QLabel("Nessuna foto selezionata")
        self.foto_button = QPushButton("Carica Foto")
        self.foto_button.clicked.connect(self.carica_foto)

        # Layout form
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

        # Bottoni OK/Annulla
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def carica_foto(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Seleziona Foto", "", "Immagini (*.png *.jpg *.jpeg *.bmp)")
        if file_name:
            self.foto_path = file_name
            pixmap = QPixmap(file_name).scaledToWidth(100)
            self.foto_label.setPixmap(pixmap)

    def get_dati(self):
        indirizzo = f"{self.via.text()}, {self.citta.text()}, {self.nazione.currentText()}"
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


    def calcola_cf_automaticamente(self):
        if self.nazione.currentText().strip().lower() != "italia":
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
        
        indirizzo = f"{self.via.text()}, {self.citta.text()}, {self.nazione.currentText()}"
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


class FinestraGestioneSoci(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestione Soci Annuali - Windsurf Ceresio")
        self.setMinimumSize(1000, 600)

        main_layout = QHBoxLayout(self)

        # Colonna sinistra
        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout()
        self.left_panel.setLayout(self.left_layout)

        self.btn_aggiungi = QPushButton("Aggiungi Socio")
        self.btn_modifica = QPushButton("Modifica Selezionato")
        self.btn_elimina = QPushButton("Elimina Selezionato")
        self.btn_export_csv = QPushButton("Esporta CSV")
        self.btn_sollecita_quota = QPushButton("Sollecita Quota")
        self.btn_stampa_pdf = QPushButton("Stampa Tessera PDF")

        self.left_layout.addWidget(self.btn_aggiungi)
        self.left_layout.addWidget(self.btn_modifica)
        self.left_layout.addWidget(self.btn_elimina)
        self.left_layout.addWidget(self.btn_export_csv)
        self.left_layout.addWidget(self.btn_sollecita_quota)
        self.left_layout.addWidget(self.btn_stampa_pdf)

        # Tabella soci
        self.tabella = QTableWidget()
        self.tabella.setColumnCount(6)
        self.tabella.setHorizontalHeaderLabels(["ID", "Nome", "Cognome", "Email", "Quota", "Foto"])

        # Collegamenti
        self.btn_aggiungi.clicked.connect(self.apri_finestra_aggiunta)
        self.btn_modifica.clicked.connect(self.apri_finestra_modifica)

        main_layout.addWidget(self.left_panel)
        main_layout.addWidget(self.tabella)

        self.carica_dati()

    def carica_dati(self):
        soci = get_all_soci()
        self.tabella.setRowCount(0)
        for row_num, socio in enumerate(soci):
            self.tabella.insertRow(row_num)
            for col_num, valore in enumerate(socio[:6]):
                item = QTableWidgetItem(str(valore))
                self.tabella.setItem(row_num, col_num, item)

    def apri_finestra_aggiunta(self):
     dialogo = DialogoAggiuntaSoci(self)
     if dialogo.exec() == QDialog.Accepted:
        dati = dialogo.get_dati()
        try:
            insert_socio_esteso(dati)
            self.carica_dati()
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Errore", f"Errore durante il salvataggio: {e}")

    def apri_finestra_modifica(self):
        row = self.tabella.currentRow()
        if row < 0:
         QMessageBox.warning(self, "Attenzione", "Seleziona un socio da modificare.")
        return

        id_socio = self.tabella.item(row, 0).text()  # Colonna 0: ID
        nome = self.tabella.item(row, 1).text()
        cognome = self.tabella.item(row, 2).text()
        email = self.tabella.item(row, 3).text()
        quota = self.tabella.item(row, 4).text()
        nuovo_nome, ok = QInputDialog.getText(self, "Modifica Nome", "Nuovo nome:", text=nome)
        if not ok:
          return
    # (Poi mostreremo una finestra completa, ora facciamo test con nome)
        from data_access import update_socio
        update_socio(id_socio, nuovo_nome, cognome, email, quota)
        self.carica_dati()
