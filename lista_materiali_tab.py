
# lista_materiali_tab.py

import os
from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QComboBox,
    QVBoxLayout, QHBoxLayout, QCheckBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QGroupBox,
    QSpacerItem, QSizePolicy, QAbstractItemView
)
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt, Signal

# Importa le funzioni di accesso ai dati necessarie a questa scheda
from data_access import (
    elimina_materiale,
    carica_materiali,
    carica_materiali_rig # Per popolare la mappa dei Rig
)

class MaterialiListaTab(QWidget):
    # Segnali per comunicare con il dialogo principale
    material_selected = Signal(int)
    add_new_material_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # --- SPOSTA QUESTO BLOCCO ALL'INIZIO DI __init__ ---
        self.rig_padri_map = {}
        self._carica_rig_padri_map()
        # ----------------------------------------------------
        
        self.init_ui() # init_ui ora è chiamato dopo che rig_padri_map è pronto
        
        # Questa chiamata a carica_tabella() qui è ridondante se le combobox
        # già la attivano. Potremmo valutarne la rimozione dopo aver verificato
        # il comportamento, ma per ora la lasciamo per sicurezza.
        self.carica_tabella() 

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # --- Filtri ---
        filtri_group_box = QGroupBox("Filtri")
        filtri_layout = QHBoxLayout()

        self.filtro_tipo = QComboBox()
        self.filtro_tipo.addItems(["Tutti", "Sup", "Canoa", "Pagaia", "Salvagente", "Tavola Windsurf", "Vela", "Boma", "Albero", "Bici d'acqua", "Tandem Sup", "Rig", "Muta", "Trapezio", "Accessorio"])
        self.filtro_tipo.currentTextChanged.connect(self.carica_tabella) # Questa connessione ora chiamerà carica_tabella DOPO che la mappa è pronta
        filtri_layout.addWidget(QLabel("Tipo:"))
        filtri_layout.addWidget(self.filtro_tipo)

        self.filtro_nome = QLineEdit()
        self.filtro_nome.setPlaceholderText("Filtra per nome...")
        self.filtro_nome.textChanged.connect(self.carica_tabella)
        filtri_layout.addWidget(QLabel("Nome:"))
        filtri_layout.addWidget(self.filtro_nome)

        self.filtro_produttore = QLineEdit()
        self.filtro_produttore.setPlaceholderText("Filtra per produttore...")
        self.filtro_produttore.textChanged.connect(self.carica_tabella)
        filtri_layout.addWidget(QLabel("Produttore:"))
        filtri_layout.addWidget(self.filtro_produttore)

        self.filtro_disponibile = QCheckBox("Solo Disponibili")
        self.filtro_disponibile.stateChanged.connect(self.carica_tabella)
        filtri_layout.addWidget(self.filtro_disponibile)
        
        filtri_layout.addStretch(1)
        filtri_group_box.setLayout(filtri_layout)
        main_layout.addWidget(filtri_group_box)

        # --- Tabella Materiali ---
        self.tabella = QTableWidget()
        self.tabella.setColumnCount(12)
        self.tabella.setHorizontalHeaderLabels([
            "ID", "Codice", "Tipo", "Nome", "Produttore", "Provenienza",
            "Descrizione", "Note", "Codice a Barre", "Foto Path", "Disponibile", "Rig Padre"
        ])
        self.tabella.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tabella.horizontalHeader().setStretchLastSection(True)
        self.tabella.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabella.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabella.doubleClicked.connect(self.modifica_materiale_selezionato)
        main_layout.addWidget(self.tabella)

        # --- Bottoni ---
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Aggiungi Materiale")
        self.add_button.clicked.connect(self.add_new_material_requested.emit)
        button_layout.addWidget(self.add_button)

        self.edit_button = QPushButton("Modifica Materiale")
        self.edit_button.clicked.connect(self.modifica_materiale_selezionato)
        button_layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("Elimina Materiale")
        self.delete_button.clicked.connect(self.elimina_materiale_selezionato)
        button_layout.addWidget(self.delete_button)

        self.refresh_button = QPushButton("Aggiorna Lista")
        self.refresh_button.clicked.connect(self.carica_tabella)
        button_layout.addWidget(self.refresh_button)

        button_layout.addStretch(1)
        main_layout.addLayout(button_layout)

    def _carica_rig_padri_map(self):
        """Carica una mappa degli ID dei materiali 'Rig' ai loro nomi."""
        self.rig_padri_map = {0: "Nessuno"}
        rig_materials = carica_materiali_rig()
        for rig in rig_materials:
            if rig.get('id') is not None and rig.get('nome') is not None:
                self.rig_padri_map[rig.get('id')] = rig.get('nome')

    def carica_tabella(self):
        self.tabella.setRowCount(0)

        tipo_selezionato = self.filtro_tipo.currentText()
        nome_filtro = self.filtro_nome.text().strip().lower()
        produttore_filtro = self.filtro_produttore.text().strip().lower()
        solo_disponibili = self.filtro_disponibile.isChecked()
        
        materiali = carica_materiali() 

        materiali_filtrati = []

        for mat_data in materiali:
            tipo = mat_data.get('tipo', '')
            nome = mat_data.get('nome', '')
            produttore = mat_data.get('produttore', '')
            disponibile = mat_data.get('disponibile', 1) 

            if tipo_selezionato != "Tutti" and tipo != tipo_selezionato:
                continue
            if nome_filtro and nome_filtro not in nome.lower():
                continue
            if produttore_filtro and produttore_filtro not in produttore.lower():
                continue
            if solo_disponibili and not disponibile:
                continue

            materiali_filtrati.append(mat_data)

        self.tabella.setRowCount(len(materiali_filtrati))
        for row_idx, mat_data in enumerate(materiali_filtrati):
            self.tabella.setItem(row_idx, 0, QTableWidgetItem(str(mat_data.get("id", ""))))
            self.tabella.setItem(row_idx, 1, QTableWidgetItem(mat_data.get("codice", "")))
            self.tabella.setItem(row_idx, 2, QTableWidgetItem(mat_data.get("tipo", "")))
            self.tabella.setItem(row_idx, 3, QTableWidgetItem(mat_data.get("nome", "")))
            self.tabella.setItem(row_idx, 4, QTableWidgetItem(mat_data.get("produttore", "")))
            self.tabella.setItem(row_idx, 5, QTableWidgetItem(mat_data.get("provenienza", "")))
            self.tabella.setItem(row_idx, 6, QTableWidgetItem(mat_data.get("descrizione", "")))
            self.tabella.setItem(row_idx, 7, QTableWidgetItem(mat_data.get("note", "")))
            self.tabella.setItem(row_idx, 8, QTableWidgetItem(mat_data.get("codice_barre", ""))) 
            self.tabella.setItem(row_idx, 9, QTableWidgetItem(mat_data.get("foto_path", "")))
            
            disponibile_item = QTableWidgetItem("Sì" if mat_data.get('disponibile', 1) else "No")
            disponibile_item.setTextAlignment(Qt.AlignCenter)
            self.tabella.setItem(row_idx, 10, disponibile_item)

            rig_padre_id = mat_data.get('rig', 0)
            rig_padre_nome = self.rig_padri_map.get(rig_padre_id, "Nessuno") 
            self.tabella.setItem(row_idx, 11, QTableWidgetItem(rig_padre_nome)) 

            self.tabella.setColumnHidden(5, True) # Provenienza
            self.tabella.setColumnHidden(6, True) # Descrizione
            self.tabella.setColumnHidden(7, True) # Note
            self.tabella.setColumnHidden(9, True) # Foto Path
            
            if not mat_data.get('disponibile', 1):
                for col in range(self.tabella.columnCount()):
                    item = self.tabella.item(row_idx, col)
                    if item:
                        item.setBackground(QColor(255, 200, 200))

    def modifica_materiale_selezionato(self):
        selected_rows = self.tabella.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Selezione Materiale", "Seleziona un materiale da modificare.")
            return

        row_idx = selected_rows[0].row()
        material_id = int(self.tabella.item(row_idx, 0).text())
        self.material_selected.emit(material_id)

    def elimina_materiale_selezionato(self):
        selected_rows = self.tabella.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Selezione Materiale", "Seleziona uno o più materiali da eliminare.")
            return

        reply = QMessageBox.question(self, 'Conferma Eliminazione', 
                                    "Sei sicuro di voler eliminare i materiali selezionati?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            ids_da_eliminare = []
            for row_model_index in selected_rows:
                row_idx = row_model_index.row()
                material_id = int(self.tabella.item(row_idx, 0).text())
                ids_da_eliminare.append(material_id)
            
            success_count = 0
            for material_id in ids_da_eliminare:
                if elimina_materiale(material_id):
                    success_count += 1
            
            if success_count > 0:
                QMessageBox.information(self, "Eliminazione Completata", 
                                        f"Eliminati {success_count} materiali con successo.")
                self.carica_tabella()
            else:
                QMessageBox.warning(self, "Errore Eliminazione", "Nessun materiale è stato eliminato.")