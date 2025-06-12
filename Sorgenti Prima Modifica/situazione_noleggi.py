
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QPushButton, QHBoxLayout, QMessageBox, QScrollArea
from PySide6.QtCore import QTimer
from datetime import datetime, timedelta
from data_access import get_noleggi_attivi, chiudi_noleggio
    

class SituazioneNoleggi(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Situazione Noleggi Attivi")
        self.layout = QVBoxLayout()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.container = QWidget()
        self.container_layout = QVBoxLayout()
        self.container.setLayout(self.container_layout)
        scroll.setWidget(self.container)
        self.layout.addWidget(scroll)
        self.setLayout(self.layout)

        self.aggiorna_lista()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.aggiorna_lista)
        self.timer.start(60000)

    def aggiorna_lista(self):
        for i in reversed(range(self.container_layout.count())):
            widget = self.container_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        for riga in get_noleggi_attivi():
            widget = self.crea_riga(riga)
            self.container_layout.addWidget(widget)



    def crea_riga(self, riga):
        from data_access import get_materiale_by_id # Import locale per evitare circular import se data_access dipende da SituazioneNoleggi

        nome = riga["nome_cliente"]
        cognome = riga["cognome_cliente"]
        # Inizia la sezione modificata per gestire None
        data_inizio_str = riga['data_inizio']
        ora_inizio_str = riga['ora_inizio']

        if data_inizio_str is not None and ora_inizio_str is not None:
            try:
                ora_inizio = datetime.strptime(f"{data_inizio_str} {ora_inizio_str}", "%Y-%m-%d %H:%M:%S")
            except ValueError:
                # Se il formato è sbagliato ma non è None, usa ora attuale
                ora_inizio = datetime.now()
                print(f"DEBUG: Formato data/ora inizio non valido per noleggio ID {riga['id']}. Usata ora attuale.")
        else:
            # Se data o ora sono None, considera noleggio non iniziato o con dati incompleti
            ora_inizio = datetime.now() # O un'altra data/ora di default a tua scelta
            print(f"DEBUG: Data/Ora inizio mancante per noleggio ID {riga['id']}. Usata ora attuale.")
        # Fine della sezione modificata

        durata = int(riga["durata_ore"]) # Questa riga rimane invariata

        ora_fine = ora_inizio + timedelta(hours=durata)
        ora_attuale = datetime.now()

        

        # Calcolo progresso
        totale_sec = (ora_fine - ora_inizio).total_seconds()
        trascorso_sec = (ora_attuale - ora_inizio).total_seconds()
        progresso = max(0, min(int((trascorso_sec / totale_sec) * 100), 100))

        # Testo tempo rimanente
        tempo_rimanente = ora_fine - ora_attuale
        minuti = int(tempo_rimanente.total_seconds() // 60)
        testo_tempo = f"⏳ Tempo rimanente: {minuti} min" if minuti >= 0 else "⏰ Noleggio scaduto"
        lbl_tempo = QLabel(testo_tempo)

        # Colore barra
        barra = QProgressBar()
        barra.setMinimumHeight(20) # AGGIUNGI QUESTA NUOVA RIGA
        barra.setMinimumWidth(150)
        barra.setMaximumWidth(150)
        barra.setValue(progresso)
        if progresso < 60:
         barra.setStyleSheet("QProgressBar::chunk { background-color: green; }")
        elif progresso < 100:
         barra.setStyleSheet("QProgressBar::chunk { background-color: orange; }")
        else:
         barra.setStyleSheet("QProgressBar::chunk { background-color: red; }")
         barra.setFixedWidth(150) # Rendi la barra più compatta

        # Recupera dati materiale
        materiale = get_materiale_by_id(riga["id_materiale"])
        if materiale:
         materiale_str = f"{materiale['tipo']} {materiale['nome']} ({materiale['produttore']})"
        else:
         materiale_str = "???"

        info = QLabel(f"<b>{nome} {cognome}</b> – {materiale_str} dalle {ora_inizio.strftime('%H:%M')} per {durata}h")
        info.setWordWrap(True) # Se il testo è lungo

        # Pulsante chiudi
        btn_chiudi = QPushButton("Chiudi Noleggio")
        btn_chiudi.setFixedWidth(120) # Rendi il pulsante più compatto
        btn_chiudi.clicked.connect(lambda _, idn=riga["id"], idm=riga["id_materiale"]: self.chiudi_e_refresh(idn, idm))

        # Layout per la riga
        layout_riga_principale = QHBoxLayout() # Un layout orizzontale per la riga completa

        # Colonna di sinistra (Info Cliente/Materiale)
        layout_info_cliente_materiale = QVBoxLayout()
        layout_info_cliente_materiale.addWidget(info)

        # Colonna di destra (Tempo, Barra, Chiudi)
        layout_stato_azione = QHBoxLayout()
        layout_stato_azione.addWidget(lbl_tempo)
        layout_stato_azione.addWidget(barra)
        layout_stato_azione.addWidget(btn_chiudi)
        layout_stato_azione.addStretch(1) # Spinge tutto a sinistra

        layout_riga_principale.addLayout(layout_info_cliente_materiale)
        layout_riga_principale.addStretch(1) # Spazio tra info e stato/azione
        layout_riga_principale.addLayout(layout_stato_azione)

        # Aggiungi un QFrame per dare un bordo a ogni riga, per migliorarne la visibilità
        from PySide6.QtWidgets import QFrame
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setFrameShadow(QFrame.Raised)
        frame.setLayout(layout_riga_principale) # Assegna il layout orizzontale al frame

        return frame # Ritorna il frame invece del container




    def chiudi_e_refresh(self, id_noleggio, id_materiale):
        chiudi_noleggio(id_noleggio, id_materiale)
        self.aggiorna_lista()  # o qualunque funzione tu usi per ricaricare la lista