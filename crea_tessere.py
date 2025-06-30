# crea_tessera_noleggi.py

# crea_tessera_noleggi.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QComboBox, QPushButton, QMessageBox, QLabel
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QDoubleValidator # Assicurati di importare QDoubleValidator
from data_access import cerca_o_crea_cliente, salva_tessera

class FinestraCreaTessera(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Crea Tessera Noleggi/Corsi")
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # --- Sezione Dati Cliente ---
        cliente_group = QLabel("<h3>Dati Cliente</h3>")
        cliente_group.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(cliente_group)

        form_layout_cliente = QFormLayout()
        self.txt_nome = QLineEdit()
        self.txt_cognome = QLineEdit()
        self.txt_email = QLineEdit()
        self.txt_telefono = QLineEdit()
        self.txt_indirizzo = QLineEdit()
        
        self.cmb_nazione = QComboBox()
        self.cmb_nazione.addItems(["Italia", "Olanda", "Germania", "Spagna", "Francia", "Altro"]) # Aggiunto "Altro" come opzione generale
        self.cmb_nazione.setCurrentText("Italia") # Imposta un valore predefinito

        form_layout_cliente.addRow("Nome:", self.txt_nome)
        form_layout_cliente.addRow("Cognome:", self.txt_cognome)
        form_layout_cliente.addRow("Email:", self.txt_email)
        form_layout_cliente.addRow("Telefono:", self.txt_telefono)
        form_layout_cliente.addRow("Indirizzo:", self.txt_indirizzo)
        form_layout_cliente.addRow("Nazione:", self.cmb_nazione) # Aggiunta la QComboBox per la Nazione

        main_layout.addLayout(form_layout_cliente)
        main_layout.addSpacing(20)

        # --- Sezione Dati Tessera ---
        tessera_group = QLabel("<h3>Dati Tessera</h3>")
        tessera_group.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(tessera_group)

        form_layout_tessera = QFormLayout()
        
        self.cmb_tipo_tessera = QComboBox()
        self.cmb_tipo_tessera.addItems(["Lezione Windsurf", "Noleggio Materiale"]) # Selezione tipo di tessera
        
        self.txt_prezzo_totale = QLineEdit("0.00")
        self.txt_prezzo_totale.setValidator(QDoubleValidator(0.0, 10000.0, 2))
        
        self.cmb_numero_item = QComboBox()
        self.cmb_numero_item.addItems(["5", "10", "15", "20"])

        form_layout_tessera.addRow("Tipo Tessera:", self.cmb_tipo_tessera) # Aggiunta la QComboBox per il Tipo Tessera
        form_layout_tessera.addRow("Prezzo Totale (€):", self.txt_prezzo_totale)
        form_layout_tessera.addRow("Numero Item:", self.cmb_numero_item)

        main_layout.addLayout(form_layout_tessera)
        main_layout.addSpacing(30)

        # --- Pulsanti Azione ---
        button_layout = QHBoxLayout()
        self.btn_salva = QPushButton("💾 Crea e Salva Tessera")
        self.btn_stampa_promemoria = QPushButton("🖨️ Stampa Promemoria")

        self.btn_salva.clicked.connect(self.crea_e_salva_tessera)
        self.btn_stampa_promemoria.clicked.connect(self.stampa_promemoria) # Connetti il pulsante di stampa
        
        button_layout.addStretch(1)
        button_layout.addWidget(self.btn_salva)
        button_layout.addWidget(self.btn_stampa_promemoria) # Aggiungi il pulsante Stampa
        button_layout.addStretch(1)
        
        main_layout.addLayout(button_layout)
        
        main_layout.addStretch(1)

    def crea_e_salva_tessera(self):
        nome = self.txt_nome.text().strip()
        cognome = self.txt_cognome.text().strip()
        email = self.txt_email.text().strip()
        telefono = self.txt_telefono.text().strip()
        indirizzo = self.txt_indirizzo.text().strip()
        nazione = self.cmb_nazione.currentText().strip() # Ottieni la nazione

        tipo_tessera = self.cmb_tipo_tessera.currentText().strip() # Ottieni il tipo di tessera
        prezzo_str = self.txt_prezzo_totale.text().strip().replace(",", ".")
        numero_item_str = self.cmb_numero_item.currentText().strip()

        # Validazione input
        if not nome or not cognome or not prezzo_str or not numero_item_str or not tipo_tessera:
            QMessageBox.warning(self, "Input Mancante", "Nome, Cognome, Tipo Tessera, Prezzo Totale e Numero Item sono obbligatori.")
            return
        
        try:
            prezzo_totale = float(prezzo_str)
            numero_item_totale = int(numero_item_str)
        except ValueError:
            QMessageBox.warning(self, "Errore Formato", "Assicurati che Prezzo Totale sia un numero valido e Numero Item sia intero.")
            return
        
        if prezzo_totale < 0:
            QMessageBox.warning(self, "Prezzo Non Valido", "Il prezzo totale non può essere negativo.")
            return

        data_creazione = QDate.currentDate().toString(Qt.ISODate) # 'YYYY-MM-DD'

        # 1. Cerca o crea il cliente
        # Passa la nazione alla funzione
        id_cliente = cerca_o_crea_cliente(nome, cognome, email, telefono, indirizzo, nazione=nazione)

        if id_cliente == -1:
            QMessageBox.critical(self, "Errore DB Cliente", "Errore durante la ricerca o creazione del cliente nel database.")
            return

        # 2. Salva la tessera (passando anche il tipo_tessera)
        success = salva_tessera(id_cliente, tipo_tessera, prezzo_totale, numero_item_totale, data_creazione)

        if success:
            QMessageBox.information(self, "Tessera Creata", f"Tessera '{tipo_tessera}' per {nome} {cognome} creata con successo!")
            self.clear_fields()
        else:
            QMessageBox.critical(self, "Errore DB Tessera", "Errore durante il salvataggio della tessera nel database.")
    
    def clear_fields(self):
        """Pulisce tutti i campi di input dopo il salvataggio."""
        self.txt_nome.clear()
        self.txt_cognome.clear()
        self.txt_email.clear()
        self.txt_telefono.clear()
        self.txt_indirizzo.clear()
        self.cmb_nazione.setCurrentText("Italia") # Resetta la nazione a Italia
        
        self.cmb_tipo_tessera.setCurrentIndex(0) # Resetta a "Lezione Windsurf"
        self.txt_prezzo_totale.setText("0.00")
        self.cmb_numero_item.setCurrentIndex(0)

    def stampa_promemoria(self):
        # Implementa qui la logica di stampa del promemoria
        # Puoi riutilizzare o adattare la logica di stampa_manager.py
        # Dovrai raccogliere i dati dai campi dell'interfaccia
        nome = self.txt_nome.text().strip()
        cognome = self.txt_cognome.text().strip()
        email = self.txt_email.text().strip()
        telefono = self.txt_telefono.text().strip()
        indirizzo = self.txt_indirizzo.text().strip()
        nazione = self.cmb_nazione.currentText().strip()

        tipo_tessera = self.cmb_tipo_tessera.currentText().strip()
        prezzo_totale = self.txt_prezzo_totale.text().strip()
        numero_item = self.cmb_numero_item.currentText().strip()
        data_creazione = QDate.currentDate().toString(Qt.ISODate)

        # Esempio molto base di stampa su QMessageBox
        promemoria_text = (
            f"--- Promemoria Tessera ---\n"
            f"Cliente: {nome} {cognome}\n"
            f"Email: {email}\n"
            f"Telefono: {telefono}\n"
            f"Indirizzo: {indirizzo}, {nazione}\n\n"
            f"Tipo Tessera: {tipo_tessera}\n"
            f"Numero Item: {numero_item}\n"
            f"Prezzo Totale: {prezzo_totale} €\n"
            f"Data Creazione: {data_creazione}\n"
            f"-------------------------"
        )
        QMessageBox.information(self, "Promemoria Tessera", promemoria_text)
        
        # Per una stampa vera e propria (es. PDF), potresti voler passare questi dati a una funzione in stampa_manager.py
        # from stampa_manager import stampa_tessera_promemoria # Dovrai creare questa funzione
        # stampa_tessera_promemoria(nome, cognome, email, telefono, indirizzo, nazione, tipo_tessera, prezzo_totale, numero_item, data_creazione)
        pass

# Per testare questa finestra direttamente (rimuovi o commenta quando integrata)
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    window = FinestraCreaTessera()
    window.show()
    sys.exit(app.exec())