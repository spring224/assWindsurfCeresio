# noleggio_materiale.py

from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QFileDialog, QDateEdit, QTimeEdit, QSpinBox, QComboBox,
    QTableWidget, QTableWidgetItem, QMessageBox, QDialog, QGridLayout, QFormLayout, QGroupBox
)
from PySide6.QtCore import QDate, QTime, Qt # Aggiunto Qt per allineamento
import datetime
import cv2
import os
import pytesseract
from datetime import datetime as dt_now # Rinominato per evitare conflitti con PySide6.QtCore.QTime
from data_access import inserisci_noleggio, aggiorna_disponibilita_materiale, get_materiale_by_barcode, get_prezzo_orario_by_tipo, get_prossimo_numero_ricevuta, salva_ricevuta ,inserisci_dettaglio_noleggio
from Utils import stampa_privacy, genera_ricevuta_pdf_multilingua # Ho rimosso stampa_ricevuta_completa che non sembra essere definita
from avvio_noleggio import finalizza_noleggio
from seleziona_materiale_disponibile import SelezionaMaterialeDisponibile
from gestione_stampe_ricevute import gestisci_stampa_ricevuta


class NoleggioMateriale(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Associazione Windsurf Ceresio Noleggio Materiale")
        self.materiali_noleggiati = [] # Lista di tuple (id_db, codice, nome, tipo, produttore, descrizione)
        self.privacy_stampata = False
        self.ricevuta_stampata = False
        self.pagamento_scelto = None # Per memorizzare il metodo di pagamento selezionato
        self.importo_totale_noleggio = 0.0 # Per memorizzare l'importo totale calcolato
         # <<< AGGIUNGI QUESTE INIZIALIZZAZIONI MANCANTI >>>
        self.id_noleggio_corrente = None # Questo è l'ID del noleggio corrente nel database
        self.percorso_doc_privacy = None # Questo memorizzerà il percorso del documento privacy stampato
        # <<< FINE AGGIUNTE >>>c
        self.init_ui()

    def init_ui(self):
        layout_main = QVBoxLayout()

        # 📸 Acquisizione e OCR (Group Box)
        group_ocr = QGroupBox("Dati Cliente da Documento")
        layout_ocr = QFormLayout()
        
        self.txt_nome_ocr = QLineEdit()
        self.txt_nome_ocr.setPlaceholderText("Nome (da OCR)")
        layout_ocr.addRow("Nome:", self.txt_nome_ocr)

        self.txt_cognome_ocr = QLineEdit()
        self.txt_cognome_ocr.setPlaceholderText("Cognome (da OCR)")
        layout_ocr.addRow("Cognome:", self.txt_cognome_ocr)

        btn_acquisisci_documento = QPushButton("📷 Acquisisci Documento & OCR")
        btn_acquisisci_documento.clicked.connect(self.acquisisci_documento_da_webcam) # Collegato alla tua funzione esistente
        layout_ocr.addRow(btn_acquisisci_documento)
        group_ocr.setLayout(layout_ocr)
        layout_main.addWidget(group_ocr)
        
        # 📝 Dati Manuali Cliente (Group Box)
        group_manuale = QGroupBox("Dati Cliente Manuali")
        layout_manuale = QFormLayout()
        
        self.txt_nome = QLineEdit()
        self.txt_nome.setPlaceholderText("Nome Cliente")
        self.txt_nome.textChanged.connect(self.verifica_condizioni_avvio) # Aggiunto per abilitazione pulsanti
        layout_manuale.addRow("Nome:", self.txt_nome)

        self.txt_cognome = QLineEdit()
        self.txt_cognome.setPlaceholderText("Cognome Cliente")
        self.txt_cognome.textChanged.connect(self.verifica_condizioni_avvio) # Aggiunto per abilitazione pulsanti
        layout_manuale.addRow("Cognome:", self.txt_cognome)

        group_manuale.setLayout(layout_manuale)
        layout_main.addWidget(group_manuale)

        # 🗓️ Dati Noleggio (Group Box)
        group_noleggio = QGroupBox("Dati Noleggio")
        layout_noleggio = QFormLayout()

        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        layout_noleggio.addRow("Data Noleggio:", self.date_edit)

        self.time_edit = QTimeEdit(QTime.currentTime())
        self.time_edit.setDisplayFormat("HH:mm")
        layout_noleggio.addRow("Ora Noleggio:", self.time_edit)

        self.spin_durata = QSpinBox()
        self.spin_durata.setMinimum(1)
        self.spin_durata.setMaximum(24)
        self.spin_durata.setSuffix(" ore")
        self.spin_durata.valueChanged.connect(self.calcola_importo_totale)
        layout_noleggio.addRow("Durata Noleggio:", self.spin_durata)

        self.cmb_lingua = QComboBox()
        self.cmb_lingua.addItem("Italiano")
        self.cmb_lingua.addItem("English")
        layout_noleggio.addRow("Lingua Ricevuta:", self.cmb_lingua)

        group_noleggio.setLayout(layout_noleggio)
        layout_main.addWidget(group_noleggio)

        # 🛶 Materiali Noleggiati (Group Box)
        group_materiali = QGroupBox("Materiali Noleggiati")
        layout_materiali = QVBoxLayout()
        
        # Layout per input barcode e pulsanti aggiungi/rimuovi
        layout_input_materiale = QHBoxLayout()
        self.txt_barcode = QLineEdit()
        self.txt_barcode.setPlaceholderText("Inserisci o scansiona codice a barre")
        # 🚨 MODIFICA: Limita la larghezza del QLineEdit del barcode
        self.txt_barcode.setFixedWidth(200) # Puoi aggiustare questo valore
        self.txt_barcode.returnPressed.connect(self.aggiungi_materiale_da_barcode) # Ho rinominato la tua funzione
        layout_input_materiale.addWidget(self.txt_barcode)

        btn_seleziona_materiale = QPushButton("➕ Manuale") # 🚨 MODIFICA: Testo del pulsante visibile
        btn_seleziona_materiale.clicked.connect(self.apri_selettore_materiale)
        layout_input_materiale.addWidget(btn_seleziona_materiale)

        btn_rimuovi_materiale = QPushButton("➖ Rimuovi Selezionato")
        btn_rimuovi_materiale.clicked.connect(self.rimuovi_materiale_selezionato) # Ho rinominato la tua funzione
        layout_input_materiale.addWidget(btn_rimuovi_materiale)
        
        layout_input_materiale.addStretch(1) # Spinge i pulsanti a sinistra

        layout_materiali.addLayout(layout_input_materiale) # Aggiunto il layout orizzontale al layout verticale

        # Tabella materiali
        self.tabella_materiali = QTableWidget()
        self.tabella_materiali.setColumnCount(5) 
        self.tabella_materiali.setHorizontalHeaderLabels(["ID", "Codice", "Nome", "Tipo", "Produttore"])
        self.tabella_materiali.setColumnHidden(0, True) 
        self.tabella_materiali.horizontalHeader().setStretchLastSection(True) 
        layout_materiali.addWidget(self.tabella_materiali)

        group_materiali.setLayout(layout_materiali)
        layout_main.addWidget(group_materiali)

        # 💰 Metodo di Pagamento e Totale (Group Box)
        group_pagamento = QGroupBox("Pagamento e Totale") # Ho combinato pagamento e totale in un unico box
        layout_pagamento = QVBoxLayout()

        layout_metodo_pagamento = QHBoxLayout()
        self.btn_paga_contanti = QPushButton("Contanti")
        self.btn_paga_contanti.setCheckable(True)
        self.btn_paga_contanti.clicked.connect(lambda: self.set_metodo_pagamento("Contanti"))
        layout_metodo_pagamento.addWidget(self.btn_paga_contanti)

        self.btn_paga_carta = QPushButton("Carta")
        self.btn_paga_carta.setCheckable(True)
        self.btn_paga_carta.clicked.connect(lambda: self.set_metodo_pagamento("Carta"))
        layout_metodo_pagamento.addWidget(self.btn_paga_carta)

        self.btn_paga_altro = QPushButton("Altro") # Ho rinominato btn_altro a btn_paga_altro per chiarezza
        self.btn_paga_altro.setCheckable(True)
        self.btn_paga_altro.clicked.connect(lambda: self.set_metodo_pagamento("Altro"))
        layout_metodo_pagamento.addWidget(self.btn_paga_altro)
        
        layout_metodo_pagamento.addStretch(1) # Spinge i pulsanti a sinistra

        layout_pagamento.addLayout(layout_metodo_pagamento)

        self.lbl_importo_totale = QLabel("Totale: EUR 0.00")
        self.lbl_importo_totale.setStyleSheet("font-size: 18px; font-weight: bold; color: green;")
        layout_pagamento.addWidget(self.lbl_importo_totale)

        group_pagamento.setLayout(layout_pagamento)
        layout_main.addWidget(group_pagamento)

        # 🖨️ Pulsanti di Azione (Stampa Privacy, Stampa Ricevuta, Avvia Noleggio, Nuovo Noleggio)
        # 🚨 MODIFICA: Creazione del GroupBox per i pulsanti di azione
        group_actions = QGroupBox("Azioni Noleggio") 
        layout_actions = QHBoxLayout()

        self.btn_stampa_privacy = QPushButton("📄 Stampa Privacy")
        self.btn_stampa_privacy.clicked.connect(self.on_click_stampa_privacy)
        layout_actions.addWidget(self.btn_stampa_privacy)

        self.btn_stampa_ricevuta = QPushButton("🧾 Stampa Ricevuta")
        self.btn_stampa_ricevuta.clicked.connect(self.stampa_ricevuta)
        layout_actions.addWidget(self.btn_stampa_ricevuta)
        
        self.btn_avvia = QPushButton("▶️ Avvia Noleggio")
        self.btn_avvia.setEnabled(False) # Inizialmente disabilitato
        self.btn_avvia.clicked.connect(self.lancio_avvio_noleggio) # Ho rinominato la tua funzione
        layout_actions.addWidget(self.btn_avvia)
        
        self.btn_nuovo_noleggio = QPushButton("🔄 Nuovo Noleggio")
        self.btn_nuovo_noleggio.clicked.connect(self.reset_form)
        layout_actions.addWidget(self.btn_nuovo_noleggio)

        layout_actions.addStretch(1) # Spinge i pulsanti a sinistra
        group_actions.setLayout(layout_actions) # Imposta il layout per il GroupBox
        layout_main.addWidget(group_actions) # Aggiungi il GroupBox al layout principale

        self.setLayout(layout_main)
        self.verifica_condizioni_avvio() # Inizializza lo stato dei pulsanti


    # --- METODI DI SUPPORTO ---

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
                timestamp = dt_now.now().strftime("%Y%m%d_%H%M%S") # Usare dt_now
                nome_file = f"documento_{timestamp}.jpg"
                cartella = os.path.join(os.getcwd(), "Documenti_per_noleggio")
                os.makedirs(cartella, exist_ok=True)
                path_completo = os.path.join(cartella, nome_file)
                cv2.imwrite(path_completo, frame)
                QMessageBox.information(self, "Documento acquisito", f"Documento salvato in:\n{path_completo}")
                
                # --- Parte OCR (aggiunta o modificata) ---
                try:
                    # Assicurati che pytesseract sia configurato correttamente
                    # es. pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
                    testo_ocr = pytesseract.image_to_string(path_completo, lang='ita+eng') # Puoi specificare più lingue

                    import re
                    # Espressione regolare più robusta per nomi e cognomi
                    # Cerca due parole che iniziano con maiuscola (potrebbe essere migliorata)
                    match = re.search(r"\b[A-Z][a-zA-ZàèéìòùÀÈÉÌÒÙ'\-]+\s+[A-Z][a-zA-ZàèéìòùÀÈÉÌÒÙ'\-]+\b", testo_ocr)
                    if match:
                        # Potrebbe catturare "Nome Cognome" o "Nome Cognome" su due righe se il documento è fatto così
                        # In questo esempio, assumiamo che trovi la prima occorrenza di due parole maiuscole
                        nome_cognome_trovato = match.group(0).split(' ', 1) # Divide solo sul primo spazio
                        self.txt_nome_ocr.setText(nome_cognome_trovato[0])
                        if len(nome_cognome_trovato) > 1:
                            self.txt_cognome_ocr.setText(nome_cognome_trovato[1])
                        QMessageBox.information(self, "OCR Completato", f"Nome (OCR): {self.txt_nome_ocr.text()}\nCognome (OCR): {self.txt_cognome_ocr.text()}")
                    else:
                        QMessageBox.warning(self, "OCR", "Nome e cognome non rilevati automaticamente. Inserire manualmente.")
                        self.txt_nome_ocr.clear()
                        self.txt_cognome_ocr.clear()

                except Exception as e:
                    QMessageBox.critical(self, "Errore OCR", f"Impossibile eseguire OCR: {e}. Controlla installazione Tesseract.")
                    self.txt_nome_ocr.clear()
                    self.txt_cognome_ocr.clear()
                # --- Fine Parte OCR ---
                
                break

        cap.release()
        cv2.destroyAllWindows()
        self.verifica_condizioni_avvio() # Verifica dopo aver potenzialmente riempito i campi OCR


    def apri_selettore_materiale(self): # Rinominato da inserisci_materiale_manualmente per chiarezza
        dialog = SelezionaMaterialeDisponibile(self)
        if dialog.exec() == QDialog.Accepted:
            materiale_selezionato_dict = dialog.materiale_scelto # Ora ricevi un dizionario completo
            if materiale_selezionato_dict:
                self.aggiungi_materiale_tabella(
                    id_db=materiale_selezionato_dict['id'], # Passa l'ID del DB
                    codice=materiale_selezionato_dict['codice'],
                    nome=materiale_selezionato_dict['nome'],
                    tipo=materiale_selezionato_dict['tipo'], 
                    produttore=materiale_selezionato_dict['produttore'],
                    descrizione=materiale_selezionato_dict.get('descrizione', '') # Usa .get per sicurezza
                )
                self.calcola_importo_totale() 
                self.verifica_condizioni_avvio() 
            else:
                QMessageBox.warning(self, "Materiale", "Nessun materiale selezionato o dettagli non trovati.")


    def aggiungi_materiale_da_barcode(self): # Rinominato da leggi_codice_barre per chiarezza
        codice = self.txt_barcode.text().strip()
        if not codice:
            return
        
        materiale = get_materiale_by_barcode(codice)
        if materiale:
            self.aggiungi_materiale_tabella(
                id_db=materiale['id'], # Passa l'ID del DB
                codice=materiale['codice'],
                nome=materiale['nome'],
                tipo=materiale['tipo'],
                produttore=materiale['produttore'],
                descrizione=materiale.get('descrizione', '')
            )
            self.txt_barcode.clear()
            self.calcola_importo_totale() 
            self.verifica_condizioni_avvio() 
        else:
            QMessageBox.warning(self, "Errore", "Materiale non trovato o già noleggiato!")
        self.txt_barcode.clear()


    def aggiungi_materiale_tabella(self, id_db, codice, nome, tipo, produttore, descrizione):
        for mat_id, _, _, _, _, _ in self.materiali_noleggiati: # Controlla solo l'ID
            if mat_id == id_db: 
                QMessageBox.warning(self, "Duplicato", "Materiale già aggiunto al noleggio.")
                return

        riga = self.tabella_materiali.rowCount()
        self.tabella_materiali.insertRow(riga)
        self.tabella_materiali.setItem(riga, 0, QTableWidgetItem(str(id_db))) # Colonna nascosta per l'ID
        self.tabella_materiali.setItem(riga, 1, QTableWidgetItem(codice))
        self.tabella_materiali.setItem(riga, 2, QTableWidgetItem(nome))
        self.tabella_materiali.setItem(riga, 3, QTableWidgetItem(tipo)) 
        self.tabella_materiali.setItem(riga, 4, QTableWidgetItem(produttore))

        # Assicurati che self.materiali_noleggiati memorizzi la tupla completa
        self.materiali_noleggiati.append((id_db, codice, nome, tipo, produttore, descrizione)) 
        self.tabella_materiali.resizeColumnsToContents()
        self.tabella_materiali.setColumnWidth(4, 150) # Imposta una larghezza per produttore

    def rimuovi_materiale_selezionato(self): # Rinominato da rimuovi_riga_materiale
        riga_selezionata = self.tabella_materiali.currentRow()
        if riga_selezionata >= 0:
            conferma = QMessageBox.question(self, "Rimuovi Materiale", "Sei sicuro di voler rimuovere il materiale selezionato?",
                                             QMessageBox.Yes | QMessageBox.No)
            if conferma == QMessageBox.Yes:
                self.tabella_materiali.removeRow(riga_selezionata)
                del self.materiali_noleggiati[riga_selezionata]
                self.calcola_importo_totale() 
                self.verifica_condizioni_avvio() 
        else:
            QMessageBox.warning(self, "Selezione", "Seleziona un materiale da rimuovere.")


    def calcola_importo_totale(self):
        self.importo_totale_noleggio = 0.0
        if not self.materiali_noleggiati:
            self.lbl_importo_totale.setText("Totale: EUR 0.00")
            self.verifica_condizioni_avvio()
            return

        durata = self.spin_durata.value()
        
        for mat in self.materiali_noleggiati:
            tipo_materiale = mat[3] # Il tipo è l'elemento in posizione 3 della tupla
            prezzo_orario = get_prezzo_orario_by_tipo(tipo_materiale)
            if prezzo_orario is not None:
                self.importo_totale_noleggio += prezzo_orario * durata
            else:
                QMessageBox.warning(self, "Prezzo", f"Prezzo orario non trovato per tipo: {tipo_materiale}")
        
        self.lbl_importo_totale.setText(f"Totale: EUR {self.importo_totale_noleggio:.2f}")
        self.verifica_condizioni_avvio()


    def set_metodo_pagamento(self, metodo):
        self.pagamento_scelto = metodo
        # Gestisci lo stato dei pulsanti checkable
        self.btn_paga_contanti.setChecked(metodo == "Contanti")
        self.btn_paga_carta.setChecked(metodo == "Carta")
        self.btn_paga_altro.setChecked(metodo == "Altro") # Aggiunto il pulsante "Altro"

        self.verifica_condizioni_avvio()


    def verifica_condizioni_avvio(self):
        # Nome e Cognome (da campi manuali o OCR)
        nome_ok = bool(self.txt_nome.text().strip()) or bool(self.txt_nome_ocr.text().strip())
        cognome_ok = bool(self.txt_cognome.text().strip()) or bool(self.txt_cognome_ocr.text().strip())
        
        # Materiali selezionati
        materiali_selezionati = bool(self.materiali_noleggiati)
        
        # Metodo di pagamento selezionato
        metodo_pagamento_selezionato = self.pagamento_scelto is not None

        # Condizioni preliminari per tutte le azioni
        condizioni_minime_ok = (
            nome_ok and
            cognome_ok and
            materiali_selezionati and
            metodo_pagamento_selezionato
        )
        
        # Abilita/Disabilita pulsante "Stampa Privacy"
        # La privacy può essere stampata se ci sono nome e cognome
        self.btn_stampa_privacy.setEnabled(nome_ok and cognome_ok)

        # Abilita/Disabilita pulsante "Stampa Ricevuta"
        # La ricevuta richiede condizioni minime OK E privacy stampata
        self.btn_stampa_ricevuta.setEnabled(condizioni_minime_ok and self.privacy_stampata)

        # Abilita/Disabilita pulsante "Avvia Noleggio"
        # Avvia Noleggio richiede tutte le condizioni minime OK E privacy stampata E ricevuta stampata
        if (condizioni_minime_ok and self.privacy_stampata and self.ricevuta_stampata):
            self.btn_avvia.setEnabled(True)
        else:
            self.btn_avvia.setEnabled(False)


    def on_click_stampa_privacy(self):
        nome = self.txt_nome.text().strip() or self.txt_nome_ocr.text().strip()
        cognome = self.txt_cognome.text().strip() or self.txt_cognome_ocr.text().strip()

        if not nome or not cognome:
            QMessageBox.warning(self, "Dati Mancanti", "Inserisci Nome e Cognome del cliente prima di stampare la Privacy.")
            return

        if self.privacy_stampata:
            QMessageBox.information(self, "Privacy", "La privacy è già stata stampata per questo noleggio.")
            return
        
        lingua = self.cmb_lingua.currentText().strip().lower() # Assicurati che sia in minuscolo per la funzione Utils
        
        path_privacy = stampa_privacy(lingua) 
        
        if path_privacy:
            self.privacy_stampata = True
            self.percorso_doc_privacy = path_privacy #
            QMessageBox.information(self, "Stampa Privacy", f"Documento privacy creato e aperto in:\n{path_privacy}")
            self.verifica_condizioni_avvio() 
        else:
            QMessageBox.critical(self, "Errore Stampa Privacy", "Errore durante la creazione del documento privacy. Controlla i log.")


    def stampa_ricevuta(self):
        if self.ricevuta_stampata:
            QMessageBox.information(self, "Ricevuta", "La ricevuta è già stata stampata per questo noleggio.")
            return

        nome = self.txt_nome.text().strip() or self.txt_nome_ocr.text().strip()
        cognome = self.txt_cognome.text().strip() or self.txt_cognome_ocr.text().strip()
        data_noleggio_per_pdf = self.date_edit.date().toString("dd/MM/yyyy") # Formato per PDF
        data_noleggio_db_format = self.date_edit.date().toString("yyyy-MM-dd") # Formato per il DB
        ora_noleggio = self.time_edit.time().toString("HH:mm")
        durata_ore = self.spin_durata.value()
        metodo_pagamento = self.pagamento_scelto
        lingua = self.cmb_lingua.currentText().strip().lower()

        # Controlli di validazione (li mantengo come i tuoi attuali)
        if not (bool(nome) and bool(cognome) and self.materiali_noleggiati and metodo_pagamento and self.privacy_stampata):
            QMessageBox.warning(self, "Dati Mancanti", "Completa tutti i campi (Nome, Cognome, Materiali, Pagamento) e stampa la Privacy prima di stampare la ricevuta.")
            return

        # <<< PUNTO FONDAMENTALE: CREA IL NOLEGGIO QUI PRIMA DI STAMPARE LA RICEVUTA >>>
        if self.id_noleggio_corrente is None:
            # Assumiamo che self.percorso_doc_privacy sia già disponibile qui
            if not hasattr(self, 'percorso_doc_privacy') or not self.percorso_doc_privacy:
                QMessageBox.critical(self, "Errore", "Percorso del documento privacy non disponibile. Stampa prima la privacy.")
                return

            # Chiamiamo la funzione di data_access per inserire il noleggio principale
            self.id_noleggio_corrente = inserisci_noleggio(
                nome_cliente=nome,
                cognome_cliente=cognome,
                data_noleggio=data_noleggio_db_format,
                ora_noleggio=ora_noleggio,
                durata_ore=durata_ore,
                percorso_documento_privacy=self.percorso_doc_privacy, # Utilizza il tuo percorso esistente
                lingua=lingua,
                metodo_pagamento=metodo_pagamento,
                importo_totale=self.importo_totale_noleggio
            )

            if not self.id_noleggio_corrente:
                QMessageBox.critical(self, "Errore Noleggio", "Impossibile registrare il noleggio nel database.")
                return

            # Inserisci i dettagli del noleggio e aggiorna la disponibilità dei materiali
            for id_db, codice, _, _, _, _ in self.materiali_noleggiati: # Scomponi solo l'ID e il codice
                materiale = get_materiale_by_barcode(codice)
                if materiale:
                    id_materiale = materiale["id"]
                    aggiorna_disponibilita_materiale(id_materiale, 0) # Metti a non disponibile
                    inserisci_dettaglio_noleggio(self.id_noleggio_corrente, id_materiale, codice)
                else:
                    QMessageBox.warning(self, "Materiale mancante", f"Materiale con codice {codice} non trovato. Noleggio parziale.")

        print(f"DEBUG: ID Noleggio corrente (dopo potenziale creazione): {self.id_noleggio_corrente}")

        # Ottieni il prossimo numero di ricevuta (es. "0001/2024")
        numero_ricevuta_per_stampa = get_prossimo_numero_ricevuta() 
        if not numero_ricevuta_per_stampa:
            QMessageBox.critical(self, "Errore Ricevuta", "Impossibile generare il numero di ricevuta.")
            return

        # Ora chiama gestisci_stampa_ricevuta con tutti i parametri, incluso il nuovo id_noleggio_corrente
        # Ho rimosso l'istanza del widget dal primo parametro perché gestisci_stampa_ricevuta
        # nel tuo file (gestione_stampe_ricevute.py) sembra aspettarsi 12 parametri.
        # Se ricevi un errore, potremmo dover rivedere la definizione di gestisci_stampa_ricevuta.
        ricevuta_successo = gestisci_stampa_ricevuta(
            # Questi sono i 12 parametri che gestisci_stampa_ricevuta si aspetta
            # (nome_cliente, cognome_cliente, materiali_noleggiati_list, data_noleggio, ora_noleggio,
            # durata_ore, metodo_pagamento, importo_totale, lingua, id_noleggio_corrente, numero_ricevuta_completo)
            nome_cliente=nome,
            cognome_cliente=cognome,
            materiali_noleggiati_list=self.materiali_noleggiati, 
            data_noleggio=data_noleggio_per_pdf, # Formato DD/MM/YYYY per il PDF
            ora_noleggio=ora_noleggio,
            durata_ore=durata_ore,
            metodo_pagamento=metodo_pagamento,
            importo_totale=self.importo_totale_noleggio,
            lingua=lingua,
            id_noleggio_corrente=self.id_noleggio_corrente,       # <<< PASSA L'ID APPENA CREATO/RECUPERATO
            numero_ricevuta_completo=numero_ricevuta_per_stampa   # <<< PASSA IL NUMERO DI RICEVUTA
        )

        if ricevuta_successo:
            self.ricevuta_stampata = True
            QMessageBox.information(self, "Stampa Ricevuta", "Ricevuta generata e salvata con successo!")
            self.verifica_condizioni_avvio() # Questa funzione ora può abilitare "Avvia Noleggio"
        else:
            QMessageBox.warning(self, "Stampa Ricevuta", "Errore durante la stampa")
            

    # In noleggio_materiale.py, dentro la classe NoleggioMateriale

    def lancio_avvio_noleggio(self):
        # Questa funzione dovrebbe essere chiamata solo DOPO che privacy e ricevuta sono stampate.
        # E il noleggio dovrebbe avere già un ID.

        if self.id_noleggio_corrente is None or not self.ricevuta_stampata or not self.privacy_stampata:
            QMessageBox.critical(self, "Errore", "Assicurati che tutti i dati siano completi, la privacy stampata, e la ricevuta generata prima di finalizzare il noleggio.")
            return

        # Chiama la nuova funzione per finalizzare il noleggio
        successo_finalizzazione = finalizza_noleggio(self.id_noleggio_corrente) 

        if successo_finalizzazione:
            QMessageBox.information(self, "Noleggio Avviato", f"Noleggio {self.id_noleggio_corrente} finalizzato con successo!")
            self.reset_form() # Resetta il form solo dopo aver finalizzato il noleggio
        else:
            QMessageBox.critical(self, "Errore Finalizzazione", f"Impossibile finalizzare il noleggio {self.id_noleggio_corrente}.")


    def reset_form(self):
        self.txt_nome_ocr.clear()
        self.txt_cognome_ocr.clear()
        self.txt_nome.clear()
        self.txt_cognome.clear()
        self.txt_barcode.clear()
        
        self.date_edit.setDate(QDate.currentDate())
        self.time_edit.setTime(QTime.currentTime())
        
        self.spin_durata.setValue(1)
        
        self.tabella_materiali.setRowCount(0)
        self.materiali_noleggiati.clear()

        self.privacy_stampata = False
        self.ricevuta_stampata = False

        self.pagamento_scelto = None
        self.btn_paga_contanti.setChecked(False)
        self.btn_paga_carta.setChecked(False)
        self.btn_paga_altro.setChecked(False) # Resetta anche il pulsante "Altro"
        
        self.importo_totale_noleggio = 0.0
        self.lbl_importo_totale.setText("Totale: EUR 0.00")

        self.verifica_condizioni_avvio()
        
        QMessageBox.information(self, "Reset", "Modulo noleggio resettato. Pronto per un nuovo noleggio.")