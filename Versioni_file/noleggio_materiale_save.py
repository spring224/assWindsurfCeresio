from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QFileDialog, QDateEdit, QTimeEdit, QSpinBox, QComboBox
)
from PySide6.QtCore import QDate, QTime
import datetime
import cv2
import os
import pytesseract
from datetime import datetime
from PySide6.QtWidgets import QMessageBox
from data_access import inserisci_noleggio, aggiorna_disponibilita_materiale, get_materiale_by_barcode
from Utils import genera_ricevuta_pdf, calcola_prossimo_numero

class NoleggioMateriale(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Noleggio Materiale")
        self.init_ui()

    def init_ui(self):
        # Campi cliente
        self.btn_doc = QPushButton("📸 Acquisisci Documento")
        self.btn_doc.clicked.connect(self.acquisisci_documento)

        self.btn_avvia = QPushButton("✅ Avvia Noleggio")
        self.btn_avvia.setEnabled(False)  # Abilitato solo dopo il pagamento

        self.txt_nome = QLineEdit()
        self.txt_cognome = QLineEdit()
        self.cmb_lingua = QComboBox()
        self.cmb_lingua.addItems(["Italiano", "Nederlands"])

        # Campi materiale
        self.txt_barcode = QLineEdit()
        self.txt_barcode.setPlaceholderText("Scansiona barcode...")
        self.txt_barcode.returnPressed.connect(self.carica_materiale)

        self.lbl_tipo = QLabel("Tipo: -")
        self.lbl_produttore = QLabel("Produttore: -")
        self.lbl_nome = QLabel("Nome: -")

        # Campi tempo
        self.date_edit = QDateEdit(QDate.currentDate())
        self.time_edit = QTimeEdit(QTime.currentTime())
        self.spin_durata = QSpinBox()
        self.spin_durata.setRange(1, 24)
        self.spin_durata.setSuffix(" ore")

        # Pulsanti
        
        self.btn_avvia = QPushButton("✅ Avvia Noleggio")
        self.btn_privacy = QPushButton("📝 Stampa Privacy")

        layout = QVBoxLayout()
        layout.addWidget(self.btn_doc)
        layout.addWidget(QLabel("Nome:")); layout.addWidget(self.txt_nome)
        layout.addWidget(QLabel("Cognome:")); layout.addWidget(self.txt_cognome)
        layout.addWidget(QLabel("Lingua:")); layout.addWidget(self.cmb_lingua)

        layout.addWidget(QLabel("Codice a Barre:")); layout.addWidget(self.txt_barcode)
        layout.addWidget(self.lbl_tipo)
        layout.addWidget(self.lbl_produttore)
        layout.addWidget(self.lbl_nome)

        layout.addWidget(QLabel("Data:")); layout.addWidget(self.date_edit)
        layout.addWidget(QLabel("Ora:")); layout.addWidget(self.time_edit)
        layout.addWidget(QLabel("Durata:")); layout.addWidget(self.spin_durata)

        layout.addWidget(self.btn_avvia)
        layout.addWidget(self.btn_privacy)

        layout.addWidget(QLabel("Metodo di Pagamento:"))
        # Sezione pagamento
        self.pagamento_scelto = None

        self.btn_cash = QPushButton("💵 Cash")
        self.btn_sumup = QPushButton("💳 SumUp")
        self.btn_altro = QPushButton("🔄 Altro")

        self.btn_cash.clicked.connect(lambda: self.set_pagamento("Cash"))
        self.btn_sumup.clicked.connect(lambda: self.set_pagamento("SumUp"))
        self.btn_altro.clicked.connect(lambda: self.set_pagamento("Altro"))

        self.btn_avvia.clicked.connect(self.avvia_noleggio)

        pag_layout = QHBoxLayout()
        pag_layout.addWidget(self.btn_cash)
        pag_layout.addWidget(self.btn_sumup)
        pag_layout.addWidget(self.btn_altro)

        layout.addLayout(pag_layout)
        layout.addWidget(self.btn_avvia)
        layout.addWidget(self.btn_privacy)
#Sezione Stampa Ricevuta
        self.btn_ricevuta = QPushButton("🧾 Stampa Ricevuta")
        self.btn_ricevuta.clicked.connect(self.stampa_ricevuta)
        layout.addWidget(self.btn_ricevuta)

        self.setLayout(layout)

    def acquisisci_documento(self):
        # (mock temporaneo — inserire funzione webcam + OCR)
        nome = "Mario"
        cognome = "Rossi"
        self.txt_nome.setText(nome)
        self.txt_cognome.setText(cognome)

    def carica_materiale(self):
        codice = self.txt_barcode.text()
        # chiamata a data_access per caricare da barcode
        # esempio:
        # tipo, produttore, nome = carica_dati_materiale(codice)
        tipo, produttore, nome = "SUP", "Fanatic", "Race"
        self.lbl_tipo.setText(f"Tipo: {tipo}")
        self.lbl_produttore.setText(f"Produttore: {produttore}")
        self.lbl_nome.setText(f"Nome: {nome}")

    def avvia_noleggio(self):
    

       nome = self.txt_nome.text().strip()
       cognome = self.txt_cognome.text().strip()
       barcode = self.txt_barcode.text().strip()
       data = self.date_edit.date().toString("yyyy-MM-dd")
       ora = self.time_edit.time().toString("HH:mm")
       durata = self.spin_durata.value()
       lingua = self.cmb_lingua.currentText()
       metodo_pagamento = self.pagamento_scelto
       percorso_doc = ""  # da salvare se disponibile

       if not nome or not cognome or not barcode or not metodo_pagamento:
            QMessageBox.warning(self, "Dati mancanti", "Compila tutti i campi e seleziona un metodo di pagamento.")
            return

    # Cerca ID materiale da barcode
    
       materiale = get_materiale_by_barcode(barcode)
       if not materiale:
        QMessageBox.warning(self, "Errore", "Materiale non trovato.")
        return

       id_materiale = materiale["id"]
       tipo = materiale["tipo"]
       produttore = materiale["produttore"]
       nome_materiale = materiale["nome"]

       inserisci_noleggio(nome, cognome, id_materiale, barcode, data, ora, durata, percorso_doc, lingua, metodo_pagamento)
       aggiorna_disponibilita_materiale(id_materiale, 0)

       QMessageBox.information(self, "Noleggio registrato", f"{nome} {cognome} ha noleggiato {nome_materiale} ({barcode}) per {durata} ore.")
       self.btn_avvia.setEnabled(False)
    
    def set_pagamento(self, metodo):
        self.pagamento_scelto = metodo
        self.btn_avvia.setEnabled(True)
        QMessageBox.information(self, "Pagamento selezionato", f"Hai selezionato: {metodo}")


    def stampa_ricevuta(self):
        nome = self.txt_nome.text().strip()
        cognome = self.txt_cognome.text().strip()
        barcode = self.txt_barcode.text().strip()
        durata = self.spin_durata.value()
        pagamento = self.pagamento_scelto or "N/D"
        data = self.date_edit.date().toString("yyyy-MM-dd")
        ora = self.time_edit.time().toString("HH:mm")


        materiale = get_materiale_by_barcode(barcode)
        if not materiale:
          QMessageBox.warning(self, "Errore", "Materiale non trovato.")
          return

        nome_materiale = materiale["nome"]
        produttore = materiale["produttore"]
        tipo = materiale["tipo"]

        anno_corrente = datetime.now().year
        numero = calcola_prossimo_numero(anno_corrente)

        path_pdf = genera_ricevuta_pdf(
          numero, nome, cognome, f"{tipo} {nome_materiale} ({produttore})",
          data, ora, durata, pagamento
          )

        QMessageBox.information(self, "Ricevuta Generata", f"Ricevuta salvata in:\n{path_pdf}")


    # Se su Windows e pytesseract non è in PATH
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def acquisisci_documento(self):
    cartella = "Documenti_per_noleggio"
    os.makedirs(cartella, exist_ok=True)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        QMessageBox.critical(self, "Errore", "Webcam non disponibile.")
        return

    QMessageBox.information(self, "Istruzioni", "Premi [SPAZIO] per scattare la foto del documento.\nPremi [ESC] per annullare.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        cv2.imshow("Webcam - Documento", frame)
        key = cv2.waitKey(1)
        if key == 27:  # ESC
            cap.release()
            cv2.destroyAllWindows()
            return
        elif key == 32:  # SPACE
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            path_img = os.path.join(cartella, f"documento_{timestamp}.png")
            cv2.imwrite(path_img, frame)
            break

    cap.release()
    cv2.destroyAllWindows()

    # OCR
    testo_ocr = pytesseract.image_to_string(path_img)

    import re
    match = re.search(r"\b([A-Z][a-z]+)\s+([A-Z][a-z]+)\b", testo_ocr)
    if match:
        nome = match.group(1)
        cognome = match.group(2)
        self.txt_nome.setText(nome)
        self.txt_cognome.setText(cognome)
        QMessageBox.information(self, "Documento acquisito", f"Nome: {nome}\nCognome: {cognome}")
    else:
        QMessageBox.warning(self, "OCR fallito", "Non è stato possibile rilevare nome e cognome dal documento.")

def set_pagamento(self, metodo):
    self.pagamento_scelto = metodo
    self.btn_avvia.setEnabled(True)
    QMessageBox.information(self, "Pagamento selezionato", f"Hai selezionato: {metodo}")

