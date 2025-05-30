import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QDialog, QLineEdit, QFormLayout, QDialogButtonBox,
    QTreeWidget, QTreeWidgetItem
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

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
        self.setWindowTitle("Windsurf Ceresio")
        self.ruolo = ruolo

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)

        # QTreeWidget come menu ad albero
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)

        # Nodo Home
        item_home = QTreeWidgetItem(["🏠 Home"])
        self.tree.addTopLevelItem(item_home)

        # Nodo Gestione Tesserati
        item_tesserati = QTreeWidgetItem(["👥 Gestione Tesserati"])
        item_tesserati_annuali = QTreeWidgetItem(["Tesserati Annuali"])
        item_tesserati_giornalieri = QTreeWidgetItem(["Tesserati Giornalieri"])
        item_tesserati.addChildren([item_tesserati_annuali, item_tesserati_giornalieri])
        if self.ruolo == "admin":
            self.tree.addTopLevelItem(item_tesserati)

        # Nodo Materiali
        item_materiali = QTreeWidgetItem(["🧱 Gestione Materiali"])
        self.tree.addTopLevelItem(item_materiali)

        # Nodo Noleggi
        item_noleggi = QTreeWidgetItem(["🚲 Gestione Noleggi"])
        self.tree.addTopLevelItem(item_noleggi)

        self.tree.expandAll()
        layout.addWidget(self.tree, 2)

        # Area contenuto
        self.stack = QStackedWidget()
        layout.addWidget(self.stack, 5)

        # Pagine
        logo_label = QLabel()
        pixmap = QPixmap("logo_windsurf_resized.jpg")
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        self.stack.addWidget(logo_label)  # 0

        self.stack.addWidget(QLabel("📋 Tesserati Annuali"))        # 1
        self.stack.addWidget(QLabel("📋 Tesserati Giornalieri"))    # 2
        self.stack.addWidget(QLabel("🔧 Gestione Materiali"))       # 3
        self.stack.addWidget(QLabel("📦 Gestione Noleggi"))         # 4
        self.stack.addWidget(QLabel("📚 Gestione Corsi"))           # 5
        self.stack.addWidget(QLabel("⚙️ Gestione Applicazione"))    # 6
        self.stack.addWidget(QLabel("📊 Statistiche e Report"))     # 7
        self.stack.addWidget(QLabel("🔒 Impostazioni di Sicurezza"))  # 8

        self.tree.currentItemChanged.connect(self.cambia_pagina)
# main_albero_menu.py
    def cambia_pagina(self, item):
        if not item:
            return
        testo = item.text(0)
        if "Home" in testo:
            self.stack.setCurrentIndex(0)
        elif "Annuali" in testo:
            self.stack.setCurrentIndex(1)
        elif "Giornalieri" in testo:
            self.stack.setCurrentIndex(2)
        elif "Materiali" in testo:
            self.stack.setCurrentIndex(3)
        elif "Noleggi" in testo:
            self.stack.setCurrentIndex(4)
        elif "Corsi" in testo:
            self.stack.setCurrentIndex(5)
        elif "Applicazione" in testo:
            self.stack.setCurrentIndex(6)
        elif "Statistiche" in testo:
            self.stack.setCurrentIndex(7)
        elif "Sicurezza" in testo:
            self.stack.setCurrentIndex(8)

# Avvio app
app = QApplication(sys.argv)

login = LoginDialog()
if login.exec() == QDialog.Accepted:
    user, pwd = login.get_credentials()
    if user == "admin" and pwd == "admin":
        window = MainWindow("admin")
        window.resize(900, 550)
        window.show()
        sys.exit(app.exec())
    elif user == "operatore" and pwd == "operatore":
        window = MainWindow("operatore")
        window.resize(900, 550)
        window.show()
        sys.exit(app.exec())
    else:
        print("❌ Credenziali errate.")
else:
    print("❌ Login annullato.")