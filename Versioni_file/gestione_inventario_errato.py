from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QTextEdit, QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
    QFileDialog, QVBoxLayout, QHBoxLayout, QHeaderView, QMessageBox, QCheckBox, QAbstractItemView
)
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt
import os
import shutil
from data_access import inserisci_materiale, elimina_materiale, carica_materiali, carica_materiali_per_tipo

FOTO_DIR = "foto_materiali"
os.makedirs(FOTO_DIR, exist_ok=True)

class AnagraficaMateriali(QWidget):
    def __init__(self):
        super().__init__()

        # Campi form
        self.codice = QLineEdit()
        self.tipo = QComboBox()
        self.tipo.addItems(["Sup", "Canoa", "Pagaia", "Salvagente", "Tavola Windsurf", "Vela", "Boma",
                             "Barca a Vela", "Albero", "Bici d'acqua", "Tandem Sup"])
        self.nome = QLineEdit()
        self.produttore = QLineEdit()
        self.provenienza = QComboBox()
        self.provenienza.addItems(["Acquistato", "Altro"])
        self.descrizione = QTextEdit()
        self.note = QTextEdit()

        # RIG
        self.rig_checkbox = QCheckBox("Componi RIG (Albero + Boma + Vela)")
        self.rig_checkbox.stateChanged.connect(self.toggle_rig)
        self.combo_albero = QComboBox()
        self.combo_boma = QComboBox()
        self.combo_vela = QComboBox()
        self.combo_albero.setVisible(False)
        self.combo_boma.setVisible(False)
        self.combo_vela.setVisible(False)

        # Foto
        self.btn_foto = QPushButton("Carica Foto")
        self.foto_label = QLabel("Anteprima Foto")
        self.foto_path = None
        self.btn_foto.clicked.connect(self.carica_foto)

        # Pulsanti
        self.btn_salva = QPushButton("Salva")
        self.btn_elimina = QPushButton("Elimina")
        self.btn_aggiorna = QPushButton("Aggiorna Lista")
        self.btn_salva.clicked.connect(self.salva_materiale)
        self.btn_elimina.clicked.connect(self.elimina_selezionato)
        self.btn_aggiorna.clicked.connect(self.carica_tabella)

        # Tabella
        self.tabella = QTableWidget()
        self.tabella.setColumnCount(12)
        self.tabella.setHorizontalHeaderLabels([
            "ID", "Codice", "Tipo", "Nome", "Produttore", "Provenienza", "Descrizione",
            "Note", "Barcode", "Disponibile", "Rig", "Foto"])
        self.tabella.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tabella.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.tabella.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        # Filtri
        self.filtro_tipo = QComboBox()
        self.filtro_tipo.addItems(["Tutti"] + ["Sup", "Canoa", "Pagaia", "Salvagente", "Tavola Windsurf", "Vela",
                                               "Boma", "Barca a Vela", "Albero", "Bici d'acqua", "Tandem Sup"])
        self.filtro_nome = QLineEdit()
        self.filtro_produttore = QLineEdit()
        self.filtro_disponibile = QCheckBox("Solo Disponibili")

        # Layout filtri
        filtro_layout = QHBoxLayout()
        filtro_layout.addWidget(QLabel("Tipo:"))
        filtro_layout.addWidget(self.filtro_tipo)
        filtro_layout.addWidget(QLabel("Nome:"))
        filtro_layout.addWidget(self.filtro_nome)
        filtro_layout.addWidget(QLabel("Produttore:"))
        filtro_layout.addWidget(self.filtro_produttore)
        filtro_layout.addWidget(self.filtro_disponibile)

        # Form
        form_layout = QVBoxLayout()
        form_layout.addWidget(self.codice)
        form_layout.addWidget(self.tipo)
        form_layout.addWidget(self.nome)
        form_layout.addWidget(self.produttore)
        form_layout.addWidget(self.provenienza)
        form_layout.addWidget(self.descrizione)
        form_layout.addWidget(self.note)
        form_layout.addWidget(self.rig_checkbox)
        form_layout.addWidget(self.foto_label)
        form_layout.addWidget(self.btn_foto)
        form_layout.addWidget(self.combo_albero)
        form_layout.addWidget(self.combo_boma)
        form_layout.addWidget(self.combo_vela)
        form_layout.addWidget(self.btn_salva)
        form_layout.addWidget(self.btn_elimina)
        form_layout.addWidget(self.btn_aggiorna)

        left_layout = QVBoxLayout()
        left_layout.addLayout(form_layout)

        main_layout = QVBoxLayout()
        main_layout.addLayout(filtro_layout)
        main_layout.addWidget(self.tabella)

        layout = QHBoxLayout()
        layout.addLayout(left_layout)
        layout.addLayout(main_layout)
        self.setLayout(layout)

        self.carica_materiali_rig()
        self.carica_tabella()

    def carica_foto(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleziona immagine")
        if file_path:
            self.foto_path = file_path
            self.foto_label.setPixmap(QPixmap(file_path).scaled(120, 80))

    def toggle_rig(self, stato):
        is_rig = stato == Qt.Checked
        self.combo_albero.setVisible(is_rig)
        self.combo_boma.setVisible(is_rig)
        self.combo_vela.setVisible(is_rig)
        self.tipo.setDisabled(is_rig)
        if is_rig:
            self.tipo.setCurrentText("Rig")

    def carica_materiali_rig(self):
        self.combo_albero.clear()
        self.combo_boma.clear()
        self.combo_vela.clear()
        for tipo, combo in [("Albero", self.combo_albero), ("Boma", self.combo_boma), ("Vela", self.combo_vela)]:
            for mat in carica_materiali_per_tipo(tipo):
                combo.addItem(mat[1])  # codice

    def salva_materiale(self):
        rig = 1 if self.rig_checkbox.isChecked() else 0
        if rig:
            cod_alb = self.combo_albero.currentText()
            cod_bom = self.combo_boma.currentText()
            cod_vel = self.combo_vela.currentText()
            codice = cod_alb + cod_bom + cod_vel
            nome = f"Rig {cod_alb}-{cod_bom}-{cod_vel}"
            codice_barre = f"{cod_alb}-{cod_bom}-{cod_vel}"
            tipo = "Rig"
        else:
            codice = self.codice.text()
            nome = self.nome.text()
            tipo = self.tipo.currentText()
            codice_barre = f"{codice}-{self.produttore.text()}-{nome}"

        foto_blob = None
        if self.foto_path:
            with open(self.foto_path, "rb") as f:
                foto_blob = f.read()

        dati = (
            codice,
            tipo,
            nome,
            self.produttore.text(),
            self.provenienza.currentText(),
            self.descrizione.toPlainText(),
            self.note.toPlainText(),
            codice_barre,
            foto_blob,
            rig
        )
        try:
            inserisci_materiale(dati)
            self.carica_tabella()
        except Exception as e:
            QMessageBox.critical(self, "Errore salvataggio", str(e))

    def elimina_selezionato(self):
        row = self.tabella.currentRow()
        if row >= 0:
            id_mat = self.tabella.item(row, 0).text()
            elimina_materiale(id_mat)
            self.carica_tabella()

    def carica_tabella(self):
        self.tabella.setRowCount(0)
        materiali = carica_materiali()

        tipo_sel = self.filtro_tipo.currentText()
        nome_fil = self.filtro_nome.text().lower()
        prod_fil = self.filtro_produttore.text().lower()
        solo_disp = self.filtro_disponibile.isChecked()

        for mat in materiali:
            tipo, nome, prod, disp = mat[2], mat[3], mat[4], mat[10]
            if tipo_sel != "Tutti" and tipo != tipo_sel:
                continue
            if nome_fil and nome_fil not in nome.lower():
                continue
            if prod_fil and prod_fil not in prod.lower():
                continue
            if solo_disp and disp != 1:
                continue

            row = self.tabella.rowCount()
            self.tabella.insertRow(row)
            for col in range(11):
                valore = mat[col]
                if col == 10:  # disponibile
                    valore = "SI" if valore else "NO"
                self.tabella.setItem(row, col, QTableWidgetItem(str(valore)))

            # colonna immagine
            if mat[11]:
                pixmap = QPixmap()
                pixmap.loadFromData(mat[11])
                icon_item = QLabel()
                icon_item.setPixmap(pixmap.scaled(60, 40))
                self.tabella.setCellWidget(row, 11, icon_item)