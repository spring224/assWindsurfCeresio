# dialogo_comunicazioni.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QLineEdit, QComboBox, QListWidget, QListWidgetItem,
    QMessageBox, QTabWidget, QWidget, QFormLayout, QScrollArea, QCheckBox
)
from PySide6.QtCore import Qt, QSize, QDate
from PySide6.QtGui import QIcon
import os

# Importa le funzioni di accesso ai dati
from data_access import get_all_soci, get_socio_by_id

# Funzione per simulare l'invio di email (temporanea)
def send_email_simulated(to_email, subject, body, attachment=None):
    """
    Simula l'invio di una email.
    In un'implementazione reale, qui useresti smtplib.
    """
    print(f"--- EMAIL SIMULATA INVIATA ---")
    print(f"A: {to_email}")
    print(f"Oggetto: {subject}")
    print(f"Corpo:\n{body}\n")
    if attachment:
        print(f"Allegato: {attachment}")
    print(f"------------------------------")
    return True

class DialogoComunicazioni(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestione Comunicazioni Soci")
        self.setMinimumSize(800, 600)
        self.all_soci_data = [] # Lista per memorizzare tutti i soci
        self.email_template_sollecito = {
            "oggetto": "Sollecito Quota Associativa Anno in Corso - Circolo Nautico Porlezza",
            "corpo": """Gentile {nome} {cognome},

ti ricordiamo che la quota associativa per l'anno in corso ({anno_corrente}) risulta ancora da saldare.

Il tuo contributo è fondamentale per sostenere le attività del Circolo Nautico Porlezza e per garantire la migliore esperienza ai nostri associati.

Ti preghiamo di provvedere al pagamento quanto prima. Puoi contattarci per qualsiasi informazione o per concordare le modalità di pagamento.

Grazie per la collaborazione.

Cordiali saluti,

La Segreteria del Circolo Nautico Porlezza
Email: segreteria@circolonauticoporlezza.com
Sito Web: www.circolonauticoporlezza.com
"""
        }

        self.init_ui()
        self.carica_soci_per_selezione()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        self.tab_widget = QTabWidget(self)

        # Tab 1: Sollecito Pagamento
        self.tab_sollecito = QWidget()
        self.setup_sollecito_tab()
        self.tab_widget.addTab(self.tab_sollecito, "Sollecito Pagamento")

        # Tab 2: Comunicazione Generica
        self.tab_generica = QWidget()
        self.setup_generica_tab()
        self.tab_widget.addTab(self.tab_generica, "Comunicazione Generica")

        main_layout.addWidget(self.tab_widget)

        # Pulsante Chiudi
        close_button = QPushButton("Chiudi")
        close_button.clicked.connect(self.accept)
        main_layout.addWidget(close_button, alignment=Qt.AlignCenter)

    def setup_sollecito_tab(self):
        layout = QVBoxLayout(self.tab_sollecito)
        
        # Filtro per Soci con Quota NON Pagata
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Soci con quota non pagata:")
        self.soci_non_paganti_list = QListWidget()
        self.soci_non_paganti_list.setSelectionMode(QListWidget.MultiSelection) # Permette selezione multipla
        self.btn_carica_non_paganti = QPushButton("Carica Soci Non Paganti")
        self.btn_seleziona_tutti_non_paganti = QPushButton("Seleziona Tutti")

        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.btn_carica_non_paganti)
        filter_layout.addWidget(self.btn_seleziona_tutti_non_paganti)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        layout.addWidget(self.soci_non_paganti_list)

        # Anteprima Email Sollecito
        layout.addWidget(QLabel("Oggetto Email:"))
        self.sollecito_oggetto_input = QLineEdit()
        self.sollecito_oggetto_input.setReadOnly(True) # Oggetto predefinito
        self.sollecito_oggetto_input.setText(self.email_template_sollecito["oggetto"])
        layout.addWidget(self.sollecito_oggetto_input)

        layout.addWidget(QLabel("Corpo Email (modificabile):"))
        self.sollecito_corpo_text = QTextEdit()
        self.sollecito_corpo_text.setText(self.email_template_sollecito["corpo"].replace("{anno_corrente}", str(QDate.currentDate().year())))
        layout.addWidget(self.sollecito_corpo_text)
        
        # Opzioni aggiuntive per sollecito
        sollecito_options_layout = QHBoxLayout()
        self.check_allega_tessera_sollecito = QCheckBox("Allega Tessera (PDF) se disponibile")
        sollecito_options_layout.addWidget(self.check_allega_tessera_sollecito)
        sollecito_options_layout.addStretch()
        layout.addLayout(sollecito_options_layout)

        # Pulsante per invio sollecito
        self.btn_invia_sollecito = QPushButton("Invia Sollecito Email")
        layout.addWidget(self.btn_invia_sollecito, alignment=Qt.AlignCenter)

        # Connessioni
        self.btn_carica_non_paganti.clicked.connect(self.carica_soci_non_paganti)
        self.btn_seleziona_tutti_non_paganti.clicked.connect(self.soci_non_paganti_list.selectAll)
        self.btn_invia_sollecito.clicked.connect(self.invia_sollecito_pagamento)

    def setup_generica_tab(self):
        layout = QVBoxLayout(self.tab_generica)

        # Selezione Destinatari
        recipients_group_layout = QHBoxLayout()
        
        # Soci selezionabili
        soci_selection_layout = QVBoxLayout()
        soci_selection_layout.addWidget(QLabel("Seleziona Destinatari:"))
        self.soci_generici_list = QListWidget()
        self.soci_generici_list.setSelectionMode(QListWidget.MultiSelection)
        soci_selection_layout.addWidget(self.soci_generici_list)
        
        select_buttons_layout = QVBoxLayout()
        self.btn_seleziona_tutti_generici = QPushButton("Seleziona Tutti")
        self.btn_deseleziona_tutti_generici = QPushButton("Deseleziona Tutti")
        select_buttons_layout.addWidget(self.btn_seleziona_tutti_generici)
        select_buttons_layout.addWidget(self.btn_deseleziona_tutti_generici)
        select_buttons_layout.addStretch() # Spinge i pulsanti in alto
        soci_selection_layout.addLayout(select_buttons_layout)

        recipients_group_layout.addLayout(soci_selection_layout)
        
        layout.addLayout(recipients_group_layout)

        # Oggetto e Corpo Email Generica
        layout.addWidget(QLabel("Oggetto Email:"))
        self.generica_oggetto_input = QLineEdit()
        self.generica_oggetto_input.setPlaceholderText("Inserisci l'oggetto della comunicazione")
        layout.addWidget(self.generica_oggetto_input)

        layout.addWidget(QLabel("Corpo Email:"))
        self.generica_corpo_text = QTextEdit()
        self.generica_corpo_text.setPlaceholderText("Scrivi qui il testo della tua comunicazione...")
        layout.addWidget(self.generica_corpo_text)

        # Opzioni aggiuntive per comunicazione generica
        generica_options_layout = QHBoxLayout()
        self.check_allega_tessera_generica = QCheckBox("Allega Tessera (PDF) per i selezionati")
        generica_options_layout.addWidget(self.check_allega_tessera_generica)
        generica_options_layout.addStretch()
        layout.addLayout(generica_options_layout)

        # Pulsante per invio comunicazione generica
        self.btn_invia_generica = QPushButton("Invia Comunicazione Email")
        layout.addWidget(self.btn_invia_generica, alignment=Qt.AlignCenter)

        # Connessioni
        self.btn_seleziona_tutti_generici.clicked.connect(self.soci_generici_list.selectAll)
        self.btn_deseleziona_tutti_generici.clicked.connect(self.soci_generici_list.clearSelection)
        self.btn_invia_generica.clicked.connect(self.invia_comunicazione_generica)

    def carica_soci_per_selezione(self):
        """Carica tutti i soci in entrambe le liste di selezione (sollecito e generica)."""
        self.all_soci_data = get_all_soci() # get_all_soci deve restituire una lista di dizionari con i dati completi

        self.soci_non_paganti_list.clear()
        self.soci_generici_list.clear()

        for socio in self.all_soci_data:
            # Per la tab generica, aggiungi tutti i soci
            item_gen = QListWidgetItem(f"{socio.get('nome', '')} {socio.get('cognome', '')} ({socio.get('email', 'N/A')})")
            item_gen.setData(Qt.UserRole, socio.get('id')) # Memorizza l'ID del socio
            self.soci_generici_list.addItem(item_gen)
            
            # Solo se quota_pagata è 0 (No)
            if socio.get('quota_pagata', 0) == 0:
                item_non_pag = QListWidgetItem(f"{socio.get('nome', '')} {socio.get('cognome', '')} ({socio.get('email', 'N/A')})")
                item_non_pag.setData(Qt.UserRole, socio.get('id'))
                self.soci_non_paganti_list.addItem(item_non_pag)

    def carica_soci_non_paganti(self):
        """Ricarica solo la lista dei soci non paganti e la filtra."""
        self.soci_non_paganti_list.clear()
        soci_filtered = [s for s in self.all_soci_data if s.get('quota_pagata', 0) == 0]
        for socio in soci_filtered:
            item = QListWidgetItem(f"{socio.get('nome', '')} {socio.get('cognome', '')} ({socio.get('email', 'N/A')})")
            item.setData(Qt.UserRole, socio.get('id'))
            self.soci_non_paganti_list.addItem(item)
        
        if not soci_filtered:
            QMessageBox.information(self, "Informazione", "Nessun socio con quota non pagata trovato.")

    def invia_sollecito_pagamento(self):
        selected_items = self.soci_non_paganti_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Selezione", "Seleziona almeno un socio a cui inviare il sollecito.")
            return

        socio_ids = [item.data(Qt.UserRole) for item in selected_items]
        
        oggetto = self.sollecito_oggetto_input.text()
        corpo_template = self.sollecito_corpo_text.toPlainText()
        
        success_count = 0
        fail_count = 0

        # Importa la funzione di stampa tessera qui per evitare import circolari
        from stampa_tessera_soci import stampa_tessera_pdf

        for socio_id in socio_ids:
            socio = get_socio_by_id(socio_id)
            if not socio or not socio.get('email'):
                QMessageBox.warning(self, "Errore Dati", f"Impossibile inviare email per socio ID {socio_id} (dati mancanti o email non valida).")
                fail_count += 1
                continue

            # Personalizza il corpo dell'email
            personalized_body = corpo_template.format(
                nome=socio.get('nome', 'Socio'),
                cognome=socio.get('cognome', ''),
                anno_corrente=QDate.currentDate().year()
            )
            
            to_email = socio['email']
            attachment_path = None

            if self.check_allega_tessera_sollecito.isChecked():
                try:
                    # Genera la tessera in una directory temporanea o specifica per allegati
                    temp_output_dir = "temp_allegati_email"
                    os.makedirs(temp_output_dir, exist_ok=True)
                    temp_filename = os.path.join(temp_output_dir, f"tessera_{socio['nome']}_{socio['cognome']}_{socio['id']}.pdf")
                    # Chiama la funzione di stampa tessera, passando il path di output
                    # Potrebbe essere necessario modificare stampa_tessera_pdf per restituire il path
                    # o accettare un path di output
                    stampa_tessera_pdf(socio_id, parent_widget=self) # La funzione stampa_tessera_pdf già salva
                    # Assumo che stampa_tessera_pdf salvi in "tessere_associati"
                    attachment_path = os.path.join("tessere_associati", f"tessera_{socio['nome']}_{socio['cognome']}_{socio['id']}.pdf")

                    if not os.path.exists(attachment_path):
                        QMessageBox.warning(self, "Errore Allegato", f"Impossibile trovare la tessera PDF per {socio['nome']} {socio['cognome']}. Non sarà allegata.")
                        attachment_path = None # Non allegare se non trovata
                except Exception as e:
                    QMessageBox.warning(self, "Errore Allegato", f"Errore durante la generazione della tessera per {socio['nome']} {socio['cognome']}: {e}. Non sarà allegata.")
                    attachment_path = None


            if send_email_simulated(to_email, oggetto, personalized_body, attachment_path):
                success_count += 1
            else:
                fail_count += 1
        
        QMessageBox.information(self, "Invio Solleciti", 
                                f"Invio solleciti completato.\n"
                                f"Inviate con successo: {success_count}\n"
                                f"Fallite: {fail_count}")

    def invia_comunicazione_generica(self):
        selected_items = self.soci_generici_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Selezione", "Seleziona almeno un socio a cui inviare la comunicazione.")
            return

        oggetto = self.generica_oggetto_input.text().strip()
        corpo = self.generica_corpo_text.toPlainText().strip()

        if not oggetto or not corpo:
            QMessageBox.warning(self, "Dati Mancanti", "Oggetto e corpo dell'email non possono essere vuoti.")
            return
        
        socio_ids = [item.data(Qt.UserRole) for item in selected_items]
        
        success_count = 0
        fail_count = 0

        # Importa la funzione di stampa tessera qui per evitare import circolari
        from stampa_tessera_soci import stampa_tessera_pdf

        for socio_id in socio_ids:
            socio = get_socio_by_id(socio_id)
            if not socio or not socio.get('email'):
                QMessageBox.warning(self, "Errore Dati", f"Impossibile inviare email per socio ID {socio_id} (dati mancanti o email non valida).")
                fail_count += 1
                continue

            to_email = socio['email']
            attachment_path = None

            if self.check_allega_tessera_generica.isChecked():
                try:
                    # Genera la tessera
                    stampa_tessera_pdf(socio_id, parent_widget=self)
                    attachment_path = os.path.join("tessere_associati", f"tessera_{socio['nome']}_{socio['cognome']}_{socio['id']}.pdf")
                    if not os.path.exists(attachment_path):
                        QMessageBox.warning(self, "Errore Allegato", f"Impossibile trovare la tessera PDF per {socio['nome']} {socio['cognome']}. Non sarà allegata.")
                        attachment_path = None
                except Exception as e:
                    QMessageBox.warning(self, "Errore Allegato", f"Errore durante la generazione della tessera per {socio['nome']} {socio['cognome']}: {e}. Non sarà allegata.")
                    attachment_path = None
            
            # Il corpo del messaggio generico non viene personalizzato con nome/cognome per default
            # Se vuoi personalizzarlo, puoi aggiungere placeholder qui e sostituirli
            if send_email_simulated(to_email, oggetto, corpo, attachment_path):
                success_count += 1
            else:
                fail_count += 1
        
        QMessageBox.information(self, "Invio Comunicazioni", 
                                f"Invio comunicazioni completato.\n"
                                f"Inviate con successo: {success_count}\n"
                                f"Fallite: {fail_count}")

# Esempio di esecuzione per testare solo questo dialogo (opzionale)
if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication
    # Importa i mock per data_access se vuoi testare questo file singolarmente
    # Senza i mock, questo test fallirà a meno che data_access.py non sia configurato correttamente
    # e il DB sia accessibile.
    
    # Esempio di mock per test locale, NON USARE NELL'APP FINALE
    class MockSocio:
        def __init__(self, id, nome, cognome, email, quota_pagata):
            self.data = {'id': id, 'nome': nome, 'cognome': cognome, 'email': email, 'quota_pagata': quota_pagata,
                         'numero_tessera': '12345', 'anno': 2025, 'data_scadenza': '2025-12-31'}
        def get(self, key, default=None):
            return self.data.get(key, default)

    mock_db_soci = [
        MockSocio(1, 'Mario', 'Rossi', 'mario.rossi@example.com', 0), # Quota non pagata
        MockSocio(2, 'Anna', 'Verdi', 'anna.verdi@example.com', 1), # Quota pagata
        MockSocio(3, 'Luca', 'Bianchi', 'luca.bianchi@example.com', 0), # Quota non pagata
        MockSocio(4, 'Giulia', 'Neri', 'giulia.neri@example.com', 1),
        MockSocio(5, 'Paolo', 'Gialli', 'paolo.gialli@example.com', 0), # Quota non pagata
    ]

    # Mock per le funzioni di data_access
    def mock_get_all_soci():
        return [s.data for s in mock_db_soci]

    def mock_get_socio_by_id(socio_id):
        for s in mock_db_soci:
            if s.data['id'] == socio_id:
                return s
        return None
    
    # Mock per stampa_tessera_pdf nel contesto di test di questo file
    # Non è il vero stampa_tessera_pdf, ma uno che "fa finta"
    def mock_stampa_tessera_pdf(socio_id, parent_widget=None):
        print(f"SIMULAZIONE: Generazione tessera PDF per socio ID {socio_id}")
        # Crea un file finto per simulare l'allegato
        temp_file = os.path.join("tessere_associati", f"tessera_mock_{socio_id}.pdf")
        os.makedirs("tessere_associati", exist_ok=True)
        with open(temp_file, 'w') as f:
            f.write(f"Tessera finta per socio ID {socio_id}")
        return temp_file # Restituisci il percorso simulato


    # Inietta i mock nel modulo corrente per il test
    import sys
    sys.modules['data_access'].get_all_soci = mock_get_all_soci
    sys.modules['data_access'].get_socio_by_id = mock_get_socio_by_id
    sys.modules['stampa_tessera_soci'] = type('module', (object,), {'stampa_tessera_pdf': mock_stampa_tessera_pdf})() # Crea un modulo fittizio

    app = QApplication(sys.argv)
    dialog = DialogoComunicazioni()
    dialog.exec()
    sys.exit(app.exec())