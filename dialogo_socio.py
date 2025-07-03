# dialogo_socio.py
# dialogo_socio.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QLabel, QPushButton, QComboBox, QSpinBox, QDateEdit,
    QFileDialog, QMessageBox, QWidget, QScrollArea
)
from PySide6.QtCore import Qt, QDate, QLocale, QBuffer, QIODevice
from PySide6.QtGui import QPixmap, QDoubleValidator

# Importa le funzioni dai tuoi moduli esistenti
from data_access import insert_socio_esteso, update_socio_esteso, get_socio_by_id, get_socio_photo_blob
from codice_fiscale_utils import calcola_codice_fiscale # CORREZIONE QUI: Usa il nome corretto della funzione
class DialogoSocio(QDialog):
    def __init__(self,socio_id=None, parent=None): # <-- MODIFICA QUI: Aggiungi 'db_path'
        super().__init__(parent)
        #self.db_path = db_path # <-- AGGIUNGI QUI: Salva il db_path come variabile della classe
        self.socio_id = socio_id
        self.socio_data = None
        self.photo_blob = None

        self.setWindowTitle("Aggiungi Nuovo Socio" if socio_id is None else "Modifica Socio Esistente")
        self.setMinimumSize(800, 700) # Dimensioni minime per una buona leggibilità

        self.inputs = {} # Dizionario per contenere i riferimenti a tutti i widget di input
        self.current_photo_path = None # Percorso temporaneo della foto caricata

        self.init_ui()

        # Se in modalità modifica, carica i dati del socio

        if self.socio_id:
    
            self.socio_data = get_socio_by_id(self.socio_id)
            if self.socio_data:
                self.populate_form()
            else:
                QMessageBox.warning(self, "Errore", f"Socio con ID {self.socio_id} non trovato.")
                self.reject() # Chiude il dialogo se il socio non esiste


    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30) # Margini esterni
        main_layout.setSpacing(20) # Spazio tra i blocchi principali

        # Stili CSS globali per il dialogo, applicati a tutti i widget figli
        self.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 5px;
            }
            QLineEdit, QComboBox, QDateEdit, QSpinBox {
                font-size: 18px;
                padding: 8px;
                border: 1px solid #BDC3C7;
                border-radius: 5px;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QSpinBox:focus {
                border: 2px solid #3498DB;
            }
            QPushButton {
                font-size: 16px;
                padding: 10px 20px;
                border-radius: 5px;
                background-color: #3498DB;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
            QPushButton:pressed {
                background-color: #21618C;
            }
        """)

        # Titolo del dialogo
        title_label = QLabel("Inserisci i Dati del Nuovo Socio" if self.socio_id is None else "Modifica Socio Esistente")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 28px; font-weight: bold; margin-bottom: 20px; color: #34495E;")
        main_layout.addWidget(title_label)

        # Area scrollabile per contenere il form (essenziale per form lunghi)
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_content_widget = QWidget()
        form_layout = QFormLayout(scroll_content_widget)
        form_layout.setContentsMargins(10, 10, 10, 10) # Margini interni del form
        form_layout.setVerticalSpacing(15) # Spazio verticale tra le righe del form
        form_layout.setHorizontalSpacing(20) # Spazio orizzontale tra label e campo

        # --- Funzione helper per la creazione centralizzata dei campi di input ---
        def create_input_field(placeholder="", validator=None, default_value=None, field_type="QLineEdit", items_list=None):
            widget = None
            if field_type == "QLineEdit":
                widget = QLineEdit()
                widget.setPlaceholderText(placeholder)
                if validator:
                    widget.setValidator(validator)
                if default_value is not None:
                    widget.setText(str(default_value))
            elif field_type == "QComboBox":
                widget = QComboBox()
                if items_list:
                    widget.addItems(items_list)
                if default_value is not None:
                    widget.setCurrentText(str(default_value))
            elif field_type == "QDateEdit":
                widget = QDateEdit()
                widget.setCalendarPopup(True)
                widget.setDisplayFormat("dd/MM/yyyy")
                widget.setDate(QDate.currentDate())
                if default_value and QDate.fromString(str(default_value), Qt.ISODate).isValid():
                    widget.setDate(QDate.fromString(str(default_value), Qt.ISODate))
            elif field_type == "QSpinBox":
                widget = QSpinBox()
                widget.setRange(1900, QDate.currentDate().year() + 5)
                widget.setValue(QDate.currentDate().year())
                if default_value is not None:
                    widget.setValue(int(default_value))
            return widget

        # --- Creazione e aggiunta dei campi di input al QFormLayout ---
        self.inputs["nome"] = create_input_field("Inserisci il nome")
        form_layout.addRow("Nome:", self.inputs["nome"])
        
        self.inputs["cognome"] = create_input_field("Inserisci il cognome")
        form_layout.addRow("Cognome:", self.inputs["cognome"])

        self.inputs["data_nascita"] = create_input_field(field_type="QDateEdit")
        form_layout.addRow("Data di Nascita:", self.inputs["data_nascita"])
        
        self.inputs["luogo_nascita"] = create_input_field("Città di nascita")
        form_layout.addRow("Luogo di Nascita:", self.inputs["luogo_nascita"])

        self.inputs["sesso"] = create_input_field(field_type="QComboBox", items_list=["", "M", "F", "Altro"])
        form_layout.addRow("Sesso:", self.inputs["sesso"])

        cf_layout = QHBoxLayout()
        self.inputs["codice_fiscale"] = create_input_field("Sarà calcolato o inserito")
        self.inputs["codice_fiscale"].setInputMask("AAAAAA99A99A999A999A")
        
        self.btn_calcola_cf = QPushButton("Calcola CF")
        self.btn_modifica_cf = QPushButton("Modifica CF")
        
        cf_layout.addWidget(self.inputs["codice_fiscale"])
        cf_layout.addWidget(self.btn_calcola_cf)
        cf_layout.addWidget(self.btn_modifica_cf)
        form_layout.addRow("Codice Fiscale:", cf_layout)

        self.inputs["indirizzo"] = create_input_field("Via, numero civico")
        form_layout.addRow("Indirizzo:", self.inputs["indirizzo"])

        self.inputs["cap"] = create_input_field("CAP")
        form_layout.addRow("CAP:", self.inputs["cap"])

        self.inputs["citta"] = create_input_field("Città di residenza")
        form_layout.addRow("Città:", self.inputs["citta"])

        self.inputs["provincia"] = create_input_field("Provincia (Sigla)")
        form_layout.addRow("Provincia:", self.inputs["provincia"])

        self.inputs["nazione"] = create_input_field("Nazione", default_value="Italia")
        form_layout.addRow("Nazione:", self.inputs["nazione"])
        
        self.inputs["email"] = create_input_field("indirizzo@esempio.com")
        form_layout.addRow("Email:", self.inputs["email"])

        self.inputs["telefono"] = create_input_field("Es. +39 123 4567890")
        form_layout.addRow("Telefono:", self.inputs["telefono"])

        self.inputs["anno"] = create_input_field(field_type="QSpinBox")
        self.inputs["anno"].setRange(2000, QDate.currentDate().year() + 5)
        form_layout.addRow("Anno di Iscrizione:", self.inputs["anno"])

        self.inputs["quota_pagata"] = create_input_field(field_type="QComboBox", items_list=["No", "Sì"])
        form_layout.addRow("Quota Pagata:", self.inputs["quota_pagata"])
        
        quota_validator = QDoubleValidator(0.00, 99999.99, 2, self)
        quota_validator.setLocale(QLocale(QLocale.Italian, QLocale.Italy))
        self.inputs["quota_associazione"] = create_input_field("Es. 50,00", validator=quota_validator)
        form_layout.addRow("Quota Associazione (€):", self.inputs["quota_associazione"])

        self.inputs["tipo_tesseramento"] = create_input_field("Es. FIV / UISP")
        form_layout.addRow("Tipo Tesseramento:", self.inputs["tipo_tesseramento"])

        self.inputs["numero_tessera"] = create_input_field("Numero della tessera")
        form_layout.addRow("Numero Tessera:", self.inputs["numero_tessera"])

        self.inputs["data_emissione"] = create_input_field(field_type="QDateEdit")
        form_layout.addRow("Data Emissione:", self.inputs["data_emissione"])

        self.inputs["data_scadenza"] = create_input_field(field_type="QDateEdit")
        form_layout.addRow("Data Scadenza:", self.inputs["data_scadenza"])

        # Gestione Foto
        photo_layout = QHBoxLayout()
        self.photo_label = QLabel("Nessuna foto")
        self.photo_label.setFixedSize(150, 150)
        self.photo_label.setStyleSheet("border: 1px solid #BDC3C7; background-color: #ECF0F1; text-align: center;")
        self.photo_label.setAlignment(Qt.AlignCenter)
        
        photo_buttons_layout = QVBoxLayout()
        self.btn_carica_foto = QPushButton("Carica Foto")
        self.btn_rimuovi_foto = QPushButton("Rimuovi Foto")
        
        photo_buttons_layout.addWidget(self.btn_carica_foto)
        photo_buttons_layout.addWidget(self.btn_rimuovi_foto)
        photo_buttons_layout.addStretch(1)

        photo_layout.addWidget(self.photo_label)
        photo_layout.addLayout(photo_buttons_layout)
        form_layout.addRow("Foto:", photo_layout)

        # Aggiungi l'area scorrevole al layout principale del dialogo
        scroll_area.setWidget(scroll_content_widget)
        main_layout.addWidget(scroll_area)

        # Pulsanti OK e Cancel
        buttons_layout = QHBoxLayout()
        self.btn_cancel = QPushButton("Cancel")
        self.btn_ok = QPushButton("OK")

        buttons_layout.addStretch(1)
        buttons_layout.addWidget(self.btn_cancel)
        buttons_layout.addWidget(self.btn_ok)
        buttons_layout.addStretch(1)
        main_layout.addLayout(buttons_layout)

        # Connessioni dei segnali ai rispettivi metodi
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_ok.clicked.connect(self.save_socio)
        self.btn_carica_foto.clicked.connect(self.carica_foto)
        self.btn_rimuovi_foto.clicked.connect(self.rimuovi_foto)
        self.btn_calcola_cf.clicked.connect(self.calcola_codice_fiscale_completo)

        # Connessioni per l'aggiornamento automatico dello stato del pulsante CF
        self.inputs["data_nascita"].dateChanged.connect(self.aggiorna_cf_automatico)
        self.inputs["luogo_nascita"].textChanged.connect(self.aggiorna_cf_automatico)
        self.inputs["sesso"].currentTextChanged.connect(self.aggiorna_cf_automatico)

    def get_socio_data(self):
        """Raccoglie i dati inseriti nei campi del form."""
        data = {
            "nome": self.inputs["nome"].text().strip(),
            "cognome": self.inputs["cognome"].text().strip(),
            "sesso": self.inputs["sesso"].currentText().strip(),
            "data_nascita": self.inputs["data_nascita"].date().toString("yyyy-MM-dd"),
            "luogo_nascita": self.inputs["luogo_nascita"].text().strip(),
            "codice_fiscale": self.inputs["codice_fiscale"].text().strip().upper(),
            "indirizzo": self.inputs["indirizzo"].text().strip(),
            "cap": self.inputs["cap"].text().strip(),
            "citta": self.inputs["citta"].text().strip(),
            "provincia": self.inputs["provincia"].text().strip().upper(),
            "nazione": self.inputs["nazione"].text().strip(),
            "telefono": self.inputs["telefono"].text().strip(),
            "email": self.inputs["email"].text().strip(),
            "anno": self.inputs["anno"].value(),
            "quota_pagata": 1 if self.inputs["quota_pagata"].currentText() == "Sì" else 0,
            "quota_associazione": float(self.inputs["quota_associazione"].text().replace(',', '.') or 0.00), # Sostituisce virgola con punto
            "tipo_tesseramento": self.inputs["tipo_tesseramento"].text().strip(),
            "numero_tessera": self.inputs["numero_tessera"].text().strip(),
            "data_emissione": self.inputs["data_emissione"].date().toString("yyyy-MM-dd"),
            "data_scadenza": self.inputs["data_scadenza"].date().toString("yyyy-MM-dd"),
            "foto_blob": self.photo_blob, # <--- AGGIUNGI QUESTA RIGA!
            "attivo": 1 # Per ora, assumiamo che i nuovi soci siano attivi
        }
        return data

    def populate_form(self):
        """Popola il form con i dati del socio esistente."""
        if not self.socio_data:
            return

        for key, widget in self.inputs.items():
            value = self.socio_data.get(key)
            if value is None:
                continue

            if isinstance(widget, QLineEdit):
                widget.setText(str(value))
            elif isinstance(widget, QComboBox):
                # Gestione speciale per 'quota_pagata' se il valore è 0 o 1 dal DB
                if key == "quota_pagata":
                    display_text = "Sì" if value == 1 else "No"
                    index = widget.findText(display_text)
                    if index != -1:
                        widget.setCurrentIndex(index)
                else: # Per tutti gli altri QComboBox
                    index = widget.findText(str(value))
                    if index != -1:
                        widget.setCurrentIndex(index)
            elif isinstance(widget, QDateEdit):
                # Gestisce date valide e ignora date nulle/non valide come "0000-00-00"
                if isinstance(value, str) and value and value != "0000-00-00":
                    date = QDate.fromString(value, Qt.ISODate)
                    if date.isValid():
                        widget.setDate(date)
            elif isinstance(widget, QSpinBox):
                widget.setValue(int(value))

        # Popola la foto se presente
                # Popola la foto se presente
        print(f"DEBUG (Popola Foto): Tentativo di recuperare foto per socio_id: {self.socio_id}")
        photo_blob = get_socio_photo_blob(self.socio_id)
        if photo_blob:
            pixmap = QPixmap()
            pixmap.loadFromData(photo_blob)
            print(f"DEBUG (Popola Foto): photo_blob recuperato. Dimensione: {len(photo_blob)} bytes.")
            # Scala la foto per adattarla al QLabel, mantenendo le proporzioni
            self.photo_label.setPixmap(pixmap.scaled(self.photo_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.photo_blob = photo_blob # Memorizza per un potenziale ri-salvataggio

    def save_socio(self):
        """Salva o aggiorna i dati del socio nel database."""
        socio_data = self.get_socio_data()

        # Aggiungi i dati della foto al dizionario socio_data
        socio_data["foto"] = self.photo_blob

        # Validazione minima per campi obbligatori
        if not socio_data["nome"] or not socio_data["cognome"] or not socio_data["email"]:
            QMessageBox.warning(self, "Errore di Validazione", "Nome, Cognome ed Email sono campi obbligatori.")
            return

        try:
            if self.socio_id:
                # Aggiorna socio esistente
                update_socio_esteso(self.socio_id, socio_data)
                QMessageBox.information(self, "Successo", "Socio aggiornato con successo!")
            else:
                # Inserisci nuovo socio
                insert_socio_esteso(socio_data)
                QMessageBox.information(self, "Successo", "Nuovo socio aggiunto con successo!")
            self.accept() # Chiude il dialogo con stato "Accepted"
        except Exception as e:
            QMessageBox.critical(self, "Errore Database", f"Si è verificato un errore durante il salvataggio: {e}")

    def carica_foto(self):
        """Permette all'utente di caricare una foto."""
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Immagini (*.png *.jpg *.jpeg *.bmp *.gif)")
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.current_photo_path = selected_files[0]
                pixmap = QPixmap(self.current_photo_path)
                if not pixmap.isNull():
                    self.photo_label.setPixmap(pixmap.scaled(self.photo_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    
                    # Converte l'immagine in BLOB per il salvataggio nel DB
                    buffer = QBuffer()
                    buffer.open(QIODevice.WriteOnly)
                    pixmap.save(buffer, "PNG") # Salva come PNG per mantenere trasparenza se presente
                    self.photo_blob = buffer.data() # Ottieni i dati binari
                    buffer.close()
                else:
                    QMessageBox.warning(self, "Errore Foto", "Impossibile caricare l'immagine. Assicurati sia un formato immagine valido.")

    def rimuovi_foto(self):
        """Rimuove la foto dal QLabel e resetta il BLOB."""
        self.photo_label.clear()
        self.photo_label.setText("Nessuna foto")
        self.photo_blob = None
        self.current_photo_path = None # Resetta il percorso

    def calcola_codice_fiscale_completo(self):
        """Calcola il codice fiscale usando i dati del form e lo imposta nel campo."""
        nome = self.inputs["nome"].text().strip()
        cognome = self.inputs["cognome"].text().strip()
        data_nascita_qdate = self.inputs["data_nascita"].date()
        data_nascita_str = data_nascita_qdate.toString("dd/MM/yyyy") # Formato per la funzione CF
        luogo_nascita = self.inputs["luogo_nascita"].text().strip()
        sesso = self.inputs["sesso"].currentText().strip()

        if not (nome and cognome and data_nascita_qdate.isValid() and luogo_nascita and sesso):
            QMessageBox.warning(self, "Dati Mancanti", "Per calcolare il Codice Fiscale sono necessari: Nome, Cognome, Data di Nascita, Luogo di Nascita e Sesso.")
            return

        try:
            # Chiama la funzione esterna per il calcolo del codice fiscale
    
            cf = calcola_codice_fiscale(nome, cognome, data_nascita_str, sesso, luogo_nascita) # <--- MODIFICATO
            print(f"DEBUG (Calcolo CF): Codice Fiscale calcolato: {cf}")
            self.inputs["codice_fiscale"].setText(cf.upper())
        except Exception as e:
            QMessageBox.critical(self, "Errore Calcolo CF", f"Impossibile calcolare il Codice Fiscale: {e}. Controlla i dati inseriti.")

    def aggiorna_cf_automatico(self):
        """Metodo per aggiornare lo stato del pulsante 'Calcola CF' in base ai campi obbligatori."""
        nome = self.inputs["nome"].text().strip()
        cognome = self.inputs["cognome"].text().strip()
        data_nascita_qdate = self.inputs["data_nascita"].date()
        luogo_nascita = self.inputs["luogo_nascita"].text().strip()
        sesso = self.inputs["sesso"].currentText().strip()

        # Abilita il pulsante solo se tutti i campi necessari per il calcolo CF sono compilati
        if nome and cognome and data_nascita_qdate.isValid() and luogo_nascita and sesso:
            self.btn_calcola_cf.setEnabled(True)
        else:
            self.btn_calcola_cf.setEnabled(False)

# Non ci deve essere nessun codice sotto questa riga per evitare problemi di esecuzione diretta
# quando il file è importato come modulo.
