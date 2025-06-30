# dettagli_materiali_tab.py

import os
import shutil # Per copiare/spostare file (foto)
from pathlib import Path # Per gestire i percorsi dei file
from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QTextEdit, QPushButton, QComboBox,
    QVBoxLayout, QHBoxLayout, QCheckBox, QFileDialog, QMessageBox,
    QGroupBox, QSpacerItem, QSizePolicy, QFormLayout # QFormLayout è specifico per i dettagli
)
from PySide6.QtGui import QPixmap, QImage # QImage per convertire da BLOB se necessario
from PySide6.QtCore import Qt, Signal

# Importa le funzioni di accesso ai dati necessarie a questa scheda
from data_access import (
    inserisci_materiale,
    get_materiale_by_id,
    aggiorna_materiale,
    carica_materiali_rig # Per la combo box dei Rig Padri
)

# Definisci la directory per le foto (QUESTA DEFINIZIONE È QUI!)
FOTO_DIR = "foto_materiali"
os.makedirs(FOTO_DIR, exist_ok=True) # Assicurati che la directory esista

class MaterialiDettagliTab(QWidget):
    # Segnali per comunicare con il dialogo principale
    material_saved = Signal() # Emette quando un materiale viene salvato
    cancel_edit_requested = Signal() # Emette quando si annulla la modifica/aggiunta

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_material_id = None # ID del materiale che si sta modificando (None per nuovo)
        self.foto_path_attuale = None # Percorso della foto attuale (per evitare ricaricamenti inutili)
        self.new_photo_selected = False # Flag per indicare se è stata selezionata una nuova foto
        self.rig_padri_map = {} # Mappa ID Rig -> Nome Rig
        self.rig_padri_combo_box_items = [] # Per memorizzare gli items della combobox in ordine

        self.init_ui()
        self._popola_rig_padri_combo() # Popola la combo dei Rig all'avvio

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        form_group_box = QGroupBox("Dettagli Materiale")
        form_layout = QFormLayout()

        # Campi input
        self.codice_le = QLineEdit()
        form_layout.addRow("Codice:", self.codice_le)

        self.tipo_cb = QComboBox()
        self.tipo_cb.addItems(["Sup", "Canoa", "Pagaia", "Salvagente", "Tavola Windsurf", "Vela", "Boma", "Albero", "Bici d'acqua", "Tandem Sup", "Rig", "Muta", "Trapezio", "Accessorio"])
        form_layout.addRow("Tipo:", self.tipo_cb)

        self.nome_le = QLineEdit()
        form_layout.addRow("Nome:", self.nome_le)

        self.produttore_le = QLineEdit()
        form_layout.addRow("Produttore:", self.produttore_le)

        self.provenienza_le = QLineEdit()
        form_layout.addRow("Provenienza:", self.provenienza_le)

        self.descrizione_te = QTextEdit()
        self.descrizione_te.setFixedHeight(60) # Altezza fissa
        form_layout.addRow("Descrizione:", self.descrizione_te)

        self.note_te = QTextEdit()
        self.note_te.setFixedHeight(60) # Altezza fissa
        form_layout.addRow("Note:", self.note_te)

        self.codice_barre_le = QLineEdit() # Campo per codice_barre (non barcode)
        form_layout.addRow("Codice a Barre:", self.codice_barre_le)

        # --- Campo Rig Padre ---
        self.rig_padre_cb = QComboBox()
        form_layout.addRow("Rig Padre (per vele/bomi):", self.rig_padre_cb)
        # ---------------------

        self.disponibile_cb = QCheckBox("Disponibile per il Noleggio")
        self.disponibile_cb.setChecked(True) # Di default è disponibile
        form_layout.addRow("", self.disponibile_cb)

        form_group_box.setLayout(form_layout)
        main_layout.addWidget(form_group_box)

        # --- Gestione Foto ---
        foto_group_box = QGroupBox("Foto Materiale")
        foto_layout = QHBoxLayout()

        self.foto_label = QLabel("Nessuna foto")
        self.foto_label.setFixedSize(200, 200) # Dimensioni fisse per la preview
        self.foto_label.setAlignment(Qt.AlignCenter)
        self.foto_label.setStyleSheet("border: 1px solid gray;")
        self.foto_label.setScaledContents(True) # Scala l'immagine per adattarsi al QLabel
        foto_layout.addWidget(self.foto_label)

        foto_buttons_layout = QVBoxLayout()
        self.scegli_foto_button = QPushButton("Scegli Foto")
        self.scegli_foto_button.clicked.connect(self.scegli_foto)
        foto_buttons_layout.addWidget(self.scegli_foto_button)

        self.rimuovi_foto_button = QPushButton("Rimuovi Foto")
        self.rimuovi_foto_button.clicked.connect(self.rimuovi_foto)
        foto_buttons_layout.addWidget(self.rimuovi_foto_button)
        foto_buttons_layout.addStretch(1) # Spinge i bottoni in alto

        foto_layout.addLayout(foto_buttons_layout)
        foto_group_box.setLayout(foto_layout)
        main_layout.addWidget(foto_group_box)

        # --- Bottoni Azione ---
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Salva")
        self.save_button.clicked.connect(self.salva_materiale)
        button_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("Annulla")
        self.cancel_button.clicked.connect(self.cancel_edit_requested.emit)
        button_layout.addWidget(self.cancel_button)

        button_layout.addStretch(1)
        main_layout.addLayout(button_layout)
        main_layout.addStretch(1) # Spinge tutto il contenuto verso l'alto

    def _popola_rig_padri_combo(self):
        """Popola la QComboBox dei Rig Padri con i nomi dei Rig."""
        self.rig_padre_cb.clear()
        self.rig_padri_map = {0: "Nessuno"} # Reset e aggiunta di "Nessuno"
        self.rig_padri_combo_box_items = [("Nessuno", 0)] # Tupla (nome, id)

        rig_materials = carica_materiali_rig() # Carica tutti i materiali di tipo 'Rig'
        for rig in rig_materials:
            rig_id = rig.get('id')
            rig_nome = rig.get('nome')
            if rig_id is not None and rig_nome is not None:
                self.rig_padri_map[rig_id] = rig_nome
                self.rig_padri_combo_box_items.append((rig_nome, rig_id))

        # Ordina gli elementi per nome prima di aggiungerli alla combobox
        self.rig_padri_combo_box_items.sort(key=lambda x: x[0].lower())

        for nome, _ in self.rig_padri_combo_box_items:
            self.rig_padre_cb.addItem(nome)

    def scegli_foto(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Scegli Foto", "", "Immagini (*.png *.jpg *.jpeg *.gif)", options=options)
        if file_path:
            self.foto_path_attuale = file_path
            self.new_photo_selected = True # Imposta il flag perché è stata selezionata una nuova foto
            self._aggiorna_anteprima_foto(file_path)

    def rimuovi_foto(self):
        self.foto_path_attuale = None
        self.new_photo_selected = True # Considera la rimozione come "nuova selezione" (vuota)
        self.foto_label.setText("Nessuna foto")
        self.foto_label.setPixmap(QPixmap()) # Rimuovi l'immagine

    def _aggiorna_anteprima_foto(self, path):
        if path and os.path.exists(path):
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                self.foto_label.setPixmap(pixmap.scaled(self.foto_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                self.foto_label.setText("Errore caricamento foto")
        else:
            self.foto_label.setText("Nessuna foto")
            self.foto_label.setPixmap(QPixmap())

    def _salva_foto_e_aggiorna_path(self):
        """
        Salva la foto selezionata nella FOTO_DIR e restituisce il percorso relativo.
        Gestisce anche la rimozione di vecchie foto se una nuova viene selezionata.
        """
        if not self.new_photo_selected: # Nessuna nuova foto selezionata/rimossa
            return self.foto_path_attuale # Restituisce il percorso esistente

        if self.foto_path_attuale is None: # Foto rimossa
            # Qui potresti aggiungere la logica per eliminare la vecchia foto dal FOTO_DIR
            # se era presente e associata al current_material_id
            return "" # Percorso vuoto per indicare nessuna foto

        # Se è stata selezionata una nuova foto
        try:
            # Genera un nome file univoco
            file_ext = Path(self.foto_path_attuale).suffix
            new_file_name = f"{Path(self.foto_path_attuale).stem}_{os.urandom(4).hex()}{file_ext}"
            dest_path = Path(FOTO_DIR) / new_file_name

            # Copia la nuova foto
            shutil.copy2(self.foto_path_attuale, dest_path)
            self.new_photo_selected = False # Resetta il flag dopo il salvataggio
            return str(dest_path)
        except Exception as e:
            QMessageBox.warning(self, "Errore Foto", f"Impossibile salvare la foto: {e}")
            return "" # Restituisce stringa vuota in caso di errore

    def nuovo_materiale(self):
        # Resetta tutti i campi per l'inserimento di un nuovo materiale
        self.current_material_id = None
        self.codice_le.clear()
        self.tipo_cb.setCurrentIndex(0)
        self.nome_le.clear()
        self.produttore_le.clear()
        self.provenienza_le.clear()
        self.descrizione_te.clear()
        self.note_te.clear()
        self.codice_barre_le.clear()
        self.rig_padre_cb.setCurrentIndex(0) # Seleziona "Nessuno"
        self.disponibile_cb.setChecked(True)
        self.foto_path_attuale = None
        self.new_photo_selected = False
        self.foto_label.setText("Nessuna foto")
        self.foto_label.setPixmap(QPixmap())
        self._popola_rig_padri_combo() # Ricarica i Rig per essere sicuro che siano aggiornati

    def carica_materiale_per_modifica(self, material_id):
        self.current_material_id = material_id
        self.new_photo_selected = False # Nessuna nuova foto selezionata all'inizio della modifica
        self._popola_rig_padri_combo() # Ricarica i Rig per essere sicuro che siano aggiornati

        material_data = get_materiale_by_id(material_id)
        if material_data:
            self.codice_le.setText(material_data.get('codice', ''))
            self.tipo_cb.setCurrentText(material_data.get('tipo', ''))
            self.nome_le.setText(material_data.get('nome', ''))
            self.produttore_le.setText(material_data.get('produttore', ''))
            self.provenienza_le.setText(material_data.get('provenienza', ''))
            self.descrizione_te.setText(material_data.get('descrizione', ''))
            self.note_te.setText(material_data.get('note', ''))
            self.codice_barre_le.setText(material_data.get('codice_barre', ''))

            # Seleziona il Rig Padre corretto nella combobox
            rig_id_corrente = material_data.get('rig', 0)
            try:
                # Trova l'indice dell'elemento corrispondente all'ID del rig
                index = next(i for i, (nome, id_rig) in enumerate(self.rig_padri_combo_box_items) if id_rig == rig_id_corrente)
                self.rig_padre_cb.setCurrentIndex(index)
            except StopIteration:
                self.rig_padre_cb.setCurrentIndex(0) # Se non trovato, seleziona "Nessuno"

            self.disponibile_cb.setChecked(bool(material_data.get('disponibile', 1)))

            self.foto_path_attuale = material_data.get('foto_path', '')
            self._aggiorna_anteprima_foto(self.foto_path_attuale)

        else:
            QMessageBox.warning(self, "Errore", "Materiale non trovato.")
            self.nuovo_materiale() # Resetta il form se l'ID non è valido

    def salva_materiale(self):
        codice = self.codice_le.text().strip()
        tipo = self.tipo_cb.currentText()
        nome = self.nome_le.text().strip()
        produttore = self.produttore_le.text().strip()
        provenienza = self.provenienza_le.text().strip()
        descrizione = self.descrizione_te.toPlainText().strip()
        note = self.note_te.toPlainText().strip()
        codice_barre = self.codice_barre_le.text().strip()
        disponibile = 1 if self.disponibile_cb.isChecked() else 0

        # Recupera l'ID del Rig Padre dalla combobox
        selected_rig_nome = self.rig_padre_cb.currentText()
        # Trova l'ID corrispondente al nome selezionato
        rig_padre_id = next((id_rig for nome, id_rig in self.rig_padri_combo_box_items if nome == selected_rig_nome), 0)


        if not codice or not tipo or not nome:
            QMessageBox.warning(self, "Dati Mancanti", "Codice, Tipo e Nome sono campi obbligatori.")
            return False

        # Salva la foto e ottieni il percorso aggiornato
        foto_path_finale = self._salva_foto_e_aggiorna_path()

        # Prepara i dati da salvare
        dati_materiale = {
            'codice': codice,
            'tipo': tipo,
            'nome': nome,
            'produttore': produttore,
            'provenienza': provenienza,
            'descrizione': descrizione,
            'note': note,
            'codice_barre': codice_barre, # Usa il campo codice_barre
            'foto_path': foto_path_finale,
            'disponibile': disponibile,
            'rig': rig_padre_id # Inserisce l'ID numerico del Rig Padre
        }

        success = False
        if self.current_material_id is None:
            # Inserisci nuovo materiale
            success = inserisci_materiale(dati_materiale)
            if success:
                QMessageBox.information(self, "Salvataggio Completato", "Materiale aggiunto con successo.")
                self.nuovo_materiale() # Resetta il form per il prossimo inserimento
        else:
            # Aggiorna materiale esistente
            success = aggiorna_materiale(self.current_material_id, dati_materiale)
            if success:
                QMessageBox.information(self, "Salvataggio Completato", "Materiale aggiornato con successo.")

        if success:
            self.material_saved.emit() # Emette il segnale per aggiornare la lista principale
            return True
        else:
            QMessageBox.critical(self, "Errore di Salvataggio", "Si è verificato un errore durante il salvataggio del materiale.")
            return False
