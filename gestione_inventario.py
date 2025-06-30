# gestione_inventario.py (File principale per il Dialogo Anagrafica Materiali)

import os # Mantenuto per Path se BASE_DIR fosse qui, ma verrà rimosso se non serve più
import sqlite3 # Mantenuto per eventuali funzioni di data_access se chiamate direttamente (ma verranno rimosse)
from PySide6.QtWidgets import (
    QApplication, # Necessario se fosse l'entry point principale dell'applicazione, ma verrà rimosso per il QDialog
    QWidget, # Base per i widget
    QVBoxLayout, QHBoxLayout, # Layout principali
    QTabWidget, # Per gestire le schede
    QMessageBox, # Per i messaggi di dialogo
    QDialog # La classe base per questo dialogo
    # Tutti gli altri widget (QLineEdit, QTextEdit, QPushButton, QComboBox, QCheckBox,
    # QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox,
    # QSpacerItem, QSizePolicy, QAbstractItemView, QScrollArea, QScrollBar, QFormLayout)
    # NON SONO UTILIZZATI DIRETTAMENTE da DialogoAnagraficaMateriali e verranno rimossi.
)
from PySide6.QtGui import QIcon # Mantenuto se usato per icone nel dialogo, altrimenti rimuovere
from PySide6.QtCore import Qt, Signal # Qt per costanti, Signal per la comunicazione

# --- IMPORT DELLE CLASSI DELLE SCHEDE (DA CREARE NEI LORO FILE SEPARATI) ---
# Assicurati che questi nomi corrispondano ai nomi dei file che creerai:
from lista_materiali_tab import MaterialiListaTab
from dettagli_materiali_tab import MaterialiDettagliTab

# --- RIMOZIONE: FOTO_DIR e os.makedirs non appartengono qui, vanno in dettagli_materiali_tab.py ---
# FOTO_DIR = "foto_materiali"
# os.makedirs(FOTO_DIR, exist_ok=True)

# --- RIMOZIONE: Import delle funzioni di data_access.py non appartengono qui ---
# Saranno importate direttamente da lista_materiali_tab.py e dettagli_materiali_tab.py
# from data_access import (
#     inserisci_materiale,
#     elimina_materiale,
#     carica_materiali,
#     carica_materiali_per_tipo,
#     carica_materiali_rig,
#     get_materiale_by_id,
#     aggiorna_materiale
# )


# --- CLASSE DIALOGO PRINCIPALE ---
class DialogoAnagraficaMateriali(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestione Anagrafica Materiali")
        self.setMinimumSize(1000, 700) # Dimensioni appropriate

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Inizializza le schede (le classi verranno importate dai loro rispettivi file)
        self.lista_tab = MaterialiListaTab()
        self.dettagli_tab = MaterialiDettagliTab()

        # Aggiungi le schede al QTabWidget
        self.tab_widget.addTab(self.lista_tab, "Lista Materiali")
        self.tab_widget.addTab(self.dettagli_tab, "Dettagli Materiale")

        # Connetti i segnali tra le schede e il dialogo principale
        self.lista_tab.material_selected.connect(self.handle_material_selected_from_list)
        self.lista_tab.add_new_material_requested.connect(self.handle_add_new_material_request)
        self.dettagli_tab.material_saved.connect(self.handle_material_saved)
        self.dettagli_tab.cancel_edit_requested.connect(self.handle_cancel_edit_request) # Connettiamo anche l'annullamento

        # Imposta la scheda iniziale all'avvio
        self.tab_widget.setCurrentWidget(self.lista_tab)

    def handle_material_selected_from_list(self, material_id):
        # Carica il materiale selezionato nella scheda dettagli e cambia scheda
        self.dettagli_tab.carica_materiale_per_modifica(material_id)
        self.tab_widget.setCurrentWidget(self.dettagli_tab) # Passa alla scheda dettagli

    def handle_add_new_material_request(self):
        # Resetta il form per un nuovo materiale e cambia scheda
        self.dettagli_tab.nuovo_materiale()
        self.tab_widget.setCurrentWidget(self.dettagli_tab) # Passa alla scheda dettagli

    def handle_material_saved(self):
        # Aggiorna la lista dopo che un materiale è stato salvato/modificato
        self.lista_tab.carica_tabella()
        self.tab_widget.setCurrentWidget(self.lista_tab) # Torna alla scheda lista

    def handle_cancel_edit_request(self):
        # Torna alla scheda lista se l'utente annulla la modifica/aggiunta
        self.tab_widget.setCurrentWidget(self.lista_tab)


# --- RIMOZIONE: Blocco per il test indipendente, come richiesto ---
# if __name__ == "__main__":
#     from PySide6.QtWidgets import QApplication
#     import sys

#     app = QApplication(sys.argv)
#     dialog = DialogoAnagraficaMateriali()
#     dialog.exec()
#     sys.exit(app.exec())