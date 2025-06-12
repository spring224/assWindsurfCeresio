# situazione_noleggi.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QDialog, QLabel
)
from PySide6.QtCore import Qt, QTimer, QDateTime # Importa QDateTime per calcoli data/ora
from data_access import get_noleggi_attivi, chiudi_noleggio, aggiorna_disponibilita_materiale_by_id # Assicurati di avere queste funzioni in data_access.py

class SituazioneNoleggi(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Situazione Noleggi Attivi")
        self.init_ui()
        self.load_noleggi()

        # Inizializza un QTimer per aggiornare il tempo residuo ogni minuto
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_tempo_residuo)
        self.timer.start(60 * 1000) # Aggiorna ogni 60 secondi (1 minuto)

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Layout per pulsanti e intestazioni
        header_layout = QHBoxLayout()
        self.lbl_titolo = QLabel("Noleggi Attivi")
        self.lbl_titolo.setAlignment(Qt.AlignCenter)
        self.lbl_titolo.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(self.lbl_titolo)
        
        self.btn_aggiorna = QPushButton("Aggiorna")
        self.btn_aggiorna.clicked.connect(self.load_noleggi)
        header_layout.addWidget(self.btn_aggiorna)

        main_layout.addLayout(header_layout)

        # Tabella per visualizzare i noleggi
        self.table_noleggi = QTableWidget()
        # Definisci le colonne: ID Noleggio, Cliente, Materiali, Inizio, Fine Prevista, Tempo Residuo, Azioni
        self.table_noleggi.setColumnCount(7) 
        self.table_noleggi.setHorizontalHeaderLabels([
            "ID Noleggio", "Cliente", "Materiali", "Inizio Noleggio", 
            "Fine Prevista", "Tempo Residuo", "Azioni"
        ])
        
        # Ridimensiona le colonne per riempire lo spazio disponibile
        self.table_noleggi.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_noleggi.verticalHeader().setVisible(False) # Nasconde l'header verticale numerico
        self.table_noleggi.setEditTriggers(QTableWidget.NoEditTriggers) # Rendi la tabella non modificabile
        self.table_noleggi.setSelectionBehavior(QTableWidget.SelectRows) # Selezione per righe intere
        main_layout.addWidget(self.table_noleggi)

        self.setLayout(main_layout)
        self.setMinimumSize(800, 600) # Imposta una dimensione minima per la finestra

    def load_noleggi(self):
        self.table_noleggi.setRowCount(0) # Pulisci la tabella
        noleggi_attivi = get_noleggi_attivi() # Questa funzione deve recuperare tutti i noleggi attivi

        for row_idx, noleggio in enumerate(noleggi_attivi):
            self.table_noleggi.insertRow(row_idx)

            # Estrai i dati dal dizionario/oggetto noleggio. Assicurati che questi campi esistano nel tuo DB/modello.
            # Esempio:
            id_noleggio = noleggio.get("id", "N/A")
            nome_cliente = noleggio.get("nome_cliente", "N/A")
            cognome_cliente = noleggio.get("cognome_cliente", "")
            materiali_str = ", ".join([mat.get('nome', 'N/A') for mat in noleggio.get('materiali', [])]) # Assumi lista di dict per materiali
            data_inizio_str = noleggio.get("data_inizio", "N/A")
            ora_inizio_str = noleggio.get("ora_inizio", "N/A")
            durata_ore = noleggio.get("durata_ore", 0)

            # Combina data e ora per calcoli
            try:
                dt_inizio_str = f"{data_inizio_str} {ora_inizio_str}"
                dt_inizio = QDateTime.fromString(dt_inizio_str, "yyyy-MM-dd HH:mm")
                dt_fine_prevista = dt_inizio.addSecs(durata_ore * 3600) # Aggiungi ore convertite in secondi
                fine_prevista_str = dt_fine_prevista.toString("dd/MM/yyyy HH:mm")
            except Exception as e:
                fine_prevista_str = "Errore Data"
                dt_fine_prevista = QDateTime.currentDateTime() # Fallback per calcolo tempo residuo
                print(f"DEBUG: Errore parsing data/ora per noleggio {id_noleggio}: {e}")

            # Calcola il tempo residuo iniziale
            tempo_residuo_str = self.calculate_tempo_residuo(dt_fine_prevista)

            self.table_noleggi.setItem(row_idx, 0, QTableWidgetItem(str(id_noleggio)))
            self.table_noleggi.setItem(row_idx, 1, QTableWidgetItem(f"{nome_cliente} {cognome_cliente}"))
            self.table_noleggi.setItem(row_idx, 2, QTableWidgetItem(materiali_str))
            self.table_noleggi.setItem(row_idx, 3, QTableWidgetItem(f"{data_inizio_str} {ora_inizio_str}"))
            self.table_noleggi.setItem(row_idx, 4, QTableWidgetItem(fine_prevista_str))
            
            tempo_residuo_item = QTableWidgetItem(tempo_residuo_str)
            self.table_noleggi.setItem(row_idx, 5, tempo_residuo_item)
            # Puoi cambiare il colore del testo per il tempo residuo se scaduto/vicino alla scadenza
            if "SCADUTO" in tempo_residuo_str:
                tempo_residuo_item.setForeground(Qt.red)
            elif "ore" in tempo_residuo_str or "minuti" in tempo_residuo_str: # Esempio per evidenziare quelli con poco tempo
                tempo_residuo_item.setForeground(Qt.darkYellow)


            # Aggiungi il pulsante "Chiudi Noleggio"
            btn_chiudi = QPushButton("Chiudi Noleggio")
            # Connetti il pulsante a una funzione che riceve l'ID del noleggio
            # Usa una lambda per passare l'ID corretto
            btn_chiudi.clicked.connect(lambda _, id_n=id_noleggio: self.chiudi_noleggio_selezionato(id_n))
            self.table_noleggi.setCellWidget(row_idx, 6, btn_chiudi)

    def calculate_tempo_residuo(self, dt_fine_prevista: QDateTime) -> str:
        now = QDateTime.currentDateTime()
        diff_ms = now.msecsTo(dt_fine_prevista) # Millisecondi da ora alla fine prevista

        if diff_ms <= 0:
            return "SCADUTO"
        
        diff_s = diff_ms // 1000
        days = diff_s // (3600 * 24)
        diff_s %= (3600 * 24)
        hours = diff_s // 3600
        diff_s %= 3600
        minutes = diff_s // 60

        parts = []
        if days > 0:
            parts.append(f"{days} giorni")
        if hours > 0:
            parts.append(f"{hours} ore")
        if minutes > 0:
            parts.append(f"{minutes} minuti")
        
        return ", ".join(parts) if parts else "Meno di un minuto"

    def update_tempo_residuo(self):
        # Itera sulle righe esistenti e aggiorna solo la colonna "Tempo Residuo"
        for row_idx in range(self.table_noleggi.rowCount()):
            fine_prevista_str = self.table_noleggi.item(row_idx, 4).text()
            try:
                dt_fine_prevista = QDateTime.fromString(fine_prevista_str, "dd/MM/yyyy HH:mm")
                tempo_residuo_str = self.calculate_tempo_residuo(dt_fine_prevista)
                
                tempo_residuo_item = self.table_noleggi.item(row_idx, 5)
                if not tempo_residuo_item: # Crea l'item se non esiste (dovrebbe esistere)
                    tempo_residuo_item = QTableWidgetItem()
                    self.table_noleggi.setItem(row_idx, 5, tempo_residuo_item)
                
                tempo_residuo_item.setText(tempo_residuo_str)
                # Aggiorna il colore in base allo stato
                if "SCADUTO" in tempo_residuo_str:
                    tempo_residuo_item.setForeground(Qt.red)
                elif "ore" in tempo_residuo_str or "minuti" in tempo_residuo_str:
                    tempo_residuo_item.setForeground(Qt.darkYellow)
                else: # Colore di default
                    tempo_residuo_item.setForeground(self.palette().color(self.table_noleggi.foregroundRole()))

            except Exception as e:
                print(f"DEBUG: Errore nell'aggiornamento tempo residuo per riga {row_idx}: {e}")
                self.table_noleggi.item(row_idx, 5).setText("Errore")
                self.table_noleggi.item(row_idx, 5).setForeground(Qt.darkGray)


    def chiudi_noleggio_selezionato(self, id_noleggio):
        reply = QMessageBox.question(self, 'Conferma Chiusura', 
                                    f'Sei sicuro di voler chiudere il noleggio ID: {id_noleggio}?',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # Recupera i materiali associati a questo noleggio per aggiornarne la disponibilità
            # Questa parte richiede una funzione in data_access per ottenere i materiali di un noleggio
            # Esempio (ASSUMENDO che get_noleggio_by_id restituisca anche i materiali noleggiati):
            
            # --- NUOVA FUNZIONE RICHIESTA IN data_access.py ---
            # get_dettagli_noleggio(id_noleggio) -> dovrebbe restituire info noleggio + lista materiali (id_materiale, codice)
            # Se questa funzione non esiste, dovrai crearla.
            # Per ora, simuliamo una chiamata a una funzione esistente se get_noleggi_attivi già include i materiali
            
            noleggi_attivi = get_noleggi_attivi() # Ricarica per trovare il noleggio giusto, oppure passa l'oggetto noleggio direttamente
            noleggio_da_chiudere = next((n for n in noleggi_attivi if n.get('id') == id_noleggio), None)

            if noleggio_da_chiudere and noleggio_da_chiudere.get('materiali'):
                for materiale_dettaglio in noleggio_da_chiudere.get('materiali'):
                    id_materiale_db = materiale_dettaglio.get('id_materiale') # Assumiamo che il dict materiale_dettaglio abbia 'id_materiale'
                    if id_materiale_db:
                        aggiorna_disponibilita_materiale_by_id(id_materiale_db, 1) # Metti a disponibile (valore 1)
                        print(f"DEBUG: Materiale ID {id_materiale_db} rimesso disponibile.")
                    else:
                        print(f"DEBUG: ID Materiale non trovato per un dettaglio del noleggio {id_noleggio}.")

            # Chiudi il noleggio nel database (setta lo stato a "completato" o data_fine)
            success = chiudi_noleggio(id_noleggio) # Questa funzione deve esistere in data_access.py

            if success:
                QMessageBox.information(self, "Noleggio Chiuso", f"Noleggio ID {id_noleggio} chiuso con successo e materiali resi disponibili.")
                self.load_noleggi() # Ricarica la tabella per riflettere i cambiamenti
            else:
                QMessageBox.critical(self, "Errore Chiusura", f"Impossibile chiudere il noleggio ID {id_noleggio}.")
        else:
            QMessageBox.information(self, "Annullato", "Chiusura noleggio annullata.")

    def closeEvent(self, event):
        # Assicurati di fermare il timer quando la finestra viene chiusa
        if self.timer.isActive():
            self.timer.stop()
        super().closeEvent(event)
