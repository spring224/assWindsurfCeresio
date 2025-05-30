from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QCheckBox, QFileDialog, QMessageBox
from data_access import carica_materiali
from barcode import Code128
from barcode.writer import ImageWriter
import qrcode
from fpdf import FPDF
import os
from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QMessageBox
from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QMessageBox


class StampaCodiciBarre(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stampa Codici a Barre")

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Stampa Codice Singolo:"))
        self.combo_singolo = QComboBox()
        self.materiali = carica_materiali()
        for mat in self.materiali:
            self.combo_singolo.addItem(f"{mat[1]} - {mat[3]}", mat)  # codice + nome
        layout.addWidget(self.combo_singolo)

        self.flag_barcode = QCheckBox("Includi Codice a Barre")
        self.flag_qrcode = QCheckBox("Includi QR Code")
        self.flag_barcode.setChecked(True)
        layout.addWidget(self.flag_barcode)
        layout.addWidget(self.flag_qrcode)

        self.btn_stampa_singolo = QPushButton("Stampa Codice Singolo")
        self.btn_stampa_singolo.clicked.connect(self.stampa_codice_singolo)
        layout.addWidget(self.btn_stampa_singolo)

        self.btn_stampa_multiplo = QPushButton("Stampa Tutti i Codici (con filtro)")
        self.btn_stampa_multiplo.clicked.connect(self.stampa_codici_multipli)
        layout.addWidget(self.btn_stampa_multiplo)

        self.setLayout(layout)

    def stampa_codice_singolo(self):
        mat = self.combo_singolo.currentData()
        self._genera_pdf([mat])

    def stampa_codici_multipli(self):
        materiali = [m for m in self.materiali if m[8] == 1]  # solo disponibili
        self._genera_pdf(materiali)

    def _genera_pdf(self, materiali):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        for mat in materiali:
            codice = mat[1]
            nome = mat[3]
            produttore = mat[4]
            barcode_str = mat[8] or f"{codice}-{produttore}-{nome}"

            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(200, 10, f"Codice: {codice}", ln=True)
            pdf.set_font("Arial", "", 14)
            pdf.cell(200, 10, f"Nome: {nome}", ln=True)
            pdf.cell(200, 10, f"Produttore: {produttore}", ln=True)

            if self.flag_barcode.isChecked():
                barcode_img = Code128(barcode_str, writer=ImageWriter()).render()
                barcode_path = f"{codice}_barcode.png"
                barcode_img.save(barcode_path)
                pdf.image(barcode_path, x=10, y=pdf.get_y(), w=100)
                os.remove(barcode_path)

            if self.flag_qrcode.isChecked():
                qr = qrcode.make(barcode_str)
                qr_path = f"{codice}_qr.png"
                qr.save(qr_path)
                pdf.image(qr_path, x=120, y=pdf.get_y(), w=50)
                os.remove(qr_path)

        save_path, _ = QFileDialog.getSaveFileName(self, "Salva PDF", "", "PDF Files (*.pdf)")
        if save_path:
            pdf.output(save_path)
            QMessageBox.information(self, "Stampa completata", f"PDF salvato in: {save_path}")

    def stampa_pdf_da_file(parent_widget, pdf_path):
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, parent_widget)

        if dialog.exec():
           pdf_doc = QPdfDocument()
        if pdf_doc.load(pdf_path) != QPdfDocument.NoError:
            QMessageBox.critical(parent_widget, "Errore", "Impossibile caricare il PDF.")
            return

        painter = QPainter()
        if not painter.begin(printer):
            QMessageBox.critical(parent_widget, "Errore", "Impossibile iniziare la stampa.")
            return

        for page_number in range(pdf_doc.pageCount()):
            image = pdf_doc.render(page_number)
            if image:
                painter.drawImage(0, 0, image)
            if page_number < pdf_doc.pageCount() - 1:
                printer.newPage()

        painter.end()