# gestione_soci_annuali_pyside.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox,
    QFormLayout, QDialogButtonBox, QDialog, QComboBox, QSpinBox, QDateEdit,
    QInputDialog, QGroupBox, QScrollArea, QGridLayout, QSizePolicy, QTextEdit, QHeaderView
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QPixmap
import os
import shutil
from pathlib import Path
from io import BytesIO

# Importazioni per PDF e QR Code
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import landscape
from reportlab.lib.colors import HexColor, black
from reportlab.lib.utils import ImageReader
import qrcode
from qrcode.image.pil import PilImage

# Importazioni da data_access e codice_fiscale_utils
# Assicurati che questi moduli e le relative funzioni esistano e siano aggiornate nel tuo progetto
from data_access import get_all_soci, insert_socio_esteso, get_socio_by_id, update_socio_esteso, delete_socio, mark_quota_pagata, get_socio_photo_blob
from codice_fiscale_utils import calcola_codice_fiscale

# Importazione per il dialogo di modifica (assicurati che esista)
from dialogo_modifica_socio import DialogoModificaSoci


# --- Configurazione Globale ---
FOTO_SOCI_DIR = "foto_soci"
os.makedirs(FOTO_SOCI_DIR, exist_ok=True)


class DialogoAggiuntaSoci(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nuovo Socio Completo")
        self.resize(850, 750)  # Dimensione iniziale generosa per il dialogo

        # Layout principale del dialogo che conterrà la QScrollArea e i bottoni OK/Cancel
        main_dialog_layout = QVBoxLayout(self)

        # Widget contenitore per tutti i GroupBox, che sarà reso scrollabile
        scrollable_content_widget = QWidget()
        # Layout verticale che organizzerà tutti i GroupBox all'interno del widget scrollabile
        form_content_layout = QVBoxLayout(scrollable_content_widget)

        # --- GroupBox Dati Anagrafici ---
        group_anagrafici = QGroupBox("Dati Anagrafici")
        layout_anagrafici_grid = QGridLayout()

        layout_anagrafici_grid.addWidget(QLabel("Nome:"), 0, 0, Qt.AlignRight)
        self.nome = QLineEdit()
        layout_anagrafici_grid.addWidget(self.nome, 0, 1)

        layout_anagrafici_grid.addWidget(QLabel("Cognome:"), 0, 2, Qt.AlignRight)
        self.cognome = QLineEdit()
        layout_anagrafici_grid.addWidget(self.cognome, 0, 3)

        layout_anagrafici_grid.addWidget(QLabel("Data Nascita:"), 1, 0, Qt.AlignRight)
        self.data_nascita = QDateEdit(QDate.currentDate())
        self.data_nascita.setCalendarPopup(True)
        self.data_nascita.setDisplayFormat("dd/MM/yyyy")
        # Connessioni per il calcolo CF, attivate anche da cambiamenti nei campi
        self.data_nascita.dateChanged.connect(self.calcola_cf_automaticamente)
        layout_anagrafici_grid.addWidget(self.data_nascita, 1, 1)

        layout_anagrafici_grid.addWidget(QLabel("Luogo Nascita:"), 1, 2, Qt.AlignRight)
        self.luogo_nascita = QLineEdit()
        self.luogo_nascita.textChanged.connect(self.calcola_cf_automaticamente)
        layout_anagrafici_grid.addWidget(self.luogo_nascita, 1, 3)

        layout_anagrafici_grid.addWidget(QLabel("Sesso:"), 2, 0, Qt.AlignRight)
        self.sesso = QComboBox()
        self.sesso.addItems(["M", "F"])
        self.sesso.currentIndexChanged.connect(self.calcola_cf_automaticamente)
        layout_anagrafici_grid.addWidget(self.sesso, 2, 1)

        layout_anagrafici_grid.addWidget(QLabel("Codice Fiscale:"), 2, 2, Qt.AlignRight)
        self.codice_fiscale = QLineEdit()
        self.codice_fiscale.setPlaceholderText("Calcolato se Italia")
        self.codice_fiscale.setReadOnly(True) # Reso non modificabile manualmente
        layout_anagrafici_grid.addWidget(self.codice_fiscale, 2, 3)
        
        self.btn_calcola_cf = QPushButton("Calcola Codice Fiscale")
        self.btn_calcola_cf.clicked.connect(self.calcola_cf_automaticamente)
        layout_anagrafici_grid.addWidget(self.btn_calcola_cf, 3, 3, alignment=Qt.AlignRight) # Posizionato sotto il campo CF

        layout_anagrafici_grid.setColumnStretch(1, 1)
        layout_anagrafici_grid.setColumnStretch(3, 1)

        group_anagrafici.setLayout(layout_anagrafici_grid)
        form_content_layout.addWidget(group_anagrafici)


        # --- GroupBox Dati Residenza ---
        group_residenza = QGroupBox("Dati Residenza")
        layout_residenza_grid = QGridLayout()

        layout_residenza_grid.addWidget(QLabel("Via:"), 0, 0, Qt.AlignRight)
        self.via = QLineEdit()
        layout_residenza_grid.addWidget(self.via, 0, 1)

        layout_residenza_grid.addWidget(QLabel("Città:"), 0, 2, Qt.AlignRight)
        self.citta = QLineEdit()
        layout_residenza_grid.addWidget(self.citta, 0, 3)

        layout_residenza_grid.addWidget(QLabel("CAP:"), 1, 0, Qt.AlignRight)
        self.cap = QLineEdit()
        layout_residenza_grid.addWidget(self.cap, 1, 1)

        layout_residenza_grid.addWidget(QLabel("Provincia:"), 1, 2, Qt.AlignRight)
        self.provincia = QLineEdit()
        layout_residenza_grid.addWidget(self.provincia, 1, 3)

        layout_residenza_grid.addWidget(QLabel("Nazione:"), 2, 0, Qt.AlignRight)
        self.nazione = QComboBox()
        nazioni_europee = ["Italia", "Svizzera", "Francia", "Germania", "Austria", "Belgio", "Paesi Bassi", "Portogallo", "Regno Unito", "Altro"]
        self.nazione.addItems(nazioni_europee)
        self.nazione.currentIndexChanged.connect(self.calcola_cf_automaticamente) # Connessione per CF
        layout_residenza_grid.addWidget(self.nazione, 2, 1)

        layout_residenza_grid.setColumnStretch(1, 1)
        layout_residenza_grid.setColumnStretch(3, 1)

        group_residenza.setLayout(layout_residenza_grid)
        form_content_layout.addWidget(group_residenza)


        # --- GroupBox Dati Contatto ---
        group_contatto = QGroupBox("Dati Contatto")
        layout_contatto_grid = QGridLayout()

        layout_contatto_grid.addWidget(QLabel("Telefono:"), 0, 0, Qt.AlignRight)
        self.telefono = QLineEdit()
        layout_contatto_grid.addWidget(self.telefono, 0, 1)

        layout_contatto_grid.addWidget(QLabel("Email:"), 0, 2, Qt.AlignRight)
        self.email = QLineEdit()
        layout_contatto_grid.addWidget(self.email, 0, 3)

        layout_contatto_grid.setColumnStretch(1, 1)
        layout_contatto_grid.setColumnStretch(3, 1)

        group_contatto.setLayout(layout_contatto_grid)
        form_content_layout.addWidget(group_contatto)


        # --- GroupBox Dati Associazione e Tesseramento ---
        group_associazione_tesseramento = QGroupBox("Dati Associazione e Tesseramento")
        layout_associazione_tesseramento = QFormLayout()

        self.anno_iscrizione = QSpinBox() # Rinominato per chiarezza nel DB
        self.anno_iscrizione.setRange(2000, 2100)
        self.anno_iscrizione.setValue(QDate.currentDate().year()) # Anno corrente come default
        layout_associazione_tesseramento.addRow("Anno Iscrizione/Attività:", self.anno_iscrizione)
        
        self.tipo_tesseramento = QComboBox()
        self.tipo_tesseramento.addItems(["Nessuno", "Base", "Completo", "Sostenitore"])
        layout_associazione_tesseramento.addRow("Tipo Tesseramento:", self.tipo_tesseramento)
        
        self.numero_tessera = QLineEdit()
        layout_associazione_tesseramento.addRow("Numero Tessera:", self.numero_tessera)

        self.data_emissione_tessera = QDateEdit(QDate.currentDate())
        self.data_emissione_tessera.setCalendarPopup(True)
        self.data_emissione_tessera.setDisplayFormat("dd/MM/yyyy")
        layout_associazione_tesseramento.addRow("Data Emissione Tessera:", self.data_emissione_tessera)
        
        # Scadenza predefinita a 1 anno dalla data di emissione
        self.data_scadenza_tessera = QDateEdit(QDate.currentDate().addYears(1))
        self.data_scadenza_tessera.setCalendarPopup(True)
        self.data_scadenza_tessera.setDisplayFormat("dd/MM/yyyy")
        layout_associazione_tesseramento.addRow("Data Scadenza Tessera:", self.data_scadenza_tessera)

        self.note = QTextEdit()
        self.note.setPlaceholderText("Eventuali note aggiuntive...")
        self.note.setFixedHeight(60) # Altezza fissa per la QTextEdit
        layout_associazione_tesseramento.addRow("Note:", self.note)

        group_associazione_tesseramento.setLayout(layout_associazione_tesseramento)
        form_content_layout.addWidget(group_associazione_tesseramento)


        # --- GroupBox Foto Socio ---
        group_foto = QGroupBox("Foto Socio")
        layout_foto = QVBoxLayout()
        
        self.foto_path = "" # Inizializza il percorso della foto
        self.foto_label = QLabel("Nessuna Foto")
        self.foto_label.setFixedSize(160, 120) # Dimensione fissa per la visualizzazione della foto
        self.foto_label.setAlignment(Qt.AlignCenter)
        self.foto_label.setStyleSheet("border: 1px solid gray; background-color: lightgray;")
        layout_foto.addWidget(self.foto_label, alignment=Qt.AlignCenter)

        self.foto_button = QPushButton("Seleziona Foto")
        self.foto_button.clicked.connect(self.carica_foto)
        layout_foto.addWidget(self.foto_button, alignment=Qt.AlignCenter)
        
        group_foto.setLayout(layout_foto)
        form_content_layout.addWidget(group_foto)

        # --- Aggiungi uno stretch alla fine del layout dei contenuti del form ---
        form_content_layout.addStretch(1) 

        # --- Imposta la QScrollArea ---
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True) # Cruciale: permette al contenuto di ridimensionarsi
        scroll_area.setWidget(scrollable_content_widget) # Il widget che contiene tutti i GroupBox

        # Aggiungi la QScrollArea al layout principale del dialogo
        main_dialog_layout.addWidget(scroll_area)

        # Bottoni OK/Cancel
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_dialog_layout.addWidget(button_box)


    def calcola_cf_automaticamente(self):
        # Assicurati che l'ordine dei parametri per calcola_codice_fiscale sia corretto
        # rispetto alla definizione in codice_fiscale_utils.py

        if self.nazione.currentText().strip().lower() != "italia":
            self.codice_fiscale.clear()
            self.codice_fiscale.setPlaceholderText("Solo per Italia")
            return
        
        self.codice_fiscale.setPlaceholderText("Calcolato automaticamente")

        nome = self.nome.text().strip()
        cognome = self.cognome.text().strip()
        sesso = self.sesso.currentText()
        data = self.data_nascita.date().toString("yyyy-MM-dd")
        luogo = self.luogo_nascita.text().strip()

        if nome and cognome and sesso and data and luogo:
            try:
                # Usa l'ordine dei parametri come da codice_fiscale_utils.py
                cf = calcola_codice_fiscale(nome, cognome, sesso, data, luogo) 
                self.codice_fiscale.setText(cf)
            except Exception as e:
                self.codice_fiscale.setText("Errore calcolo CF")
                print(f"Errore nel calcolo del codice fiscale: {e}")
        else:
            self.codice_fiscale.clear()

    def carica_foto(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Seleziona Foto Socio", "", "Immagini (*.png *.jpg *.jpeg *.gif *.bmp)")
        if file_name:
            self.foto_path = file_name
            pixmap = QPixmap(self.foto_path)
            # Scala l'immagine per adattarsi al QLabel mantenendo le proporzioni
            scaled_pixmap = pixmap.scaled(self.foto_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.foto_label.setPixmap(scaled_pixmap)
            self.foto_label.setText("") # Rimuovi il testo "Nessuna Foto"

    def get_dati(self):
        nome_file_foto_salvato = None
        if self.foto_path and os.path.exists(self.foto_path):
            try:
                # Crea un nome univoco per la foto
                timestamp = QDate.currentDate().toString("yyyyMMdd_hhmmss")
                file_extension = Path(self.foto_path).suffix
                # Assicurati che il nome non contenga caratteri speciali per il filesystem
                clean_cognome = "".join(c for c in self.cognome.text().strip() if c.isalnum())
                clean_nome = "".join(c for c in self.nome.text().strip() if c.isalnum())
                nome_file_foto_salvato = f"{clean_cognome}_{clean_nome}_{timestamp}{file_extension}"
                dest_path = os.path.join(FOTO_SOCI_DIR, nome_file_foto_salvato)
                shutil.copy(self.foto_path, dest_path)
            except Exception as e:
                QMessageBox.warning(self, "Errore Foto", f"Impossibile salvare la foto: {e}")
                nome_file_foto_salvato = None

        return {
            "nome": self.nome.text().strip(),
            "cognome": self.cognome.text().strip(),
            "data_nascita": self.data_nascita.date().toString("yyyy-MM-dd"),
            "luogo_nascita": self.luogo_nascita.text().strip(),
            "sesso": self.sesso.currentText(),
            "codice_fiscale": self.codice_fiscale.text().strip(),
            "via": self.via.text().strip(),
            "citta": self.citta.text().strip(),
            "cap": self.cap.text().strip(),
            "provincia": self.provincia.text().strip(),
            "nazione": self.nazione.currentText(),
            "telefono": self.telefono.text().strip(),
            "email": self.email.text().strip(),
            "tipo_tesseramento": self.tipo_tesseramento.currentText(),
            "numero_tessera": self.numero_tessera.text().strip(),
            "data_emissione_tessera": self.data_emissione_tessera.date().toString("yyyy-MM-dd"),
            "data_scadenza_tessera": self.data_scadenza_tessera.date().toString("yyyy-MM-dd"),
            "anno_iscrizione": self.anno_iscrizione.value(),
            "note": self.note.toPlainText().strip(),
            "percorso_foto": nome_file_foto_salvato # Sarà None se non selezionata/salvata
        }

    def accept(self):
        # Validazione minimale prima di chiudere il dialogo e passare i dati
        if not self.nome.text().strip() or not self.cognome.text().strip() or \
           not self.data_nascita.date().isValid() or not self.luogo_nascita.text().strip() or \
           not self.sesso.currentText():
            QMessageBox.warning(self, "Dati Mancanti", "Nome, Cognome, Data/Luogo di Nascita e Sesso sono obbligatori.")
            return

        super().accept()


class FinestraGestioneSoci(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestione Soci Annuali - Windsurf Ceresio")
        self.setMinimumSize(1000, 600)

        main_layout = QHBoxLayout(self)

        # Colonna sinistra con i pulsanti
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
        # Ho aggiunto più colonne qui per riflettere i nuovi campi.
        # Assicurati che i nomi delle colonne corrispondano a quelli nel tuo DB per facilità.
        self.tabella.setColumnCount(12) # Aumentato il numero di colonne
        self.tabella.setHorizontalHeaderLabels([
            "ID", "Nome", "Cognome", "Email", "Telefono", "Nazione", "Anno Iscr.", 
            "Tipo Tess.", "N. Tess.", "Data Emiss.", "Data Scad.", "Quota Pagata"
        ])
        self.tabella.setSelectionBehavior(QTableWidget.SelectRows) # Selezione intera riga
        self.tabella.setSelectionMode(QTableWidget.SingleSelection) # Solo una riga selezionabile

        # Collegamenti
        self.btn_aggiungi.clicked.connect(self.apri_finestra_aggiunta)
        self.btn_modifica.clicked.connect(self.apri_finestra_modifica)
        self.btn_elimina.clicked.connect(self.elimina_socio_selezionato)
        self.btn_export_csv.clicked.connect(lambda: QMessageBox.information(self, "Esporta CSV", "Funzionalità non implementata"))
        self.btn_sollecita_quota.clicked.connect(self.sollecita_quota)
        self.btn_stampa_pdf.clicked.connect(self.stampa_tessera_pdf)
        self.btn_quota.clicked.connect(self.marca_quota_pagata) # Connessione mancante, aggiunta
        self.btn_foto.clicked.connect(self.visualizza_foto) # Connessione mancante, aggiunta
       

        main_layout.addWidget(self.left_panel)
        main_layout.addWidget(self.tabella)

        self.carica_dati()

    def carica_dati(self):
        # Questa funzione dovrà essere aggiornata per popolare la tabella con i nuovi campi
        soci = get_all_soci()
        self.tabella.setRowCount(0)
        # Assicurati che get_all_soci restituisca tutti i campi nell'ordine corretto
        # o almeno i campi che vuoi visualizzare nella tabella.
        # Ho aggiunto un mapping ipotetico basato sui nuovi campi.
        headers = [
            "id", "nome", "cognome", "email", "telefono", "nazione", 
            "anno_iscrizione", "tipo_tesseramento", "numero_tessera", 
            "data_emissione_tessera", "data_scadenza_tessera", "attivo" # 'attivo' per quota pagata
        ]
        self.tabella.setColumnCount(len(headers))
        self.tabella.setHorizontalHeaderLabels([
            "ID", "Nome", "Cognome", "Email", "Telefono", "Nazione", "Anno Iscr.", 
            "Tipo Tess.", "N. Tess.", "Data Emiss.", "Data Scad.", "Quota Pagata"
        ])

        for row_num, socio_dict in enumerate(soci):
            self.tabella.insertRow(row_num)
            for col_idx, key in enumerate(headers):
                value = socio_dict.get(key, "") # Usa .get per evitare errori se la chiave manca
                if key == "attivo": # Converte 1/0 in "Sì"/"No" per la colonna Quota Pagata
                    value = "Sì" if value == 1 else "No"
                item = QTableWidgetItem(str(value))
                self.tabella.setItem(row_num, col_idx, item)
        self.tabella.horizontalHeader().setStretchLastSection(True)
        self.tabella.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)


    def apri_finestra_aggiunta(self):
     dialogo = DialogoAggiuntaSoci(self)
     if dialogo.exec() == QDialog.Accepted:
        dati = dialogo.get_dati()
        try:
            # Qui la funzione insert_socio_esteso in data_access.py dovrà accettare tutti i nuovi campi.
            # Assicurati che la tua funzione sia aggiornata per gestire un dizionario o una lista estesa di valori.
            insert_socio_esteso(dati) # Passa il dizionario direttamente
            QMessageBox.information(self, "Successo", "Socio aggiunto con successo!")
            self.carica_dati()
        except Exception as e:
            QMessageBox.critical(self, "Errore Salva Socio", f"Errore durante il salvataggio del socio: {e}")
            print(f"Errore dettagliato: {e}") # Stampa l'errore per debugging


    def apri_finestra_modifica(self):
        row = self.tabella.currentRow()
        if row < 0:
          QMessageBox.warning(self, "Attenzione", "Seleziona un socio da modificare.")
          return

        # Assicurati che la colonna 0 della tabella contenga l'ID del socio
        id_socio = self.tabella.item(row, 0).text()

        socio = get_socio_by_id(id_socio)
        if not socio:
           QMessageBox.warning(self, "Errore", "Impossibile trovare il socio nel database.")
           return

        # Assicurati che DialogoModificaSoci sia aggiornato per gestire tutti i nuovi campi
        dialogo = DialogoModificaSoci(socio, self)
        if dialogo.exec() == QDialog.Accepted:
            nuovi_dati = dialogo.get_dati()
            try:
                # Anche update_socio_esteso in data_access.py dovrà essere aggiornato
                update_socio_esteso(id_socio, nuovi_dati)
                QMessageBox.information(self, "Successo", "Socio modificato con successo!")
                self.carica_dati()
            except Exception as e:
                QMessageBox.critical(self, "Errore Modifica Socio", f"Errore durante la modifica del socio: {e}")
                print(f"Errore dettagliato: {e}")


    def elimina_socio_selezionato(self):
        row = self.tabella.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona un socio da eliminare.")
            return

        id_socio = self.tabella.item(row, 0).text()
        conferma = QMessageBox.question(self, "Conferma Eliminazione", 
                                       f"Sei sicuro di voler eliminare il socio con ID {id_socio}?",
                                       QMessageBox.Yes | QMessageBox.No)
        if conferma == QMessageBox.Yes:
            try:
                delete_socio(id_socio)
                QMessageBox.information(self, "Successo", "Socio eliminato con successo!")
                self.carica_dati()
            except Exception as e:
                QMessageBox.critical(self, "Errore Eliminazione", f"Errore durante l'eliminazione del socio: {e}")


    def marca_quota_pagata(self):
        row = self.tabella.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona un socio da aggiornare.")
            return

        id_socio = self.tabella.item(row, 0).text()
        # Chiedi conferma
        current_status = self.tabella.item(row, self.tabella.columnCount() - 1).text() # Ultima colonna
        new_status = 1 if current_status == "No" else 0 # 1 per pagato, 0 per non pagato
        action_text = "marca come PAGATA" if new_status == 1 else "marca come NON PAGATA"

        conferma = QMessageBox.question(self, "Conferma Quota", 
                                       f"Vuoi {action_text} la quota per il socio con ID {id_socio}?",
                                       QMessageBox.Yes | QMessageBox.No)
        if conferma == QMessageBox.Yes:
            try:
                mark_quota_pagata(id_socio, new_status)
                QMessageBox.information(self, "Successo", "Stato quota aggiornato!")
                self.carica_dati()
            except Exception as e:
                QMessageBox.critical(self, "Errore Aggiornamento Quota", f"Errore durante l'aggiornamento della quota: {e}")


    def visualizza_foto(self):
        row = self.tabella.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona un socio.")
            return

        id_socio = self.tabella.item(row, 0).text()
        try:
            # get_socio_photo_blob deve restituire il BLOB della foto o il percorso del file
            # Dato che ora salviamo il percorso, recuperiamo quello
            socio_data = get_socio_by_id(id_socio)
            if not socio_data or not socio_data.get('percorso_foto'):
                QMessageBox.information(self, "Foto", "Nessuna foto disponibile per questo socio.")
                return

            photo_path_relative = socio_data['percorso_foto']
            full_photo_path = os.path.join(FOTO_SOCI_DIR, photo_path_relative)

            if os.path.exists(full_photo_path):
                dialog = QDialog(self)
                dialog.setWindowTitle("Foto del Socio")
                layout = QVBoxLayout(dialog)
                label = QLabel()
                pixmap = QPixmap(full_photo_path)
                # Adatta la foto a una dimensione ragionevole nel dialogo
                label.setPixmap(pixmap.scaledToWidth(400, Qt.SmoothTransformation))
                layout.addWidget(label)
                dialog.exec()
            else:
                QMessageBox.warning(self, "Foto Non Trovata", f"Il file della foto non è stato trovato al percorso:\n{full_photo_path}")
        except Exception as e:
            QMessageBox.critical(self, "Errore Visualizzazione Foto", f"Errore durante la visualizzazione della foto: {e}")
            print(f"Errore dettagliato visualizza_foto: {e}")


    def sollecita_quota(self):
        row = self.tabella.currentRow()
        if row < 0:
         QMessageBox.warning(self, "Attenzione", "Seleziona un socio.")
         return

        # Assumendo che la colonna Email sia all'indice 3
        email = self.tabella.item(row, 3).text()
        # Assumendo che la colonna Nome sia all'indice 1 e Cognome all'indice 2
        nome_completo = f"{self.tabella.item(row, 1).text()} {self.tabella.item(row, 2).text()}"

        if not email:
            QMessageBox.warning(self, "Dati Mancanti", "Email del socio non disponibile per il sollecito.")
            return
        
        # Qui potresti integrare una vera funzione di invio email.
        # Per ora, è una simulazione come nel tuo codice originale.
        QMessageBox.information(self, "Sollecito Quota", 
                                f"Simulazione invio email di sollecito per la quota a:\n{nome_completo} <{email}>.\n\n"
                                "Questa funzionalità richiede integrazione con un servizio email per l'invio effettivo.")


    def stampa_tessera_pdf(self):
        CARD_WIDTH = 85.6 * mm
        CARD_HEIGHT = 53.98 * mm
        ORANGE_DUTCH = HexColor('#FF7F00')
        LOGO_PATH = "logo_onda.png" # Assicurati che questo file logo_onda.png esista nella stessa directory dell'applicazione

        row = self.tabella.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona un socio per stampare la tessera.")
            return

        id_socio = self.tabella.item(row, 0).text()
        socio = get_socio_by_id(id_socio)
        if not socio:
            QMessageBox.warning(self, "Errore", "Socio non trovato nel database. Impossibile stampare la tessera.")
            return

        os.makedirs("tessere_associati", exist_ok=True)
        output_filename = os.path.join("tessere_associati", f"tessera_{socio['nome']}_{socio['cognome']}_{socio['id']}.pdf")
        
        try:
            c = canvas.Canvas(output_filename, pagesize=(CARD_WIDTH, CARD_HEIGHT))

            # Logo
            try:
                if os.path.exists(LOGO_PATH):
                    logo = ImageReader(LOGO_PATH)
                    logo_width = CARD_WIDTH * 0.35
                    logo_height = logo_width * (logo.getSize()[1] / logo.getSize()[0])
                    c.drawImage(logo, 5 * mm, CARD_HEIGHT - logo_height - 5 * mm, width=logo_width, height=logo_height, mask='auto')
                else:
                    c.setFont('Helvetica-Bold', 10)
                    c.drawString(5 * mm, CARD_HEIGHT - 15 * mm, "LOGO MANCANTE")
            except Exception as e:
                print(f"Errore caricamento logo: {e}")
                c.setFont('Helvetica-Bold', 10)
                c.drawString(5 * mm, CARD_HEIGHT - 15 * mm, "ERRORE LOGO")

            # Dati socio
            text_x = 5 * mm
            text_y = CARD_HEIGHT - 30 * mm
            c.setFont('Helvetica-Bold', 8)
            c.drawString(text_x, text_y, "Numero Tessera:")
            c.setFont('Helvetica', 8)
            c.drawString(text_x + 25 * mm, text_y, str(socio.get('numero_tessera', 'N/A'))) # Usa nuovo campo numero_tessera

            text_y -= 5 * mm
            c.setFont('Helvetica-Bold', 8)
            c.drawString(text_x, text_y, "Nome Associato:")
            c.setFont('Helvetica', 8)
            c.drawString(text_x + 25 * mm, text_y, f"{socio.get('nome', '')} {socio.get('cognome', '')}")

            text_y -= 5 * mm
            c.setFont('Helvetica-Bold', 8)
            c.drawString(text_x, text_y, "Anno Validità:")
            c.setFont('Helvetica', 8)
            c.drawString(text_x + 25 * mm, text_y, str(socio.get('anno_iscrizione', 'N/A'))) # Usa nuovo campo anno_iscrizione

            text_y -= 5 * mm
            c.setFont('Helvetica-Bold', 8)
            c.drawString(text_x, text_y, "Scadenza:")
            c.setFont('Helvetica', 8)
            c.drawString(text_x + 25 * mm, text_y, socio.get('data_scadenza_tessera', 'N/A')) # Usa nuovo campo data_scadenza_tessera

            # Foto Socio (con percorso dal DB)
            photo_x = CARD_WIDTH - 25 * mm - 5 * mm
            photo_y = CARD_HEIGHT - 28 * mm - 5 * mm
            photo_width = 20 * mm
            photo_height = 28 * mm
            
            percorso_foto_socio = socio.get('percorso_foto')
            if percorso_foto_socio:
                full_path_foto = os.path.join(FOTO_SOCI_DIR, percorso_foto_socio)
                if os.path.exists(full_path_foto):
                    try:
                        c.drawImage(ImageReader(full_path_foto), photo_x, photo_y, width=photo_width, height=photo_height, preserveAspectRatio=True)
                    except Exception as e:
                        print(f"Errore caricamento foto socio per PDF: {e}")
                        c.rect(photo_x, photo_y, photo_width, photo_height)
                        c.setFont('Helvetica', 6)
                        c.setFillColor(black)
                        c.drawCentredString(photo_x + photo_width / 2, photo_y + photo_height / 2 - 2 * mm, "Errore")
                        c.drawCentredString(photo_x + photo_width / 2, photo_y + photo_height / 2 - 5 * mm, "Foto")
                else:
                    c.rect(photo_x, photo_y, photo_width, photo_height)
                    c.setFont('Helvetica', 6)
                    c.setFillColor(black)
                    c.drawCentredString(photo_x + photo_width / 2, photo_y + photo_height / 2 - 2 * mm, "Spazio")
                    c.drawCentredString(photo_x + photo_width / 2, photo_y + photo_height / 2 - 5 * mm, "Foto Socio (non trovata)")
            else:
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
                qr_data = (f"Numero Tessera: {socio.get('numero_tessera', 'N/A')}\n"
                           f"Nome: {socio.get('nome', '')} {socio.get('cognome', '')}\n"
                           f"Anno: {socio.get('anno_iscrizione', 'N/A')}\n"
                           f"Scadenza: {socio.get('data_scadenza_tessera', 'N/A')}")
                qr.add_data(qr_data)
                qr.make(fit=True)
                qr_img = qr.make_image(image_factory=PilImage)
                img_bytes = BytesIO()
                qr_img.save(img_bytes, format='PNG')
                img_bytes.seek(0)
                qr_image = ImageReader(img_bytes)
                qr_size = 15 * mm
                c.drawImage(qr_image, CARD_WIDTH - qr_size - 5 * mm, 5 * mm, width=qr_size, height=qr_size)
            except Exception as e:
                print(f"Errore generazione QR code: {e}")
                c.setFont('Helvetica-Bold', 8)
                c.setFillColor(black)
                c.drawString(CARD_WIDTH - 30 * mm, 15 * mm, "QR CODE")
                c.drawString(CARD_WIDTH - 30 * mm, 10 * mm, "MANCANTE")

            # Bordo arancione
            c.setStrokeColor(ORANGE_DUTCH)
            c.setLineWidth(0.5 * mm)
            c.rect(0.5 * mm, 0.5 * mm, CARD_WIDTH - 1 * mm, CARD_HEIGHT - 1 * mm)

            c.save()
            QMessageBox.information(self, "PDF generato", f"Tessera salvata in:\n{output_filename}")
        except Exception as e:
            QMessageBox.critical(self, "Errore Stampa Tessera", f"Errore durante la generazione o il salvataggio della tessera PDF: {e}")
            print(f"Errore dettagliato stampa_tessera_pdf: {e}")
