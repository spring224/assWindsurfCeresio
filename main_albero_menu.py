import sys
import os
from pathlib import Path
import shutil

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QDialog, QLineEdit, QFormLayout, QDialogButtonBox,
    QTreeWidget, QTreeWidgetItem, QSpacerItem, QSizePolicy, QPushButton, QMessageBox, QFrame # AGGIUNGI QFrame
)
from PySide6.QtGui import QPixmap, QFontDatabase, QFont
from PySide6.QtCore import Qt

# !!! AGGIUNGI QUESTI NUOVI IMPORT PER LE CLASSI DELLE TESSERE NOLEGGIO !!!
# Assicurati che questi file esistano e contengano le classi FinestraCreaTessera e FinestraGestisciTessera
from crea_tessere import FinestraCreaTessera
from gestisci_tessere import FinestraGestisciTessera
# !!! FINE NUOVI IMPORT !!!

# Importazioni per gli altri moduli
from gestione_inventario import DialogoAnagraficaMateriali
from stampa_codici_barre import FinestraStampaCodici
from noleggio_materiale import NoleggioMateriale
from situazione_noleggi import SituazioneNoleggi
from data_access import get_connection # <-- Questa funzione dovrà essere aggiornata
from gestione_noleggi import GestioneNoleggi
from gestione_soci_annuali_pyside import FinestraGestioneSoci
from dialogo_comunicazioni import DialogoComunicazioni


# ==============================================================================
# --- INIZIO CODICE PER LA GESTIONE DEI PERCORSI DELLE RISORSE E DEL DB (GIÀ DISCUSSO) ---
# ==============================================================================

# main_app.py (DOPO I TUOI IMPORT ESISTENTI)

# --- 1. Definizione Percorsi Base per Risorse e Dati Utente ---
# (Copiare/incollare questo blocco esattamente come fornito prima)
if getattr(sys, 'frozen', False):
    resource_base_dir = Path(sys._MEIPASS)
else:
    resource_base_dir = Path(__file__).resolve().parent

if os.name == 'nt':
    persistent_app_data_root = Path(os.environ['APPDATA'])
elif os.name == 'posix':
    persistent_app_data_root = Path.home() / '.local' / 'share'
else:
    persistent_app_data_root = Path.home()

# --- 2. Nomi dei File e delle Cartelle Specifici ---
# (Copiare/incollare questo blocco esattamente come fornito prima)
APP_DATA_FOLDER_NAME = "AssociazioneWindsurfCeresioAppDati" # <<< INSERISCI QUI IL NOME DESIDERATO
DB_FILENAME = "applicazionedb.db"

# --- 3. Definizione Percorsi Completi ---
# (Copiare/incollare questo blocco esattamente come fornito prima)
template_db_path = resource_base_dir / "gestione_dati" / DB_FILENAME
persistent_app_data_path = persistent_app_data_root / APP_DATA_FOLDER_NAME
final_db_path = persistent_app_data_path / DB_FILENAME

# --- 4. Logica di Copia del Database all'Avvio (Solo per App Compilate) ---
# (Copiare/incollare questo blocco esattamente come fornito prima)
if getattr(sys, 'frozen', False):
    persistent_app_data_path.mkdir(parents=True, exist_ok=True)
    if not final_db_path.exists():
        try:
            print(f"DEBUG: Tentativo di copiare il database da: {template_db_path} a: {final_db_path}")
            shutil.copy2(template_db_path, final_db_path)
            print(f"DEBUG: Database copiato con successo in {final_db_path}")
        except Exception as e:
            print(f"ERRORE GRAVE: Impossibile copiare il database! Dettagli: {e}")
            print(f"DEBUG: Percorso sorgente (template_db_path) cercato: {template_db_path}")
            print(f"DEBUG: Esistenza sorgente: {template_db_path.exists()}")
            print(f"DEBUG: Percorso destinazione (final_db_path): {final_db_path}")
            print(f"DEBUG: Esistenza cartella destinazione: {final_db_path.parent.exists()}")
            sys.exit(1)
else:
    (resource_base_dir / "gestione_dati").mkdir(parents=True, exist_ok=True)
    print(f"DEBUG: Applicazione in modalità sviluppo. Il database locale sarà in: {resource_base_dir / 'gestione_dati' / DB_FILENAME}")

# --- ASSICURATI CHE L'APP USI SEMPRE 'final_db_path' PER LE OPERAZIONI DB ---
# Questo è FONDAMENTALE. Tutte le tue chiamate a 'get_connection' (in data_access.py)
# o a qualsiasi altra funzione che interagisce con il database DEVONO USARE 'final_db_path'.
# Ad esempio, se hai una classe MainApp o MainWindow, potresti passarglielo così:
# self.db_path_per_uso = final_db_path
# E poi le tue classi DialogoListaSoci, DialogoSocio, etc. devono ricevere questo percorso.
# ==============================================================================
# --- FINE CODICE PER LA GESTIONE DEI PERCORSI ---
# ==============================================================================


# ==============================================================================
# --- INIZIO CODICE: Pannello di Login Integrato nella Main Window ---
# ==============================================================================
class LoginPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.login_button = QPushButton("Login")
        self.login_button.setDefault(True) # Rende il bottone predefinito per ENTER

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        # Carica il logo per la schermata di login
        logo_label = QLabel()
        # Usa app_base_path per il logo
        img_path = resource_base_dir / "logo_windsurf_resized.jpg"
        if img_path.exists():
            pixmap = QPixmap(str(img_path))
            logo_label.setPixmap(pixmap)
        else:
            logo_label.setText("Logo non trovato")
            print(f"AVVISO: Immagine logo non trovata in {img_path} per la schermata di login.")
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)

        # Spaziatore superiore per centrare il form
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        form_layout.addRow("Username:", self.username_input)
        form_layout.addRow("Password:", self.password_input)
        
        # Aggiunge il form layout al layout principale
        layout.addLayout(form_layout)
        
        # Spaziatore inferiore
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Aggiunge il bottone di login (allineato al centro)
        button_layout = QHBoxLayout()
        button_layout.addStretch() # Spaziatore per centrare
        button_layout.addWidget(self.login_button)
        button_layout.addStretch() # Spaziatore per centrare
        layout.addLayout(button_layout)

        # Allineamento centrale per il pannello stesso
        layout.setAlignment(Qt.AlignCenter)

# ==============================================================================
# --- FINE CODICE: Pannello di Login Integrato ---
# ==============================================================================


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.widget_cache = {}
        self.setWindowTitle("Gestionale Associazione All Sport Circolo Nautico Ceresio")
        self.ruolo = None
        self.db_path = final_db_path

        # --- Carica il QSS (Stile) ---
        qss_path = resource_base_dir / "style.qss"
        if qss_path.exists():
            with open(qss_path, "r") as f:
                 self.setStyleSheet(f.read()) # <<< COMMENTA QUESTA RIGA
                #print("DEBUG: Caricamento style.qss disabilitato per test.")
        else:
            print(f"AVVISO: File style.qss non trovato in {qss_path}. Lo stile predefinito verrà utilizzato.")

        # --- Carica Font Awesome per le icone ---
        font_awesome_path = resource_base_dir / "fa-solid-900.ttf"
        if font_awesome_path.exists():
            if QFontDatabase.addApplicationFont(str(font_awesome_path)) == -1:
                print(f"ERRORE: Impossibile caricare il font Font Awesome da {font_awesome_path}.")
        else:
            print(f"AVVISO: File 'fa-solid-900.ttf' non trovato in {font_awesome_path}. Le icone potrebbero non essere visualizzate correttamente.")
        
        self.icon_font = QFont("Font Awesome 6 Free", 14)
        self.icon_font.setStyleHint(QFont.Cursive)

        # Stack principale per gestire il cambio tra login e interfaccia completa dell'applicazione
        self.app_stack = QStackedWidget()
        self.setCentralWidget(self.app_stack)

        # Stack dedicato ai contenuti che appaiono nell'area destra DOPO il login
        # Inizializzato qui, non in init_main_ui
        self.content_stack = QStackedWidget()

        self.init_login_ui() # Inizializza la schermata di login e la aggiunge a self.app_stack
        self.init_main_ui()  # Inizializza il layout principale dell'applicazione e lo aggiunge a self.app_stack
        
        # Tutti i pannelli di contenuto sono creati e aggiunti qui.
        self.init_content_widgets() # NUOVA CHIAMATA QUI PER INIZIALIZZARE TUTTI I CONTENUTI

        self.app_stack.setCurrentWidget(self.login_panel) # Imposta il pannello di login come vista iniziale

    def init_login_ui(self):
        """Inizializza il pannello di login e lo aggiunge allo stack principale."""
        self.login_panel = LoginPanel(self)
        self.app_stack.addWidget(self.login_panel) # USA self.app_stack
        self.login_panel.login_button.clicked.connect(self.attempt_login)

    def init_main_ui(self):
        """Inizializza il layout principale dell'applicazione (menu e contenitore per i contenuti)."""
        # Questo sarà il widget che contiene l'albero e lo stack dei contenuti, aggiunto a self.app_stack
        self.main_app_widget = QWidget() # Rinominato per chiarezza
        main_app_layout = QHBoxLayout(self.main_app_widget)

        # QTreeWidget come menu ad albero (parte sinistra)
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.itemClicked.connect(self.on_item_clicked)
        main_app_layout.addWidget(self.tree, 1) # Stretch factor per bilanciare lo spazio

        # Contenitore per lo stack dei contenuti (parte destra)
        content_frame = QFrame()
        content_frame.setFrameShape(QFrame.StyledPanel)
        content_frame_layout = QVBoxLayout(content_frame)
        content_frame_layout.setContentsMargins(0, 0, 0, 0) # Rimuovi margini interni

        # AGGIUNGIAMO self.content_stack al layout del frame dei contenuti
        content_frame_layout.addWidget(self.content_stack)
        main_app_layout.addWidget(content_frame, 4) # Stretch factor maggiore per l'area contenuti

        # Aggiunge il widget contenente l'intera UI dell'app a self.app_stack
        # Questo widget sarà mostrato dopo il login.
        self.app_stack.addWidget(self.main_app_widget) # Aggiunge il widget del contenuto principale allo stack generale

    def init_content_widgets(self):
        """
        Inizializza e aggiunge tutti i widget dei contenuti a self.content_stack.
        Questo metodo è chiamato una sola volta all'avvio dell'applicazione.
        """
        # Home Page
        home_widget = QWidget()
        home_layout = QVBoxLayout(home_widget)
        home_label = QLabel("Benvenuto! Seleziona una voce dal menu.")
        home_label.setAlignment(Qt.AlignCenter)
        home_label.setStyleSheet("font-size: 24px; color: #555;")
        home_layout.addWidget(home_label)
        self.widget_cache["Home"] = home_widget
        self.content_stack.addWidget(home_widget)

        # Tesserati Annuali
        self.widget_cache["TesseratiAnnuali"] = FinestraGestioneSoci()
        self.content_stack.addWidget(self.widget_cache["TesseratiAnnuali"])

        # Anagrafica Materiali
        self.widget_cache["AnagraficaMateriali"] = DialogoAnagraficaMateriali()
        self.content_stack.addWidget(self.widget_cache["AnagraficaMateriali"])

        # Stampa Codici a Barre
        self.widget_cache["StampaBarcode"] = FinestraStampaCodici()
        self.content_stack.addWidget(self.widget_cache["StampaBarcode"])
        
        # Noleggio Materiale
        self.widget_cache["NoleggioMateriale"] = NoleggioMateriale()
        self.content_stack.addWidget(self.widget_cache["NoleggioMateriale"])

        # Situazione Noleggi
        self.widget_cache["SituazioneNoleggi"] = SituazioneNoleggi()
        self.content_stack.addWidget(self.widget_cache["SituazioneNoleggi"])

        # Gestione Noleggi
        self.widget_cache["GestioneNoleggi"] = GestioneNoleggi()
        self.content_stack.addWidget(self.widget_cache["GestioneNoleggi"])

        # Crea Tessera Noleggi o Corsi
        self.widget_cache["CreaTessera"] = FinestraCreaTessera()
        self.content_stack.addWidget(self.widget_cache["CreaTessera"])

        # Gestisci Tessera Noleggi o Corsi
        self.widget_cache["GestisciTessera"] = FinestraGestisciTessera()
        self.content_stack.addWidget(self.widget_cache["GestisciTessera"])

        # Imposta la Home page come widget iniziale dello stack dei contenuti
        self.content_stack.setCurrentWidget(self.widget_cache["Home"])

    def attempt_login(self):
        """Tenta il login con le credenziali inserite."""
        username = self.login_panel.username_input.text()
        password = self.login_panel.password_input.text()

        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT ruolo FROM Utenti WHERE username = ? AND password = ?", (username, password))
                result = cursor.fetchone()
                
                if result:
                    self.ruolo = result[0]
                    self.populate_menu() # Popola il menu in base al ruolo
                    self.app_stack.setCurrentWidget(self.main_app_widget) # USA self.app_stack e self.main_app_widget
                    self.tree.expandAll() # Espandi il menu
                    self.resize(1280, 800) # Imposta la dimensione desiderata dopo il login
                    # Dopo il login, mostra la Home page nello stack dei contenuti
                    self.content_stack.setCurrentWidget(self.widget_cache["Home"])
                else:
                    QMessageBox.warning(self, "Login Fallito", "Username o Password errati.")
                    self.login_panel.password_input.clear() # Cancella la password
        except Exception as e:
            QMessageBox.critical(self, "Errore Database", f"Impossibile connettersi al database: {e}")
            print(f"ERRORE DB DURANTE LOGIN: {e}")
            sys.exit(1)

    def populate_menu(self):
        """Popola il QTreeWidget con le voci di menu basate sul ruolo dell'utente."""
        self.tree.clear()

        item_home = QTreeWidgetItem(["\uf015 Home"])
        item_home.setFont(0, self.icon_font)
        self.tree.addTopLevelItem(item_home)

        item_tesserati = QTreeWidgetItem(["\uf0c0 Gestione Tesserati"])
        item_tesserati.setFont(0, self.icon_font)
        item_tesserati_annuali = QTreeWidgetItem(["Tesserati Annuali"])
        item_tesserati_giornalieri = QTreeWidgetItem(["Tesserati Giornalieri"])
        item_tesserati.addChildren([item_tesserati_annuali, item_tesserati_giornalieri])
        if self.ruolo == "admin":
            self.tree.addTopLevelItem(item_tesserati)

        item_materiali = QTreeWidgetItem(["\uf7d9 Gestione Materiali"])
        item_materiali.setFont(0, self.icon_font)
        item_materiali_anagrafica = QTreeWidgetItem(["Anagrafica Materiali"])
        item_materiali_stampa = QTreeWidgetItem(["Stampa Lista Inventario"]) # Suppongo che questo sia un placeholder, non hai una classe per questo.
        item_materiali_stampa_codici = QTreeWidgetItem(["Stampa Codici a Barre"])
        item_materiali.addChildren([item_materiali_anagrafica, item_materiali_stampa, item_materiali_stampa_codici])
        if self.ruolo == "admin":
           self.tree.addTopLevelItem(item_materiali)

        item_noleggi = QTreeWidgetItem(["\uf445 Programma Noleggio Materiale"])
        item_noleggi.setFont(0, self.icon_font)
        item_noleggi_noleggio_materiale = QTreeWidgetItem(["Noleggio Materiale"])
        item_noleggi_situazione_noleggi = QTreeWidgetItem(["Situazione Noleggi"])
        item_noleggi_gestione_noleggi = QTreeWidgetItem(["Gestione Noleggi"])
        
        item_noleggi.addChild(item_noleggi_noleggio_materiale)
        item_noleggi.addChild(item_noleggi_situazione_noleggi)
        if self.ruolo == "admin" or self.ruolo == "operatore": # L'operatore può vedere Noleggio e Situazione
            self.tree.addTopLevelItem(item_noleggi)
        if self.ruolo == "admin": # Solo l'admin vede Gestione Noleggi
            item_noleggi.addChild(item_noleggi_gestione_noleggi)
        
        item_tessere_parent = QTreeWidgetItem(["\uf3ff Tessere Noleggi e Corsi"])
        item_tessere_parent.setFont(0, self.icon_font)
        
        item_crea_tessera = QTreeWidgetItem(["Crea Tessera Noleggi o Corsi"])
        item_gestisci_tessera = QTreeWidgetItem(["Gestisci Tessera Noleggi o Corsi"])
        
        item_tessere_parent.addChildren([item_crea_tessera, item_gestisci_tessera])
        
        if self.ruolo == "admin":
            self.tree.addTopLevelItem(item_tessere_parent)
        
        self.tree.expandAll()

    def on_item_clicked(self, item, column):
        text = item.text(0)
        print(f"DEBUG: Cliccato su: {text}. Tentativo di caricare la finestra.")

        # Mappa le voci di menu alle chiavi della widget_cache
        menu_to_cache_map = {
            "\uf015 Home": "Home",
            "Tesserati Annuali": "TesseratiAnnuali",
            "Anagrafica Materiali": "AnagraficaMateriali",
            "Stampa Codici a Barre": "StampaBarcode",
            "Noleggio Materiale": "NoleggioMateriale",
            "Situazione Noleggi": "SituazioneNoleggi",
            "Gestione Noleggi": "GestioneNoleggi",
            "Crea Tessera Noleggi o Corsi": "CreaTessera",
            "Gestisci Tessera Noleggi o Corsi": "GestisciTessera",
        }

        cache_key = menu_to_cache_map.get(text)

        if cache_key:
            # Crea l'istanza del widget solo se non è già in cache
            if cache_key not in self.widget_cache:
                print(f"DEBUG: Finestra {cache_key} non in cache. Creazione nuova istanza.")
                if cache_key == "TesseratiAnnuali":
                    self.widget_cache[cache_key] = FinestraGestioneSoci(self.db_path)
                elif cache_key == "AnagraficaMateriali":
                    self.widget_cache[cache_key] = DialogoAnagraficaMateriali()
                elif cache_key == "StampaBarcode":
                    self.widget_cache[cache_key] = FinestraStampaCodici()
                elif cache_key == "NoleggioMateriale":
                    self.widget_cache[cache_key] = NoleggioMateriale()
                elif cache_key == "SituazioneNoleggi":
                    self.widget_cache[cache_key] = SituazioneNoleggi()
                elif cache_key == "GestioneNoleggi":
                    self.widget_cache[cache_key] = GestioneNoleggi()
                elif cache_key == "CreaTessera":
                    self.widget_cache[cache_key] = FinestraCreaTessera()
                elif cache_key == "GestisciTessera":
                    self.widget_cache[cache_key] = FinestraGestisciTessera()
                # Aggiungi qui gli altri casi per i nuovi widget, se necessario
                
                # Aggiungi il widget appena creato al self.content_stack
                self.content_stack.addWidget(self.widget_cache[cache_key]) # <<< QUI È FONDAMENTALE USARE content_stack

            # Imposta il widget corrente nello stack dei contenuti
            self.content_stack.setCurrentWidget(self.widget_cache[cache_key]) # <<< QUI È FONDAMENTALE USARE content_stack
            print(f"DEBUG: Finestra {cache_key} impostata come widget corrente.")
        else:
            print(f"AVVISO: La voce '{text}' non ha un widget associato o non è ancora implementata.")
            QMessageBox.information(self, "Funzionalità Non Disponibile",
                                    f"La funzionalità '{text}' non è ancora implementata o disponibile.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())