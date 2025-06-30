# gestisci_tessere.py
# >>> MODIFICA QUI GLI IMPORT:
from PySide6.QtGui import QTextDocument, QDesktopServices # QPrinter non è più qui
from PySide6.QtPrintSupport import QPrinter, QPrintDialog # QPrinter e QPrintDialog sono qui ora!
from PySide6.QtCore import Qt, QDate, QUrl # Aggiungo QUrl per aprire i file locali
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QTabWidget, QLabel,
    QDialog, QFormLayout, QLineEdit, QComboBox, QTimeEdit, QListWidget,
    QPlainTextEdit, QCalendarWidget,QGridLayout # QCalendarWidget spostato qui
)
# Per QPrinter e QPrintDialog (per la stampa)
from PySide6.QtPrintSupport import QPrinter # Solo QPrinter per il PDF
# Per QTextDocument, QDesktopServices, QFont, QColor
from PySide6.QtGui import QTextDocument, QDesktopServices, QFont, QColor
# Per Qt, QDate, QUrl, QTime
from PySide6.QtCore import Qt, QDate, QUrl, QTime

# Importa le funzioni dal tuo data_access.py
# <<< FINE MODIFICA IMPORT
# Aggiorna l'import delle funzioni dal data_access
from data_access import (
    get_tessere, usa_item_tessera,
    salva_lezione_programmata, get_lezioni_per_data, 
    aggiorna_stato_lezione, cancella_lezione_programmata,
    get_tessere_per_selezione_lezione, get_lezione_by_id # Aggiunto get_lezione_by_id
)

import os
from pathlib import Path

class FinestraGestisciTessera(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestione Tessere Noleggi e Corsi")
        self.init_ui()
        self.load_tessere_attive() # Carica le tessere attive all'avvio
        self.calendar_widget.setSelectedDate(QDate.currentDate()) # Seleziona la data odierna sul calendario
        self.load_lezioni_for_selected_date() # Carica le lezioni per la data odierna

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # --- Tab: Tessere Attive (Codice esistente, non lo riporto per brevità) ---
        self.tab_attive = QWidget()
        self.tab_widget.addTab(self.tab_attive, "Tessere Attive")
        self.layout_attive = QVBoxLayout(self.tab_attive)
        # ... (tutto il tuo codice esistente per self.table_attive e i bottoni) ...
        self.table_attive = QTableWidget()
        self.table_attive.setColumnCount(8)
        self.table_attive.setHorizontalHeaderLabels([
            "ID Tessera", "Cliente", "Tipo Tessera", "Items Totali", 
            "Items Usati", "Prezzo Totale", "Data Creazione", "Nazione"
        ])
        self.table_attive.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_attive.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_attive.setEditTriggers(QTableWidget.NoEditTriggers)
        self.layout_attive.addWidget(self.table_attive)
        
        buttons_attive_layout = QHBoxLayout()
        self.btn_usa_item = QPushButton("✅ Usa un Item Selezionato")
        self.btn_stampa_promemoria = QPushButton("🖨️ Stampa Promemoria Tessera")
        self.btn_rinfresca_attive = QPushButton("🔄 Ricarica")

        self.btn_usa_item.clicked.connect(self.usa_item_tessera_selezionata)
        self.btn_stampa_promemoria.clicked.connect(self.stampa_promemoria_tessera_selezionata)
        self.btn_rinfresca_attive.clicked.connect(self.load_tessere_attive)

        buttons_attive_layout.addWidget(self.btn_usa_item)
        buttons_attive_layout.addWidget(self.btn_stampa_promemoria)
        buttons_attive_layout.addWidget(self.btn_rinfresca_attive)
        self.layout_attive.addLayout(buttons_attive_layout)


        # --- Tab: Storico Tessere (Codice esistente, non lo riporto per brevità) ---
        self.tab_storico = QWidget()
        self.tab_widget.addTab(self.tab_storico, "Storico Tessere")
        self.layout_storico = QVBoxLayout(self.tab_storico)
        # ... (tutto il tuo codice esistente per self.table_storico e i bottoni) ...
        self.table_storico = QTableWidget()
        self.table_storico.setColumnCount(8)
        self.table_storico.setHorizontalHeaderLabels([
            "ID Tessera", "Cliente", "Tipo Tessera", "Items Totali", 
            "Items Usati", "Prezzo Totale", "Data Creazione", "Nazione"
        ])
        self.table_storico.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_storico.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_storico.setEditTriggers(QTableWidget.NoEditTriggers)
        self.layout_storico.addWidget(self.table_storico)

        buttons_storico_layout = QHBoxLayout()
        self.btn_rinfresca_storico = QPushButton("🔄 Ricarica Storico")
        self.btn_rinfresca_storico.clicked.connect(self.load_storico_tessere)
        buttons_storico_layout.addWidget(self.btn_rinfresca_storico)
        self.layout_storico.addLayout(buttons_storico_layout)


        # --- NUOVO TAB: Calendario Lezioni ---
        self.tab_calendario = QWidget()
        self.tab_widget.addTab(self.tab_calendario, "Calendario Lezioni")
        self.layout_calendario = QHBoxLayout(self.tab_calendario)

        # Lato sinistro: Calendario
        left_layout = QVBoxLayout()
        self.calendar_widget = QCalendarWidget()
        self.calendar_widget.setGridVisible(True)
        self.calendar_widget.clicked[QDate].connect(self.load_lezioni_for_selected_date)
        left_layout.addWidget(QLabel("<h2>Seleziona Data Lezione</h2>"))
        left_layout.addWidget(self.calendar_widget)
        self.layout_calendario.addLayout(left_layout, 2) # Peso 1

        # Lato destro: Dettagli Lezioni per la data selezionata
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("<h2>Lezioni Programmate per Data Selezionata</h2>"))
       
        
        self.lessons_list_widget = QListWidget()
        self.lessons_list_widget.itemClicked.connect(self.display_lezione_details)
        right_layout.addWidget(self.lessons_list_widget)

        # Campi di input per Aggiungi/Modifica Lezione
        form_lezione_layout = QFormLayout()
        self.cmb_tessera_lezione = QComboBox()
        self.cmb_tessera_lezione.setPlaceholderText("Seleziona Tessera...")
        form_lezione_layout.addRow("Tessera Cliente:", self.cmb_tessera_lezione)

        self.time_edit_lezione = QTimeEdit()
        self.time_edit_lezione.setDisplayFormat("HH:mm")
        self.time_edit_lezione.setTime(QTime(9, 0)) # Ora di default
        form_lezione_layout.addRow("Ora Lezione:", self.time_edit_lezione)

        self.txt_descrizione_lezione = QLineEdit()
        form_lezione_layout.addRow("Descrizione:", self.txt_descrizione_lezione)

        self.txt_note_lezione = QPlainTextEdit()
        self.txt_note_lezione.setPlaceholderText("Note aggiuntive sulla lezione...")
        self.txt_note_lezione.setMaximumHeight(60) # Limita altezza
        form_lezione_layout.addRow("Note:", self.txt_note_lezione)

        right_layout.addLayout(form_lezione_layout)

        #Pulsanti per Aggiungi/Modifica/Elimina/Stato Lezione
        # Modifica: Usa QGridLayout per disporre i pulsanti su due colonne
        buttons_lezioni_layout = QGridLayout() # CAMBIATO IN QGridLayout

        self.btn_aggiungi_lezione = QPushButton("➕ Aggiungi Lezione")
        self.btn_modifica_lezione = QPushButton("✏️ Modifica Lezione Selezionata")
        self.btn_elimina_lezione = QPushButton("🗑️ Elimina Lezione Selezionata")
        self.btn_segna_completata = QPushButton("✅ Segna Completata")
        self.btn_segna_confermata = QPushButton("👍 Segna Confermata")
        self.btn_reset_lezione_form = QPushButton("🧹 Reset Form")

        self.btn_aggiungi_lezione.clicked.connect(self.aggiungi_lezione)
        self.btn_modifica_lezione.clicked.connect(self.modifica_lezione)
        self.btn_elimina_lezione.clicked.connect(self.elimina_lezione)
        self.btn_segna_completata.clicked.connect(lambda: self.aggiorna_stato_lezione_selezionata(completata=1))
        self.btn_segna_confermata.clicked.connect(lambda: self.aggiorna_stato_lezione_selezionata(confermata=1))
        self.btn_reset_lezione_form.clicked.connect(self.reset_lezione_form)

        # Disposizione su 2 colonne con QGridLayout
        buttons_lezioni_layout.addWidget(self.btn_aggiungi_lezione, 0, 0) # Riga 0, Colonna 0
        buttons_lezioni_layout.addWidget(self.btn_modifica_lezione, 0, 1) # Riga 0, Colonna 1
        buttons_lezioni_layout.addWidget(self.btn_elimina_lezione, 1, 0) # Riga 1, Colonna 0
        buttons_lezioni_layout.addWidget(self.btn_segna_completata, 1, 1) # Riga 1, Colonna 1
        buttons_lezioni_layout.addWidget(self.btn_segna_confermata, 2, 0) # Riga 2, Colonna 0
        buttons_lezioni_layout.addWidget(self.btn_reset_lezione_form, 2, 1) # Riga 2, Colonna 1

        right_layout.addLayout(buttons_lezioni_layout)
        self.layout_calendario.addLayout(right_layout, 3) # Peso 2

        # Connetti il cambio di tab per caricare i dati corrispondenti
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

        self.current_lezione_id = None # Per tenere traccia della lezione selezionata in modifica

        self._populate_tessere_for_lezioni() # Popola la ComboBox delle tessere


        # --- Sezione per il Calendario (Opzionale e da implementare con cura) ---
        # Per ora la abbozzo, ma richiederà una gestione a parte per salvare/visualizzare gli appuntamenti.
        # calendar_group = QLabel("<h3>Programmazione Lezioni</h3>")
        # calendar_group.setAlignment(Qt.AlignCenter)
        # main_layout.addWidget(calendar_group)
        # self.calendar_widget = QCalendarWidget()
        # main_layout.addWidget(self.calendar_widget)
        # self.calendar_widget.selectionChanged.connect(self.on_calendar_date_selected)
        # # ... (potresti aggiungere un QListWidget per gli eventi del giorno selezionato) ...


    def load_tessere_attive(self):
        """Carica le tessere attive nella tabella."""
        self.table_attive.setRowCount(0) # Pulisci la tabella
        tessere = get_tessere(solo_attive=True)
        self._populate_table(self.table_attive, tessere)
        print("DEBUG: Tessere attive caricate.")

    def load_storico_tessere(self):
        """Carica tutte le tessere (incluse le chiuse) nella tabella dello storico."""
        self.table_storico.setRowCount(0) # Pulisci la tabella
        tessere = get_tessere(solo_attive=False) # Recupera tutte le tessere
        self._populate_table(self.table_storico, tessere)
        print("DEBUG: Storico tessere caricato.")

    def _populate_table(self, table: QTableWidget, tessere: list):
        """Popola una QTableWidget con i dati delle tessere."""
        table.setRowCount(len(tessere))
        for row_idx, tessera in enumerate(tessere):
            table.setItem(row_idx, 0, QTableWidgetItem(str(tessera['id'])))
            table.setItem(row_idx, 1, QTableWidgetItem(f"{tessera['nome']} {tessera['cognome']}"))
            table.setItem(row_idx, 2, QTableWidgetItem(tessera['tipo_tessera']))
            table.setItem(row_idx, 3, QTableWidgetItem(str(tessera['numero_item_totale'])))
            table.setItem(row_idx, 4, QTableWidgetItem(str(tessera['item_usati'])))
            table.setItem(row_idx, 5, QTableWidgetItem(f"{tessera['prezzo_totale']:.2f} €"))
            table.setItem(row_idx, 6, QTableWidgetItem(tessera['data_creazione']))
            table.setItem(row_idx, 7, QTableWidgetItem(tessera['nazione']))
            
            # Colora le righe delle tessere esaurite o disattivate nello storico
            if table == self.table_storico and (tessera['item_usati'] >= tessera['numero_item_totale'] or tessera['attiva'] == 0):
                for col in range(table.columnCount()):
                    table.item(row_idx, col).setBackground(Qt.red) # Puoi scegliere il colore che preferisci

    def on_tab_changed(self, index: int):
        """Gestisce il cambio di tab per caricare i dati."""
        if self.tab_widget.tabText(index) == "Tessere Attive":
            self.load_tessere_attive()
        elif self.tab_widget.tabText(index) == "Storico Tessere":
            self.load_storico_tessere()

    def usa_item_tessera_selezionata(self):
        selected_rows = self.table_attive.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Nessuna Selezione", "Seleziona una tessera dalla tabella per usare un item.")
            return

        row = selected_rows[0].row()
        id_tessera = int(self.table_attive.item(row, 0).text())
        cliente_nome = self.table_attive.item(row, 1).text()
        tipo_tessera = self.table_attive.item(row, 2).text()
        item_usati = int(self.table_attive.item(row, 4).text())
        items_totali = int(self.table_attive.item(row, 3).text())

        if item_usati >= items_totali:
            QMessageBox.information(self, "Tessera Esaurita", f"La tessera di {cliente_nome} ({tipo_tessera}) è già esaurita ({item_usati}/{items_totali}).")
            return

        reply = QMessageBox.question(self, "Conferma Utilizzo Item",
                                    f"Confermi di voler registrare l'utilizzo di un item per la tessera ID {id_tessera} di {cliente_nome} ({tipo_tessera})?\n"
                                    f"Items rimanenti: {items_totali - item_usati}",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            success = usa_item_tessera(id_tessera)
            if success:
                QMessageBox.information(self, "Item Usato", f"Un item per la tessera ID {id_tessera} è stato registrato come usato.")
                self.load_tessere_attive() # Ricarica per aggiornare lo stato
                self.load_storico_tessere() # Ricarica lo storico, potrebbe essere passata lì
            else:
                QMessageBox.critical(self, "Errore", f"Impossibile registrare l'utilizzo dell'item per la tessera ID {id_tessera}.")
        
    def stampa_promemoria_tessera_selezionata(self):
        selected_rows = self.table_attive.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Nessuna Selezione", "Seleziona una tessera dalla tabella per stampare il promemoria.")
            return

        row = selected_rows[0].row()
        
        # Recupera tutti i dati necessari per il promemoria dalla tabella
        id_tessera = int(self.table_attive.item(row, 0).text())
        cliente_completo = self.table_attive.item(row, 1).text() # "Nome Cognome"
        tipo_tessera = self.table_attive.item(row, 2).text()
        items_totali = int(self.table_attive.item(row, 3).text())
        items_usati = int(self.table_attive.item(row, 4).text())
        prezzo_totale = self.table_attive.item(row, 5).text()
        data_creazione = self.table_attive.item(row, 6).text()
        nazione = self.table_attive.item(row, 7).text()

        # Estrai nome e cognome
        nome_cliente = cliente_completo.split(' ', 1)[0] if ' ' in cliente_completo else cliente_completo
        cognome_cliente = cliente_completo.split(' ', 1)[1] if ' ' in cliente_completo else ""

        # Genera il contenuto HTML per il PDF
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; text-align: center; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
                h2 {{ color: #555; margin-top: 20px; border-bottom: 1px solid #ccc; padding-bottom: 5px; }}
                p {{ margin-bottom: 5px; line-height: 1.5; }}
                .highlight {{ background-color: #e9f5ff; padding: 15px; border-radius: 8px; margin-bottom: 15px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }}
                .item-status {{ font-weight: bold; color: {'green' if items_usati < items_totali else 'red'}; }}
                .footer {{ margin-top: 40px; text-align: center; font-size: 0.8em; color: #777; border-top: 1px solid #eee; padding-top: 10px; }}
            </style>
        </head>
        <body>
            <h1>Promemoria Tessera Noleggi/Corsi</h1>
            
            <div class="highlight">
                <h2>Dati Cliente:</h2>
                <p><strong>Nome Completo:</strong> {cliente_completo}</p>
                <p><strong>Nazione:</strong> {nazione}</p>
                </div>

            <div class="highlight">
                <h2>Dettagli Tessera:</h2>
                <p><strong>ID Tessera:</strong> {id_tessera}</p>
                <p><strong>Tipo Tessera:</strong> {tipo_tessera}</p>
                <p><strong>Items Totali:</strong> {items_totali}</p>
                <p><strong>Items Usati:</strong> {items_usati} <span class="item-status">({items_totali - items_usati} rimanenti)</span></p>
                <p><strong>Stato:</strong> <span class="item-status">{'Attiva' if items_usati < items_totali else 'Completata/Esaurita'}</span></p>
                <p><strong>Prezzo Totale:</strong> {prezzo_totale}</p>
                <p><strong>Data Creazione:</strong> {data_creazione}</p>
            </div>

            <div class="footer">
                <p>Generato da Windsurf Ceresio Application</p>
                <p>Data e Ora Generazione: {QDate.currentDate().toString(Qt.DefaultLocaleLongDate)}</p>
                <p>Questo promemoria non è un documento fiscale.</p>
            </div>
        </body>
        </html>
        """
        
        # Crea il documento HTML
        document = QTextDocument()
        document.setHtml(html_content)

        # Prepara la directory di output
        output_dir = Path("PromemoriaTessere") # Crea una sottocartella nella stessa directory dello script
        try:
            output_dir.mkdir(parents=True, exist_ok=True) # Crea la cartella se non esiste
        except Exception as e:
            QMessageBox.critical(self, "Errore Cartella", f"Impossibile creare la cartella 'PromemoriaTessere': {e}")
            print(f"ERRORE: Impossibile creare la cartella: {e}")
            return

        # Costruisci il nome del file PDF
        # Rimuovi caratteri non validi dal nome del file
        safe_cliente_nome = "".join(c for c in nome_cliente if c.isalnum() or c in (' ', '_')).strip()
        safe_cliente_cognome = "".join(c for c in cognome_cliente if c.isalnum() or c in (' ', '_')).strip()
        
        file_name = f"Promemoria_Tessera_{safe_cliente_nome}_{safe_cliente_cognome}_ID{id_tessera}.pdf"
        output_path = output_dir / file_name

        try:
            # Configura il QPrinter per generare un PDF
            printer = QPrinter(QPrinter.PrinterResolution) # Usa una risoluzione generica
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(str(output_path))
            
            # Stampa il documento sul "printer" (che in questo caso è un file PDF)
            document.print(printer)
            
            QMessageBox.information(self, "PDF Generato", f"Il promemoria è stato salvato come PDF in:\n{output_path}\nOra verrà aperto.")
            
            # Apri il PDF con il visualizzatore predefinito del sistema
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(output_path)))

        except Exception as e:
            QMessageBox.critical(self, "Errore Generazione PDF", f"Si è verificato un errore durante la generazione/apertura del PDF: {e}")
            print(f"ERRORE PDF DETTAGLIATO: {e}")
    
    def _populate_tessere_for_lezioni(self):
        """Popola la QComboBox con le tessere attive per la selezione di una lezione."""
        self.cmb_tessera_lezione.clear()
        self.cmb_tessera_lezione.addItem("Seleziona una tessera...", userData=None) # Item placeholder
        tessere = get_tessere_per_selezione_lezione()
        for tessera in tessere:
            display_text = f"ID:{tessera['id']} - {tessera['nome']} {tessera['cognome']} ({tessera['tipo_tessera']} - Usati:{tessera['item_usati']}/{tessera['numero_item_totale']})"
            self.cmb_tessera_lezione.addItem(display_text, userData=tessera['id'])
        print("DEBUG: ComboBox tessere per lezioni popolata.")

    def load_lezioni_for_selected_date(self):
        """Carica e visualizza le lezioni per la data selezionata nel calendario."""
        self.lessons_list_widget.clear()
        selected_date = self.calendar_widget.selectedDate().toString("yyyy-MM-dd")
        lezioni = get_lezioni_per_data(selected_date)

        if not lezioni:
            self.lessons_list_widget.addItem("Nessuna lezione programmata per questa data.")
            self.btn_modifica_lezione.setEnabled(False)
            self.btn_elimina_lezione.setEnabled(False)
            self.btn_segna_completata.setEnabled(False)
            self.btn_segna_confermata.setEnabled(False)
            self.reset_lezione_form()
            return
        
        self.btn_modifica_lezione.setEnabled(True)
        self.btn_elimina_lezione.setEnabled(True)
        self.btn_segna_completata.setEnabled(True)
        self.btn_segna_confermata.setEnabled(True)

        for lezione in lezioni:
            status_text = []
            if lezione['confermata']:
                status_text.append("CONF")
            if lezione['completata']:
                status_text.append("COMPL")
            
            status_str = f" [{', '.join(status_text)}]" if status_text else ""
            
            item_text = (f"{lezione['ora_lezione'] or 'N/A'} - {lezione['cognome']} {lezione['nome']} "
                         f"({lezione['tipo_tessera']}) - {lezione['descrizione']}{status_str}")
            
            list_item = QTableWidgetItem(item_text) # Uso QTableWidgetItem per poter usare setData
            list_item.setData(Qt.UserRole, lezione['id']) # Salva l'ID della lezione nell'item

            if lezione['completata']:
                list_item.setBackground(QColor(200, 255, 200)) # Verde chiaro per completate
            elif lezione['confermata']:
                list_item.setBackground(QColor(255, 255, 200)) # Giallo chiaro per confermate
            
            self.lessons_list_widget.addItem(list_item)
        
        self.reset_lezione_form() # Pulisci il form quando cambi data

    def display_lezione_details(self, item):
        """Visualizza i dettagli della lezione selezionata nel form."""
        lezione_id = item.data(Qt.UserRole)
        self.current_lezione_id = lezione_id
        
        lezione_data = get_lezione_by_id(lezione_id)
        if lezione_data:
            # Imposta la tessera nel QComboBox
            idx = self.cmb_tessera_lezione.findData(lezione_data['id_tessera'])
            if idx != -1:
                self.cmb_tessera_lezione.setCurrentIndex(idx)
            
            self.time_edit_lezione.setTime(QTime.fromString(lezione_data['ora_lezione'], "HH:mm") if lezione_data['ora_lezione'] else QTime(9,0))
            self.txt_descrizione_lezione.setText(lezione_data['descrizione'])
            self.txt_note_lezione.setPlainText(lezione_data['note'])
            
            # Abilita/Disabilita pulsanti stato in base allo stato attuale
            self.btn_segna_completata.setEnabled(not bool(lezione_data['completata']))
            self.btn_segna_confermata.setEnabled(not bool(lezione_data['confermata']))

            # Se già completata, disabilita il form
            if bool(lezione_data['completata']):
                self.cmb_tessera_lezione.setEnabled(False)
                self.time_edit_lezione.setEnabled(False)
                self.txt_descrizione_lezione.setEnabled(False)
                self.txt_note_lezione.setEnabled(False)
                self.btn_aggiungi_lezione.setEnabled(False)
                self.btn_modifica_lezione.setEnabled(False)
            else:
                self.cmb_tessera_lezione.setEnabled(True)
                self.time_edit_lezione.setEnabled(True)
                self.txt_descrizione_lezione.setEnabled(True)
                self.txt_note_lezione.setEnabled(True)
                self.btn_aggiungi_lezione.setEnabled(True) # Riabilita aggiungi
                self.btn_modifica_lezione.setEnabled(True) # Riabilita modifica

        else:
            self.reset_lezione_form()

    def reset_lezione_form(self):
        """Resetta i campi del form di lezione."""
        self.current_lezione_id = None
        self.cmb_tessera_lezione.setCurrentIndex(0) # Seleziona l'item placeholder
        self.time_edit_lezione.setTime(QTime(9, 0))
        self.txt_descrizione_lezione.clear()
        self.txt_note_lezione.clear()
        
        # Riabilita tutto
        self.cmb_tessera_lezione.setEnabled(True)
        self.time_edit_lezione.setEnabled(True)
        self.txt_descrizione_lezione.setEnabled(True)
        self.txt_note_lezione.setEnabled(True)
        self.btn_aggiungi_lezione.setEnabled(True) 
        self.btn_modifica_lezione.setEnabled(True) 
        self.btn_elimina_lezione.setEnabled(True)
        self.btn_segna_completata.setEnabled(True)
        self.btn_segna_confermata.setEnabled(True)

    def aggiungi_lezione(self):
        id_tessera = self.cmb_tessera_lezione.currentData()
        data_lezione = self.calendar_widget.selectedDate().toString("yyyy-MM-dd")
        ora_lezione = self.time_edit_lezione.time().toString("HH:mm")
        descrizione = self.txt_descrizione_lezione.text().strip()
        note = self.txt_note_lezione.toPlainText().strip()

        if not id_tessera:
            QMessageBox.warning(self, "Input Mancante", "Seleziona una tessera per la lezione.")
            return
        if not descrizione:
            QMessageBox.warning(self, "Input Mancante", "Inserisci una descrizione per la lezione.")
            return

        lezione_id = salva_lezione_programmata(id_tessera, data_lezione, ora_lezione, descrizione, note)
        if lezione_id:
            QMessageBox.information(self, "Successo", "Lezione aggiunta con successo!")
            self.load_lezioni_for_selected_date()
            self.reset_lezione_form()
        else:
            QMessageBox.critical(self, "Errore", "Errore nell'aggiungere la lezione.")

    def modifica_lezione(self):
        if self.current_lezione_id is None:
            QMessageBox.warning(self, "Nessuna Selezione", "Seleziona una lezione da modificare dalla lista.")
            return
        
        # Recupera i nuovi dati dal form
        id_tessera = self.cmb_tessera_lezione.currentData()
        data_lezione = self.calendar_widget.selectedDate().toString("yyyy-MM-dd") # La data è fissa dalla selezione calendario
        ora_lezione = self.time_edit_lezione.time().toString("HH:mm")
        descrizione = self.txt_descrizione_lezione.text().strip()
        note = self.txt_note_lezione.toPlainText().strip()

        if not id_tessera:
            QMessageBox.warning(self, "Input Mancante", "Seleziona una tessera per la lezione.")
            return
        if not descrizione:
            QMessageBox.warning(self, "Input Mancante", "Inserisci una descrizione per la lezione.")
            return

        # Per semplicità, la funzione di modifica non è stata ancora esposta in data_access.
        # Dovremmo aggiungere una funzione update_lezione_programmata in data_access.py.
        # Per ora, simulo un aggiornamento dello stato per dimostrare il concetto,
        # ma è necessario implementare la logica di aggiornamento completa.
        QMessageBox.information(self, "Funzionalità da Estendere", 
                                "La modifica completa dei dettagli della lezione non è ancora implementata. "
                                "Dovrai aggiungere la funzione update_lezione_programmata in data_access.py.")
        # Esempio di come potresti chiamare una funzione di aggiornamento completa:
        # success = update_lezione_programmata(self.current_lezione_id, id_tessera, data_lezione, ora_lezione, descrizione, note)
        # if success:
        #    QMessageBox.information(self, "Successo", "Lezione modificata con successo!")
        #    self.load_lezioni_for_selected_date()
        #    self.reset_lezione_form()
        # else:
        #    QMessageBox.critical(self, "Errore", "Errore nella modifica della lezione.")


    def elimina_lezione(self):
        if self.current_lezione_id is None:
            QMessageBox.warning(self, "Nessuna Selezione", "Seleziona una lezione da eliminare dalla lista.")
            return

        reply = QMessageBox.question(self, "Conferma Eliminazione",
                                    f"Sei sicuro di voler eliminare la lezione selezionata (ID: {self.current_lezione_id})?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            success = cancella_lezione_programmata(self.current_lezione_id)
            if success:
                QMessageBox.information(self, "Successo", "Lezione eliminata con successo!")
                self.load_lezioni_for_selected_date()
                self.reset_lezione_form()
            else:
                QMessageBox.critical(self, "Errore", "Errore nell'eliminazione della lezione.")

    def aggiorna_stato_lezione_selezionata(self, confermata: int = None, completata: int = None):
        if self.current_lezione_id is None:
            QMessageBox.warning(self, "Nessuna Selezione", "Seleziona una lezione per aggiornare lo stato.")
            return

        success = aggiorna_stato_lezione(self.current_lezione_id, confermata=confermata, completata=completata)
        if success:
            QMessageBox.information(self, "Successo", "Stato lezione aggiornato con successo!")
            self.load_lezioni_for_selected_date() # Ricarica per visualizzare il cambio di stato
        else:
            QMessageBox.critical(self, "Errore", "Errore nell'aggiornare lo stato della lezione.")

