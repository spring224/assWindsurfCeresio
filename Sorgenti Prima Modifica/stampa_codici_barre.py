import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QCheckBox, QFileDialog, QHBoxLayout, QMessageBox)
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.graphics.barcode import code128, qr
from reportlab.lib.units import mm
from PySide6.QtGui import QFont
from data_access import carica_materiali

class FinestraStampaCodici(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stampa Codici a Barre")
        self.resize(400, 300)

        layout = QVBoxLayout()

        self.combo_materiale = QComboBox()
        self.combo_materiale.setPlaceholderText("Seleziona materiale")

        materiali = carica_materiali()
        self.materiali = materiali
        self.materiali_dict = {}
        for mat in materiali:
            codice, tipo, nome, produttore = mat[0], mat[1], mat[2], mat[3]
            self.combo_materiale.addItem(f"{codice} - {nome}", userData=codice)
            self.materiali_dict[codice] = mat

        self.checkbox_barcode = QCheckBox("Stampa Codice a Barre")
        self.checkbox_barcode.setChecked(True)
        self.checkbox_qrcode = QCheckBox("Stampa QR Code")

        self.checkbox_solo_disponibili = QCheckBox("Solo disponibili")
        self.checkbox_solo_disponibili.setChecked(True)

        btn_stampa_singolo = QPushButton("Stampa Codice Singolo")
        btn_stampa_singolo.clicked.connect(self.stampa_codice_singolo)

        btn_stampa_multiplo = QPushButton("Stampa Tutti i Codici (con filtro)")
        btn_stampa_multiplo.clicked.connect(self.stampa_codici_multipli)

        layout.addWidget(QLabel("Materiale Singolo"))
        layout.addWidget(self.combo_materiale)
        layout.addWidget(self.checkbox_barcode)
        layout.addWidget(self.checkbox_qrcode)
        layout.addWidget(self.checkbox_solo_disponibili)
        layout.addWidget(btn_stampa_singolo)
        layout.addWidget(btn_stampa_multiplo)

        self.setLayout(layout)

    def stampa_codice_singolo(self):
        codice = self.combo_materiale.currentData()
        if not codice:
            QMessageBox.warning(self, "Attenzione", "Seleziona un materiale.")
            return
        mat = self.materiali_dict.get(codice)
        if not mat:
            return

        nome, produttore = mat[2], mat[3]
        barcode = f"{codice}-{produttore}-{nome}"

        filepath, _ = QFileDialog.getSaveFileName(self, "Salva PDF", "codice_singolo.pdf", "PDF files (*.pdf)")
        if not filepath:
            return
        self._genera_pdf(filepath, [(codice, nome, produttore, barcode)])

    def stampa_codici_multipli(self):
        da_stampare = []
        for mat in self.materiali:
            codice, tipo, nome, produttore, _, _, _, codice_barre, _, disponibile = mat[:10]
            if self.checkbox_solo_disponibili.isChecked() and disponibile != "SI":
                continue
            da_stampare.append((codice, nome, produttore, codice_barre))

        if not da_stampare:
            QMessageBox.information(self, "Nessun materiale", "Nessun materiale disponibile per la stampa.")
            return

        filepath, _ = QFileDialog.getSaveFileName(self, "Salva PDF", "codici_materiali.pdf", "PDF files (*.pdf)")
        if not filepath:
            return
        self._genera_pdf(filepath, da_stampare)

    def _genera_pdf(self, path, lista_materiali):
        c = canvas.Canvas(path, pagesize=A4)
        larghezza, altezza = A4
        y = altezza - 30 * mm

        for codice, nome, produttore, codice_barre in lista_materiali:
            c.setFont("Helvetica", 12)
            c.drawString(20 * mm, y, f"Codice: {codice}")
            c.drawString(20 * mm, y - 5 * mm, f"Nome: {nome}")
            c.drawString(20 * mm, y - 10 * mm, f"Produttore: {produttore}")

            if self.checkbox_barcode.isChecked():
                barcode_obj = code128.Code128(codice_barre, barHeight=15 * mm, barWidth=0.4 * mm)
                barcode_obj.drawOn(c, 20 * mm, y - 30 * mm)

            if self.checkbox_qrcode.isChecked():
                qr_code = qr.QrCodeWidget(codice_barre)
                bounds = qr_code.getBounds()
                width = bounds[2] - bounds[0]
                height = bounds[3] - bounds[1]
                d = 25 * mm
                qr_code.drawOn(c, larghezza - d - 20 * mm, y - d)

            y -= 60 * mm
            if y < 60 * mm:
                c.showPage()
                y = altezza - 30 * mm

        c.save()
        QMessageBox.information(self, "Salvataggio completato", f"PDF salvato: {os.path.basename(path)}")