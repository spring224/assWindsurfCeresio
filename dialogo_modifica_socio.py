# dialogo_modifica_socio.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QFormLayout, QDialogButtonBox, QMessageBox, QComboBox,
    QSpinBox, QDateEdit, QPushButton, QFileDialog, QSizePolicy
)
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt, QDate
import os
import shutil # Per copiare le immagini
from pathlib import Path
from io import BytesIO

# Importa le funzioni di accesso ai dati
from data_access import insert_socio_esteso, update_socio_esteso, get_socio_photo_blob
from codice_fiscale_utils import calcola_codice_fiscale

# Configurazione per le foto
FOTO_SOCI_DIR = "foto_soci"
if not os.path.exists(FOTO_SOCI_DIR):
    os.makedirs(FOTO_SOCI_DIR)

class DialogoModificaSoci(QDialog):
    def __init__(self, socio_data=None, parent=None):
        super().__init__(parent)
        self.socio_data = socio_data # Dizionario con i dati del socio da modificare (o None per nuovo)
        self.photo_path = None # Percorso temporaneo della foto selezionata
        self.original_photo_filename = None # Nome file foto originale se presente

        if self.socio_data:
            self.setWindowTitle("Modifica Socio Esistente")
            # Se c'è un socio, salva il nome del file della foto esistente
            self.original_photo_filename = self.socio_data.get('nome_file_foto')
        else:
            self.setWindowTitle("Aggiungi Nuovo Socio")

        self.init_ui()
        if self.socio_data:
            self.popola_campi() # Popola i campi se stiamo modificando

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # Campi di input
        self.nome_input = QLineEdit()
        self.cognome_input = QLineEdit()
        self.data_nascita_input = QDateEdit(calendarPopup=True)
        self.data_nascita_input.setDisplayFormat("dd/MM/yyyy")
        self.luogo_nascita_input = QLineEdit()
        self.sesso_input = QComboBox()
        self.sesso_input.addItems(["M", "F", "Altro"])
        self.codice_fiscale_input = QLineEdit()
        self.indirizzo_input = QLineEdit()
        self.cap_input = QLineEdit()
        self.citta_input = QLineEdit()
        self.provincia_input = QLineEdit()
        self.nazione_input = QLineEdit()
        self.email_input = QLineEdit()
        self.telefono_input = QLineEdit()
        self.anno_iscrizione_input = QSpinBox()
        self.anno_iscrizione_input.setRange(2000, QDate.currentDate().year() + 1)
        self.anno_iscrizione_input.setValue(QDate.currentDate().year())
        self.tipo_tesseramento_input = QLineEdit()
        self.numero_tessera_input = QLineEdit()
        self.data_emissione_input = QDateEdit(calendarPopup=True)
        self.data_emissione_input.setDisplayFormat("dd/MM/yyyy")
        self.data_emissione_input.setDate(QDate.currentDate())
        self.data_scadenza_input = QDateEdit(calendarPopup=True)
        self.data_scadenza_input.setDisplayFormat("dd/MM/yyyy")
        self.data_scadenza_input.setDate(QDate.currentDate().addYears(1)) # Scadenza predefinita 1 anno

        # Bottone per calcolare il Codice Fiscale
        cf_layout = QHBoxLayout()
        cf_layout.addWidget(self.codice_fiscale_input)
        self.btn_calcola_cf = QPushButton("Calcola CF")
        self.btn_calcola_cf.clicked.connect(self.calcola_codice_fiscale_from_fields)
        cf_layout.addWidget(self.btn_calcola_cf)

        # Campi e bottoni per la foto
        self.foto_label = QLabel("Nessuna foto")
        self.foto_label.setFixedSize(150, 150) # Dimensione fissa per la foto
        self.foto_label.setAlignment(Qt.AlignCenter)
        self.foto_label.setStyleSheet("border: 1px solid gray; background-color: #f0f0f0;")

        foto_buttons_layout = QVBoxLayout()
        self.btn_carica_foto = QPushButton("Carica Foto")
        self.btn_carica_foto.clicked.connect(self.seleziona_foto)
        self.btn_rimuovi_foto = QPushButton("Rimuovi Foto")
        self.btn_rimuovi_foto.clicked.connect(self.rimuovi_foto)
        foto_buttons_layout.addWidget(self.btn_carica_foto)
        foto_buttons_layout.addWidget(self.btn_rimuovi_foto)
        foto_buttons_layout.addStretch(1) # Spazio per spingere i bottoni in alto

        foto_section_layout = QHBoxLayout()
        foto_section_layout.addWidget(self.foto_label)
        foto_section_layout.addLayout(foto_buttons_layout)
        foto_section_layout.addStretch(1) # Spaziatore a destra della foto per centrarla se la finestra è larga

        # Aggiungi i campi al Form Layout
        form_layout.addRow("Nome:", self.nome_input)
        form_layout.addRow("Cognome:", self.cognome_input)
        form_layout.addRow("Data di Nascita:", self.data_nascita_input)
        form_layout.addRow("Luogo di Nascita:", self.luogo_nascita_input)
        form_layout.addRow("Sesso:", self.sesso_input)
        form_layout.addRow("Codice Fiscale:", cf_layout) # Layout per CF e bottone
        form_layout.addRow("Indirizzo:", self.indirizzo_input)
        form_layout.addRow("CAP:", self.cap_input)
        form_layout.addRow("Città:", self.citta_input)
        form_layout.addRow("Provincia:", self.provincia_input)
        form_layout.addRow("Nazione:", self.nazione_input)
        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("Telefono:", self.telefono_input)
        form_layout.addRow("Anno Iscrizione:", self.anno_iscrizione_input)
        form_layout.addRow("Tipo Tesseramento:", self.tipo_tesseramento_input)
        form_layout.addRow("Numero Tessera:", self.numero_tessera_input)
        form_layout.addRow("Data Emissione:", self.data_emissione_input)
        form_layout.addRow("Data Scadenza:", self.data_scadenza_input)
        form_layout.addRow("Foto:", foto_section_layout) # Sezione per la foto

        main_layout.addLayout(form_layout)

        # Bottoni OK e Annulla
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        buttons.accepted.connect(self.accept) # Chiude il dialogo con Accepted
        buttons.rejected.connect(self.reject) # Chiude il dialogo con Rejected
        main_layout.addWidget(buttons)

    def popola_campi(self):
        if not self.socio_data:
            return

        # Applica str() a tutti i valori recuperati per i QLineEdit
        self.nome_input.setText(str(self.socio_data.get('nome', '')))
        self.cognome_input.setText(str(self.socio_data.get('cognome', '')))
        
        # Gestione della data di nascita (già gestita correttamente)
        data_nascita_str = self.socio_data.get('data_nascita')
        if data_nascita_str:
            q_date = QDate.fromString(str(data_nascita_str), "yyyy-MM-dd") # Anche qui, sicurezza con str()
            if q_date.isValid():
                self.data_nascita_input.setDate(q_date)

        self.luogo_nascita_input.setText(str(self.socio_data.get('luogo_nascita', '')))
        
        sesso = str(self.socio_data.get('sesso', '')) # Assicurati che sesso sia una stringa
        index = self.sesso_input.findText(sesso)
        if index != -1:
            self.sesso_input.setCurrentIndex(index)
            
        self.codice_fiscale_input.setText(str(self.socio_data.get('codice_fiscale', '')))
        self.indirizzo_input.setText(str(self.socio_data.get('indirizzo', '')))
        self.cap_input.setText(str(self.socio_data.get('cap', '')))
        self.citta_input.setText(str(self.socio_data.get('citta', '')))
        self.provincia_input.setText(str(self.socio_data.get('provincia', '')))
        self.nazione_input.setText(str(self.socio_data.get('nazione', '')))
        self.email_input.setText(str(self.socio_data.get('email', '')))
        self.telefono_input.setText(str(self.socio_data.get('telefono', '')))
        
        # QSpinBox accetta int, quindi non serve str() qui
        self.anno_iscrizione_input.setValue(self.socio_data.get('anno_iscrizione', QDate.currentDate().year()))
        
        self.tipo_tesseramento_input.setText(str(self.socio_data.get('tipo_tesseramento', '')))
        self.numero_tessera_input.setText(str(self.socio_data.get('numero_tessera', '')))

        # Gestione delle date di emissione e scadenza (già gestite correttamente)
        data_emissione_str = self.socio_data.get('data_emissione_tessera')
        if data_emissione_str:
            q_date = QDate.fromString(str(data_emissione_str), "yyyy-MM-dd") # Sicurezza con str()
            if q_date.isValid():
                self.data_emissione_input.setDate(q_date)

        data_scadenza_str = self.socio_data.get('data_scadenza_tessera')
        if data_scadenza_str:
            q_date = QDate.fromString(str(data_scadenza_str), "yyyy-MM-dd") # Sicurezza con str()
            if q_date.isValid():
                self.data_scadenza_input.setDate(q_date)

        # Carica la foto se esiste (questa parte dovrebbe essere già corretta)
        if self.original_photo_filename:
            photo_blob = get_socio_photo_blob(self.socio_data.get('id'))
            if photo_blob:
                pixmap = QPixmap()
                pixmap.loadFromData(photo_blob)
                self.foto_label.setPixmap(pixmap.scaled(self.foto_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                self.foto_label.setText("Foto non trovata")


    def calcola_codice_fiscale_from_fields(self):
        nome = self.nome_input.text()
        cognome = self.cognome_input.text()
        data_nascita_str = self.data_nascita_input.date().toString("dd/MM/yyyy")
        luogo_nascita = self.luogo_nascita_input.text()
        sesso = self.sesso_input.currentText()

        try:
            cf = calcola_codice_fiscale(cognome, nome, data_nascita_str, sesso, luogo_nascita)
            self.codice_fiscale_input.setText(cf)
        except ValueError as e:
            QMessageBox.warning(self, "Errore Codice Fiscale", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Si è verificato un errore inatteso: {e}")

    def seleziona_foto(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleziona Foto", "", "Immagini (*.png *.jpg *.jpeg *.bmp *.gif)")
        if file_path:
            self.photo_path = file_path # Memorizza il percorso temporaneo
            pixmap = QPixmap(file_path)
            self.foto_label.setPixmap(pixmap.scaled(self.foto_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def rimuovi_foto(self):
        self.photo_path = "REMOVE" # Imposta un flag speciale per indicare la rimozione
        self.foto_label.setText("Nessuna foto")
        self.foto_label.clear() # Rimuove l'immagine

    def accept(self):
        # Questo metodo viene chiamato quando l'utente clicca OK
        socio_data_to_save = self.ottieni_dati_input()

        if not socio_data_to_save: # Se ottieni_dati_input ha riscontrato un errore
            return # Non chiudere il dialogo

        # Gestione della foto: copia il file temporaneo nella cartella permanente
        if self.photo_path and self.photo_path != "REMOVE":
            # Genera un nome file univoco, per evitare sovrascritture
            photo_filename = f"socio_{socio_data_to_save['codice_fiscale']}_{self.cognome_input.text()}.jpg"
            final_photo_path = os.path.join(FOTO_SOCI_DIR, photo_filename)
            try:
                shutil.copy(self.photo_path, final_photo_path)
                socio_data_to_save['nome_file_foto'] = photo_filename
            except Exception as e:
                QMessageBox.warning(self, "Errore Foto", f"Impossibile salvare la foto: {e}")
                socio_data_to_save['nome_file_foto'] = None # Non salvare il percorso se c'è stato un errore
        elif self.photo_path == "REMOVE":
            socio_data_to_save['nome_file_foto'] = "REMOVE" # Flag per la rimozione nel DB
        elif self.original_photo_filename:
            # Se non è stata selezionata una nuova foto e non è stata richiesta la rimozione,
            # mantiene il nome del file della foto originale (se presente)
            socio_data_to_save['nome_file_foto'] = self.original_photo_filename
        else:
            socio_data_to_save['nome_file_foto'] = None # Nessuna foto

        if self.socio_data: # Se stiamo modificando un socio esistente
            socio_data_to_save['id'] = self.socio_data.get('id') # Aggiungi l'ID per l'update
            success = update_socio_esteso(socio_data_to_save)
            if success:
                QMessageBox.information(self, "Successo", "Socio modificato con successo!")
                super().accept() # Chiude il dialogo solo se l'operazione ha successo
            else:
                QMessageBox.critical(self, "Errore", "Errore nella modifica del socio.")
        else: # Se stiamo aggiungendo un nuovo socio
            success = update_socio_esteso(socio_id=socio_data_to_save['id'], dati=socio_data_to_save)
            if success:
                QMessageBox.information(self, "Successo", "Socio aggiunto con successo!")
                super().accept() # Chiude il dialogo
            else:
                QMessageBox.critical(self, "Errore", "Errore nell'aggiunta del socio. Controlla il log.")

    def ottieni_dati_input(self):
        # Recupera tutti i dati dai campi del form
        nome = self.nome_input.text().strip()
        cognome = self.cognome_input.text().strip()
        data_nascita = self.data_nascita_input.date().toString("yyyy-MM-dd")
        luogo_nascita = self.luogo_nascita_input.text().strip()
        sesso = self.sesso_input.currentText().strip()
        codice_fiscale = self.codice_fiscale_input.text().strip().upper()
        indirizzo = self.indirizzo_input.text().strip()
        cap = self.cap_input.text().strip()
        citta = self.citta_input.text().strip()
        provincia = self.provincia_input.text().strip()
        nazione = self.nazione_input.text().strip()
        email = self.email_input.text().strip()
        telefono = self.telefono_input.text().strip()
        anno_iscrizione = self.anno_iscrizione_input.value()
        tipo_tesseramento = self.tipo_tesseramento_input.text().strip()
        numero_tessera = self.numero_tessera_input.text().strip()
        data_emissione_tessera = self.data_emissione_input.date().toString("yyyy-MM-dd")
        data_scadenza_tessera = self.data_scadenza_input.date().toString("yyyy-MM-dd")

        # Validazione minima dei campi obbligatori
        if not nome or not cognome or not data_nascita or not codice_fiscale:
            QMessageBox.warning(self, "Campi Obbligatori", "Nome, Cognome, Data di Nascita e Codice Fiscale sono obbligatori.")
            return None # Indica che la validazione è fallita

        # Crea il dizionario dei dati del socio
        socio_data = {
            'nome': nome,
            'cognome': cognome,
            'data_nascita': data_nascita,
            'luogo_nascita': luogo_nascita,
            'sesso': sesso,
            'codice_fiscale': codice_fiscale,
            'indirizzo': indirizzo,
            'cap': cap,
            'citta': citta,
            'provincia': provincia,
            'nazione': nazione,
            'email': email,
            'telefono': telefono,
            'anno_iscrizione': anno_iscrizione,
            'tipo_tesseramento': tipo_tesseramento,
            'numero_tessera': numero_tessera,
            'data_emissione_tessera': data_emissione_tessera,
            'data_scadenza_tessera': data_scadenza_tessera,
            'quota_pagata': self.socio_data.get('quota_pagata', 0) if self.socio_data else 0, # Mantiene lo stato esistente o 0 per nuovo
            'attivo': self.socio_data.get('attivo', 1) if self.socio_data else 1 # Mantiene lo stato esistente o 1 per nuovo
        }
        return socio_data


# Blocco per testare il dialogo di modifica/aggiunta individualmente (opzionale)
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    # Simula un socio esistente per testare la modifica
    test_socio_data = {
        'id': 1,
        'nome': 'Mario',
        'cognome': 'Rossi',
        'data_nascita': '1980-05-15',
        'luogo_nascita': 'Roma',
        'sesso': 'M',
        'codice_fiscale': 'RSSMRA80E15H501K',
        'indirizzo': 'Via Prova, 1',
        'cap': '00100',
        'citta': 'Roma',
        'provincia': 'RM',
        'nazione': 'Italia',
        'email': 'mario.rossi@example.com',
        'telefono': '3331234567',
        'anno_iscrizione': 2024,
        'tipo_tesseramento': 'Standard',
        'numero_tessera': 'TS001',
        'data_emissione_tessera': '2024-01-01',
        'data_scadenza_tessera': '2025-01-01',
        'quota_pagata': 1,
        'attivo': 1,
        'nome_file_foto': None # o il nome di un file foto esistente se vuoi testare
    }

    app = QApplication(sys.argv)

    # Test per la modifica:
    dialog_edit = DialogoModificaSoci(socio_data=test_socio_data)
    if dialog_edit.exec() == QDialog.Accepted:
        print("Socio modificato (test):", dialog_edit.ottieni_dati_input())

    # Test per l'aggiunta di un nuovo socio:
    # dialog_add = DialogoModificaSoci()
    # if dialog_add.exec() == QDialog.Accepted:
    #     print("Nuovo socio aggiunto (test):", dialog_add.ottieni_dati_input())

    sys.exit(app.exec())
