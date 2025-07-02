# dialogo_comunicazioni.py
# dialogo_comunicazioni.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QLineEdit, QComboBox, QListWidget, QListWidgetItem,
    QMessageBox, QTabWidget, QWidget, QFormLayout, QFileDialog ,QScrollArea, QCheckBox
)
from PySide6.QtCore import Qt, QSize, QDate
from PySide6.QtGui import QIcon
import os

# --- INIZIO AGGIUNTE PER INVIO EMAIL REALE ---
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase # Necessario per gli allegati
from email import encoders # Necessario per gli allegati
# --- FINE AGGIUNTE ---

# Importa le funzioni di accesso ai dati
from data_access import get_all_soci, get_socio_by_id

# --- INIZIO: FUNZIONE PER L'INVIO DI EMAIL REALE ---
# Questi parametri sono presi dal tuo test_Email.py
# NOTA: Per un'applicazione reale, le credenziali (email_address, email_password)
# NON dovrebbero essere hardcoded direttamente nel codice. Considera l'uso
# di variabili d'ambiente o di un sistema di configurazione sicuro.
smtp_server = "smtps.aruba.it"
smtp_port = 465 # Porta SSL
email_address = "info@circolonauticoporlezza.com"
email_password = "Foil2025!" # ATTENZIONE: CREDENZIALI HARDCODED

def send_real_email(to_email, subject, body, attachment=None):
    """
    Invia una email reale usando SMTP_SSL.
    """
    msg = MIMEMultipart()
    msg["From"] = email_address
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    if attachment:
        try:
            with open(attachment, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {os.path.basename(attachment)}",
            )
            msg.attach(part)
        except Exception as e:
            QMessageBox.warning(None, "Errore Allegato", f"Impossibile allegare il file {attachment}: {e}")
            return False # Fallisce l'invio se l'allegato non va

    try:
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(email_address, email_password)
        server.sendmail(email_address, to_email, msg.as_string())
        server.quit() # Chiudi la connessione
        print(f"Email inviata con successo a: {to_email}")
        return True
    except Exception as e:
        print(f"Errore durante l'invio dell'email a {to_email}: {e}")
        QMessageBox.critical(None, "Errore Invio Email", f"Si è verificato un errore durante l'invio dell'email a {to_email}: {e}")
        return False
# --- FINE: FUNZIONE PER L'INVIO DI EMAIL REALE ---


class DialogoComunicazioni(QDialog):
    def __init__(self, db_path, parent=None): # <<< DEVE ESSERE COSÌ
        super().__init__(parent)
        self.db_path = db_path # <<< DEVE ESSERE QUESTA RIGA QUI
        self.setWindowTitle("Gestione Comunicazioni Soci")
        self.setMinimumSize(800, 600)
        self.all_soci_data = []
        self.email_template_sollecito = """
Gentile {nome} {cognome},

Ti ricordiamo che la quota associativa per l'anno {anno} è in scadenza o non è stata ancora saldata.
Ti invitiamo a regolarizzare la tua posizione il prima possibile per continuare a usufruire di tutti i servizi del circolo.

Grazie per la collaborazione.

Cordiali saluti,
Il Circolo Nautico Ceresio
"""
        self.email_template_custom = "" # Inizializza il template personalizzato

        self.init_ui()
        self.load_soci() # Carica i soci all'avvio del dialogo

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        self.tab_widget = QTabWidget(self)
        main_layout.addWidget(self.tab_widget)

        # Tab "Invia Email"
        send_email_tab = QWidget()
        self.tab_widget.addTab(send_email_tab, "Invia Email")
        send_email_layout = QHBoxLayout(send_email_tab)

        # Sezione sinistra: Selezione Soci
        left_layout = QVBoxLayout()
        send_email_layout.addLayout(left_layout)

        left_layout.addWidget(QLabel("Seleziona Destinatari:"))
        
        self.combo_destinatari = QComboBox(self)
        self.combo_destinatari.addItem("Tutti i soci")
        self.combo_destinatari.addItem("Solo soci con quota NON pagata")
        self.combo_destinatari.addItem("Seleziona dalla lista qui sotto")
        self.combo_destinatari.currentIndexChanged.connect(self.update_socio_list_filter)
        left_layout.addWidget(self.combo_destinatari)

        self.list_soci = QListWidget(self)
        self.list_soci.setSelectionMode(QListWidget.MultiSelection) # Permette selezione multipla
        left_layout.addWidget(self.list_soci)

        # Sezione destra: Composizione Email
        right_layout = QVBoxLayout()
        send_email_layout.addLayout(right_layout)

        form_layout = QFormLayout()
        self.subject_input = QLineEdit(self)
        form_layout.addRow("Oggetto:", self.subject_input)

        self.template_combo = QComboBox(self)
        self.template_combo.addItem("Messaggio Personalizzato")
        self.template_combo.addItem("Sollecito Quota Associativa")
        self.template_combo.currentIndexChanged.connect(self.load_email_template)
        form_layout.addRow("Template:", self.template_combo)
        
        self.body_input = QTextEdit(self)
        self.body_input.setPlaceholderText("Scrivi qui il corpo del messaggio...")
        form_layout.addRow("Corpo:", self.body_input)
        right_layout.addLayout(form_layout)

        # Allegato (opzionale)
        attachment_layout = QHBoxLayout()
        self.attachment_path_input = QLineEdit(self)
        self.attachment_path_input.setPlaceholderText("Percorso file allegato (opzionale)")
        self.attachment_path_input.setReadOnly(True) # L'utente non digita direttamente
        self.btn_browse_attachment = QPushButton("Sfoglia...")
        self.btn_browse_attachment.clicked.connect(self.browse_attachment)
        attachment_layout.addWidget(self.attachment_path_input)
        attachment_layout.addWidget(self.btn_browse_attachment)
        right_layout.addLayout(attachment_layout)
        
        self.btn_send_email = QPushButton("Invia Email")
        self.btn_send_email.clicked.connect(self.confirm_and_send_emails)
        right_layout.addWidget(self.btn_send_email)
        
        # Tab "Storico Comunicazioni" (Opzionale, non implementato qui)
        # history_tab = QWidget()
        # self.tab_widget.addTab(history_tab, "Storico Comunicazioni")


    def load_soci(self):
        self.all_soci_data = get_all_soci(self.db_path) # 
        self.update_socio_list_filter()

    def update_socio_list_filter(self):
        self.list_soci.clear()
        filter_type = self.combo_destinatari.currentText()
        
        soci_to_display = []
        if filter_type == "Tutti i soci":
            soci_to_display = self.all_soci_data
        elif filter_type == "Solo soci con quota NON pagata":
            soci_to_display = [s for s in self.all_soci_data if s.get('quota_pagata', 0) == 0]
        # "Seleziona dalla lista" non applica un filtro iniziale, lascia tutti e l'utente seleziona manualmente
        elif filter_type == "Seleziona dalla lista qui sotto":
            soci_to_display = self.all_soci_data # Mostra tutti, ma non seleziona automaticamente

        for socio in soci_to_display:
            item_text = f"{socio.get('nome', '')} {socio.get('cognome', '')} ({socio.get('email', 'Nessuna Email')})"
            list_item = QListWidgetItem(item_text)
            # Memorizza i dati completi del socio nell'item per un facile recupero
            list_item.setData(Qt.UserRole, socio) 
            self.list_soci.addItem(list_item)
            
            # Se la quota è non pagata, seleziona automaticamente se il filtro è "Solo soci con quota NON pagata"
            if filter_type == "Solo soci con quota NON pagata":
                list_item.setSelected(True)


    def load_email_template(self):
        selected_template = self.template_combo.currentText()
        if selected_template == "Sollecito Quota Associativa":
            # Questo template verrà riempito con i dati del socio specifico prima dell'invio
            self.subject_input.setText("Sollecito Quota Associativa Circolo Nautico Ceresio")
            self.body_input.setText(self.email_template_sollecito.strip())
        else: # Messaggio Personalizzato
            self.subject_input.clear()
            self.body_input.clear()
            # Qui potresti caricare un template salvato precedentemente se avessi tale funzionalità
            # Per ora, si limita a svuotare i campi per un messaggio personalizzato

    def browse_attachment(self):
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Seleziona File Allegato")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.attachment_path_input.setText(selected_files[0])


    def confirm_and_send_emails(self):
        subject = self.subject_input.text().strip()
        body = self.body_input.toPlainText().strip()
        attachment_path = self.attachment_path_input.text().strip()
        
        if not subject or not body:
            QMessageBox.warning(self, "Campi Vuoti", "Oggetto e Corpo del messaggio non possono essere vuoti.")
            return

        selected_items = self.list_soci.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Nessun Destinatario", "Seleziona almeno un socio a cui inviare l'email.")
            return

        recipients = []
        for item in selected_items:
            socio_data = item.data(Qt.UserRole)
            email = socio_data.get('email')
            if email and '@' in email: # Semplice validazione email
                recipients.append(socio_data)
            else:
                QMessageBox.warning(self, "Email Non Valida", f"L'email per {socio_data.get('nome')} {socio_data.get('cognome')} non è valida o mancante. Il socio verrà saltato.")
        
        if not recipients:
            QMessageBox.warning(self, "Nessun Destinatario Valido", "Nessun destinatario valido per l'invio dell'email.")
            return

        confirmation = QMessageBox.question(
            self,
            "Conferma Invio Email",
            f"Sei sicuro di voler inviare questa email a {len(recipients)} soci?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirmation == QMessageBox.No:
            return

        # Invia le email
        sent_count = 0
        failed_count = 0
        for socio in recipients:
            to_email = socio.get('email')
            
            # Personalizza il corpo del messaggio per il sollecito
            final_body = body.replace("{nome}", socio.get('nome', '')) \
                             .replace("{cognome}", socio.get('cognome', '')) \
                             .replace("{anno}", str(socio.get('anno', '')))

            # <<< QUI CHIAMIAMO LA FUNZIONE DI INVIO EMAIL REALE >>>
            if send_real_email(to_email, subject, final_body, attachment_path if attachment_path else None):
                sent_count += 1
            else:
                failed_count += 1

        QMessageBox.information(self, "Invio Completato", 
                                f"Invio email completato.\nInviate con successo: {sent_count}\nFallite: {failed_count}")

# Esempio di utilizzo (solo per test, questa parte non deve essere attiva nel codice finale principale)
# if __name__ == '__main__':
#     import sys
#     from PySide6.QtWidgets import QApplication
#     # Questo db_path è solo per il test autonomo di questo dialogo
#     # Assicurati che 'soci.db' esista o venga creato per i test
#     # db_path = os.path.join(os.path.dirname(__file__), "soci.db") 

#     app = QApplication(sys.argv)
#     dialog = DialogoComunicazioni()
#     dialog.exec()
#     sys.exit(app.exec())
