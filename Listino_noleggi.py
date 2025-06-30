# Listino_noleggi.py
# Listino_noleggi.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QComboBox, QHeaderView, QAbstractItemView,
    QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt
# IMPORTANTE: Importa la nuova funzione
from data_access import get_all_material_types_and_names, carica_listino, salva_listino


class FinestraListino(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestione Listino Noleggio")
        self.resize(900, 600) # Aumenta la larghezza per la nuova colonna
        
        # Ora carichiamo una lista di tuple (tipo, nome)
        self.material_types_and_names = []
        self._carica_tipi_e_nomi_materiali()
        
        self.init_ui()
        self.carica_listino_ui()

    def _carica_tipi_e_nomi_materiali(self):
        """Carica i tipi e nomi distinti dei materiali dal database Materiali."""
        # Ottiene (tipo, nome) da Materiali
        material_pairs = get_all_material_types_and_names()
        
        # Prepara la lista per la QComboBox, es: ["Tipo1 - Nome1", "Tipo2 - Nome2"]
        # E una voce iniziale "Seleziona Materiale"
        self.material_types_and_names = ["Seleziona Materiale"] + \
                                        [f"{t[0]} - {t[1]}" for t in material_pairs]
        # print(f"DEBUG: Tipi e nomi materiali caricati: {self.material_types_and_names}") # DEBUG

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # --- Tabella ---
        self.tabella = QTableWidget()
        # Aumentato a 4 colonne
        self.tabella.setColumnCount(4)
        self.tabella.setHorizontalHeaderLabels(["Tipo", "Nome Materiale", "Descrizione", "Prezzo Orario (€)"])
        
        # Imposta la larghezza delle colonne
        self.tabella.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents) # Tipo
        self.tabella.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents) # Nome Materiale
        self.tabella.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch) # Descrizione
        self.tabella.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents) # Prezzo
        
        self.tabella.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.SelectedClicked)
        self.tabella.itemChanged.connect(self._handle_item_changed)
        
        main_layout.addWidget(self.tabella)

        # ... (Bottoni di Gestione Righe - rimangono uguali per ora) ...
        row_buttons_layout = QHBoxLayout()
        self.add_row_button = QPushButton("Aggiungi Riga")
        self.add_row_button.clicked.connect(self.add_listino_row)
        row_buttons_layout.addWidget(self.add_row_button)

        self.remove_row_button = QPushButton("Rimuovi Riga")
        self.remove_row_button.clicked.connect(self.remove_listino_row)
        row_buttons_layout.addWidget(self.remove_row_button)

        row_buttons_layout.addStretch(1)
        main_layout.addLayout(row_buttons_layout)

        # ... (Bottoni Azione - rimangono uguali) ...
        action_buttons_layout = QHBoxLayout()
        self.save_button = QPushButton("Salva Modifiche")
        self.save_button.clicked.connect(self.salva_listino_noleggio)
        action_buttons_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("Annulla Modifiche")
        self.cancel_button.clicked.connect(self.carica_listino_ui)
        action_buttons_layout.addWidget(self.cancel_button)

        action_buttons_layout.addStretch(1)
        main_layout.addLayout(action_buttons_layout)
    
    def _handle_item_changed(self, item):
        """Gestisce il cambio del testo in una cella."""
        # Se la modifica avviene nelle colonne Tipo (0) o Nome Materiale (1), non facciamo nulla qui
        # perché la gestione della QComboBox è separata
        if item.column() == 0 or item.column() == 1:
            return
        
        # Validazione prezzo
        if item.column() == 3: # Prezzo Orario (€) è ora la colonna 3
            try:
                float(item.text().replace(",", "."))
                item.setBackground(Qt.white)
            except ValueError:
                item.setBackground(Qt.red)
                QMessageBox.warning(self, "Errore Formato", "Il prezzo deve essere un numero valido.")

    def add_listino_row(self):
        """Aggiunge una nuova riga vuota alla tabella del listino."""
        current_row_count = self.tabella.rowCount()
        self.tabella.insertRow(current_row_count)

        # Colonna "Tipo" e "Nome Materiale" (0): Inserisci una QComboBox che contiene entrambi
        combo_box = QComboBox()
        combo_box.addItems(self.material_types_and_names)
        combo_box.currentIndexChanged.connect(
            lambda index, row=current_row_count: self._update_table_items_from_combobox(row, index, combo_box)
        )
        self.tabella.setCellWidget(current_row_count, 0, combo_box)
        
        # Inizializza QTableWidgetItem per Tipo e Nome Materiale (IMPORTANTE per la lettura)
        self.tabella.setItem(current_row_count, 0, QTableWidgetItem("")) # Tipo
        self.tabella.setItem(current_row_count, 1, QTableWidgetItem("")) # Nome Materiale
        
        # Colonna "Descrizione" (2)
        desc_item = QTableWidgetItem("")
        self.tabella.setItem(current_row_count, 2, desc_item)
        
        # Colonna "Prezzo Orario" (3)
        price_item = QTableWidgetItem("0.0")
        price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.tabella.setItem(current_row_count, 3, price_item) # Ora colonna 3
        
        self.tabella.setCurrentCell(current_row_count, 0)
        
    def _update_table_items_from_combobox(self, row, index, combo_box):
        """Aggiorna i QTableWidgetItem di Tipo e Nome Materiale quando la QComboBox cambia selezione."""
        selected_text = combo_box.currentText()
        if selected_text == "Seleziona Materiale":
            if self.tabella.item(row, 0): self.tabella.item(row, 0).setText("")
            if self.tabella.item(row, 1): self.tabella.item(row, 1).setText("")
            return

        # Splitta il testo per ottenere tipo e nome
        parts = selected_text.split(' - ', 1) # Splitta solo al primo ' - '
        tipo = parts[0].strip()
        nome_materiale = parts[1].strip() if len(parts) > 1 else ""

        # Aggiorna il QTableWidgetItem per la colonna Tipo (0)
        item_tipo = self.tabella.item(row, 0)
        if item_tipo is None:
            item_tipo = QTableWidgetItem()
            self.tabella.setItem(row, 0, item_tipo)
        item_tipo.setText(tipo)
        
        # Aggiorna il QTableWidgetItem per la colonna Nome Materiale (1)
        item_nome = self.tabella.item(row, 1)
        if item_nome is None:
            item_nome = QTableWidgetItem()
            self.tabella.setItem(row, 1, item_nome)
        item_nome.setText(nome_materiale)


    def remove_listino_row(self):
        """Rimuove la riga selezionata dalla tabella del listino."""
        selected_rows = self.tabella.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Selezione Riga", "Seleziona una o più righe da rimuovere.")
            return

        reply = QMessageBox.question(self, 'Conferma Eliminazione', 
                                    "Sei sicuro di voler eliminare le righe selezionate?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            rows_to_remove = sorted([r.row() for r in selected_rows], reverse=True)
            for row_idx in rows_to_remove:
                widget = self.tabella.cellWidget(row_idx, 0)
                if isinstance(widget, QComboBox):
                    widget.currentIndexChanged.disconnect()
                self.tabella.removeRow(row_idx)
            QMessageBox.information(self, "Righe Rimosse", "Le righe selezionate sono state rimosse.")


    def carica_listino_ui(self):
        """Carica i dati del listino dal database e li visualizza nella tabella."""
        self.tabella.setRowCount(0)
        listino_data = carica_listino() # Ottiene i dati dal data_access

        if not listino_data:
            return

        self.tabella.setRowCount(len(listino_data))
        for row_idx, item_data in enumerate(listino_data):
            # Colonna "Tipo" (0): QComboBox (visualizza "Tipo - Nome Materiale")
            combo_box = QComboBox()
            combo_box.addItems(self.material_types_and_names)
            
            # Cerca il testo combinato "Tipo - Nome Materiale" per impostare la ComboBox
            combined_text = f"{item_data.get('tipo', '')} - {item_data.get('nome_materiale', '')}"
            try:
                current_index = self.material_types_and_names.index(combined_text)
                combo_box.setCurrentIndex(current_index)
            except ValueError:
                # Se la combinazione non esiste nella lista, imposta su "Seleziona Materiale"
                combo_box.setCurrentIndex(0)
            
            combo_box.currentIndexChanged.connect(
                lambda index, row=row_idx: self._update_table_items_from_combobox(row, index, combo_box)
            )
            self.tabella.setCellWidget(row_idx, 0, combo_box)

            # Crea/Aggiorna i QTableWidgetItem per Tipo e Nome Materiale (necessari per la lettura)
            type_item = QTableWidgetItem(item_data.get("tipo", ""))
            self.tabella.setItem(row_idx, 0, type_item)
            
            name_item = QTableWidgetItem(item_data.get("nome_materiale", ""))
            self.tabella.setItem(row_idx, 1, name_item) # Colonna 1 per Nome Materiale
            
            # Colonna "Descrizione" (2)
            desc_item = QTableWidgetItem(item_data.get("descrizione", ""))
            self.tabella.setItem(row_idx, 2, desc_item) # Ora colonna 2
            
            # Colonna "Prezzo Orario" (3)
            prezzo_value = item_data.get('prezzo_orario', 0.0)
            if isinstance(prezzo_value, str):
                try:
                    prezzo_value = float(prezzo_value.replace(",", "."))
                except ValueError:
                    prezzo_value = 0.0
            
            prezzo_str = f"{prezzo_value:.2f}"
            price_item = QTableWidgetItem(prezzo_str.replace(".", ","))
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabella.setItem(row_idx, 3, price_item) # Ora colonna 3


    def salva_listino_noleggio(self):
        """Raccoglie i dati dalla tabella e li salva nel database."""
        righe_da_salvare = []
        for row_idx in range(self.tabella.rowCount()):
            # Recupera il Tipo dalla QTableWidgetItem della colonna 0
            tipo_item = self.tabella.item(row_idx, 0)
            tipo = tipo_item.text().strip() if tipo_item else ""
            
            # Recupera il Nome Materiale dalla QTableWidgetItem della colonna 1
            nome_materiale_item = self.tabella.item(row_idx, 1)
            nome_materiale = nome_materiale_item.text().strip() if nome_materiale_item else ""
            
            descrizione_item = self.tabella.item(row_idx, 2) # Ora colonna 2
            descrizione = descrizione_item.text().strip() if descrizione_item else ""

            prezzo_item = self.tabella.item(row_idx, 3) # Ora colonna 3
            if not prezzo_item or not prezzo_item.text():
                QMessageBox.warning(self, "Errore", f"Prezzo mancante alla riga {row_idx+1}.")
                return

            try:
                prezzo = float(prezzo_item.text().strip().replace(",", "."))
            except ValueError:
                QMessageBox.warning(self, "Errore", f"Prezzo non valido alla riga {row_idx+1}. Inserire un numero.")
                return
            
            # Validazione più robusta
            if not tipo or tipo == "Seleziona Materiale" or not nome_materiale:
                QMessageBox.warning(self, "Dati Incompleti", f"Riga {row_idx+1}: Selezionare un Tipo e Nome Materiale validi.")
                return
            
            if prezzo < 0:
                QMessageBox.warning(self, "Dati Non Validi", f"Riga {row_idx+1}: Il prezzo non può essere negativo.")
                return

            # Aggiungi sia tipo che nome_materiale al dizionario
            righe_da_salvare.append({
                "tipo": tipo,
                "nome_materiale": nome_materiale,
                "descrizione": descrizione,
                "prezzo_orario": prezzo
            })

        if not righe_da_salvare:
            QMessageBox.information(self, "Nessun Dato", "Nessuna riga valida da salvare.")
            return

        success, errore = salva_listino(righe_da_salvare)
        if success:
            QMessageBox.information(self, "Listino Salvato", "Le modifiche sono state salvate con successo.")
            self.carica_listino_ui()
        else:
            QMessageBox.critical(self, "Errore di Salvataggio", f"Si è verificato un errore durante il salvataggio del listino: {errore}")