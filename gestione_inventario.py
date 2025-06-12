import os
import shutil
import sqlite3
from PySide6.QtWidgets import (QWidget, QLabel, QLineEdit, QTextEdit, QPushButton, QComboBox,
                               QVBoxLayout, QHBoxLayout, QCheckBox, QFileDialog, QTableWidget,
                               QTableWidgetItem, QHeaderView, QMessageBox, QGroupBox, QSpacerItem, QSizePolicy, QAbstractItemView)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from data_access import (
    inserisci_materiale, 
    elimina_materiale,
    carica_materiali,
    carica_materiali_per_tipo,
    carica_materiali_rig,
    get_materiale_by_id,
    aggiorna_materiale
)
from pathlib import Path


FOTO_DIR = "foto_materiali"
os.makedirs(FOTO_DIR, exist_ok=True)

class AnagraficaMateriali(QWidget):
    def __init__(self):
        super().__init__()

        self.current_material_id = None

        # --- Campi Form ---
        self.codice = QLineEdit()
        self.tipo = QComboBox()
        self.tipo.addItems(["Sup", "Canoa", "Pagaia", "Salvagente", "Tavola Windsurf", "Vela", "Boma",
                             "Barca a Vela", "Albero", "Bici d'acqua", "Tandem Sup", "Rig"])
        self.nome = QLineEdit()
        self.produttore = QLineEdit()
        self.provenienza = QComboBox()
        self.provenienza.addItems(["Acquistato", "Altro"])
        self.descrizione = QTextEdit()
        self.note = QTextEdit() # Campo Note

        self.rig_checkbox = QCheckBox("Componi RIG (Albero + Boma + Vela)")
        self.foto_path = ""
        self.foto_label = QLabel("Anteprima Foto")
        self.foto_label.setAlignment(Qt.AlignCenter)
        self.foto_label.setFixedSize(150, 100)

        # --- Campi RIG ---
        self.combo_albero = QComboBox()
        self.combo_boma = QComboBox()
        self.combo_vela = QComboBox()
        self.combo_albero.setVisible(False)
        self.combo_boma.setVisible(False)
        self.combo_vela.setVisible(False)

        self.carica_materiali_rig()

        self.rig_checkbox.stateChanged.connect(self.toggle_rig)

        # --- Pulsanti ---
        self.btn_crea_o_salva_nuovo = QPushButton("Crea Nuovo Materiale") # Pulsante con doppia funzione
        self.btn_salva_modifiche = QPushButton("Salva Modifiche")     
        self.btn_elimina = QPushButton("Elimina Selezionato")
        self.btn_carica_foto = QPushButton("Carica Foto")

        # Connessioni dei pulsanti alle funzioni
        self.btn_crea_o_salva_nuovo.clicked.connect(self.handle_crea_o_salva_nuovo_click) 
        self.btn_salva_modifiche.clicked.connect(self.salva_modifiche_materiale_action) 
        self.btn_elimina.clicked.connect(self.elimina_selezionato)
        self.btn_carica_foto.clicked.connect(self.carica_foto)

        # --- Layout del Form (Colonna Sinistra) ---
        form_layout = QVBoxLayout()
        form_layout.addWidget(QLabel("Codice:"))
        form_layout.addWidget(self.codice)
        form_layout.addWidget(QLabel("Tipo:"))
        form_layout.addWidget(self.tipo)
        form_layout.addWidget(QLabel("Nome:"))
        form_layout.addWidget(self.nome)
        form_layout.addWidget(QLabel("Produttore:"))
        form_layout.addWidget(self.produttore)
        form_layout.addWidget(QLabel("Provenienza:"))
        form_layout.addWidget(self.provenienza)
        form_layout.addWidget(QLabel("Descrizione:"))
        form_layout.addWidget(self.descrizione)
        form_layout.addWidget(QLabel("Note:"))
        form_layout.addWidget(self.note) # Campo Note posizionato correttamente

        # Sezione RIG in un GroupBox per chiarezza
        rig_group_box = QGroupBox("Composizione RIG")
        rig_layout = QVBoxLayout()
        rig_layout.addWidget(self.rig_checkbox)
        rig_layout.addWidget(QLabel("Albero:"))
        rig_layout.addWidget(self.combo_albero)
        rig_layout.addWidget(QLabel("Boma:"))
        rig_layout.addWidget(self.combo_boma)
        rig_layout.addWidget(QLabel("Vela:"))
        rig_layout.addWidget(self.combo_vela)
        rig_group_box.setLayout(rig_layout)
        form_layout.addWidget(rig_group_box)
        
        # Sezione Foto
        foto_layout = QVBoxLayout()
        foto_layout.addWidget(QLabel("Foto:"))
        foto_layout.addWidget(self.btn_carica_foto)
        foto_layout.addWidget(self.foto_label)
        form_layout.addLayout(foto_layout)

        # Pulsanti di azione in un GroupBox per maggiore stabilità nel layout
        button_group_box = QGroupBox("Azioni Materiale")
        button_form_layout = QVBoxLayout()
        button_form_layout.addWidget(self.btn_crea_o_salva_nuovo) 
        button_form_layout.addWidget(self.btn_salva_modifiche)   
        button_form_layout.addWidget(self.btn_elimina)
        button_group_box.setLayout(button_form_layout)
        form_layout.addWidget(button_group_box) # Aggiungi il GroupBox dei pulsanti
        form_layout.addStretch(1) # Stretch per spingere il contenuto in alto

        # --- Tabella ---
        self.tabella = QTableWidget()
        self.tabella.setColumnCount(14) 
        self.tabella.setHorizontalHeaderLabels([
            "ID", "Codice", "Tipo", "Nome", "Produttore", "Provenienza",
            "Descrizione", "Note", "Codice Barre", "Foto Path", "Disponibile",
            "Barcode", "Rig", "Foto BLOB"
        ])
        self.tabella.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabella.setEditTriggers(QAbstractItemView.NoEditTriggers) 
        self.tabella.cellClicked.connect(self.carica_dettagli_riga) 
        
        # Nascondi le colonne che non vuoi mostrare all'utente nella tabella
        self.tabella.setColumnHidden(0,True)    # ID
        self.tabella.setColumnHidden(8, True)   # codice_barre (se preferisci usare barcode)
        self.tabella.setColumnHidden(9, True)   # foto_path
        self.tabella.setColumnHidden(11, True)  # barcode (se preferisci usare codice_barre)
        self.tabella.setColumnHidden(13, True)  # foto (BLOB)

        # --- Filtri e pulsante Aggiorna Lista (Colonna Destra) ---
        self.filtro_tipo = QComboBox()
        self.filtro_tipo.addItem("Tutti")
        self.filtro_tipo.addItems(["Sup", "Canoa", "Pagaia", "Salvagente", "Tavola Windsurf", "Vela", "Boma", "Barca a Vela", "Albero", "Bici d'acqua", "Tandem Sup", "Rig"])

        self.filtro_nome = QLineEdit()
        self.filtro_nome.setPlaceholderText("Filtra per nome")

        self.filtro_produttore = QLineEdit()
        self.filtro_produttore.setPlaceholderText("Filtra per produttore")

        self.filtro_disponibile = QCheckBox("Solo disponibili")
        self.btn_aggiorna = QPushButton("Aggiorna Lista")
        self.btn_aggiorna.clicked.connect(self.carica_tabella)

        self.filtro_tipo.currentTextChanged.connect(self.carica_tabella)
        self.filtro_nome.textChanged.connect(self.carica_tabella)
        self.filtro_produttore.textChanged.connect(self.carica_tabella)
        self.filtro_disponibile.stateChanged.connect(self.carica_tabella) 
        

        filtro_layout = QHBoxLayout()
        filtro_layout.addWidget(QLabel("Tipo:"))
        filtro_layout.addWidget(self.filtro_tipo)
        filtro_layout.addWidget(QLabel("Nome:"))
        filtro_layout.addWidget(self.filtro_nome)
        filtro_layout.addWidget(QLabel("Produttore:"))
        filtro_layout.addWidget(self.filtro_produttore)
        filtro_layout.addWidget(self.filtro_disponibile)
        filtro_layout.addWidget(self.btn_aggiorna)

        # Layout principale
        main_layout = QHBoxLayout(self)
        
        # Aggiungi il layout del form a sinistra
        main_layout.addLayout(form_layout, 1)

        # Layout per tabella e filtri a destra
        table_section_layout = QVBoxLayout()
        table_section_layout.addLayout(filtro_layout)
        table_section_layout.addWidget(self.tabella)
        main_layout.addLayout(table_section_layout, 3)

        # Inizializzazione stato dei pulsanti (CHIAMATA UNA SOLA VOLTA ALL'AVVIO)
        self.nuovo_materiale() 
        self.carica_tabella()  

    def carica_foto(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleziona immagine", "", "Immagini (*.png *.jpg *.jpeg *.bmp *.gif)")
        if file_path:
            nome_file = os.path.basename(file_path)
            destinazione = os.path.join(FOTO_DIR, nome_file)
            try:
                shutil.copy(file_path, destinazione)
                self.foto_path = destinazione
                pixmap = QPixmap(str(destinazione))
                self.foto_label.setPixmap(pixmap.scaled(self.foto_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            except Exception as e:
                QMessageBox.critical(self, "Errore Foto", f"Impossibile copiare la foto: {e}")
                self.foto_path = ""
                self.foto_label.clear()


    def toggle_rig(self, stato):
        is_rig = stato == 2
        self.combo_albero.setVisible(is_rig)
        self.combo_boma.setVisible(is_rig)
        self.combo_vela.setVisible(is_rig)
        if is_rig:
            self.tipo.setCurrentText("Rig")
            self.tipo.setDisabled(True)
        else:
            self.tipo.setDisabled(False)
            if self.tipo.currentText() == "Rig":
                self.tipo.setCurrentIndex(0)


    def carica_materiali_rig(self):
        self.combo_albero.clear()
        self.combo_boma.clear()
        self.combo_vela.clear()
        self.combo_albero.addItem("Seleziona Albero")
        self.combo_boma.addItem("Seleziona Boma")
        self.combo_vela.addItem("Seleziona Vela")

        tipi_combo = [("Albero", self.combo_albero), ("Boma", self.combo_boma), ("Vela", self.combo_vela)]

        for tipo, combo in tipi_combo:
            risultati = carica_materiali_per_tipo(tipo)
            if risultati:
                codici = [r[1] for r in risultati if r[1]]
                combo.addItems(codici)

    def handle_crea_o_salva_nuovo_click(self):
        if self.current_material_id is not None:
            self.nuovo_materiale()
        else:
            self.aggiungi_nuovo_materiale_action()

    def aggiungi_nuovo_materiale_action(self):
        codice = self.codice.text().strip()
        tipo = self.tipo.currentText()
        nome = self.nome.text().strip()
        produttore = self.produttore.text().strip()
        provenienza = self.provenienza.currentText()
        descrizione = self.descrizione.toPlainText().strip()
        note = self.note.toPlainText().strip() 
        
        rig_checked = 1 if self.rig_checkbox.isChecked() else 0
        
        disponibile = 1
        barcode_val = ""

        codice_barre_val = ""
        if produttore and nome:
            codice_barre_val = f"{codice}-{produttore}-{nome}"
        elif codice:
            codice_barre_val = codice
        
        if not barcode_val:
            barcode_val = codice_barre_val

        if not codice or not nome or not tipo:
            QMessageBox.warning(self, "Input Mancante", "Codice, Nome e Tipo sono campi obbligatori.")
            return

        if rig_checked:
            cod_alb = self.combo_albero.currentText().strip()
            cod_bom = self.combo_boma.currentText().strip()
            cod_vel = self.combo_vela.currentText().strip()
            
            if "Seleziona" in cod_alb or "Seleziona" in cod_bom or "Seleziona" in cod_vel:
                 QMessageBox.warning(self, "Selezione RIG Mancante", "Se hai selezionato 'Componi RIG', devi selezionare Albero, Boma e Vela validi.")
                 return

            codice = f"{cod_alb}-{cod_bom}-{cod_vel}"
            nome = f"Rig {cod_alb}-{cod_bom}-{cod_vel}"
            codice_barre_val = codice 
            barcode_val = codice_barre_val 
            tipo = "Rig"
            provenienza = "Composto"
            produttore = "N/A"

        foto_blob_data = None
        if self.foto_path and os.path.exists(self.foto_path):
            try:
                with open(self.foto_path, 'rb') as f:
                    foto_blob_data = f.read()
            except Exception as e:
                QMessageBox.warning(self, "Errore Lettura Foto", f"Impossibile leggere il file foto: {e}. Il materiale sarà salvato senza immagine BLOB.")
                foto_blob_data = None

        dati_per_db = (
            codice, tipo, nome, produttore, provenienza, descrizione, note,
            codice_barre_val, self.foto_path, disponibile, barcode_val, rig_checked, foto_blob_data
        )

        try:
            inserisci_materiale(dati_per_db)
            QMessageBox.information(self, "Successo", "Materiale aggiunto con successo!")
            self.carica_tabella()
            self.nuovo_materiale() 
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: materiali.codice" in str(e):
                QMessageBox.critical(self, "Errore di Codice", "Il codice inserito esiste già. Scegli un codice unico.")
            else:
                QMessageBox.critical(self, "Errore Database", f"Errore durante l'operazione sul database: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Errore Inserimento", str(e))

    def salva_modifiche_materiale_action(self):
        if self.current_material_id is None:
            QMessageBox.warning(self, "Attenzione", "Nessun materiale selezionato per la modifica. Seleziona una riga dalla tabella.")
            return

        codice = self.codice.text().strip()
        tipo = self.tipo.currentText()
        nome = self.nome.text().strip()
        produttore = self.produttore.text().strip()
        provenienza = self.provenienza.currentText()
        descrizione = self.descrizione.toPlainText().strip()
        note = self.note.toPlainText().strip() 
        
        rig_checked = 1 if self.rig_checkbox.isChecked() else 0
        
        disponibile = 1
        barcode_val = ""

        codice_barre_val = ""
        if produttore and nome:
            codice_barre_val = f"{codice}-{produttore}-{nome}"
        elif codice:
            codice_barre_val = codice
        
        if not barcode_val:
            barcode_val = codice_barre_val

        if not codice or not nome or not tipo:
            QMessageBox.warning(self, "Input Mancante", "Codice, Nome e Tipo sono campi obbligatori.")
            return

        if rig_checked:
            cod_alb = self.combo_albero.currentText().strip()
            cod_bom = self.combo_boma.currentText().strip()
            cod_vel = self.combo_vela.currentText().strip()
            
            if "Seleziona" in cod_alb or "Seleziona" in cod_bom or "Seleziona" in cod_vel:
                 QMessageBox.warning(self, "Selezione RIG Mancante", "Se hai selezionato 'Componi RIG', devi selezionare Albero, Boma e Vela validi.")
                 return

            codice = f"{cod_alb}-{cod_bom}-{cod_vel}"
            nome = f"Rig {cod_alb}-{cod_bom}-{cod_vel}"
            codice_barre_val = codice 
            barcode_val = codice_barre_val 
            tipo = "Rig"
            provenienza = "Composto"
            produttore = "N/A"

        # Gestione della foto BLOB (recupera BLOB esistente se non ne è stata caricata una nuova)
        foto_blob_data = None
        if self.foto_path and os.path.exists(self.foto_path):
            try:
                with open(self.foto_path, 'rb') as f:
                    foto_blob_data = f.read()
            except Exception as e:
                QMessageBox.warning(self, "Errore Lettura Foto", f"Impossibile leggere il file foto: {e}. Il materiale sarà salvato senza immagine BLOB.")
                foto_blob_data = None
        else: # Se non è stato selezionato un nuovo file foto, prova a recuperare il BLOB esistente dal DB
            materiale_esistente = get_materiale_by_id(self.current_material_id)
            if materiale_esistente and materiale_esistente[13] is not None: 
                foto_blob_data = materiale_esistente[13]
        
        dati_per_aggiornamento = (
            codice, tipo, nome, produttore, provenienza, descrizione, note,
            codice_barre_val, self.foto_path, disponibile, barcode_val, rig_checked, foto_blob_data,
            self.current_material_id 
        )
        try:
            aggiorna_materiale(dati_per_aggiornamento)
            QMessageBox.information(self, "Successo", "Materiale aggiornato con successo!")
            self.carica_tabella()
            self.nuovo_materiale() 
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: materiali.codice" in str(e):
                QMessageBox.critical(self, "Errore di Codice", "Il codice inserito esiste già. Scegli un codice unico.")
            else:
                QMessageBox.critical(self, "Errore Database", f"Errore durante l'operazione sul database: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Errore Aggiornamento", str(e))

    def elimina_selezionato(self):
        selected = self.tabella.currentRow()
        if selected >= 0:
            id_materiale_da_tabella = int(self.tabella.item(selected, 0).text())
            if self.current_material_id != id_materiale_da_tabella:
                QMessageBox.warning(self, "Selezione non valida", "Il materiale selezionato non corrisponde a quello caricato nel form. Clicca sulla riga desiderata prima di eliminare.")
                return

            reply = QMessageBox.question(self, 'Conferma Eliminazione', 
                                         f"Sei sicuro di voler eliminare il materiale con ID {self.current_material_id}?", 
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                try:
                    elimina_materiale(self.current_material_id) 
                    QMessageBox.information(self, "Successo", "Materiale eliminato con successo!")
                    self.carica_tabella()
                    self.nuovo_materiale() 
                except Exception as e:
                    QMessageBox.critical(self, "Errore Eliminazione", str(e))
        else:
            QMessageBox.warning(self, "Nessuna Selezione", "Seleziona un materiale dalla tabella per eliminarlo.")


    def carica_dettagli_riga(self):
        print("--- carica_dettagli_riga called ---")
        selected_row = self.tabella.currentRow()
        print(f"Selected row: {selected_row}")
        
        if selected_row < 0:
            print("No row selected or invalid row.")
            self.nuovo_materiale() 
            return

        id_item = self.tabella.item(selected_row, 0)
        
        if not id_item:
            print("ID item is None.")
            self.nuovo_materiale() 
            return

        try:
            self.current_material_id = int(id_item.text())
            print(f"Material ID retrieved: {self.current_material_id}")
        except ValueError as e:
            print(f"Error converting ID to int: {e}. ID text: {id_item.text()}")
            self.nuovo_materiale()
            return
        
        materiale = get_materiale_by_id(self.current_material_id)

        if materiale:
            print("Material found in DB. Populating form.")
            # Unpacking dei 14 elementi
            (
                id_db, codice, tipo, nome, produttore, provenienza, descrizione,
                note, codice_barre, foto_path_db, disponibile, barcode_db, rig, foto_db
            ) = materiale
            
            self.codice.setText(codice)
            self.tipo.setCurrentText(tipo)
            self.nome.setText(nome)
            self.produttore.setText(produttore)
            self.provenienza.setCurrentText(provenienza)
            self.descrizione.setPlainText(descrizione)
            self.note.setPlainText(note) 
            self.rig_checkbox.setChecked(bool(rig))

            # Gestione foto: assicurati che foto_db sia bytes
            loaded_photo = False 
            if foto_db: 
                pixmap = QPixmap()
                
                # Converti foto_db in bytes se è una stringa
                if isinstance(foto_db, str):
                    try:
                        foto_db = foto_db.encode('latin-1') 
                        print("DEBUG: foto_db convertito da str a bytes usando latin-1.")
                    except UnicodeEncodeError:
                        QMessageBox.warning(self, "Errore Foto", "Impossibile decodificare i dati della foto (stringa non valida o encoding errato).")
                        foto_db = None 
                
                if foto_db and isinstance(foto_db, (bytes, bytearray)): # Verifica che sia bytes prima di passare a loadFromData
                    if pixmap.loadFromData(foto_db) and not pixmap.isNull(): 
                        self.foto_label.setPixmap(pixmap.scaled(self.foto_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
                        loaded_photo = True
                        print("DEBUG: Foto caricata da BLOB con successo.")
                    else:
                        print(f"AVVISO: Caricamento foto da BLOB fallito o dati non validi. (DEBUG: foto_db type: {type(foto_db)}, len: {len(foto_db) if foto_db else 0})")
                else:
                    print(f"AVVISO: foto_db non è bytes valido per QPixmap.loadFromData. Tipo corrente: {type(foto_db)}")

                self.foto_path = "" 
            
            # Fallback al caricamento da path se il BLOB non è stato caricato
            if not loaded_photo and foto_path_db and os.path.exists(foto_path_db):
                pixmap = QPixmap(str(foto_path_db))
                if not pixmap.isNull(): 
                    self.foto_path = foto_path_db
                    self.foto_label.setPixmap(pixmap.scaled(self.foto_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    loaded_photo = True
                else:
                    print("AVVISO: Caricamento foto da PATH fallito o file non trovato/corrotto.")

            if not loaded_photo: 
                self.foto_label.clear()
                self.foto_path = ""


            # Gestione RIG
            if rig:
                parts = codice.split('-')
                if len(parts) == 3: 
                    self.combo_albero.setCurrentText(parts[0])
                    self.combo_boma.setCurrentText(parts[1])
                    self.combo_vela.setCurrentText(parts[2])
                self.rig_checkbox.setChecked(True)
                self.toggle_rig(2)
            else:
                self.rig_checkbox.setChecked(False)
                self.toggle_rig(0)
            
            # Abilita/Disabilita i pulsanti in modalità modifica
            self.btn_crea_o_salva_nuovo.setText("Crea Nuovo Materiale") 
            self.btn_crea_o_salva_nuovo.setEnabled(True) 
            self.btn_salva_modifiche.setEnabled(True)
            self.btn_elimina.setEnabled(True)
            print(f"Buttons state after population: Crea/Salva: {self.btn_crea_o_salva_nuovo.isVisible()}/{self.btn_crea_o_salva_nuovo.isEnabled()}, Salva Modifiche: {self.btn_salva_modifiche.isVisible()}/{self.btn_salva_modifiche.isEnabled()}, Elimina: {self.btn_elimina.isVisible()}/{self.btn_elimina.isEnabled()}")


        else:
            print("Material not found in DB. Resetting form.")
            self.nuovo_materiale() 
        
    def nuovo_materiale(self):
        self.current_material_id = None
        self.codice.clear()
        self.nome.clear()
        self.produttore.clear()
        self.descrizione.clear()
        self.note.clear()
        self.rig_checkbox.setChecked(False)
        self.tipo.setCurrentIndex(0)
        self.provenienza.setCurrentIndex(0)
        self.combo_albero.setCurrentIndex(0)
        self.combo_boma.setCurrentIndex(0)
        self.combo_vela.setCurrentIndex(0)
        self.foto_label.clear()
        self.foto_path = ""
        
        # Abilita/Disabilita i pulsanti in modalità nuovo inserimento
        self.btn_crea_o_salva_nuovo.setText("Salva Nuovo Materiale") 
        self.btn_crea_o_salva_nuovo.setEnabled(True) 
        self.btn_salva_modifiche.setEnabled(False) 
        self.btn_elimina.setEnabled(False) 

        self.toggle_rig(0)
        self.tipo.setDisabled(False)
    
    def carica_tabella(self):
        self.tabella.setRowCount(0)

        materiali = carica_materiali() 
        if materiali is None:
            materiali = []

        tipo_selezionato = self.filtro_tipo.currentText() if hasattr(self, "filtro_tipo") else "Tutti"
        nome_filtro = self.filtro_nome.text().lower() if hasattr(self, "filtro_nome") else ""
        produttore_filtro = self.filtro_produttore.text().lower() if hasattr(self, "filtro_produttore") else ""
        solo_disponibili = self.filtro_disponibile.isChecked() if hasattr(self, "filtro_disponibile") else False

        materiali_filtrati = []

        for mat in materiali: 
            if mat is None or len(mat) != 14: 
                print(f"AVVISO: Materiale con dati incompleti o None trovato: {mat}. Saltato.")
                continue
            
            codice = str(mat[1])
            tipo = str(mat[2])
            nome = str(mat[3])
            produttore = str(mat[4])
            disponibile = bool(mat[10])

            if tipo_selezionato != "Tutti" and tipo != tipo_selezionato:
                continue
            if nome_filtro and nome_filtro not in nome.lower():
                continue
            if produttore_filtro and produttore_filtro not in produttore.lower():
                continue
            if solo_disponibili and not disponibile:
                continue

            materiali_filtrati.append(mat)

        for row_idx, row_data in enumerate(materiali_filtrati):
            self.tabella.insertRow(row_idx)
            for col_idx in range(len(row_data)):
                self.tabella.setItem(row_idx, col_idx, QTableWidgetItem(str(row_data[col_idx])))