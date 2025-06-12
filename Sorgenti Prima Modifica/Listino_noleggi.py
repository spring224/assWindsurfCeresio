from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox
)
import sqlite3

class FinestraListino(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestione Listino Noleggio")
        self.resize(600, 400)
        self.init_ui()
        self.carica_listino()

    def init_ui(self):
        layout = QVBoxLayout()

        self.tabella = QTableWidget()
        self.tabella.setColumnCount(3)
        self.tabella.setHorizontalHeaderLabels(["Tipo", "Descrizione", "Prezzo Orario (€)"])
        layout.addWidget(self.tabella)

        bottoni = QHBoxLayout()
        self.btn_aggiungi = QPushButton("➕ Aggiungi")
        self.btn_salva = QPushButton("💾 Salva")
        self.btn_ricarica = QPushButton("🔄 Ricarica")

        self.btn_aggiungi.clicked.connect(self.aggiungi_riga)
        self.btn_salva.clicked.connect(self.salva_listino)
        self.btn_ricarica.clicked.connect(self.carica_listino)

        bottoni.addWidget(self.btn_aggiungi)
        bottoni.addWidget(self.btn_salva)
        bottoni.addWidget(self.btn_ricarica)
        layout.addLayout(bottoni)

        self.setLayout(layout)

    

    def carica_listino(self):
         from data_access import carica_listino
         print("⚙️  Caricamento listino...")  # DEBUG
         self.tabella.setRowCount(0)
         righe = carica_listino()
         print(f"✅ {len(righe)} righe trovate")  # DEBUG
         for r in righe:
          self.aggiungi_riga_precompilata(r["tipo"], r["descrizione"], r["prezzo_orario"])

    def aggiungi_riga(self):
        row = self.tabella.rowCount()
        self.tabella.insertRow(row)
        self.tabella.setItem(row, 0, QTableWidgetItem(""))
        self.tabella.setItem(row, 1, QTableWidgetItem(""))
        self.tabella.setItem(row, 2, QTableWidgetItem("0.0"))

    def aggiungi_riga_precompilata(self, tipo, descrizione, prezzo):
        row = self.tabella.rowCount()
        self.tabella.insertRow(row)
        self.tabella.setItem(row, 0, QTableWidgetItem(tipo))
        self.tabella.setItem(row, 1, QTableWidgetItem(descrizione))
        self.tabella.setItem(row, 2, QTableWidgetItem(str(prezzo)))

    def salva_listino(self):
        from data_access import salva_listino
        righe = []
        for row in range(self.tabella.rowCount()):
          tipo = self.tabella.item(row, 0).text().strip()
          descrizione = self.tabella.item(row, 1).text().strip()
        try:
            prezzo = float(self.tabella.item(row, 2).text().strip().replace(",", "."))
        except ValueError:
            QMessageBox.warning(self, "Errore", f"Prezzo non valido alla riga {row+1}")
            return
        if tipo and prezzo >= 0:
            righe.append((tipo, descrizione, prezzo))

        success, errore = salva_listino(righe)
        if success:
          QMessageBox.information(self, "Listino Salvato", "Le modifiche sono state salvate con successo.")
        else:
         QMessageBox.critical(self, "Errore", f"Errore durante il salvataggio:\n{errore}")