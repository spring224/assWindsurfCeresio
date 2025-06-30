
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox,
    QFormLayout, QDialogButtonBox, QDialog,QComboBox, QSpinBox, QDateEdit,QInputDialog)
from PySide6.QtCore import Qt
from PySide6.QtCore import QDate
from data_access import get_all_soci
from codice_fiscale_utils import calcola_codice_fiscale
from data_access import insert_socio_esteso
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QInputDialog
from dialogo_modifica_socio import DialogoModificaSoci
import os
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import landscape
from reportlab.lib.colors import HexColor, black
from reportlab.lib.utils import ImageReader
import qrcode
from qrcode.image.pil import PilImage
from io import BytesIO
from data_access import get_socio_by_id
from pathlib import Path

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
            pixmap = QPixmap(str(Path(file_name))).scaledToWidth(100)
            self.foto_label.setPixmap(pixmap)

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
        self.btn_quota = QPushButton("Marca Quota Pagata")
        self.btn_foto = QPushButton("Visualizza Foto")

        self.left_layout.addWidget(self.btn_aggiungi)
        self.left_layout.addWidget(self.btn_modifica)
        self.left_layout.addWidget(self.btn_elimina)
        self.left_layout.addWidget(self.btn_export_csv)
        self.left_layout.addWidget(self.btn_sollecita_quota)
        self.left_layout.addWidget(self.btn_stampa_pdf)
        self.left_layout.addWidget(self.btn_quota)
        self.left_layout.addWidget(self.btn_foto)

        # Tabella soci
        self.tabella = QTableWidget()
        self.tabella.setColumnCount(6)
        self.tabella.setHorizontalHeaderLabels(["Numero Tessera", "Nome", "Cognome", "Email", "Quota", "Anno"])

        # Collegamenti
        self.btn_aggiungi.clicked.connect(self.apri_finestra_aggiunta)
        self.btn_modifica.clicked.connect(self.apri_finestra_modifica)
        self.btn_elimina.clicked.connect(self.elimina_socio_selezionato)
        self.btn_export_csv.clicked.connect(lambda: QMessageBox.information(self, "Esporta CSV", "Funzionalità non implementata"))
        self.btn_sollecita_quota.clicked.connect(self.sollecita_quota)
        self.btn_stampa_pdf.clicked.connect(self.stampa_tessera_pdf)
       

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

        id_socio = self.tabella.item(row, 0).text()

        from data_access import get_socio_by_id, update_socio_esteso
        socio = get_socio_by_id(id_socio)
        if not socio:
           QMessageBox.warning(self, "Errore", "Impossibile trovare il socio.")
           return

        dialogo = DialogoModificaSoci(socio, self)
        if dialogo.exec() == QDialog.Accepted:
            nuovi_dati = dialogo.get_dati()
            update_socio_esteso(id_socio, nuovi_dati)
            self.carica_dati()

    def elimina_socio_selezionato(self):
        row = self.tabella.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona un socio da eliminare.")
            return

        id_socio = self.tabella.item(row, 0).text()
        conferma = QMessageBox.question(self, "Conferma", "Vuoi eliminare il socio selezionato?")
        if conferma == QMessageBox.Yes:
            from data_access import delete_socio
            delete_socio(id_socio)
            self.carica_dati()

    def marca_quota_pagata(self):
        row = self.tabella.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona un socio da aggiornare.")
            return

        id_socio = self.tabella.item(row, 0).text()
        from data_access import mark_quota_pagata
        mark_quota_pagata(id_socio, True)
        self.carica_dati()

    def visualizza_foto(self):
        print("Visualizza foto del socio selezionato")
        row = self.tabella.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona un socio.")
            return

        id_socio = self.tabella.item(row, 0).text()
        from data_access import get_socio_photo_blob
        blob = get_socio_photo_blob(id_socio)
        if blob:
            from PySide6.QtGui import QPixmap
            from PySide6.QtWidgets import QLabel, QDialog, QVBoxLayout
            from PySide6.QtCore import QByteArray
            import tempfile

            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            tmp_file.write(blob)
            tmp_file.close()

            dialog = QDialog(self)
            dialog.setWindowTitle("Foto del Socio")
            layout = QVBoxLayout(dialog)
            label = QLabel()
            pixmap = QPixmap(tmp_file.name)
            label.setPixmap(pixmap.scaledToWidth(250))
            layout.addWidget(label)
            dialog.exec()

    def sollecita_quota(self):
        row = self.tabella.currentRow()
        if row < 0:
         QMessageBox.warning(self, "Attenzione", "Seleziona un socio.")
         return

        email = self.tabella.item(row, 3).text()
        nome = self.tabella.item(row, 1).text()
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Sollecito", f"Simulazione invio email a {email} per {nome}.")

    def stampa_tessera_pdf(self):
    
    # Parametri tessera
        CARD_WIDTH = 85.6 * mm
        CARD_HEIGHT = 53.98 * mm
        ORANGE_DUTCH = HexColor('#FF7F00')
        LOGO_PATH = "logo_onda.png"

        row = self.tabella.currentRow()
        if row < 0:
         QMessageBox.warning(self, "Attenzione", "Seleziona un socio.")
         return

        id_socio = self.tabella.item(row, 0).text()
        socio = get_socio_by_id(id_socio)
        if not socio:
          QMessageBox.warning(self, "Errore", "Socio non trovato nel database.")
          return

        os.makedirs("tessere_associati", exist_ok=True)
        output_filename = os.path.join("tessere_associati", f"tessera_{id_socio}.pdf")
        c = canvas.Canvas(output_filename, pagesize=(CARD_WIDTH, CARD_HEIGHT))

    # Logo
        try:
            logo = ImageReader(LOGO_PATH)
            logo_width = CARD_WIDTH * 0.35
            logo_height = logo_width * (logo.getSize()[1] / logo.getSize()[0])
            c.drawImage(logo, 5 * mm, CARD_HEIGHT - logo_height - 5 * mm, width=logo_width, height=logo_height, mask='auto')
        except Exception:
            c.setFont('Helvetica-Bold', 10)
            c.drawString(5 * mm, CARD_HEIGHT - 15 * mm, str("LOGO MANCANTE"))

     # Dati socio
        text_x = 5 * mm
        text_y = CARD_HEIGHT - 30 * mm
        c.setFont('Helvetica-Bold', 8)
        c.drawString(text_x, text_y, str("Numero Tessera:"))
        c.setFont('Helvetica', 8)
        c.drawString(text_x + 25 * mm, text_y, str(socio['id']))

        text_y -= 5 * mm
        c.setFont('Helvetica-Bold', 8)
        c.drawString(text_x, text_y, str("Nome Associato:"))
        c.setFont('Helvetica', 8)
        c.drawString(text_x + 25 * mm, text_y, str(f"{socio['nome']} {socio['cognome']}"))

        text_y -= 5 * mm
        c.setFont('Helvetica-Bold', 8)
        c.drawString(text_x, text_y, str("Anno Validità:"))
        c.setFont('Helvetica', 8)
        c.drawString(text_x + 25 * mm, text_y, str(str(socio['anno'])))

    # Foto placeholder
        photo_x = CARD_WIDTH - 25 * mm - 5 * mm
        photo_y = CARD_HEIGHT - 28 * mm - 5 * mm
        photo_width = 20 * mm
        photo_height = 28 * mm
        c.rect(photo_x, photo_y, photo_width, photo_height)
        c.setFont('Helvetica', 6)
        c.setFillColor(black)
        c.drawCentredString(photo_x + photo_width / 2, photo_y + photo_height / 2 - 2 * mm, "Spazio")
        c.drawCentredString(photo_x + photo_width / 2, photo_y + photo_height / 2 - 5 * mm, "Foto Socio")

    # QR code
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=3,
                border=2,
            )
            qr_data = f"Numero Tessera: {socio['id']}\nNome: {socio['nome']} {socio['cognome']}\nAnno: {socio['anno']}"
            qr.add_data(qr_data)
            qr.make(fit=True)
            qr_img = qr.make_image(image_factory=PilImage)
            img_bytes = BytesIO()
            qr_img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            qr_image = ImageReader(img_bytes)
            qr_size = 15 * mm
            c.drawImage(qr_image, CARD_WIDTH - qr_size - 5 * mm, 5 * mm, width=qr_size, height=qr_size)
        except Exception:
            c.setFont('Helvetica-Bold', 8)
            c.setFillColor(black)
            c.drawString(CARD_WIDTH - 30 * mm, 15 * mm, str("QR CODE"))
            c.drawString(CARD_WIDTH - 30 * mm, 10 * mm, str("MANCANTE"))

    # Bordo arancione
        c.setStrokeColor(ORANGE_DUTCH)
        c.setLineWidth(0.5 * mm)
        c.rect(0.5 * mm, 0.5 * mm, CARD_WIDTH - 1 * mm, CARD_HEIGHT - 1 * mm)

        c.save()
        QMessageBox.information(self, "PDF generato", f"Tessera salvata in:\n{output_filename}")
