from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QFileDialog, QDateEdit, QTimeEdit, QSpinBox, QComboBox,
    QTableWidget, QTableWidgetItem, QMessageBox, QDialog, QGridLayout, QFormLayout, QGroupBox
)
from PySide6.QtCore import QDate, QTime
import datetime
import cv2
import os
import pytesseract
from datetime import datetime
from PySide6.QtWidgets import QMessageBox
from data_access import inserisci_noleggio, aggiorna_disponibilita_materiale, get_materiale_by_barcode,get_prezzo_orario_by_tipo,get_prossimo_numero_ricevuta, salva_ricevuta 
from Utils import stampa_ricevuta_completa, stampa_privacy , genera_ricevuta_pdf_multilingua
from avvio_noleggio import avvia_noleggio
from seleziona_materiale_disponibile import SelezionaMaterialeDisponibile
from gestione_stampe_ricevute import gestisci_stampa_ricevuta


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

         # --- Sezione Materiali Noleggiati ---
        group_box_materiali = QGroupBox("Materiali Noleggiati")
        layout_materiali_content = QVBoxLayout() # Nuovo layout per il contenuto della GroupBox

        # Tabella materiali noleggiati
        # MODIFICA QUESTA RIGA: Da 4 a 5 colonne
        self.tabella_materiali = QTableWidget(0, 5) # Ora 5 colonne: Codice, Nome, Tipo, Produttore, Descrizione
        
        # MODIFICA QUESTA RIGA: Aggiungi "Descrizione" agli header
        self.tabella_materiali.setHorizontalHeaderLabels(["Codice", "Nome", "Tipo", "Produttore", "Descrizione"])
        
        # Assicurati che le larghezze delle colonne siano impostate correttamente per tutte e 5 le colonne
        self.tabella_materiali.setColumnWidth(0, 100) # Larghezza per Codice
        self.tabella_materiali.setColumnWidth(1, 150) # Larghezza per Nome
        self.tabella_materiali.setColumnWidth(2, 100) # Larghezza per Tipo
        self.tabella_materiali.setColumnWidth(3, 150) # Larghezza per Produttore
        self.tabella_materiali.setColumnWidth(4, 200) # NUOVA RIGA: Larghezza per Descrizione (puoi aggiustare il valore)
        
        layout_main.addWidget(self.tabella_materiali)

        # Campo per codice a barre e pulsanti di gestione
        layout_input_materiale = QHBoxLayout()
        self.txt_barcode = QLineEdit() # Aggiungi un QLineEdit per l'input manuale del codice a barre
        self.txt_barcode.setPlaceholderText("Inserisci o scansiona codice a barre")
        self.txt_barcode.returnPressed.connect(self.leggi_codice_barre) # Collega INVIO
        layout_input_materiale.addWidget(self.txt_barcode)

        # Pulsanti gestione materiale (li renderei più compatti o li separerei)
        # Rimuoviamo btn_leggi_barcode perché l'input è già gestito dal returnPressed
        self.btn_aggiungi_manual = QPushButton("➕ Noleggio Manuale")
        self.btn_aggiungi_manual.setFixedWidth(120) # Fissa larghezza
        self.btn_aggiungi_manual.clicked.connect(self.inserisci_materiale_manualmente)
        layout_input_materiale.addWidget(self.btn_aggiungi_manual)

        self.btn_rimuovi = QPushButton("🗑️ Rimuovi")
        self.btn_rimuovi.setFixedWidth(100) # Fissa larghezza
        self.btn_rimuovi.clicked.connect(self.rimuovi_riga_materiale)
        layout_input_materiale.addWidget(self.btn_rimuovi)
        
        layout_materiali_content.addLayout(layout_input_materiale) # Aggiungi il layout dell'input/pulsanti alla GroupBox

        group_box_materiali.setLayout(layout_materiali_content)
        layout_main.addWidget(group_box_materiali)


        # --- Sezione Dettagli Noleggio (Cliente, Data/Ora, Pagamento) ---
        # Useremo un QHBoxLayout per mettere Informazioni Cliente e Dettagli Noleggio affiancati
        layout_dettagli_noleggio_principale = QHBoxLayout()

        # GroupBox Informazioni Cliente
        group_box_cliente = QGroupBox("Informazioni Cliente")
        layout_cliente_form = QFormLayout() # QFormLayout è ideale per etichette e input

        self.txt_nome = QLineEdit()
        self.txt_nome.setMaximumWidth(250)
        layout_cliente_form.addRow("Nome:", self.txt_nome)

        self.txt_cognome = QLineEdit()
        self.txt_cognome.setMaximumWidth(250)
        layout_cliente_form.addRow("Cognome:", self.txt_cognome)

        self.cmb_lingua = QComboBox()
        self.cmb_lingua.addItems(["Italiano", "Nederlands", "English", "Français", "Deutsch"])
        self.cmb_lingua.setMaximumWidth(150) # Adatta la larghezza se necessario
        layout_cliente_form.addRow("Lingua:", self.cmb_lingua)
        
        group_box_cliente.setLayout(layout_cliente_form)
        layout_dettagli_noleggio_principale.addWidget(group_box_cliente)
        
       
        # GroupBox Dettagli Tempo e Pagamento
        group_box_tempo_pagamento = QGroupBox("Dettagli Noleggio")
        layout_tempo_pagamento_content = QVBoxLayout()

        # Dettagli Tempo (con QFormLayout per allineamento)
        layout_tempo_form = QFormLayout()
        self.date_edit = QDateEdit(QDate.currentDate())
        layout_tempo_form.addRow("Data:", self.date_edit)

        self.time_edit = QTimeEdit(QTime.currentTime())
        layout_tempo_form.addRow("Ora:", self.time_edit)

        self.spin_durata = QSpinBox()
        self.spin_durata.setSuffix(" ore")
        self.spin_durata.setRange(1, 24)
        layout_tempo_form.addRow("Durata:", self.spin_durata)
        
        layout_tempo_pagamento_content.addLayout(layout_tempo_form)

        # Metodo di Pagamento
        layout_pagamento = QHBoxLayout()
        layout_pagamento.addWidget(QLabel("Pagamento:"))
        self.btn_cash = QPushButton("💵 Cash")
        self.btn_cash.setFixedWidth(80)
        self.btn_sumup = QPushButton("💳 SumUp")
        self.btn_sumup.setFixedWidth(80)
        self.btn_altro = QPushButton("🔄 Altro")
        self.btn_altro.setFixedWidth(80)

        # Connetti i segnali ai metodi di pagamento
        self.btn_cash.clicked.connect(lambda: self.set_pagamento("Cash"))
        self.btn_sumup.clicked.connect(lambda: self.set_pagamento("SumUp"))
        self.btn_altro.clicked.connect(lambda: self.set_pagamento("Altro"))

        layout_pagamento.addWidget(self.btn_cash)
        layout_pagamento.addWidget(self.btn_sumup)
        layout_pagamento.addWidget(self.btn_altro)
        layout_pagamento.addStretch(1) # Spinge i pulsanti a sinistra

        layout_tempo_pagamento_content.addLayout(layout_pagamento)

        group_box_tempo_pagamento.setLayout(layout_tempo_pagamento_content)
        layout_dettagli_noleggio_principale.addWidget(group_box_tempo_pagamento)
        
        layout_dettagli_noleggio_principale.addStretch(1) # Spinge le GroupBox a sinistra
        layout_main.addLayout(layout_dettagli_noleggio_principale)


        # Pulsanti finali (come già sistemato con addStretch)
        layout_finale = QHBoxLayout()
        layout_finale.addStretch(1) # Spinge i pulsanti a destra
        self.btn_avvia = QPushButton("✅ Avvia Noleggio")
        #self.btn_avvia.setEnabled(False) # Inizialmente disabilitato
        self.btn_avvia.clicked.connect(self.lancio_avvio_noleggio)
        self.btn_privacy = QPushButton("📝 Stampa Privacy")
        self.btn_privacy.clicked.connect(self.on_click_stampa_privacy)
        self.btn_ricevuta = QPushButton("🧾 Stampa Ricevuta")
        self.btn_ricevuta.clicked.connect(self.stampa_ricevuta)
        self.btn_nuovo_noleggio = QPushButton("🆕 Nuovo Noleggio")
        self.btn_nuovo_noleggio.clicked.connect(self.reset_form)


        layout_finale.addWidget(self.btn_avvia)
        layout_finale.addWidget(self.btn_privacy)
        layout_finale.addWidget(self.btn_ricevuta)
        layout_finale.addWidget(self.btn_nuovo_noleggio)
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
        # Chiama la funzione esterna, passando tutti i dati/oggetti necessari
        gestisci_stampa_ricevuta(
            self, # Passa l'istanza di NoleggioMateriale stessa
            self.ricevuta_stampata,
            self.txt_nome,
            self.txt_cognome,
            self.date_edit,
            self.time_edit,
            self.spin_durata,
            self.cmb_lingua,
            getattr(self, "pagamento_scelto", "N/A"), # Passa il valore, non l'attributo completo
            self.materiali_noleggiati,
            self.verifica_condizioni_avvio # Passa la funzione da chiamare per l'aggiornamento UI
        )

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


    def inserisci_materiale_manualmente(self):
        dialog = SelezionaMaterialeDisponibile(self)
        if dialog.exec() == QDialog.Accepted and dialog.materiale_scelto:
            # Ora sappiamo che dialog.materiale_scelto è un DIZIONARIO completo!
            materiale_selezionato = dialog.materiale_scelto 

            # Utilizza il dizionario per passare i valori alla funzione aggiungi_materiale_tabella
            self.aggiungi_materiale_tabella(
                materiale_selezionato.get("codice", ""),
                materiale_selezionato.get("nome", ""),
                materiale_selezionato.get("tipo", ""),          # Ora il 'tipo' sarà presente
                materiale_selezionato.get("produttore", ""),    # Ora il 'produttore' sarà presente
                materiale_selezionato.get("descrizione", "")    # Ora la 'descrizione' sarà presente
            )
            # Puoi anche aggiungere un QMessageBox qui per feedback visivo, se vuoi
            # QMessageBox.information(self, "Materiale Aggiunto", f"Aggiunto: {materiale_selezionato['nome']}")
        else:
        
            QMessageBox.warning(self, "Selezione Annullata", "Nessun materiale selezionato o dialogo annullato.")

    def leggi_codice_barre(self):
        print("DEBUG: Funzione leggi_codice_barre CHIAMATA.")
        codice = self.txt_barcode.text().strip()
        if not codice:
            QMessageBox.warning(self, "Attenzione", "Inserisci o scansiona un codice.")
            return

        # get_materiale_by_barcode ritorna un dizionario con id, codice, nome, tipo, produttore, descrizione, note
        materiale = get_materiale_by_barcode(codice)
        print(f"DEBUG: Contenuto di 'materiale' per codice '{codice}': {materiale}")
        # ***********************************
        if materiale:
            # Passa ESATTAMENTE 5 argomenti, nell'ordine CORRETTO
            self.aggiungi_materiale_tabella(
                materiale["codice"],     # 1° argomento: codice
                materiale["nome"],       # 2° argomento: nome
                materiale["tipo"],       # 3° argomento: tipo
                materiale["produttore"], # 4° argomento: produttore
                materiale["descrizione"] # 5° argomento: descrizione
            )
            # Aggiunto per pulire il campo barcode dopo l'aggiunta, se non lo fai già in aggiungi_materiale_tabella
            self.txt_barcode.clear()
        else:
            QMessageBox.warning(self, "Errore", f"Codice {codice} non trovato nel database.")


    def aggiungi_materiale_tabella(self, codice, nome, tipo, produttore, descrizione):
            
        riga = self.tabella_materiali.rowCount()
        self.tabella_materiali.insertRow(riga)

        valori = [codice, nome, tipo, produttore, descrizione]

        for colonna, valore in enumerate(valori):
            testo = valore if valore is not None else ""  # Protezione da None
            item = QTableWidgetItem(testo)
            self.tabella_materiali.setItem(riga, colonna, item)

        self.materiali_noleggiati.append(tuple(valori))

        self.tabella_materiali.resizeColumnsToContents()
        self.tabella_materiali.setColumnWidth(4, 300)  # Descrizione più larga

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
        
        # Chiama la funzione stampa_privacy (dal modulo Utils)
        # e gestisci il suo valore di ritorno.
        path_privacy = stampa_privacy(lingua) # <<< CHIAMATA CORRETTA, NON RICORSIVA

        if path_privacy:
            self.privacy_stampata = True
            # Il QMessageBox.information è già gestito all'interno della funzione stampa_privacy
            # per dare feedback all'utente sul tentativo di stampa.
            # Quindi qui puoi solo chiamare verifica_condizioni_avvio
            self.verifica_condizioni_avvio() # Aggiorna lo stato del pulsante Avvia Noleggio
        else:
            # La funzione stampa_privacy mostra già un messaggio di errore se qualcosa va storto,
            # quindi non è necessario mostrare un altro warning qui.
            pass

    def lancio_avvio_noleggio(self):
         avvia_noleggio(self)
    # Funzione per resettare il modulo di noleggio
    def reset_form(self):
        # Reset campi di input
        self.txt_nome.clear()
        self.txt_cognome.clear()
        self.date_edit.setDate(QDate.currentDate())
        self.time_edit.setTime(QTime.currentTime())
        self.spin_durata.setValue(1) # Resetta a durata di default
        self.txt_barcode.clear()
        
        # Pulisci la tabella dei materiali
        self.tabella_materiali.setRowCount(0)
        self.materiali_noleggiati.clear() # Pulisci la lista interna dei materiali

        # Resetta i flag di stampa
        self.privacy_stampata = False
        self.ricevuta_stampata = False

        # Resetta la selezione del metodo di pagamento se necessario
        self.pagamento_scelto = None # O imposta a un valore di default se ne hai uno
        if hasattr(self, 'btn_paga_contanti'): # Se questi bottoni cambiano stato visivo
             self.btn_paga_contanti.setChecked(False)
        if hasattr(self, 'btn_paga_carta'):
             self.btn_paga_carta.setChecked(False)

        # Resetta lo stato del pulsante "Avvia Noleggio"
        self.verifica_condizioni_avvio()
        successo_noleggio = avvia_noleggio(self) # Chiamata a avvia_noleggio.py

        if successo_noleggio: # Se la funzione esterna indica successo
            self.reset_form() # Resetta l'interfaccia per un nuovo noleggio
            # Il QMessageBox di successo è già gestito in avvia_noleggio, quindi non lo ripetiamo qui.
        # else:
            # L'errore è già gestito in avvia_noleggio, quindi non è necessario qui
        
        QMessageBox.information(self, "Reset", "Modulo noleggio resettato. Pronto per un nuovo noleggio.")