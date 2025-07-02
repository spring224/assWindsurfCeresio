

# ... (I tuoi import esistenti) ...
from gestione_inventario import DialogoAnagraficaMateriali # <--- AGGIUNGI/MODIFICA QUESTA RIGA
from stampa_codici_barre import FinestraStampaCodici
from noleggio_materiale import NoleggioMateriale
from situazione_noleggi import SituazioneNoleggi
from data_access import get_connection
from gestione_noleggi import GestioneNoleggi
from gestione_soci_annuali_pyside import FinestraGestioneSoci
from dialogo_comunicazioni import DialogoComunicazioni


# !!! AGGIUNGI QUESTI NUOVI IMPORT PER LE CLASSI DELLE TESSERE NOLEGGIO !!!
# Le classi FinestraCreaTessera e FinestraGestisciTessera
# dovranno essere definite in file Python separati (es. crea_tessere.py e gestisci_tessere.py
# Ho decommentato FinestraCreaTessera.
from crea_tessere import FinestraCreaTessera
from gestisci_tessere import FinestraGestisciTessera # <<< QUESTA CLASSE LA CREEREMO TRA POCO
# !!! FINE NUOVI IMPORT !!!

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QDialog, QLineEdit, QFormLayout, QDialogButtonBox,
    QTreeWidget, QTreeWidgetItem, QSpacerItem, QSizePolicy
)
from PySide6.QtGui import QPixmap, QFontDatabase, QFont
from PySide6.QtCore import Qt
import os
from pathlib import Path


class LoginDialog(QDialog):
    # ... (Il tuo codice esistente per LoginDialog) ...
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Login Associazione Windsurf Ceresio")
        layout = QFormLayout(self)

        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)

        layout.addRow("Username:", self.username)
        layout.addRow("Password:", self.password)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_credentials(self):
        return self.username.text(), self.password.text()


class MainWindow(QMainWindow):
    def __init__(self, ruolo):
        super().__init__()
        self.widget_cache = {}
        self.setWindowTitle("Windsurf Ceresio")
        self.ruolo = ruolo

        # --- Carica il QSS (Stile) ---
        qss_path = Path(__file__).resolve().parent / "style.qss"
        if qss_path.exists():
            with open(qss_path, "r") as f:
                self.setStyleSheet(f.read())
        else:
            print(f"AVVISO: File style.qss non trovato in {qss_path}. Lo stile predefinito verrà utilizzato.")

        # --- Carica Font Awesome per le icone ---
        font_awesome_path = Path(__file__).resolve().parent / "fa-solid-900.ttf"
        if font_awesome_path.exists():
            if QFontDatabase.addApplicationFont(str(font_awesome_path)) == -1:
                print(f"ERRORE: Impossibile caricare il font Font Awesome da {font_awesome_path}.")
        else:
            print(f"AVVISO: File 'fa-solid-900.ttf' non trovato in {font_awesome_path}. Le icone potrebbero non essere visualizzate correttamente.")
        
        # Imposta un font per le icone (Font Awesome) per il QTreeWidget
        self.icon_font = QFont("Font Awesome 6 Free", 14)
        self.icon_font.setStyleHint(QFont.Cursive)


        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)

        # QTreeWidget come menu ad albero
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        layout.addWidget(self.tree, 2)

        self.tree.itemClicked.connect(self.on_item_clicked)

        # --- Aggiunta degli elementi del menu condizionali al ruolo ---

        # Nodo Home
        item_home = QTreeWidgetItem(["\uf015 Home"])
        item_home.setFont(0, self.icon_font)
        self.tree.addTopLevelItem(item_home)

        # Nodo Gestione Tesserati (Solo Admin)
        item_tesserati = QTreeWidgetItem(["\uf0c0 Gestione Tesserati"])
        item_tesserati.setFont(0, self.icon_font)
        item_tesserati_annuali = QTreeWidgetItem(["Tesserati Annuali"])
        item_tesserati_giornalieri = QTreeWidgetItem(["Tesserati Giornalieri"])
        item_tesserati.addChildren([item_tesserati_annuali, item_tesserati_giornalieri])
        if self.ruolo == "admin":
            self.tree.addTopLevelItem(item_tesserati)

        # Nodo Materiali (Solo Admin)
        item_materiali = QTreeWidgetItem(["\uf7d9 Gestione Materiali"])
        item_materiali.setFont(0, self.icon_font)
        item_materiali_anagrafica = QTreeWidgetItem(["Anagrafica Materiali"])
        item_materiali_stampa = QTreeWidgetItem(["Stampa Lista Inventario"])
        item_materiali_stampa_codici = QTreeWidgetItem(["Stampa Codici a Barre"])
        item_materiali.addChildren([item_materiali_anagrafica, item_materiali_stampa, item_materiali_stampa_codici])
        if self.ruolo == "admin":
           self.tree.addTopLevelItem(item_materiali)

        # Nodo Noleggi (Admin e Operatore)
        item_noleggi = QTreeWidgetItem(["\uf445 Programma Noleggio Materiale"])
        item_noleggi.setFont(0, self.icon_font)
        item_noleggi_noleggio_materiale = QTreeWidgetItem(["Noleggio Materiale"])
        item_noleggi_situazione_noleggi = QTreeWidgetItem(["Situazione Noleggi"])
        item_noleggi_gestione_noleggi = QTreeWidgetItem(["Gestione Noleggi"])
        
        item_noleggi.addChild(item_noleggi_noleggio_materiale)
        item_noleggi.addChild(item_noleggi_situazione_noleggi)
        if self.ruolo == "admin":
            item_noleggi.addChild(item_noleggi_gestione_noleggi)
        
        self.tree.addTopLevelItem(item_noleggi)
        
        # --- INIZIO NUOVO CODICE PER "TESSERE NOLEGGI E CORSI" ---
        # Nodo Tessere Noleggi e Corsi (Solo Admin)
        # Icona: Ticket (fas fa-ticket-alt) - Unicode: \uf3ff (o \uf145 per 'ticket' se preferisci)
        item_tessere_parent = QTreeWidgetItem(["\uf3ff Tessere Noleggi e Corsi"]) # NOME ESATTO DEL PARENT
        item_tessere_parent.setFont(0, self.icon_font)
        
        item_crea_tessera = QTreeWidgetItem(["Crea Tessera Noleggi o Corsi"]) # NOME ESATTO DEL FIGLIO 1
        item_gestisci_tessera = QTreeWidgetItem(["Gestisci Tessera Noleggi o Corsi"]) # NOME ESATTO DEL FIGLIO 2
        
        item_tessere_parent.addChildren([item_crea_tessera, item_gestisci_tessera])
        
        if self.ruolo == "admin":
            self.tree.addTopLevelItem(item_tessere_parent)
        # --- FINE NUOVO CODICE PER "TESSERE NOLEGGI E CORSI" ---


        self.tree.expandAll()

        # Area contenuto
        self.stack = QStackedWidget()
        layout.addWidget(self.stack, 5)
        layout.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        logo_label = QLabel()
        img_path = Path(__file__).resolve().parent / "logo_windsurf_resized.jpg"
        if img_path.exists():
            pixmap = QPixmap(str(img_path))
            logo_label.setPixmap(pixmap)
        else:
            logo_label.setText("Logo non trovato")
            print(f"AVVISO: Immagine logo non trovata in {img_path}.")

        logo_label.setAlignment(Qt.AlignCenter)
        self.stack.addWidget(logo_label)
        
        self.widget_cache["Home"] = logo_label


    def on_item_clicked(self, item, column):
        # Home
        if item.text(0).endswith("Home"):
            self.stack.setCurrentWidget(self.widget_cache["Home"])
        
        # Tesserati Annuali (Solo Admin)
        elif item.text(0) == "Tesserati Annuali":
            if "TesseratiAnnuali" not in self.widget_cache:
                self.widget_cache["TesseratiAnnuali"] = FinestraGestioneSoci()
                self.stack.addWidget(self.widget_cache["TesseratiAnnuali"])
            self.stack.setCurrentWidget(self.widget_cache["TesseratiAnnuali"])
        
        # Anagrafica Materiali (Solo Admin)
        elif item.text(0) == "Anagrafica Materiali":
            if "AnagraficaMateriali" not in self.widget_cache:
                self.widget_cache["AnagraficaMateriali"] = DialogoAnagraficaMateriali()
                self.stack.addWidget(self.widget_cache["AnagraficaMateriali"])
            self.stack.setCurrentWidget(self.widget_cache["AnagraficaMateriali"])
        
        # Stampa Codici a Barre (Solo Admin)
        elif item.text(0) == "Stampa Codici a Barre":
            if "StampaBarcode" not in self.widget_cache:
                self.widget_cache["StampaBarcode"] = FinestraStampaCodici()
                self.stack.addWidget(self.widget_cache["StampaBarcode"])
            self.stack.setCurrentWidget(self.widget_cache["StampaBarcode"])
        
        # Noleggio Materiale (Admin e Operatore)
        elif item.text(0) == "Noleggio Materiale":
            if "NoleggioMateriale" not in self.widget_cache:
               self.widget_cache["NoleggioMateriale"] = NoleggioMateriale()
               self.stack.addWidget(self.widget_cache["NoleggioMateriale"])
            self.stack.setCurrentWidget(self.widget_cache["NoleggioMateriale"])
        
        # Situazione Noleggi (Admin e Operatore)
        elif item.text(0) == "Situazione Noleggi":
            if "SituazioneNoleggi" not in self.widget_cache:
                self.widget_cache["SituazioneNoleggi"] = SituazioneNoleggi()
                self.stack.addWidget(self.widget_cache["SituazioneNoleggi"])
            self.stack.setCurrentWidget(self.widget_cache["SituazioneNoleggi"])
        
        # Gestione Noleggi (Solo Admin)
        elif item.text(0) == "Gestione Noleggi":
            if "GestioneNoleggi" not in self.widget_cache:
                self.widget_cache["GestioneNoleggi"] = GestioneNoleggi()
                self.stack.addWidget(self.widget_cache["GestioneNoleggi"])
            self.stack.setCurrentWidget(self.widget_cache["GestioneNoleggi"])
            # self.widget_cache["SituazioneNoleggi"].load_noleggi() # Questa riga era per SituazioneNoleggi, non GestioneNoleggi

        # --- INIZIO NUOVO CODICE PER GESTIRE CLICK SU "TESSERE NOLEGGI E CORSI" ---
        # !!! NOME ESATTO DEL TESTO DEL MENU: "Crea Tessera Noleggi o Corsi"
        elif item.text(0) == "Crea Tessera Noleggi o Corsi": # <<< CORRETTO QUI
            # La chiave nella cache dovrebbe essere un nome semplice e unico
            if "CreaTessera" not in self.widget_cache: # <<< CHIAVE SEMPLIFICATA
                # DECOMMENTATO: Istanzia e aggiunge il widget
                self.widget_cache["CreaTessera"] = FinestraCreaTessera() # <<< NOME CLASSE DAL TUO IMPORT
                self.stack.addWidget(self.widget_cache["CreaTessera"])
                # print("DEBUG: Crea Tessera Noleggi non ancora implementata.") # <<<< Rimuovi questa riga
            self.stack.setCurrentWidget(self.widget_cache["CreaTessera"]) # <<< USA LA CHIAVE CORRETTA QUI
        
        # !!! NOME ESATTO DEL TESTO DEL MENU: "Gestisci Tessera Noleggi o Corsi"
        elif item.text(0) == "Gestisci Tessera Noleggi o Corsi": # <<< CORRETTO QUI
            print("DEBUG: Cliccato su Gestisci Tessera. Tentativo di caricare la finestra.")
            # La chiave nella cache dovrebbe essere un nome semplice e unico
            if "GestisciTessera" not in self.widget_cache: # <<< CHIAVE SEMPLIFICATA (come concordato)
                # DECOMMENTATO QUANDO AVRAI LA CLASSE:
                print("DEBUG: Finestra GestisciTessera non in cache. Creazione nuova istanza.") #
                self.widget_cache["GestisciTessera"] = FinestraGestisciTessera() # <<< NOME CLASSE DA FUTURO IMPORT
                self.stack.addWidget(self.widget_cache["GestisciTessera"])
               # print("DEBUG: Gestisci Tessera Noleggi o Corsi non ancora implementata.") # <<< Lascia per ora, rimuovi dopo
            self.stack.setCurrentWidget(self.widget_cache.get("GestisciTessera", self.widget_cache["Home"])) # <<< USA LA CHIAVE CORRETTA QUI, con fallback
            print("DEBUG: Finestra GestisciTessera impostata come widget corrente.") # <<< AGGIUNGI QUESTO
        # --- FINE NUOVO CODICE PER GESTIRE CLICK SU "TESSERE NOLEGGI E CORSI" ---
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    qss_path_app = Path(__file__).resolve().parent / "style.qss"
    if qss_path_app.exists():
        with open(qss_path_app, "r") as f:
            app.setStyleSheet(f.read())

    login = LoginDialog()
    if login.exec() == QDialog.Accepted:
        username, _ = login.get_credentials()
        
        ruolo = "user"
        if username == "admin":
            ruolo = "admin"
        elif username == "operatore":
            ruolo = "operatore"
        
        window = MainWindow(ruolo)
        window.resize(1280, 800)
        window.show()
        sys.exit(app.exec())