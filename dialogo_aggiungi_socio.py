# dialogo_aggiungi_socio.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QPushButton, QDialogButtonBox, QDateEdit, QComboBox, QMessageBox
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor, QPalette, QDoubleValidator

# Importa le funzioni dal tuo data_access.py e codice_fiscale_utils.py
from data_access import insert_socio_esteso
from codice_fiscale_utils import calcola_codice_fiscale # Assicurati che questa funzione esista e funzioni correttamente


class DialogoAggiungiSocio(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Aggiungi Nuovo Socio")
        self.setMinimumSize(500, 600) # Una dimensione adeguata per il form

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # Titolo del dialogo
        title_label = QLabel("Inserisci i Dati del Nuovo Socio")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px; color: #2C3E50;")
        main_layout.addWidget(title_label)

        # Form Layout per i campi di input
        form_layout = QFormLayout()
        form_layout.setContentsMargins(30, 20, 30, 20)
        form_layout.setVerticalSpacing(15)
        form_layout.setHorizontalSpacing(20)

        # Dizionario per memorizzare i widget di input
        self.inputs = {}

        # Funzione helper per creare e aggiungere QLineEdit con stile
        def add_line_edit(field_name, placeholder_text=""):
            line_edit = QLineEdit()
            line_edit.setPlaceholderText(placeholder_text)
            line_edit.setStyleSheet("""
                QLineEdit {
                    padding: 8px;
                    border: 1px solid #BDC3C7;
                    border-radius: 5px;
                    font-size: 16px;
                }
                QLineEdit:focus {
                    border: 2px solid #3498DB;
                }
            """)
            self.inputs[field_name] = line_edit
            return line_edit

        # Funzione helper per creare e aggiungere QDateEdit con stile
        def add_date_edit(field_name):
            date_edit = QDateEdit(calendarPopup=True)
            date_edit.setDate(QDate.currentDate())

            date_edit.setDisplayFormat("dd/MM/yyyy")
            date_edit.setStyleSheet("""
                QDateEdit {
                    padding: 8px;
                    border: 1px solid #BDC3C7;
                    border-radius: 5px;
                    font-size: 16px;
                }
                QDateEdit::drop-down {
                    subcontrol-origin: padding;
                    subcontrol-position: top right;
                    width: 20px;
                    border-left-width: 1px;
                    border-left-color: darkgray;
                    border-left-style: solid;
                    border-top-right-radius: 5px;
                    border-bottom-right-radius: 5px;
                }
            """)
            self.inputs[field_name] = date_edit
            return date_edit

        # Campo: Nome
        form_layout.addRow(QLabel("Nome:"), add_line_edit("nome", "Inserisci il nome"))
        # Campo: Cognome
        form_layout.addRow(QLabel("Cognome:"), add_line_edit("cognome", "Inserisci il cognome"))
        # Campo: Indirizzo
        form_layout.addRow(QLabel("Indirizzo:"), add_line_edit("indirizzo", "Via, numero, città, CAP"))
        # Campo: Telefono
        form_layout.addRow(QLabel("Telefono:"), add_line_edit("telefono", "Es. +39 123 4567890"))
        # Campo: Email
        form_layout.addRow(QLabel("Email:"), add_line_edit("email", "indirizzo@esempio.com"))
        # Campo: Data di Nascita
        date_nascita_input = add_date_edit("data_nascita")
        form_layout.addRow(QLabel("Data di Nascita:"), date_nascita_input)
        # Campo: Luogo di Nascita
        luogo_nascita_input = add_line_edit("luogo_nascita", "Città di nascita")
        form_layout.addRow(QLabel("Luogo di Nascita:"), luogo_nascita_input)

        # Campo: Codice Fiscale (sarà calcolato, ma con possibilità di override)
        codice_fiscale_layout = QHBoxLayout()
        self.inputs["codice_fiscale"] = add_line_edit("codice_fiscale", "Sarà calcolato automaticamente")
        self.inputs["codice_fiscale"].setReadOnly(True) # Inizialmente solo lettura
        self.btn_calcola_cf = QPushButton("Calcola CF")
        self.btn_calcola_cf.setFixedWidth(100)
        self.btn_calcola_cf.clicked.connect(self.calcola_e_popola_codice_fiscale)
        self.btn_override_cf = QPushButton("Modifica CF")
        self.btn_override_cf.setFixedWidth(100)
        self.btn_override_cf.setCheckable(True) # Pulsante a due stati
        self.btn_override_cf.clicked.connect(self.toggle_cf_readonly)

        codice_fiscale_layout.addWidget(self.inputs["codice_fiscale"])
        codice_fiscale_layout.addWidget(self.btn_calcola_cf)
        codice_fiscale_layout.addWidget(self.btn_override_cf)
        form_layout.addRow(QLabel("Codice Fiscale:"), codice_fiscale_layout)

        # Campo: Quota Pagata (Checkbox o ComboBox per Sì/No)
        # Usiamo una QComboBox per rappresentare 0/1 per coerenza con il DB
        self.inputs["quota_pagata"] = QComboBox()
        self.inputs["quota_pagata"].addItems(["No", "Sì"]) # 0=No, 1=Sì
        self.inputs["quota_pagata"].setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #BDC3C7;
                border-radius: 5px;
                font-size: 16px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: darkgray;
                border-left-style: solid;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
            }
        """)
        form_layout.addRow(QLabel("Quota Pagata:"), self.inputs["quota_pagata"])

        # Campo: Quota Associazione (Real)
        # Per semplicità, usiamo un QLineEdit e convertiamo a float.
        self.inputs["quota_associazione"] = add_line_edit("quota_associazione", "Es. 50.00")
        self.inputs["quota_associazione"].setValidator(
          QDoubleValidator(0.00, 99999.99, 2, self.inputs["quota_associazione"])
        ) # Permette solo numeri decimali con 2 cifre dopo la virgola
        form_layout.addRow(QLabel("Quota Associazione (€):"), self.inputs["quota_associazione"])


        # Campo: Anno
        self.inputs["anno"] = QLineEdit(str(QDate.currentDate().year())) # Default all'anno corrente
        self.inputs["anno"].setReadOnly(True) # L'anno è preimpostato, ma si può rendere modificabile se necessario
        self.inputs["anno"].setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #BDC3C7;
                border-radius: 5px;
                background-color: #ECF0F1; /* Colore di sfondo per solo lettura */
                font-size: 16px;
            }
        """)
        form_layout.addRow(QLabel("Anno di Iscrizione:"), self.inputs["anno"])

        main_layout.addLayout(form_layout)
        main_layout.addStretch(1) # Spazio flessibile per centrare i contenuti

        # Pulsanti OK e Annulla
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accetta_input)
        button_box.rejected.connect(self.reject) # Chiude il dialogo con stato "Rejected"
        main_layout.addWidget(button_box, alignment=Qt.AlignCenter)

        # Stile generale per il dialogo
        self.setStyleSheet("""
            QDialog {
                background-color: #ECF0F1;
            }
            QLabel {
                font-size: 16px;
                font-weight: 500;
                color: #34495E;
            }
            QPushButton {
                background-color: #3498DB;
                color: white;
                border-radius: 5px;
                padding: 10px 15px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
            QPushButton:pressed {
                background-color: #21618C;
            }
            QDialogButtonBox QPushButton {
                min-width: 80px;
            }
        """)

    def calcola_e_popola_codice_fiscale(self):
        nome = self.inputs["nome"].text().strip()
        cognome = self.inputs["cognome"].text().strip()
        data_nascita_str = self.inputs["data_nascita"].date().toString("dd/MM/yyyy")
        luogo_nascita = self.inputs["luogo_nascita"].text().strip()

        # TODO: Aggiungere il sesso (M/F) al dialogo e passarlo qui.
        # Per ora usiamo un placeholder o una logica predefinita se necessario.
        sesso = "M" # Placeholder, da migliorare

        if not (nome and cognome and data_nascita_str and luogo_nascita and sesso):
            QMessageBox.warning(self, "Dati Mancanti", "Per calcolare il Codice Fiscale, sono necessari Nome, Cognome, Data di Nascita, Luogo di Nascita e Sesso.")
            return

        try:
            # Assicurati che calcola_codice_fiscale sia robusta e gestisca i formati data
            cf = calcola_codice_fiscale(cognome, nome, data_nascita_str, sesso, luogo_nascita)
            self.inputs["codice_fiscale"].setText(cf)
            QMessageBox.information(self, "Calcolo CF", "Codice Fiscale calcolato e inserito.")
        except Exception as e:
            QMessageBox.critical(self, "Errore Calcolo CF", f"Impossibile calcolare il Codice Fiscale: {e}")
            self.inputs["codice_fiscale"].setText("Errore nel calcolo")

    def toggle_cf_readonly(self):
        is_checked = self.btn_override_cf.isChecked()
        self.inputs["codice_fiscale"].setReadOnly(not is_checked)
        if is_checked:
            self.btn_override_cf.setText("Blocca CF")
            self.inputs["codice_fiscale"].setStyleSheet(self.inputs["codice_fiscale"].styleSheet().replace("background-color: #ECF0F1;", ""))
            self.inputs["codice_fiscale"].setPlaceholderText("Inserisci manualmente il Codice Fiscale")
        else:
            self.btn_override_cf.setText("Modifica CF")
            self.inputs["codice_fiscale"].setStyleSheet(self.inputs["codice_fiscale"].styleSheet() + "background-color: #ECF0F1;")
            self.inputs["codice_fiscale"].setPlaceholderText("Sarà calcolato automaticamente")


    def get_socio_data(self):
        # Questo metodo raccoglie tutti i dati dal form e li restituisce come dizionario
        data = {}
        data['nome'] = self.inputs["nome"].text().strip()
        data['cognome'] = self.inputs["cognome"].text().strip()
        data['indirizzo'] = self.inputs["indirizzo"].text().strip()
        data['telefono'] = self.inputs["telefono"].text().strip()
        data['email'] = self.inputs["email"].text().strip()
        data['data_nascita'] = self.inputs["data_nascita"].date().toString(Qt.ISODate) # Formato YYYY-MM-DD
        data['luogo_nascita'] = self.inputs["luogo_nascita"].text().strip()
        data['codice_fiscale'] = self.inputs["codice_fiscale"].text().strip().upper() # Assicurati che sia maiuscolo
        data['quota_pagata'] = 1 if self.inputs["quota_pagata"].currentText() == "Sì" else 0
        
        try:
            data['quota_associazione'] = float(self.inputs["quota_associazione"].text().replace(',', '.'))
        except ValueError:
            data['quota_associazione'] = 0.0 # Valore di default in caso di errore di conversione

        data['anno'] = int(self.inputs["anno"].text()) # Converti a int
        data['attivo'] = 1 # Di default un nuovo socio è attivo
        data['foto'] = None # La gestione della foto sarà aggiunta in seguito

        return data

    def validate_input(self, data):
        # Semplice validazione per i campi obbligatori
        if not data['nome']:
            QMessageBox.warning(self, "Validazione", "Il campo 'Nome' è obbligatorio.")
            return False
        if not data['cognome']:
            QMessageBox.warning(self, "Validazione", "Il campo 'Cognome' è obbligatorio.")
            return False
        if not data['data_nascita']: # QDateEdit dovrebbe sempre avere un valore, ma per sicurezza
            QMessageBox.warning(self, "Validazione", "Il campo 'Data di Nascita' è obbligatorio.")
            return False
        if not data['luogo_nascita']:
            QMessageBox.warning(self, "Validazione", "Il campo 'Luogo di Nascita' è obbligatorio.")
            return False
        if not data['codice_fiscale']:
            QMessageBox.warning(self, "Validazione", "Il campo 'Codice Fiscale' è obbligatorio (calcolato o inserito manualmente).")
            return False
        
        # Validazione quota_associazione
        try:
            float(self.inputs["quota_associazione"].text().replace(',', '.'))
        except ValueError:
            QMessageBox.warning(self, "Validazione", "La 'Quota Associazione' deve essere un numero valido.")
            return False

        return True

    def accetta_input(self):
        socio_data = self.get_socio_data()

        if self.validate_input(socio_data):
            try:
                # Chiama la funzione per inserire i dati nel database
                # Passa l'intero dizionario 'socio_data' come argomento 'dati'
                insert_socio_esteso(socio_data) # <--- MODIFICATO QUI: Rimosso il **
                QMessageBox.information(self, "Successo", "Nuovo socio aggiunto con successo al database!")
                self.accept() # Chiude il dialogo con stato "Accepted"
            except Exception as e:
                QMessageBox.critical(self, "Errore Database", f"Si è verificato un errore durante l'aggiunta del socio: {e}")


# --- Codice di test (rimuovere o commentare in produzione) ---
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    # Importa una versione mock o reale di calcola_codice_fiscale e insert_socio_esteso per il test
    # Per il test, puoi creare delle funzioni placeholder
    def mock_calcola_codice_fiscale(cognome, nome, data_nascita, sesso, luogo_nascita):
        print(f"Mock CF Calculation: {cognome}, {nome}, {data_nascita}, {sesso}, {luogo_nascita}")
        return "MOCKCF12345ABC"

    def mock_insert_socio_esteso(**kwargs):
        print(f"Mock Insert Socio: {kwargs}")
        # Simula un errore per test:
        # raise Exception("Simulated DB Error")
        pass

    # Sostituisci le funzioni reali con quelle mock per il test standalone
    # Questo è un trick avanzato, assicurati di capire cosa fa prima di usarlo in produzione.
    # Per la produzione, assicurati che gli import in cima al file puntino alle tue funzioni reali.
    # sys.modules['data_access'].insert_socio_esteso = mock_insert_socio_esteso
    # sys.modules['codice_fiscale_utils'].calcola_codice_fiscale = mock_calcola_codice_fiscale

    app = QApplication(sys.argv)
    dialog = DialogoAggiungiSocio()
    if dialog.exec() == QDialog.Accepted:
        print("Dialogo chiuso con ACCETTATO")
        print("Dati inseriti (simulati):", dialog.get_socio_data())
    else:
        print("Dialogo chiuso con ANNULLATO")

    sys.exit(app.exec())