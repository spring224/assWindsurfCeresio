
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
        from data_access import get_materiale_by_id

        nome = riga["nome_cliente"]
        cognome = riga["cognome_cliente"]
        ora_inizio = datetime.strptime(f"{riga['data_inizio']} {riga['ora_inizio']}", "%Y-%m-%d %H:%M:%S")
        durata = int(riga["durata_ore"])
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
        barra.setValue(progresso)
        if progresso < 60:
           barra.setStyleSheet("QProgressBar::chunk { background-color: green; }")
        elif progresso < 100:
          barra.setStyleSheet("QProgressBar::chunk { background-color: orange; }")
        else:
          barra.setStyleSheet("QProgressBar::chunk { background-color: red; }")

    # Recupera dati materiale
        materiale = get_materiale_by_id(riga["id_materiale"])
        if materiale:
          materiale_str = f"{materiale['tipo']} {materiale['nome']} ({materiale['produttore']})"
        else:
          materiale_str = "???"

        info = QLabel(f"{nome} {cognome} – {materiale_str} dalle {ora_inizio.strftime('%H:%M')} per {durata}h")

    # Pulsante chiudi
        btn_chiudi = QPushButton("Chiudi Noleggio")
        btn_chiudi.clicked.connect(lambda _, idn=riga["id"], idm=riga["id_materiale"]: self.chiudi_e_refresh(idn, idm))

        layout_riga = QVBoxLayout()
        layout_info = QHBoxLayout()
        layout_info.addWidget(info)
        layout_info.addWidget(lbl_tempo)
        layout_info.addWidget(barra)
        layout_info.addWidget(btn_chiudi)

        layout_riga.addLayout(layout_info)

        container = QWidget()
        container.setLayout(layout_riga)
        return container

    def chiudi_e_refresh(self, id_noleggio, id_materiale):
        chiudi_noleggio(id_noleggio, id_materiale)
        self.aggiorna_lista()  # o qualunque funzione tu usi per ricaricare la lista