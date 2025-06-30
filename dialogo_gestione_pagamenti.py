# dialogo_gestione_pagamenti.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QMessageBox, QFrame, QFormLayout
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor

# Importa le funzioni di accesso ai dati
from data_access import get_socio_by_id, mark_quota_pagata

class DialogoGestionePagamenti(QDialog):
    def __init__(self, socio_id, parent=None):
        super().__init__(parent)
        self.socio_id = socio_id
        self.socio_data = {} # Per memorizzare i dati del socio
        self.setWindowTitle(f"Gestione Pagamenti Socio ID: {self.socio_id}")
        self.setMinimumSize(400, 300)

        self.init_ui()
        self.load_socio_data()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # Frame per i dettagli del socio
        socio_frame = QFrame(self)
        socio_frame.setFrameShape(QFrame.StyledPanel)
        socio_frame.setFrameShadow(QFrame.Raised)
        socio_layout = QFormLayout(socio_frame)

        self.lbl_nome_cognome = QLabel("Nome Cognome: N/A")
        self.lbl_email = QLabel("Email: N/A")
        self.lbl_anno = QLabel("Anno Iscrizione: N/A")
        self.lbl_quota_pagata = QLabel("Quota Pagata: N/A")

        socio_layout.addRow("Socio:", self.lbl_nome_cognome)
        socio_layout.addRow("Email:", self.lbl_email)
        socio_layout.addRow("Anno Iscrizione:", self.lbl_anno)
        socio_layout.addRow("Stato Quota:", self.lbl_quota_pagata)
        
        main_layout.addWidget(socio_frame)
        main_layout.addStretch() # Spinge il frame verso l'alto

        # Pulsanti di azione
        buttons_layout = QHBoxLayout()
        self.btn_marca_pagata = QPushButton("Marca Quota Come Pagata")
        self.btn_chiudi = QPushButton("Chiudi")

        buttons_layout.addStretch() # Allinea a destra
        buttons_layout.addWidget(self.btn_marca_pagata)
        buttons_layout.addWidget(self.btn_chiudi)
        buttons_layout.addStretch() # Centra i pulsanti
        main_layout.addLayout(buttons_layout)

        # Connessioni
        self.btn_marca_pagata.clicked.connect(self.marca_quota_pagata_azione)
        self.btn_chiudi.clicked.connect(self.accept)

    def load_socio_data(self):
        self.socio_data = get_socio_by_id(self.socio_id)
        if self.socio_data:
            self.lbl_nome_cognome.setText(f"{self.socio_data.get('nome', '')} {self.socio_data.get('cognome', '')}")
            self.lbl_email.setText(f"Email: {self.socio_data.get('email', 'N/A')}")
            self.lbl_anno.setText(f"Anno Iscrizione: {self.socio_data.get('anno', 'N/A')}")
            
            quota_pagata_text = "Sì" if self.socio_data.get('quota_pagata', 0) == 1 else "No"
            self.lbl_quota_pagata.setText(f"Quota Pagata: {quota_pagata_text}")
            
            # Colora lo stato della quota
            if self.socio_data.get('quota_pagata', 0) == 0:
                self.lbl_quota_pagata.setStyleSheet("color: red; font-weight: bold;")
                self.btn_marca_pagata.setEnabled(True)
            else:
                self.lbl_quota_pagata.setStyleSheet("color: green; font-weight: bold;")
                self.btn_marca_pagata.setEnabled(False) # Disabilita se già pagata
        else:
            QMessageBox.critical(self, "Errore", "Dati socio non trovati.")
            self.btn_marca_pagata.setEnabled(False) # Disabilita i pulsanti se dati non trovati

    def marca_quota_pagata_azione(self):
        if self.socio_id is None:
            QMessageBox.warning(self, "Errore", "Nessun socio selezionato per l'operazione.")
            return

        if QMessageBox.question(self, "Conferma Pagamento",
                                f"Confermi di voler marcare la quota del socio {self.socio_data.get('nome', '')} {self.socio_data.get('cognome', '')} come PAGATA per l'anno {QDate.currentDate().year()}?",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            
            if mark_quota_pagata(self.socio_id):
                QMessageBox.information(self, "Successo", "Quota marcata come pagata con successo!")
                # Aggiorna lo stato nel dialogo
                self.load_socio_data() 
                # Potresti voler emettere un segnale qui per far ricaricare la lista principale
                self.parent().carica_dati() if hasattr(self.parent(), 'carica_dati') else None
            else:
                QMessageBox.critical(self, "Errore", "Impossibile marcare la quota come pagata. Riprova.")

# Esempio di esecuzione per testare solo questo dialogo (opzionale)
if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication
    # Importa i mock per data_access se vuoi testare questo file singolarmente
    # Senza i mock, questo test fallirà a meno che data_access.py non sia configurato correttamente
    
    # Esempio di mock per test locale, NON USARE NELL'APP FINALE
    class MockSocio:
        def __init__(self, id, nome, cognome, email, quota_pagata, anno):
            self.data = {'id': id, 'nome': nome, 'cognome': cognome, 'email': email, 'quota_pagata': quota_pagata, 'anno': anno}
        def get(self, key, default=None):
            return self.data.get(key, default)

    mock_db_soci = {
        1: MockSocio(1, 'Mario', 'Rossi', 'mario.rossi@example.com', 0, 2024), # Quota non pagata
        2: MockSocio(2, 'Anna', 'Verdi', 'anna.verdi@example.com', 1, 2024), # Quota pagata
    }

    def mock_get_socio_by_id(socio_id):
        socio = mock_db_soci.get(socio_id)
        return socio.data if socio else None

    def mock_mark_quota_pagata(socio_id):
        if socio_id in mock_db_soci:
            mock_db_soci[socio_id].data['quota_pagata'] = 1
            print(f"DEBUG MOCK: Quota socio {socio_id} marcata come pagata.")
            return True
        return False

    # Inietta i mock nel modulo corrente per il test
    import sys
    sys.modules['data_access'] = type('module', (object,), {
        'get_socio_by_id': mock_get_socio_by_id,
        'mark_quota_pagata': mock_mark_quota_pagata
    })()

    app = QApplication(sys.argv)
    
    # Test con un socio non pagato (ID 1)
    print("\n--- Test Gestione Pagamenti Socio ID 1 (non pagato) ---")
    dialog_pagamenti_1 = DialogoGestionePagamenti(socio_id=1)
    dialog_pagamenti_1.exec()

    # Test con un socio già pagato (ID 2)
    print("\n--- Test Gestione Pagamenti Socio ID 2 (già pagato) ---")
    dialog_pagamenti_2 = DialogoGestionePagamenti(socio_id=2)
    dialog_pagamenti_2.exec()

    sys.exit(app.exec())