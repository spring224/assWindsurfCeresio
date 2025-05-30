import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout, QStackedWidget, QDialog, QLineEdit, QFormLayout, QDialogButtonBox
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login Windsurf Ceresio")
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

        # Menu laterale
        menu_layout = QVBoxLayout()
        menu_layout.setSpacing(10)

        btn_logo = QPushButton("Home")
        btn_tesserati = QPushButton("Gestione Tesserati")
        btn_materiali = QPushButton("Gestione Materiali")
        btn_noleggi = QPushButton("Gestione Noleggi")

        if self.ruolo != "admin":
            btn_tesserati.hide()
            btn_materiali.hide()

        btn_logo.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        btn_tesserati.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        btn_materiali.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        btn_noleggi.clicked.connect(lambda: self.stack.setCurrentIndex(3))

        for btn in [btn_logo, btn_tesserati, btn_materiali, btn_noleggi]:
            menu_layout.addWidget(btn)

        layout.addLayout(menu_layout, 1)

        # Area centrale
        self.stack = QStackedWidget()

        logo_label = QLabel()
        pixmap = QPixmap("logo_windsurf_resized.jpg")
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        self.stack.addWidget(logo_label)  # Index 0

        self.stack.addWidget(QLabel("Modulo Gestione Tesserati"))  # Index 1
        self.stack.addWidget(QLabel("Modulo Gestione Materiali"))  # Index 2
        self.stack.addWidget(QLabel("Modulo Gestione Noleggi"))    # Index 3

        layout.addWidget(self.stack, 4)

# Avvio applicazione (QApplication PRIMA di tutto)
app = QApplication(sys.argv)

login = LoginDialog()
if login.exec() == QDialog.Accepted:
    user, pwd = login.get_credentials()
    if user == "admin" and pwd == "admin":
        window = MainWindow("admin")
        window.resize(800, 500)
        window.show()
        sys.exit(app.exec())
    elif user == "operatore" and pwd == "operatore":
        window = MainWindow("operatore")
        window.resize(800, 500)
        window.show()
        sys.exit(app.exec())
    else:
        print("❌ Credenziali errate.")
else:
    print("❌ Login annullato.")