# gestione_stampe_ricevute.py

import os
from PySide6.QtWidgets import QMessageBox
from data_access import get_materiale_by_barcode, get_prezzo_orario_by_tipo, get_prossimo_numero_ricevuta, salva_ricevuta
from Utils import genera_ricevuta_pdf_multilingua
from datetime import datetime # <<< AGGIUNGI QUESTA IMPORTAZIONE se non c'è già

def gestisci_stampa_ricevuta(
    nome_cliente,              # Stringa (es: "Mario")
    cognome_cliente,           # Stringa (es: "Rossi")
    materiali_noleggiati_list, # Lista di tuple (id_db, codice, nome, tipo, produttore, descrizione)
    data_noleggio,             # Stringa "DD/MM/YYYY"
    ora_noleggio,              # Stringa "HH:MM"
    durata_ore,                # Numero intero
    metodo_pagamento,          # Stringa (es: "Contanti")
    importo_totale,            # Numero float
    lingua,                    # Stringa (es: "italiano")
    id_noleggio_corrente,      # <<< QUESTO È NUOVO: ID numerico del noleggio dal DB
    numero_ricevuta_completo   # <<< QUESTO È NUOVO: Stringa "0001/2024"
):
    """
    Gestisce la logica per la generazione e il tentativo di stampa della ricevuta.
    Accetta tutti i dati necessari come argomenti.
    """

    # --- Preparazione dei dati per salva_ricevuta ---

    # Converti data_noleggio da "DD/MM/YYYY" a "YYYY-MM-DD" per il DB
    try:
        data_dt_obj = datetime.strptime(data_noleggio, "%d/%m/%Y")
        data_creazione_str = data_dt_obj.strftime("%Y-%m-%d")
    except ValueError:
        QMessageBox.critical(None, "Errore Data", "Formato data non valido. Deve essere DD/MM/YYYY.")
        return

    # L'ora è già nel formato "HH:MM" per il DB (ora_ricevuta_str)
    ora_ricevuta_str = ora_noleggio 

    # Estrai il numero progressivo e l'anno dalla stringa "0001/2024"
    try:
        parts = numero_ricevuta_completo.split('/')
        numero_ricevuta_int = int(parts[0]) # Per la colonna 'numero_ricevuta' (1, 2, ...)
        anno_ricevuta_int = int(parts[1])   # Per le colonne 'anno_ricevuta' e 'anno' (2024, 2025, ...)
    except (ValueError, IndexError):
        QMessageBox.critical(None, "Errore Numero Ricevuta", "Formato numero ricevuta non valido. Deve essere 0001/YYYY.")
        return

    # Genera il percorso del file PDF (assumendo una cartella 'Ricevute' nella stessa directory del DB)
    # Assicurati che BASE_DIR e DB_PATH siano accessibili o passali come argomenti se necessario
    # Per ora, supponiamo una cartella "Ricevute_PDF" nella stessa directory di questo script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    ricevute_dir = os.path.join(current_dir, "Ricevute_PDF")
    os.makedirs(ricevute_dir, exist_ok=True) # Crea la cartella se non esiste

    pdf_filename = f"Ricevuta_{numero_ricevuta_completo.replace('/', '-')}_{nome_cliente}_{cognome_cliente}.pdf"
    output_pdf_path = os.path.join(ricevute_dir, pdf_filename)
    print(f"DEBUG IN GESTIONE_STAMPE_RICEVUTE: Tipo di ora_str: {type(ora_ricevuta_str)}, Valore di ora_str: {ora_ricevuta_str}")
    # --- Generazione PDF (la tua logica esistente) ---
    ricevuta_generata_con_successo = genera_ricevuta_pdf_multilingua(
        nome_cliente,
        cognome_cliente,
        materiali_noleggiati_list,
        data_noleggio, # Per il PDF potresti volere il formato "DD/MM/YYYY"
        ora_noleggio,
        durata_ore,
        metodo_pagamento,
        importo_totale,
        lingua,
        numero_ricevuta_completo, # Per il PDF il formato "0001/2024"
        output_pdf_path
    )

    if not ricevuta_generata_con_successo:
        QMessageBox.critical(None, "Errore PDF", "Impossibile generare il PDF della ricevuta.")
        return

    # --- Salvataggio nel Database (la parte cruciale) ---
    salva_ricevuta(
        numero_ricevuta_int,       # 1. numero_ricevuta_prog_int (es. 1)
        anno_ricevuta_int,         # 2. anno_ricevuta_prog_int (es. 2024)
        nome_cliente,              # 3. nome_cliente
        cognome_cliente,           # 4. cognome_cliente
        data_creazione_str,        # 5. data_creazione_str (es. "2024-06-11")
        ora_ricevuta_str,          # 6. ora_ricevuta_str (es. "09:47")
        durata_ore,                # 7. durata_ore
        metodo_pagamento,          # 8. metodo_pagamento
        importo_totale,            # 9. importo_totale
        output_pdf_path,           # 10. percorso_file_pdf
        id_noleggio_corrente,      # 11. id_noleggio_associato
        numero_ricevuta_completo,  # 12. numero_ricevuta_testo (es. "0001/2024")
        anno_ricevuta_int          # 13. anno_ricevuta_da_testo (es. 2024)
    )

    # --- Apertura/Stampa del PDF (la tua logica esistente) ---
    if output_pdf_path:
        QMessageBox.information(None, "Ricevuta", f"Ricevuta salvata: {output_pdf_path}")

        try:
            if os.name == 'posix': # macOS e Linux
                os.system(f"open '{output_pdf_path}'")
                QMessageBox.information(None, "Stampa Ricevuta", f"La ricevuta si aprirà in una nuova finestra. Clicca su Stampa.")
            elif os.name == 'nt': # Windows
                os.startfile(output_pdf_path, 'print')
                QMessageBox.information(None, "Stampa Ricevuta", f"Tentativo di stampa diretta della ricevuta.")
            else: # Altri sistemi (es. Linux con xdg-open)
                os.system(f"xdg-open '{output_pdf_path}')")
                QMessageBox.information(None, "Stampa Ricevuta", f"La ricevuta è stata generata. Aprila e clicca su Stampa: {output_pdf_path}")
        except Exception as e:
            QMessageBox.warning(None, "Errore Stampa", f"Impossibile avviare la stampa: {e}")

    # Non si aggiorna lo stato della ricevuta stampata qui,
    # in quanto questa funzione non ha accesso diretto all'istanza del widget NoleggioMateriale
    # che contiene self.ricevuta_stampata. Questo dovrà essere fatto nel chiamante (noleggio_materiale.py).