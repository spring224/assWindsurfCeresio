from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QStackedWidget, QHBoxLayout
from PySide6.QtCore import Qt # Necessario per Qt.AlignCenter

class GestioneNoleggi(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestione Noleggi")

        main_layout = QVBoxLayout(self) # Imposta il layout principale per il widget

        # Layout per i pulsanti di selezione (parte superiore)
        button_layout = QHBoxLayout()
        self.btn_listino = QPushButton("📋 Gestione Listino Noleggio")
        self.btn_resoconto = QPushButton("📈 Resoconto Noleggi")
        
        button_layout.addWidget(self.btn_listino)
        button_layout.addWidget(self.btn_resoconto)

        main_layout.addLayout(button_layout) # Aggiungi i pulsanti al layout principale

        # Crea lo QStackedWidget per contenere le diverse sezioni
        self.stacked_widget = QStackedWidget(self)
        main_layout.addWidget(self.stacked_widget) # Aggiungi lo stacked widget al layout principale

        # Inizializza le finestre secondarie e aggiungile allo stacked widget
        # Le importazioni sono qui per evitare circular imports se le classi si riferiscono l'un l'altra
        from Listino_noleggi import FinestraListino
        from resoconto_noleggi import FinestraResoconto

        self.listino_widget = FinestraListino()
        self.resoconto_widget = FinestraResoconto()

        # Aggiungi un widget di benvenuto/iniziale
        self.label_benvenuto = QLabel("Seleziona un'operazione tra quelle sopra per visualizzare i dettagli.")
        self.label_benvenuto.setAlignment(Qt.AlignCenter)
        self.label_benvenuto.setStyleSheet("font-size: 18px; color: gray;")

        self.stacked_widget.addWidget(self.label_benvenuto)    # Indice 0: Pagina di benvenuto
        self.stacked_widget.addWidget(self.listino_widget)     # Indice 1: Finestra Listino
        self.stacked_widget.addWidget(self.resoconto_widget)   # Indice 2: Finestra Resoconto

        # Mostra la pagina di benvenuto all'avvio
        self.stacked_widget.setCurrentWidget(self.label_benvenuto)

        # Connetti i pulsanti per cambiare la pagina dello stacked widget
        self.btn_listino.clicked.connect(self.show_listino)
        self.btn_resoconto.clicked.connect(self.show_resoconto)

    def show_listino(self):
        self.stacked_widget.setCurrentWidget(self.listino_widget)
        # Se FinestraListino ha un metodo per ricaricare i dati, chiamalo qui
        if hasattr(self.listino_widget, 'load_listino_data'): # Assumi che si chiami load_listino_data
            self.listino_widget.load_listino_data()
        print("DEBUG: Mostrato listino noleggi.")

    def show_resoconto(self):
        self.stacked_widget.setCurrentWidget(self.resoconto_widget)
        # Se FinestraResoconto ha un metodo per ricaricare i dati, chiamalo qui
        if hasattr(self.resoconto_widget, 'load_resoconto_data'): # Assumi che si chiami load_resoconto_data
            self.resoconto_widget.load_resoconto_data()
        print("DEBUG: Mostrato resoconto noleggi.")

    # Questo metodo può essere chiamato dalla MainWindow se necessario (es. quando questo widget viene mostrato)
    def enter_view(self):
        print("DEBUG: GestioneNoleggi è stata selezionata nella MainWindow.")
        # Puoi decidere cosa mostrare di default quando si torna a questa vista
        # self.stacked_widget.setCurrentWidget(self.label_benvenuto)
        # oppure: self.show_listino() # Per mostrare direttamente il listino