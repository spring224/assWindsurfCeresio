

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QLineEdit, QComboBox, QWidget,
    QMessageBox
)
from PySide6.QtCore import Qt # Importa Qt per i flag ItemIsSelectable, ItemIsEnabled
from data_access import get_materiali_disponibili

# Assicurati di avere una funzione che recuperi i materiali dal tuo DB
# Esempio (adattalo al tuo data_access.py):
# from data_access import get_all_materiali_disponibili, get_materiale_by_id_db
# DUMMY FUNCTION per esempio, sostituisci con la tua logica DB

class SelezionaMaterialeDisponibile(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Seleziona Materiale Disponibile per il Noleggio")
        self.materiale_scelto = None
        self.init_ui()
        self.carica_materiali()

    def init_ui(self):
        layout_principale = QVBoxLayout()

        # Layout per i filtri (Tipo e Ricerca Testo)
        layout_filtri = QHBoxLayout()
        
        self.cmb_tipo_filtro = QComboBox()
        self.cmb_tipo_filtro.addItem("Tutti i Tipi")
        # I tipi verranno aggiunti dinamicamente da carica_materiali
        self.cmb_tipo_filtro.currentIndexChanged.connect(self.filtra_materiali)
        layout_filtri.addWidget(QLabel("Tipo:"))
        layout_filtri.addWidget(self.cmb_tipo_filtro)

        self.txt_ricerca = QLineEdit()
        self.txt_ricerca.setPlaceholderText("Cerca per nome, codice o produttore...")
        self.txt_ricerca.textChanged.connect(self.filtra_materiali)
        layout_filtri.addWidget(self.txt_ricerca)
        layout_principale.addLayout(layout_filtri)

        # QListWidget per visualizzare i materiali
        self.lista_materiali = QListWidget()
        self.lista_materiali.itemDoubleClicked.connect(self.accetta_selezione) # Doppioclick per selezionare
        layout_principale.addWidget(self.lista_materiali)

        # Pulsanti di azione
        layout_pulsanti = QHBoxLayout()
        self.btn_seleziona = QPushButton("Seleziona")
        self.btn_seleziona.clicked.connect(self.accetta_selezione)
        layout_pulsanti.addWidget(self.btn_seleziona)

        self.btn_annulla = QPushButton("Annulla")
        self.btn_annulla.clicked.connect(self.reject)
        layout_pulsanti.addWidget(self.btn_annulla)
        layout_principale.addLayout(layout_pulsanti)

        self.setLayout(layout_principale)
        self.resize(500, 600) # Imposta una dimensione iniziale ragionevole

    def carica_materiali(self):
        self.tutti_i_materiali = get_materiali_disponibili() # Ottieni tutti i materiali dal DB
        self.tutti_i_materiali.sort(key=lambda m: (m["tipo"], m["nome"])) # Ordina per tipo e poi per nome

        # Popola la ComboBox dei tipi
        tipi_unici = sorted(list(set(m["tipo"] for m in self.tutti_i_materiali)))
        for tipo in tipi_unici:
            self.cmb_tipo_filtro.addItem(tipo)
        
        self.filtra_materiali() # Applica il filtro iniziale

    def filtra_materiali(self):
        self.lista_materiali.clear()
        testo_ricerca = self.txt_ricerca.text().strip().lower()
        tipo_selezionato = self.cmb_tipo_filtro.currentText()

        materiali_filtrati = []
        for m in self.tutti_i_materiali:
            matches_tipo = (tipo_selezionato == "Tutti i Tipi" or m["tipo"] == tipo_selezionato)
            
            matches_ricerca = True
            if testo_ricerca:
                if not (testo_ricerca in m["codice"].lower() or 
                        testo_ricerca in m["nome"].lower() or 
                        testo_ricerca in m["produttore"].lower()):
                    matches_ricerca = False
            
            if matches_tipo and matches_ricerca:
                materiali_filtrati.append(m)

        # Raggruppa e aggiungi alla lista
        current_tipo = None
        for m in materiali_filtrati:
            if m["tipo"] != current_tipo:
                # Aggiungi un'intestazione per la categoria
                item_header = QListWidgetItem(f"--- {m['tipo'].upper()} ---")
                item_header.setFlags(item_header.flags() & ~Qt.ItemIsSelectable) # Non selezionabile
                item_header.setTextAlignment(Qt.AlignCenter)
                self.lista_materiali.addItem(item_header)
                current_tipo = m["tipo"]

            # Aggiungi l'elemento materiale
            item_materiale = QListWidgetItem(f"{m['codice']} - {m['nome']} ({m['produttore']})")
            item_materiale.setData(Qt.UserRole, m) # Salva tutti i dati del materiale nell'elemento
            self.lista_materiali.addItem(item_materiale)


    def accetta_selezione(self):
        selected_items = self.lista_materiali.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Selezione", "Seleziona un materiale dalla lista.")
            return

        for item in selected_items:
            if item.flags() & Qt.ItemIsSelectable: # Assicurati che non sia un'intestazione
                # Semplicemente imposta materiale_scelto al dizionario completo!
                self.materiale_scelto = item.data(Qt.UserRole) 
                
                # Non fare più questa conversione a tupla che ti fa perdere i dati:
                # self.materiale_scelto = (
                #     self.materiale_scelto["id"],
                #     self.materiale_scelto["codice"],
                #     self.materiale_scelto["nome"],
                #     self.materiale_scelto["produttore"]
                # )
                
                self.accept() # Chiude il dialog con Accepted
                return
        
        QMessageBox.warning(self, "Selezione", "Seleziona un materiale valido, non un'intestazione di tipo.")


#
