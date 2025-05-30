from PySide6.QtWidgets import QDialog, QLineEdit, QFormLayout, QDialogButtonBox
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton,
    QWidget, QVBoxLayout, QLabel
)
import sys
from gestione_tesserati import GestioneTesseratiWindow

class FinestraSecondaria(QWidget):
    def __init__(self, titolo):
        super().__init__()
        self.setWindowTitle(titolo)
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Contenuto della finestra: {titolo}"))
        self.setLayout(layout)


# ---------------------------
# LoginDialog
class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        layout = QFormLayout()
        layout.addRow("Username:", self.username_input)
        layout.addRow("Password:", self.password_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def get_credentials(self):
        return self.username_input.text(), self.password_input.text()


class MenuPrincipale(QMainWindow):
    def __init__(self, ruolo):
        super().__init__()
        self.setWindowTitle("Menu Principale - Windsurf Ceresio")
        self.setFixedSize(400, 300)

        central_widget = QWidget()
        layout = QVBoxLayout()

        if ruolo == "amministrazione":

            btn_tesserati = QPushButton("Gestione Tesserati")
            btn_tesserati.clicked.connect(lambda: self.apri_finestra("Gestione Tesserati"))
            layout.addWidget(btn_tesserati)

            btn_materiali = QPushButton("Gestione Materiali")
            btn_materiali.clicked.connect(lambda: self.apri_finestra("Gestione Materiali"))
            layout.addWidget(btn_materiali)

            btn_noleggi = QPushButton("Gestione Noleggi")
            btn_noleggi.clicked.connect(lambda: self.apri_finestra("Gestione Noleggi"))
            layout.addWidget(btn_noleggi)
             
            btn_gestione_corsi = QPushButton("Gestione Corsi")
            btn_gestione_corsi.clicked.connect(lambda: self.apri_finestra("Gestione Corsi"))
            layout.addWidget(btn_gestione_corsi)

            btn_amministrazione = QPushButton("Gestione Amministrazione")
            btn_amministrazione.clicked.connect(lambda: self.apri_finestra("Gestione Amministrazione"))
            layout.addWidget(btn_amministrazione)
        elif ruolo == "operatore":
            btn_soci = QPushButton("Gestione Soci")
            btn_soci.clicked.connect(lambda: self.apri_finestra("Gestione Soci"))
            layout.addWidget(btn_soci)

            btn_noleggi = QPushButton("Gestione Noleggi")
            btn_noleggi.clicked.connect(lambda: self.apri_finestra("Gestione Noleggi"))
            layout.addWidget(btn_noleggi)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.finestre_aperte = []

    def apri_finestra(self, titolo):
        finestra = FinestraSecondaria(titolo)
        finestra.show()
        self.finestre_aperte.append(finestra)

    def apri_finestra(self, titolo):
     if titolo == "Gestione Tesserati":
        finestra = GestioneTesseratiWindow()
     else:
        finestra = FinestraSecondaria(titolo)
        finestra.show()
        self.finestre_aperte.append(finestra)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Login fittizio statico
    UTENTI = {
        "admin": {"password": "adminpass", "ruolo": "amministrazione"},
        "operatore": {"password": "op123", "ruolo": "operatore"}
    }

    login = LoginDialog()
    if login.exec() == QDialog.Accepted:
        username, password = login.get_credentials()
        if username in UTENTI and UTENTI[username]["password"] == password:
            ruolo = UTENTI[username]["ruolo"]
            finestra_principale = MenuPrincipale(ruolo)
            finestra_principale.show()
            sys.exit(app.exec())
        else:
            print("Credenziali errate.")
            sys.exit()
    else:
        sys.exit()

    def apri_gestione_tesserati(self):
        self.finestra_tesserati = GestioneTesseratiWindow()
        self.finestra_tesserati.show()