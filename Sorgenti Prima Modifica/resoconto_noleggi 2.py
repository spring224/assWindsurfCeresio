from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QDateEdit, QMessageBox
)
from PySide6.QtCore import QDate
from datetime import datetime
import sqlite3

class FinestraResoconto(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Resoconto Noleggi")
        self.resize(500, 300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Selezione modalità
        self.cmb_modalita = QComboBox()
        self.cmb_modalita.addItems(["Giorno", "Mese", "Anno", "Periodo Personalizzato"])
        self.cmb_modalita.currentIndexChanged.connect(self.aggiorna_modalita)

        layout.addWidget(QLabel("Seleziona tipo di resoconto:"))
        layout.addWidget(self.cmb_modalita)

        # Selezione date
        self.date_da = QDateEdit(QDate.currentDate())
        self.date_da.setCalendarPopup(True)
        self.date_a = QDateEdit(QDate.currentDate())
        self.date_a.setCalendarPopup(True)

        layout_date = QHBoxLayout()
        layout_date.addWidget(QLabel("Da:"))
        layout_date.addWidget(self.date_da)
        layout_date.addWidget(QLabel("A:"))
        layout_date.addWidget(self.date_a)
        layout.addLayout(layout_date)

        # Pulsante calcola
        self.btn_calcola = QPushButton("📊 Calcola")
        self.btn_calcola.clicked.connect(self.calcola_resoconto)
        layout.addWidget(self.btn_calcola)

        # Area risultati
        self.lbl_risultati = QLabel("Totale: -")
        layout.addWidget(self.lbl_risultati)

        self.setLayout(layout)
        self.aggiorna_modalita()

    def aggiorna_modalita(self):
        mode = self.cmb_modalita.currentText()
        if mode == "Giorno":
            self.date_da.setEnabled(True)
            self.date_a.setEnabled(False)
        elif mode == "Mese" or mode == "Anno":
            self.date_da.setEnabled(True)
            self.date_a.setEnabled(False)
        else:  # Periodo Personalizzato
            self.date_da.setEnabled(True)
            self.date_a.setEnabled(True)

    def calcola_resoconto(self):
        mode = self.cmb_modalita.currentText()
        data_da = self.date_da.date().toString("yyyy-MM-dd")
        data_a = self.date_a.date().toString("yyyy-MM-dd")

        query = ""
        params = ()

        if mode == "Giorno":
            query = "SELECT * FROM Noleggi WHERE data_inizio = ? AND stato = 'chiuso'"
            params = (data_da,)
        elif mode == "Mese":
            anno, mese = data_da[:4], data_da[5:7]
            query = "SELECT * FROM Noleggi WHERE strftime('%Y', data_inizio) = ? AND strftime('%m', data_inizio) = ? AND stato = 'chiuso'"
            params = (anno, mese)
        elif mode == "Anno":
            anno = data_da[:4]
            query = "SELECT * FROM Noleggi WHERE strftime('%Y', data_inizio) = ? AND stato = 'chiuso'"
            params = (anno,)
        else:  # Periodo Personalizzato
            query = "SELECT * FROM Noleggi WHERE data_inizio BETWEEN ? AND ? AND stato = 'chiuso'"
            params = (data_da, data_a)

        conn = sqlite3.connect("windsurf.db")
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(query, params)
        righe = cur.fetchall()
        conn.close()

        n_noleggi = len(righe)
        ore_totali = sum(r["durata_ore"] for r in righe)

        # Calcola guadagno stimato dal listino
        guadagno = 0.0
        conn = sqlite3.connect("windsurf.db")
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        for r in righe:
            cur.execute("SELECT prezzo_orario FROM ListinoNoleggio WHERE tipo = (SELECT tipo FROM Materiali WHERE id = ?)", (r["id_materiale"],))
            prezzo = cur.fetchone()
            if prezzo:
                guadagno += prezzo["prezzo_orario"] * r["durata_ore"]
        conn.close()

        self.lbl_risultati.setText(
            f"Noleggi: {n_noleggi}\n"
            f"Ore totali: {ore_totali}\n"
            f"Guadagno stimato: € {guadagno:.2f}"
        )