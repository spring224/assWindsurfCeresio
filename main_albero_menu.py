
from gestione_soci_annuali_pyside import FinestraGestioneSoci
from gestione_inventario import AnagraficaMateriali
from stampa_codici_barre import FinestraStampaCodici 
from noleggio_materiale import NoleggioMateriale
from situazione_noleggi import SituazioneNoleggi
from data_access import get_connection

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QDialog, QLineEdit, QFormLayout, QDialogButtonBox,
    QTreeWidget, QTreeWidgetItem 
)

from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
import os
from pathlib import Path

class LoginDialog(QDialog):
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

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)

        # QTreeWidget come menu ad albero
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        layout.addWidget(self.tree, 2)

        self.tree.itemClicked.connect(self.on_item_clicked)

        # Nodo Home
        item_home = QTreeWidgetItem(["🏠 Home"])
        self.tree.addTopLevelItem(item_home)


        # Sezione Gestione MENU ad albero
        # Nodo Gestione Tesserati
        item_tesserati = QTreeWidgetItem(["👥 Gestione Tesserati"])
        item_tesserati_annuali = QTreeWidgetItem(["Tesserati Annuali"])
        item_tesserati_giornalieri = QTreeWidgetItem(["Tesserati Giornalieri"])
        item_tesserati.addChildren([item_tesserati_annuali, item_tesserati_giornalieri])
        if self.ruolo == "admin":
            self.tree.addTopLevelItem(item_tesserati)

        # Nodo Materiali
        item_materiali = QTreeWidgetItem(["🧱 Gestione Materiali"])
        item_materiali_anagrafica = QTreeWidgetItem(["Anagrafica Materiali"])
        item_materiali_stampa = QTreeWidgetItem(["Stampa Lista Inventario"])
        Item_materiali_stampa_codici = QTreeWidgetItem(["Stampa Codici a Barre"])
        item_materiali.addChildren([item_materiali_anagrafica, item_materiali_stampa, Item_materiali_stampa_codici])
        if self.ruolo == "admin":
           self.tree.addTopLevelItem(item_materiali)

        # Nodo Noleggi
        item_noleggi = QTreeWidgetItem(["🚲 Programma Noleggio Materiale"])
        item_noleggi_noleggio_materiale = QTreeWidgetItem(["Noleggio Materiale"])
        item_noleggi_situazione_noleggi = QTreeWidgetItem(["Situazione Noleggi"])
        item_noleggi_gestione_noleggi = QTreeWidgetItem(["Gestione Noleggi"])
        item_noleggi.addChildren([item_noleggi_noleggio_materiale, item_noleggi_situazione_noleggi, item_noleggi_gestione_noleggi])
        if self.ruolo == "admin":
            self.tree.addTopLevelItem(item_noleggi)



        self.tree.expandAll()

        # Area contenuto
        self.stack = QStackedWidget()
        layout.addWidget(self.stack, 5)

        # Pagine
        logo_label = QLabel()
        img_path = Path(__file__).resolve().parent / "logo_windsurf_resized.jpg"
        pixmap = QPixmap(str(img_path))
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        self.stack.addWidget(logo_label)  # 0

        # Aggiunta widget soci annuali
        self.widget_soci_annuali = FinestraGestioneSoci()
        self.stack.addWidget(self.widget_soci_annuali)
        # Aggiunta widget materiali
        self.widget_materiali = AnagraficaMateriali()
        self.stack.addWidget(self.widget_materiali)

    def on_item_clicked(self, item, column):
        if item.text(0) == "Tesserati Annuali":
            self.stack.setCurrentWidget(self.widget_soci_annuali)

        elif item.text(0) == "Anagrafica Materiali":
         if "Materiali" not in self.widget_cache:
            self.widget_cache["Materiali"] = AnagraficaMateriali()
            self.stack.addWidget(self.widget_cache["Materiali"])
            self.stack.setCurrentWidget(self.widget_cache["Materiali"])

        elif item.text(0) == "Stampa Codici a Barre":
         if "StampaBarcode" not in self.widget_cache:
            from stampa_codici_barre import FinestraStampaCodici
            self.widget_cache["StampaBarcode"] = FinestraStampaCodici()
            self.stack.addWidget(self.widget_cache["StampaBarcode"])
            self.stack.setCurrentWidget(self.widget_cache["StampaBarcode"])
        elif item.text(0) == "Noleggio Materiale":
            if "NoleggioMateriale" not in self.widget_cache:
               from noleggio_materiale import NoleggioMateriale
               self.widget_cache["NoleggioMateriale"] = NoleggioMateriale()
               self.stack.addWidget(self.widget_cache["NoleggioMateriale"])
            self.stack.setCurrentWidget(self.widget_cache["NoleggioMateriale"])
        elif item.text(0) == "Situazione Noleggi":
            if "SituazioneNoleggi" not in self.widget_cache:
                from situazione_noleggi import SituazioneNoleggi
                self.widget_cache["SituazioneNoleggi"] = SituazioneNoleggi()
                self.stack.addWidget(self.widget_cache["SituazioneNoleggi"])
            self.stack.setCurrentWidget(self.widget_cache["SituazioneNoleggi"])
        elif item.text(0) == "Gestione Noleggi":
            if "GestioneNoleggi" not in self.widget_cache:
                from gestione_noleggi import GestioneNoleggi
                self.widget_cache["GestioneNoleggi"] = GestioneNoleggi()
                self.stack.addWidget(self.widget_cache["GestioneNoleggi"])
            self.stack.setCurrentWidget(self.widget_cache["GestioneNoleggi"])
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = LoginDialog()
    if login.exec() == QDialog.Accepted:
        username, _ = login.get_credentials()
        ruolo = "admin"  # Simulazione ruolo
        if username == "admin":
            ruolo = "admin"
        else:
            ruolo = "user" 
        window = MainWindow(ruolo)
        window.show()
        sys.exit(app.exec())
