# gestione_soci_annuali_pyside.py

# --- INIZIO: Assicurati che gli import siano questi o che includano questi ---
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGridLayout, QSpacerItem, QSizePolicy, QMessageBox, QDialog
)
from PySide6.QtCore import Qt # Necessario per Qt.AlignCenter, Qt.Horizontal ecc.
from PySide6.QtGui import QColor # Aggiungi QColor qui se vuoi la colorazione della riga nel dialogo lista

# Importa la nuova classe DialogoListaSoci
from dialogo_lista_soci import DialogoListaSoci # <--- AGGIUNGI QUESTA RIGA

from dialogo_comunicazioni import DialogoComunicazioni
from dialogo_gestione_pagamenti import DialogoGestionePagamenti


# Importazioni da data_access, codice_fiscale_utils, dialogo_modifica_socio
# Non sono necessarie per questa prima fase della GUI principale,
# ma puoi lasciarle per il momento se vuoi, le sposteremo/useremo dopo.
from data_access import (
    get_all_soci, insert_socio_esteso, get_socio_by_id,
    update_socio_esteso, delete_socio, mark_quota_pagata, get_socio_photo_blob
)
from codice_fiscale_utils import calcola_codice_fiscale
from dialogo_socio import DialogoSocio # <--- MODIFICA/AGGIUNGI QUESTA RIGA


#from dialogo_modifica_socio import DialogoModificaSoci # Se il file esiste, altrimenti commentalo
#from dialogo_aggiungi_socio import DialogoAggiungiSocio # <--- AGGIUNGI QUESTA

# Non sono più necessari in questo file centrale per ora:
# from QTableWidget, QTableWidgetItem, QLineEdit, QFileDialog, QFormLayout, QDialogButtonBox, QDialog, QComboBox, QSpinBox, QDateEdit, QInputDialog, QGroupBox, QScrollArea, QTextEdit, QHeaderView
# from PySide6.QtGui import QPixmap, QFont # o QColor
# import os, shutil, pathlib, io, BytesIO
# from reportlab.pdfgen import canvas, ... (tutto reportlab e qrcode)

# Rimuovi/Commenta le variabili globali se presenti, tipo FOTO_SOCI_DIR se non è usata qui.
# --- FINE: Import e Configurazione ---


class FinestraGestioneSoci(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestione Soci Annuali")
        self.setMinimumSize(700, 500) # Una dimensione di partenza più compatta

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter) # Centra i contenuti verticalmente

        # Titolo della finestra
        title_label = QLabel("Pannello di Controllo Soci")
        title_label.setAlignment(Qt.AlignCenter)
        # Questo è uno stile inline per rendere il titolo più visibile, il tuo QSS lo sovrascriverà
        title_label.setStyleSheet("font-size: 28px; font-weight: bold; margin-bottom: 20px;")
        main_layout.addWidget(title_label)

        # Layout per i pulsanti principali (Grid per coerenza e allineamento)
        buttons_grid_layout = QGridLayout()
        buttons_grid_layout.setContentsMargins(50, 20, 50, 20) # Margini interni
        buttons_grid_layout.setHorizontalSpacing(20) # Spazio orizzontale tra i bottoni
        buttons_grid_layout.setVerticalSpacing(20)   # Spazio verticale tra i bottoni

        # --- Creazione dei Pulsanti Principali ---
        # Ogni pulsante avrà una dimensione fissa per un aspetto coerente

        # 1. Pulsante "Aggiungi Nuovo Socio"
        self.btn_aggiungi_nuovo = QPushButton("➕ Aggiungi Nuovo Socio")
        self.btn_aggiungi_nuovo.setFixedSize(280, 80) # Dimensioni fisse
        self.btn_aggiungi_nuovo.setStyleSheet("font-size: 18px; padding: 15px;") # Stile base
        self.btn_aggiungi_nuovo.clicked.connect(self.apri_dialogo_aggiungi_socio)
        buttons_grid_layout.addWidget(self.btn_aggiungi_nuovo, 0, 0, Qt.AlignCenter) # Riga 0, Colonna 0

        # 2. Pulsante "Visualizza Lista Soci"
        self.btn_visualizza_lista = QPushButton("📋 Gestione Soci")
        self.btn_visualizza_lista.setFixedSize(280, 80)
        self.btn_visualizza_lista.setStyleSheet("font-size: 18px; padding: 15px;")
        self.btn_visualizza_lista.clicked.connect(self.apri_dialogo_lista_soci)
        buttons_grid_layout.addWidget(self.btn_visualizza_lista, 0, 1, Qt.AlignCenter) # Riga 0, Colonna 1

        # 3. Pulsante "Gestisci Pagamenti"
        self.btn_gestisci_pagamenti = QPushButton("💳 Gestisci Contabilità Soci")
        self.btn_gestisci_pagamenti.setFixedSize(280, 80)
        self.btn_gestisci_pagamenti.setStyleSheet("font-size: 18px; padding: 15px;")
        self.btn_gestisci_pagamenti.clicked.connect(self.apri_dialogo_gestione_pagamenti)
        buttons_grid_layout.addWidget(self.btn_gestisci_pagamenti, 1, 0, Qt.AlignCenter) # Riga 1, Colonna 0

        # 4. Pulsante "Invia Comunicazioni"
        self.btn_invia_comunicazioni = QPushButton("📧 Invia Comunicazioni")
        self.btn_invia_comunicazioni.setFixedSize(280, 80)
        self.btn_invia_comunicazioni.setStyleSheet("font-size: 18px; padding: 15px;")
        self.btn_invia_comunicazioni.clicked.connect(self.apri_dialogo_comunicazioni_soci)
        buttons_grid_layout.addWidget(self.btn_invia_comunicazioni, 1, 1, Qt.AlignCenter) # Riga 1, Colonna 1

        # Contenitore per centrare la griglia dei pulsanti
        container_for_grid = QHBoxLayout()
        container_for_grid.addStretch(1) # Spaziatore a sinistra
        container_for_grid.addLayout(buttons_grid_layout)
        container_for_grid.addStretch(1) # Spaziatore a destra
        main_layout.addLayout(container_for_grid)

        main_layout.addStretch(1) # Spaziatore in basso per spingere i contenuti al centro


    # --- Metodi che apriranno i nuovi dialoghi (per ora con QMessageBox di test) ---



    def apri_dialogo_aggiungi_socio(self):
        dialog = DialogoSocio(parent=self) # Crea il dialogo per un nuovo socio (socio_id=None di default)
        if dialog.exec() == QDialog.Accepted:
           QMessageBox.information(self, "Informazione", "Nuovo socio aggiunto con successo.")
        # QUI: Potresti voler aggiornare la lista dei soci nella finestra principale
        # self.carica_dati() # Se hai un metodo per ricaricare i dati della tabella
        else:
           QMessageBox.information(self, "Informazione", "Operazione di aggiunta")

    # ... all'interno della classe FinestraGestioneSoci ...

    def apri_dialogo_modifica_socio(self):
        # QUESTO È UN ESEMPIO: DOVRAI RECUPERARE L'ID DEL SOCIO SELEZIONATO DALLA TUA TABELLA/LISTA
        # Per ora, usiamo un ID di esempio per testare la modalità modifica.
        socio_selezionato_id = 1 # Esempio: modifica il socio con ID 1

        if socio_selezionato_id is None:
            QMessageBox.warning(self, "Selezione Socio", "Seleziona un socio dalla lista per modificarlo.")
            return

        dialog = DialogoSocio(socio_id=socio_selezionato_id, parent=self)
        if dialog.exec() == QDialog.Accepted:
            QMessageBox.information(self, "Informazione", "Socio modificato con successo.")
            # QUI: Potresti voler aggiornare la lista dei soci nella finestra principale
            # self.carica_dati() # Se hai un metodo per ricaricare i dati della tabella
        else:
            QMessageBox.information(self, "Informazione", "Operazione di modifica socio annullata.")

    def apri_dialogo_lista_soci(self):
            QMessageBox.information(self, "Funzionalità", "Qui si aprirà la finestra con la LISTA COMPLETA dei soci (tabella).")
            # Q_MessageBox.information(self, "Funzionalità", "Qui si aprirà la finestra con la LISTA COMPLETA dei soci (tabella).") # Rimuovi o commenta questa riga di test

            # Crea e mostra il dialogo della lista soci
            dialog = DialogoListaSoci(self) # 'self' imposta la finestra padre
            dialog.exec() # Mostra il dialogo in modo modale (blocca la finestra padre finché non viene chiuso)

    # ... (all'interno della classe FinestraGestioneSoci, ad esempio dopo init_ui o altri metodi simili) ...

    def apri_dialogo_lista_soci(self):
        """Apre il dialogo per visualizzare e gestire la lista dei soci."""
        dialog = DialogoListaSoci(parent=self) # Crea un'istanza del dialogo della lista
        dialog.exec() # Mostra il dialogo in modalità modale (blocca la finestra padre finché non viene chiuso)
        # Dopo che il dialogo della lista è stato chiuso, potresti voler ricaricare i dati
        # nella tua FinestraGestioneSoci se avesse una visualizzazione dei soci (che ora non ha)
        # o in qualche altra parte dell'applicazione che mostra i dati.
        # Per ora, non è necessario fare nulla qui a meno che tu non abbia un
        # metodo come self.aggiorna_dashboard_soci() da chiamare.

    # ... (il resto dei tuoi metodi, come apri_dialogo_aggiungi_socio, apri_dialogo_gestione_pagamenti, ecc.) ...

    # Questo metodo deve aprire il dialogo per la gestione dei pagamenti
    def apri_dialogo_gestione_pagamenti(self):
        dialog = DialogoGestionePagamenti(parent=self) # Non passiamo socio_id qui
        dialog.exec()

    def apri_dialogo_comunicazioni_soci(self):
        dialog = DialogoComunicazioni(self) # 'self' imposta la finestra padre
        dialog.exec() # Mostra il dialogo in modo modale

    # --- Rimuovi TUTTI gli altri metodi che non sono stati inclusi qui sopra. ---
    # Questi metodi (come carica_dati, filtra_soci, seleziona_socio, ecc.)
    # non appartengono più a questa classe "Pannello di Controllo".
    # Li sposteremo nelle nuove classi di dialogo pertinenti.
    # Ad esempio, il metodo 'carica_dati' che popolava la tabella, non serve più qui.
    # Anche tutti i metodi per la stampa tessera, l'aggiornamento quota, ecc.,
    # andranno nei rispettivi nuovi dialoghi.

# --- FINE della classe FinestraGestioneSoci ---

# Non modificare la parte 'if __name__ == "__main__":' in questo file.
# Se presente, lasciala come test temporaneo solo per questa finestra, ma la principale
# esecuzione sarà sempre da main_albero_menu.py.
# if __name__ == "__main__":
#     import sys
#     from PySide6.QtWidgets import QApplication
#     app = QApplication(sys.argv)
#     window = FinestraGestioneSoci()
#     window.show()
#     sys.exit(app.exec())