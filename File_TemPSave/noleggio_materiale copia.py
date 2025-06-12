from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QFileDialog, QDateEdit, QTimeEdit, QSpinBox, QComboBox,
    QTableWidget, QTableWidgetItem, QMessageBox, QDialog
)
from PySide6.QtCore import QDate, QTime
import datetime
import cv2
import os
import pytesseract
from datetime import datetime
from PySide6.QtWidgets import QMessageBox
from data_access import inserisci_noleggio, aggiorna_disponibilita_materiale, get_materiale_by_barcode,get_prezzo_orario_by_tipo
from Utils import stampa_ricevuta_completa, stampa_privacy 
from avvio_noleggio import avvia_noleggio
from seleziona_materiale_disponibile import SelezionaMaterialeDisponibile


class NoleggioMateriale(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Associazione Windsurf Ceresio Noleggio Materiale")
        self.materiali_noleggiati = []
        self.privacy_stampata = False
        self.ricevuta_stampata = False
        self.init_ui()

    def init_ui(self):
       # Dentro init_ui(self):
            
        layout_main = QVBoxLayout()

    # 📸 Acquisizione documento
        self.btn_doc = QPushButton("📸 Acquisisci Documento")
        layout_main.addWidget(self.btn_doc)
        self.btn_doc.clicked.connect(self.acquisisci_documento_da_webcam)

        # --- INIZIO MODIFICA MULTI-MATERIALE ---
        # Tabella materiali noleggiati
        self.tabella_materiali = QTableWidget(0, 3)
        self.tabella_materiali.setHorizontalHeaderLabels(["Codice", "Nome", "Produttore"])
        layout_main.addWidget(self.tabella_materiali)

        # Pulsanti gestione materiale
        layout_pulsanti = QHBoxLayout()

        self.btn_aggiungi_manual = QPushButton("➕ Inserisci Manuale")
        self.btn_aggiungi_manual.clicked.connect(self.inserisci_materiale_manualmente)
        layout_pulsanti.addWidget(self.btn_aggiungi_manual)

        self.btn_leggi_barcode = QPushButton("📷 Leggi Codice a Barre")
        self.btn_leggi_barcode.clicked.connect(self.leggi_codice_barre)
        layout_pulsanti.addWidget(self.btn_leggi_barcode)

        self.btn_rimuovi = QPushButton("🗑️ Rimuovi Selezionato")
        self.btn_rimuovi.clicked.connect(self.rimuovi_riga_materiale)
        layout_pulsanti.addWidget(self.btn_rimuovi)

        layout_main.addLayout(layout_pulsanti)
        # --- FINE MODIFICA MULTI-MATERIALE ---

    # Sezione cliente
        self.txt_nome = QLineEdit(); self.txt_nome.setMaximumWidth(200)
        self.txt_cognome = QLineEdit(); self.txt_cognome.setMaximumWidth(200)
        self.cmb_lingua = QComboBox(); self.cmb_lingua.addItems(["Italiano", "Nederlands", "English", "Français", "Deutsch"])

        layout_cliente = QVBoxLayout()
        layout_cliente.addWidget(QLabel("Nome:")); layout_cliente.addWidget(self.txt_nome)
        layout_cliente.addWidget(QLabel("Cognome:")); layout_cliente.addWidget(self.txt_cognome)
        layout_cliente.addWidget(QLabel("Lingua:")); layout_cliente.addWidget(self.cmb_lingua)

    # Sezione Noleggio materiale


# Facoltativo: lettura automatica alla pressione INVIO
       # self.txt_barcode.returnPressed.connect(self.carica_materiale_da_barcode)

    # Disposizione a colonne
        layout_colonne = QHBoxLayout()
        layout_colonne.addLayout(layout_cliente)
       # layout_colonne.addLayout(layout_materiale)
        layout_main.addLayout(layout_colonne)

    # Sezione tempo
        self.date_edit = QDateEdit(QDate.currentDate())
        self.time_edit = QTimeEdit(QTime.currentTime())
        self.spin_durata = QSpinBox(); self.spin_durata.setSuffix(" ore"); self.spin_durata.setRange(1, 24)

        layout_tempo = QHBoxLayout()
        layout_tempo.addWidget(QLabel("Data:")); layout_tempo.addWidget(self.date_edit)
        layout_tempo.addWidget(QLabel("Ora:")); layout_tempo.addWidget(self.time_edit)
        layout_tempo.addWidget(QLabel("Durata:")); layout_tempo.addWidget(self.spin_durata)
        layout_main.addLayout(layout_tempo)

    # Sezione pagamento
        self.btn_cash = QPushButton("💵 Cash"); self.btn_cash.setFixedWidth(90)
        self.btn_sumup = QPushButton("💳 SumUp"); self.btn_sumup.setFixedWidth(90)
        self.btn_altro = QPushButton("🔄 Altro"); self.btn_altro.setFixedWidth(90)

        layout_pagamento = QHBoxLayout()
        layout_pagamento.addWidget(QLabel("Metodo di Pagamento:"))
        layout_pagamento.addWidget(self.btn_cash)
        layout_pagamento.addWidget(self.btn_sumup)
        layout_pagamento.addWidget(self.btn_altro)
        layout_main.addLayout(layout_pagamento)
        if self.btn_cash.clicked:
            pagamento_scelto = "Cash"
        if self.btn_cash.clicked:
            pagamento_scelto = "SumUp"
        if self.btn_altro.clicked:
            pagamento_scelto = "Altro"
        
            
            

    # Pulsanti finali
        self.btn_avvia = QPushButton("✅ Avvia Noleggio"); 
        self.btn_avvia.clicked.connect(self.lancio_avvio_noleggio)
        self.btn_privacy = QPushButton("📝 Stampa Privacy")
        self.btn_privacy.clicked.connect(self.on_click_stampa_privacy)
        self.btn_ricevuta = QPushButton("🧾 Stampa Ricevuta")
        self.btn_ricevuta.clicked.connect(self.stampa_ricevuta)

        layout_finale = QHBoxLayout()
        layout_finale.addWidget(self.btn_avvia)
        layout_finale.addWidget(self.btn_privacy)
        layout_finale.addWidget(self.btn_ricevuta)
        layout_main.addLayout(layout_finale)

        self.setLayout(layout_main)

# FUNZIONE DA INCOLLARE NELLA CLASSE
    def acquisisci_documento_da_webcam(self):
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # CAP_DSHOW migliora compatibilità con Windows
        if not cap.isOpened():
           QMessageBox.critical(self, "Errore", "Impossibile accedere alla webcam.")
           return

        cv2.namedWindow("Premi SPAZIO per acquisire, ESC per annullare")

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            cv2.imshow("Premi SPAZIO per acquisire, ESC per annullare", frame)
            key = cv2.waitKey(1)
            if key == 27:  # ESC per uscire
                break
            elif key == 32:  # SPAZIO per acquisire
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                nome_file = f"documento_{timestamp}.jpg"
                cartella = os.path.join(os.getcwd(), "Documenti_per_noleggio")
                os.makedirs(cartella, exist_ok=True)
                path_completo = os.path.join(cartella, nome_file)
                cv2.imwrite(path_completo, frame)
                QMessageBox.information(self, "Documento acquisito", f"Documento salvato in:\n{path_completo}")
                break

        cap.release()
        cv2.destroyAllWindows()
        
    
    def set_pagamento(self, metodo):
        self.pagamento_scelto = metodo
        self.btn_avvia.setEnabled(True)
        QMessageBox.information(self, "Pagamento selezionato", f"Hai selezionato: {metodo}")

    def carica_materiale_da_barcode(self):
        codice = self.txt_barcode.text().strip()
        if not codice:
          QMessageBox.warning(self, "Attenzione", "Inserisci o scansiona un codice.")
          return

        materiale = get_materiale_by_barcode(codice)

        if materiale:
          self.lbl_tipo.setText(f"Tipo: {materiale['tipo']}")
          self.lbl_nome.setText(f"Nome: {materiale['nome']}")
          self.lbl_produttore.setText(f"Produttore: {materiale['produttore']}")
        else:
           QMessageBox.information(self, "Non trovato", f"Nessun materiale con codice: {codice}")
           self.lbl_tipo.setText("Tipo: -")
           self.lbl_nome.setText("Nome: -")
           self.lbl_produttore.setText("Produttore: -")

    def stampa_ricevuta(self):
        nome = self.txt_nome.text().strip()
        cognome = self.txt_cognome.text().strip()
        durata = self.spin_durata.value()
        metodo_pagamento = getattr(self, "pagamento_scelto", "N/D")
        data = self.date_edit.date().toString("yyyy-MM-dd")
        ora = self.time_edit.time().toString("HH:mm")
        lingua = self.cmb_lingua.currentText()

        try:
            # Calcolo importo totale dal listino
            importo_totale = 0
            for codice, _, _ in self.materiali_noleggiati:
                materiale = get_materiale_by_barcode(codice)
                if materiale:
                    tipo = materiale["tipo"]
                    prezzo_unitario = get_prezzo_orario_by_tipo(tipo)
                    importo_totale += prezzo_unitario * durata

            path_pdf, numero = stampa_ricevuta_completa(
                                nome=nome,
                                cognome=cognome,
                                durata=durata,
                                metodo_pagamento=metodo_pagamento,  # <-- cambia chiave da 'metodo_pagamento' a 'pagamento'
                                data=data,
                                ora=ora,
                                materiali_noleggiati=self.materiali_noleggiati,
                                lingua=lingua
                            )

            if path_pdf:
                QMessageBox.information(self, "Ricevuta generata", f"Ricevuta {numero} salvata in:\n{path_pdf}")
            else:
                QMessageBox.warning(self, "Errore", "Errore durante la generazione della ricevuta.")
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore imprevisto:\n{e}")




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


    
    # --- INIZIO METODI DI SUPPORTO MULTI-MATERIALE ---
    def inserisci_materiale_manualmente(self):
        dialog = SelezionaMaterialeDisponibile(self)
        if dialog.exec() == QDialog.Accepted and dialog.materiale_scelto:
          id_m, codice, nome, produttore = dialog.materiale_scelto
          self.aggiungi_materiale_tabella(codice, nome, produttore)

    def leggi_codice_barre(self):
        codice = self.txt_barcode.text().strip()
        if not codice:
           QMessageBox.warning(self, "Attenzione", "Inserisci o scansiona un codice.")
           return
        materiale = get_materiale_by_barcode(codice)
        if materiale:
           self.aggiungi_materiale_tabella(codice, materiale["nome"], materiale["produttore"])
        else:
         QMessageBox.warning(self, "Errore", f"Codice {codice} non trovato nel DB")

    def aggiungi_materiale_tabella(self, codice, nome, produttore):
        riga = self.tabella_materiali.rowCount()
        self.tabella_materiali.insertRow(riga)
        self.tabella_materiali.setItem(riga, 0, QTableWidgetItem(codice))
        self.tabella_materiali.setItem(riga, 1, QTableWidgetItem(nome))
        self.tabella_materiali.setItem(riga, 2, QTableWidgetItem(produttore))
        self.materiali_noleggiati.append((codice, nome, produttore))

    def rimuovi_riga_materiale(self):
        riga = self.tabella_materiali.currentRow()
        if riga >= 0:
            self.tabella_materiali.removeRow(riga)
            del self.materiali_noleggiati[riga]
    # --- FINE METODI DI SUPPORTO MULTI-MATERIALE ---

    def verifica_condizioni_avvio(self):
         if getattr(self, "privacy_stampata", False) and getattr(self, "ricevuta_stampata", False):
            self.btn_avvia.setEnabled(True)
         else:
            self.btn_avvia.setEnabled(False)

    def on_click_stampa_privacy(self):
        if self.privacy_stampata:
            QMessageBox.information(self, "Privacy", "La privacy è già stata stampata.")
            return
        lingua = self.cmb_lingua.currentText().strip()
        path_privacy = stampa_privacy(lingua)
        if path_privacy:
            self.privacy_stampata = True
            QMessageBox.information(self, "Privacy", "Documento privacy pronto per la stampa.")
        else:
            QMessageBox.warning(self, "Errore", "Errore durante la generazione del documento privacy.")

    def lancio_avvio_noleggio(self):
         avvia_noleggio(self)
