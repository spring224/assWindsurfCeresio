# dialogo_lista_soci.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor # Per colorare le righe della tabella, se necessario

import os
from data_access import (
    get_all_soci, delete_socio, mark_quota_pagata  # get_socio_photo_blob,
    # Aggiungi qui altre funzioni di data_access che userai per modificare/aggiungere socio
)
from dialogo_socio import DialogoSocio
from stampa_tessera_soci import stampa_tessera_pdf # Importa la funzione per stampare la tessera


class DialogoListaSoci(QDialog):
    def __init__(self, db_path, parent=None): # <-- MODIFICA QUESTA RIGA: aggiungi 'db_path'
        super().__init__(parent)
        self.db_path = db_path # <-- AGGIUNGI QUESTA RIGA: Salva il percorso del DB
        self.setWindowTitle("Lista Completa Soci Cicolo Nautico Ceresio")
        self.setMinimumSize(900, 600)
        self.init_ui() # Inizializza l'interfaccia utente

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # Sezione di Ricerca
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Cerca per nome, cognome, email o numero tessera...")
        self.search_input.setClearButtonEnabled(True)
        search_layout.addWidget(self.search_input)
        main_layout.addLayout(search_layout)

        # Tabella Soci
        self.tabella = QTableWidget(self)
        self.tabella.setColumnCount(7) # ID, Nome, Cognome, Email, Quota Pagata, Anno, Scadenza
        self.tabella.setHorizontalHeaderLabels([
            "ID", "Nome", "Cognome", "Email", "Quota Pagata", "Anno", "Scadenza"
        ])
        self.tabella.horizontalHeader().setStretchLastSection(True)
        self.tabella.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabella.setSelectionBehavior(QTableWidget.SelectRows) # Selezione intera riga
        self.tabella.setEditTriggers(QTableWidget.NoEditTriggers) # Non modificabile direttamente dalla tabella
        main_layout.addWidget(self.tabella)

        # Pulsanti Azione
        buttons_layout = QHBoxLayout()
        self.btn_aggiungi = QPushButton("Aggiungi Socio")
        self.btn_modifica = QPushButton("Modifica Socio")
        self.btn_tessera= QPushButton("Stampa Tessera") # Inizialmente disabilitato, abilitato dopo selezione
        self.btn_elimina = QPushButton("Elimina Socio")
        self.btn_quota = QPushButton("Pagamento Quota Annuale")
        self.btn_esporta_excel = QPushButton("Esporta Excel")
        self.btn_chiudi = QPushButton("Chiudi")

        buttons_layout.addWidget(self.btn_aggiungi)
        buttons_layout.addWidget(self.btn_modifica)
        buttons_layout.addWidget(self.btn_tessera)
        buttons_layout.addWidget(self.btn_elimina)
        buttons_layout.addWidget(self.btn_quota)
        buttons_layout.addStretch(1) # Spinge i pulsanti a sinistra
        buttons_layout.addWidget(self.btn_esporta_excel)
        buttons_layout.addWidget(self.btn_chiudi)
        main_layout.addLayout(buttons_layout)

        # Connessioni dei segnali
        self.btn_chiudi.clicked.connect(self.close)
        self.btn_aggiungi.clicked.connect(self.apri_dialogo_aggiungi_socio)
        self.btn_modifica.clicked.connect(self.apri_dialogo_modifica_socio)
        self.btn_tessera.clicked.connect(self.stampa_tessera_selezionata)
        self.btn_elimina.clicked.connect(self.elimina_socio_selezionato)
        self.btn_quota.clicked.connect(self.marca_quota_pagata)
        self.btn_esporta_excel.clicked.connect(self.esporta_dati_excel)
        self.search_input.textChanged.connect(self.filtra_soci)
        self.tabella.doubleClicked.connect(self.apri_dialogo_modifica_socio) # Doppio click per modificare
        self.carica_dati() # Carica i dati iniziali nella tabella

    def carica_dati(self):
        self.tabella.setRowCount(0) # Pulisce la tabella
        soci = get_all_soci(self.db_path) # <-- MODIFICA QUESTA RIGA: passa 'self.db_path

        #print(f"DEBUG: I dati restituiti da get_all_soci sono: {soci}") 

        for row_num, socio in enumerate(soci):
            self.tabella.insertRow(row_num)
            columns = [
                str(socio.get('id', '')),
                socio.get('nome', ''),
                socio.get('cognome', ''),
                socio.get('email', ''),
                "Sì" if socio.get('quota_pagata', 0) == 1 else "No",
                str(socio.get('anno', '')),
                str(socio.get('data_scadenza', ''))
            ]
            for col_num, data in enumerate(columns):
                item = QTableWidgetItem(str(data))
                item.setTextAlignment(Qt.AlignCenter)
                self.tabella.setItem(row_num, col_num, item)
            
            # Applica colorazione se la quota non è pagata
            if socio.get('quota_pagata', 0) == 0:
                for col in range(self.tabella.columnCount()):
                    self.tabella.item(row_num, col).setBackground(QColor(255, 230, 230)) # Rosso chiaro
        
        self.filtra_soci(self.search_input.text()) # Applica il filtro se c'è testo di ricerca

    def filtra_soci(self, text):
        search_text = text.strip().lower()
        for row in range(self.tabella.rowCount()):
            match = False
            for col in range(self.tabella.columnCount()):
                item = self.tabella.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.tabella.setRowHidden(row, not match)

    def apri_dialogo_aggiungi_socio(self):
        dialog = DialogoSocio(parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.carica_dati() # Ricarica i dati dopo aver aggiunto un nuovo socio

    # Nel file: dialogo_lista_soci.py

    def apri_dialogo_modifica_socio(self):
        # RECUPERA L'ID DEL SOCIO SELEZIONATO DALLA TABELLA
        row = self.tabella.currentRow()
        if row < 0: # Nessuna riga selezionata
            QMessageBox.warning(self, "Selezione Socio", "Seleziona un socio dalla lista per modificarlo.")
            return

        # L'ID del socio è nella prima colonna (indice 0)
        socio_id_item = self.tabella.item(row, 0)
        if socio_id_item is None:
            QMessageBox.warning(self, "Errore", "Impossibile recuperare l'ID del socio selezionato.")
            return

        socio_selezionato_id = int(socio_id_item.text())

        # Questa è la riga cruciale che deve passare self.db_path e socio_selezionato_id
        dialog = DialogoSocio(self.db_path, socio_id=socio_selezionato_id, parent=self) # <<< MODIFICA QUESTA RIGA
        if dialog.exec() == QDialog.Accepted:
            QMessageBox.information(self, "Informazione", "Socio modificato con successo.")
            self.carica_dati() # Ricarica i dati dopo la modifica per vedere gli aggiornamenti
        else:
            QMessageBox.information(self, "Informazione", "Operazione di modifica socio annullata.")
            
    def elimina_socio_selezionato(self):
        selected_rows = self.tabella.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Selezione", "Seleziona un socio da eliminare.")
            return

        row = selected_rows[0].row()
        socio_id_item = self.tabella.item(row, 0)
        if socio_id_item:
            socio_id = int(socio_id_item.text())

            reply = QMessageBox.question(self, 'Conferma Eliminazione',
                                         f"Sei sicuro di voler eliminare il socio con ID {socio_id}?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                if delete_socio(self.db_path, socio_id): # 
                    QMessageBox.information(self, "Successo", "Socio eliminato con successo!")
                    self.carica_dati()
                else:
                    QMessageBox.critical(self, "Errore", "Impossibile eliminare il socio.")
        else:
            QMessageBox.warning(self, "Errore", "ID Socio non trovato per la riga selezionata.")

    def marca_quota_pagata(self):
        selected_rows = self.tabella.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Selezione", "Seleziona un socio per Validare la quota annuale pagata.")
            return

        row = selected_rows[0].row()
        socio_id_item = self.tabella.item(row, 0)
        if socio_id_item:
            socio_id = int(socio_id_item.text())

            if QMessageBox.question(self, "Conferma Quota",
                                    f"Vuoi marcare la quota del socio ID {socio_id} come PAGATA?",
                                    QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                print(f"***** DEBUG (dialogo_lista_soci): STO PER CHIAMARE mark_quota_pagata con ID: {socio_id} *****") # AGGIUNGI QUESTA RIGA!
                if mark_quota_pagata(socio_id):
                    QMessageBox.information(self, "Successo", "Quota marcata come pagata!")
                    self.carica_dati()
                else:
                    QMessageBox.critical(self, "Errore", "Impossibile marcare la quota come pagata.")
        else:
            QMessageBox.warning(self, "Errore", "ID Socio non trovato per la riga selezionata.")

    def esporta_dati_excel(self):
        try:
            import openpyxl
        except ImportError:
            QMessageBox.critical(self, "Errore", "La libreria 'openpyxl' non è installata. Installa con: pip install openpyxl")
            return

        file_name, _ = QFileDialog.getSaveFileName(self, "Salva report Excel", "report_soci.xlsx", "Excel Files (*.xlsx)")
        if file_name:
            try:
                wb = openpyxl.Workbook()
                ws = wb.active
                ws.title = "Soci Windsurf"

                headers = [self.tabella.horizontalHeaderItem(col).text() for col in range(self.tabella.columnCount())]
                ws.append(headers)

                for row in range(self.tabella.rowCount()):
                    row_data = []
                    for col in range(self.tabella.columnCount()):
                        item = self.tabella.item(row, col)
                        row_data.append(item.text() if item else "")
                    ws.append(row_data)

                wb.save(file_name)
                QMessageBox.information(self, "Esportazione Completata", f"Dati esportati con successo in:\\n{file_name}")
            except Exception as e:
                QMessageBox.critical(self, "Errore Esportazione", f"Si è verificato un errore durante l'esportazione:\\n{e}")

    def stampa_tessera_selezionata(self):
        row = self.tabella.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona un socio per stampare la tessera.")
            return

        socio_id_item = self.tabella.item(row, 0)
        if socio_id_item:
            socio_id = int(socio_id_item.text())
            stampa_tessera_pdf(self.db_path, socio_id, parent_widget=self) # <<< AGGIUNTO self.db_path
            QMessageBox.information(self, "Stampa Tessera", "Tessera stampata con successo!")
        else:
            QMessageBox.warning(self, "Errore", "ID Socio non trovato per la riga selezionata.")