import os
import shutil
import sqlite3
from PySide6.QtWidgets import (QWidget, QLabel, QLineEdit, QTextEdit, QPushButton, QComboBox,
                               QVBoxLayout, QHBoxLayout, QCheckBox, QFileDialog, QTableWidget,
                               QTableWidgetItem, QHeaderView, QMessageBox,QAbstractItemView,
                               QAbstractScrollArea)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from data_access import inserisci_materiale, elimina_materiale, carica_materiali, carica_materiali_per_tipo, carica_materiali_rig


FOTO_DIR = "foto_materiali"
os.makedirs(FOTO_DIR, exist_ok=True)

class AnagraficaMateriali(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        # --- Campi Form ---
        self.codice = QLineEdit()
        self.tipo = QComboBox()
        self.tipo.addItems(["Sup", "Canoa", "Pagaia", "Salvagente", "Tavola Windsurf", "Vela", "Boma",
                             "Barca a Vela", "Albero", "Bici d'acqua", "Tandem Sup", "Rig"])
        self.nome = QLineEdit()
        self.produttore = QLineEdit()
        self.provenienza = QComboBox()
        self.provenienza.addItems(["Acquistato", "Altro"])
        self.descrizione = QTextEdit()
        self.note = QTextEdit()
        self.rig_checkbox = QCheckBox("Componi RIG (Albero + Boma + Vela)")
        self.foto_path = ""
        self.foto_label = QLabel("Anteprima Foto")
        self.foto_label.setFixedHeight(100)
        self.foto_label.setFixedWidth(150)

        # --- Campi RIG ---
        self.combo_albero = QComboBox()
        self.combo_boma = QComboBox()
        self.combo_vela = QComboBox()
        self.combo_albero.setVisible(False)
        self.combo_boma.setVisible(False)
        self.combo_vela.setVisible(False)

        self.carica_materiali_rig()

        self.rig_checkbox.stateChanged.connect(self.toggle_rig)

        # --- Pulsanti ---
        self.btn_salva = QPushButton("Salva")
        self.btn_elimina = QPushButton("Elimina")
        self.btn_aggiorna = QPushButton("Aggiorna Lista")
        self.btn_foto = QPushButton("Carica Foto")

        self.btn_salva.clicked.connect(self.salva_materiale)
        self.btn_elimina.clicked.connect(self.elimina_selezionato)
        self.btn_aggiorna.clicked.connect(self.carica_tabella)
        self.btn_foto.clicked.connect(self.carica_foto)

        # --- Tabella ---
        self.tabella = QTableWidget()
        self.tabella.setColumnCount(12)
        self.tabella.setHorizontalHeaderLabels([
    "ID", "Codice", "Tipo", "Nome", "Produttore", "Provenienza",
    "Descrizione", "Note", "Barcode", "Disponibile", "Rig", "Foto"
])
        self.tabella.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.tabella.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.tabella.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.tabella.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        layout.addWidget(self.tabella)
        self.carica_tabella()

        # --- Layout ---
        form_layout = QVBoxLayout()
        form_layout.addWidget(QLabel("Codice"))
        form_layout.addWidget(self.codice)
        form_layout.addWidget(QLabel("Tipo"))
        form_layout.addWidget(self.tipo)
        form_layout.addWidget(QLabel("Nome"))
        form_layout.addWidget(self.nome)
        form_layout.addWidget(QLabel("Produttore"))
        form_layout.addWidget(self.produttore)
        form_layout.addWidget(QLabel("Provenienza"))
        form_layout.addWidget(self.provenienza)
        form_layout.addWidget(QLabel("Descrizione"))
        form_layout.addWidget(self.descrizione)
        form_layout.addWidget(QLabel("Note"))
        form_layout.addWidget(self.note)
        form_layout.addWidget(self.rig_checkbox)
        form_layout.addWidget(QLabel("Foto"))
        form_layout.addWidget(self.btn_foto)
        form_layout.addWidget(self.foto_label)
        form_layout.addWidget(QLabel("Albero"))
        form_layout.addWidget(self.combo_albero)
        form_layout.addWidget(QLabel("Boma"))
        form_layout.addWidget(self.combo_boma)
        form_layout.addWidget(QLabel("Vela"))
        form_layout.addWidget(self.combo_vela)
        form_layout.addWidget(self.btn_salva)
        form_layout.addWidget(self.btn_elimina)
        form_layout.addWidget(self.btn_aggiorna)

        # --- Filtri ---
        self.filtro_tipo = QComboBox()
        self.filtro_tipo.addItem("Tutti")
        self.filtro_tipo.addItems(["Sup", "Canoa", "Pagaia", "Salvagente", "Tavola Windsurf", "Vela", "Boma", "Barca a Vela", "Albero", "Bici d'acqua", "Tandem Sup", "Rig"])

        self.filtro_nome = QLineEdit()
        self.filtro_nome.setPlaceholderText("Filtra per nome")

        self.filtro_produttore = QLineEdit()
        self.filtro_produttore.setPlaceholderText("Filtra per produttore")

        self.filtro_disponibile = QCheckBox("Solo disponibili")

        self.filtro_tipo.currentTextChanged.connect(self.carica_tabella)
        self.filtro_nome.textChanged.connect(self.carica_tabella)
        self.filtro_produttore.textChanged.connect(self.carica_tabella)
        self.filtro_disponibile.stateChanged.connect(self.carica_tabella) 
        

        filtro_layout = QHBoxLayout()
        filtro_layout.addWidget(QLabel("Tipo"))
        filtro_layout.addWidget(self.filtro_tipo)
        filtro_layout.addWidget(QLabel("Nome"))
        filtro_layout.addWidget(self.filtro_nome)
        filtro_layout.addWidget(QLabel("Produttore"))
        filtro_layout.addWidget(self.filtro_produttore)
        filtro_layout.addWidget(self.filtro_disponibile)

        layout = QHBoxLayout()
        layout.addLayout(filtro_layout)  # subito sopra layout.addWidget(self.tabella)
        layout = QHBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(self.tabella)
        self.setLayout(layout)

        self.carica_tabella()  

    def carica_foto(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleziona immagine")
        if file_path:
            nome_file = os.path.basename(file_path)
            destinazione = os.path.join(FOTO_DIR, nome_file)
            shutil.copy(file_path, destinazione)
            self.foto_path = destinazione
            self.foto_label.setPixmap(QPixmap(destinazione).scaled(150, 100))

    def mostra_foto(id_materiale, label_foto: QLabel):
        blob = recupera_foto_materiale(id_materiale)
        if blob:
          pixmap = QPixmap()
          pixmap.loadFromData(QByteArray(blob))
          label_foto.setPixmap(pixmap.scaled(150, 150))  # o la misura che vuoi
        else:
         label_foto.clear()

    def toggle_rig(self, stato):
        is_rig = stato == 2
        self.combo_albero.setVisible(is_rig)
        self.combo_boma.setVisible(is_rig)
        self.combo_vela.setVisible(is_rig)
        if is_rig:
            self.tipo.setCurrentText("Rig")
            self.tipo.setDisabled(True)
        else:
            self.tipo.setDisabled(False)

    # Carica i materiali per il RIG (Albero, Boma, Vela)

    def carica_materiali_rig(self):
     self.combo_albero.clear()
     self.combo_boma.clear()
     self.combo_vela.clear()

     tipi_combo = [("Albero", self.combo_albero), ("Boma", self.combo_boma), ("Vela", self.combo_vela)]

     for tipo, combo in tipi_combo:
        risultati = carica_materiali_per_tipo(tipo)
        codici = [r[1] for r in risultati]  # r[1] è 'codice'
        combo.addItems(codici)

    def salva_materiale(self):
       rig = 1 if self.rig_checkbox.isChecked() else 0
       if rig:
        cod_alb = self.combo_albero.currentText()
        cod_bom = self.combo_boma.currentText()
        cod_vel = self.combo_vela.currentText()
        codice = cod_alb + cod_bom + cod_vel
        nome = f"Rig {cod_alb}-{cod_bom}-{cod_vel}"
        tipo = "Rig"
        produttore = self.produttore.text()
       else:
        codice = self.codice.text()
        tipo = self.tipo.currentText()
        nome = self.nome.text()
        produttore = self.produttore.text()

        barcode = f"{codice}-{produttore}-{nome}"
        provenienza = self.provenienza.currentText()
        descrizione = self.descrizione.toPlainText()
        note = self.note.toPlainText()

    # Leggi immagine come blob
       foto_blob = None
       if hasattr(self, 'foto_path') and self.foto_path:
        with open(self.foto_path, "rb") as f:
            foto_blob = f.read()

        try:
            from data_access import inserisci_materiale
            inserisci_materiale(
                codice, tipo, nome, produttore, provenienza, descrizione, note, barcode, rig, foto_blob
            )
            QMessageBox.information(self, "Salvataggio", "Materiale salvato correttamente.")
            self.carica_tabella()
        except Exception as e:
            QMessageBox.critical(self, "Errore salvataggio", str(e))

    def carica_tabella(self):
        self.tabella.setRowCount(0)

        materiali = carica_materiali()

        # Filtri avanzati
        tipo_selezionato = self.filtro_tipo.currentText()
        nome_filtro = self.filtro_nome.text().lower()
        produttore_filtro = self.filtro_produttore.text().lower()
        solo_disponibili = self.filtro_disponibile.isChecked()

        materiali_filtrati = []
        for mat in materiali:
         tipo, nome, produttore, disponibile = mat[2], mat[3], mat[4], mat[9]  # attento: disponibile è indice 9

         if tipo_selezionato != "Tutti" and tipo != tipo_selezionato:
            continue
         if nome_filtro and nome_filtro not in nome.lower():
            continue
         if produttore_filtro and produttore_filtro not in produttore.lower():
            continue
         if solo_disponibili and disponibile != 1:
            continue

        materiali_filtrati.append(mat)

        for row_idx, row_data in enumerate(materiali_filtrati):
         self.tabella.insertRow(row_idx)
        for col_idx, valore in enumerate(row_data):
            if col_idx == 12 and valore:  # colonna immagine BLOB (indice 12)
                try:
                    from PIL import Image
                    from io import BytesIO
                    image = Image.open(BytesIO(valore))
                    image.thumbnail((64, 64))
                    buffer = BytesIO()
                    image.save(buffer, format="PNG")
                    pixmap = QPixmap()
                    pixmap.loadFromData(buffer.getvalue())
                    label = QLabel()
                    label.setPixmap(pixmap)
                    self.tabella.setCellWidget(row_idx, col_idx, label)
                except Exception as e:
                    self.tabella.setItem(row_idx, col_idx, QTableWidgetItem("[Errore img]"))
            else:
                item = QTableWidgetItem(str(valore) if valore is not None else "")
                self.tabella.setItem(row_idx, col_idx, item)

    def elimina_selezionato(self):
        selected = self.tabella.currentRow()
        if selected >= 0:
            id_materiale = self.tabella.item(selected, 0).text()
            elimina_materiale(id_materiale)
            self.carica_tabella()
    