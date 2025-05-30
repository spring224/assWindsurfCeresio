from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
import sys
import sqlite3
from reportlab.pdfgen import canvas

DB_FILE = "soci.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS soci (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            cognome TEXT,
            email TEXT
        )
    """)
    conn.commit()
    conn.close()

def salva_socio(nome, cognome, email):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO soci (nome, cognome, email) VALUES (?, ?, ?)", (nome, cognome, email))
    conn.commit()
    conn.close()

def carica_soci():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, nome, cognome, email FROM soci")
    dati = c.fetchall()
    conn.close()
    return dati

def genera_pdf(nome, cognome, email):
    c = canvas.Canvas(f"{nome}_{cognome}_tessera.pdf")
    c.drawString(100, 750, "Tessera Socio")
    c.drawString(100, 730, f"Nome: {nome}")
    c.drawString(100, 710, f"Cognome: {cognome}")
    c.drawString(100, 690, f"Email: {email}")
    c.save()

class Finestra(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestione Soci - Windsurf")
        self.setMinimumWidth(600)
        self.layout = QVBoxLayout()

        self.nome_input = QLineEdit()
        self.nome_input.setPlaceholderText("Nome")
        self.cognome_input = QLineEdit()
        self.cognome_input.setPlaceholderText("Cognome")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")

        self.salva_btn = QPushButton("Salva Socio")
        self.salva_btn.clicked.connect(self.salva_socio)

        self.tabella = QTableWidget()
        self.tabella.setColumnCount(4)
        self.tabella.setHorizontalHeaderLabels(["Nome", "Cognome", "Email", "Stampa"])
        self.tabella.setColumnWidth(3, 100)

        self.layout.addWidget(QLabel("Inserimento nuovo socio:"))
        self.layout.addWidget(self.nome_input)
        self.layout.addWidget(self.cognome_input)
        self.layout.addWidget(self.email_input)
        self.layout.addWidget(self.salva_btn)
        self.layout.addWidget(self.tabella)

        self.setLayout(self.layout)
        self.aggiorna_tabella()

    def salva_socio(self):
        nome = self.nome_input.text()
        cognome = self.cognome_input.text()
        email = self.email_input.text()
        if nome and cognome and email:
            salva_socio(nome, cognome, email)
            self.nome_input.clear()
            self.cognome_input.clear()
            self.email_input.clear()
            self.aggiorna_tabella()
        else:
            QMessageBox.warning(self, "Errore", "Tutti i campi sono obbligatori.")

    def aggiorna_tabella(self):
        self.tabella.setRowCount(0)
        soci = carica_soci()
        for riga_idx, socio in enumerate(soci):
            self.tabella.insertRow(riga_idx)
            self.tabella.setItem(riga_idx, 0, QTableWidgetItem(socio[1]))
            self.tabella.setItem(riga_idx, 1, QTableWidgetItem(socio[2]))
            self.tabella.setItem(riga_idx, 2, QTableWidgetItem(socio[3]))
            btn = QPushButton("PDF")
            btn.clicked.connect(lambda _, n=socio[1], c=socio[2], e=socio[3]: genera_pdf(n, c, e))
            self.tabella.setCellWidget(riga_idx, 3, btn)

if __name__ == "__main__":
    init_db()
    app = QApplication(sys.argv)
    win = Finestra()
    win.show()
    sys.exit(app.exec())
