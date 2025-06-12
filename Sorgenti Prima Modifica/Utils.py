import os
import shutil
from pathlib import Path
from fpdf import FPDF
from datetime import datetime
from PySide6.QtWidgets import QMessageBox

from data_access import (
        get_materiale_by_barcode,
        get_prossimo_numero_ricevuta,
        salva_ricevuta,
        get_noleggio_attivo_per_cliente,
        get_prezzo_orario_by_tipo,
        aggiorna_importo_noleggio
    )
from datetime import datetime

import os
import shutil
from pathlib import Path
from fpdf import FPDF

    
    
def genera_ricevuta_pdf_multilingua(
    # Questi 11 parametri devono corrispondere esattamente alla chiamata in gestione_stampe_ricevute.py
    # L'ordine è CRUCIALE!
    nome_per_pdf,                 # 1° parametro: riceve nome_cliente
    cognome_per_pdf,              # 2° parametro: riceve cognome_cliente
    materiali_per_pdf,            # 3° parametro: riceve materiali_noleggiati_list
    data_per_pdf,                 # 4° parametro: riceve data_noleggio
    ora_per_pdf,                  # 5° parametro: riceve ora_noleggio (LA TUA STRINGA "12:12")
    durata_per_pdf,               # 6° parametro: riceve durata_ore (IL TUO INT 1)
    metodo_pagamento_per_pdf,     # 7° parametro: riceve metodo_pagamento
    importo_totale_per_pdf,       # 8° parametro: riceve importo_totale
    lingua_per_pdf,               # 9° parametro: riceve lingua
    numero_ricevuta_completo_per_pdf, # 10° parametro: riceve numero_ricevuta_completo
    output_pdf_path_finale,       # 11° parametro: riceve output_pdf_path
    logo_path="logo_onda.png"     # 12° parametro: mantiene il suo valore di default, non è toccato
     ):
    

    nome = nome_per_pdf
    cognome = cognome_per_pdf
    materiali = materiali_per_pdf
    data = data_per_pdf
    ora = ora_per_pdf # <<<<<< QUI ora conterrà la STRINGA "12:12" (la tua ora di noleggio)
    durata = durata_per_pdf # <<<<<< QUI durata conterrà l'INT 1 (la tua durata)
    metodo_pagamento = metodo_pagamento_per_pdf
    importo_totale = importo_totale_per_pdf
    lingua = lingua_per_pdf
    numero = numero_ricevuta_completo_per_pdf
    lingua = lingua.strip().lower()
    traduzioni = {
        "italiano": {
            "titolo": "Ricevuta Noleggio Materiale", # Titolo più descrittivo
            "ricevuta_n": "Ricevuta N.:",
            "data_emissione": "Data Emissione:", # Nuovo campo
            "ora_emissione": "Ora Emissione:",   # Nuovo campo
            "cliente": "Cliente:",
            "materiali": "Materiali Noleggiati:",
            "codice": "Codice", # Colonna tabella
            "nome_mat": "Nome Materiale", # Colonna tabella
            "tipo_mat": "Tipo", # Colonna tabella
            "produttore_mat": "Produttore", # Colonna tabella
            "durata_contratto": "Durata Contratto:", # Nuovo campo per il riepilogo
            "pagamento": "Tipo di Pagamento:",
            "totale": "Totale:",
            "grazie": "Grazie per aver scelto Windsurf Ceresio!",
            "note_legali": "Associazione Sportiva Dilettantistica Circolo Nautico All Sport Ceresio\nVia Caduti In Guerra, 18 - 22018 Porlezza (CO)\nCodice Fiscale: CRTGLG71R05F712P\nTel: +39 031 XXXXXX | Email: windsurfporlezza@gmail.com"
        },
        "english": {
            "titolo": "Material Rental Receipt",
            "ricevuta_n": "Receipt No.:",
            "data_emissione": "Issue Date:",
            "ora_emissione": "Issue Time:",
            "cliente": "Client:",
            "materiali": "Rented Materials:",
            "codice": "Code",
            "nome_mat": "Material Name",
            "tipo_mat": "Type",
            "produttore_mat": "Manufacturer",
            "durata_contratto": "Rental Duration:",
            "pagamento": "Payment Method:",
            "totale": "Total:",
            "grazie": "Thank you for choosing Windsurf Ceresio!",
            "note_legali": "Associazione Sportiva Dilettantistica Circolo Nautico All Sport Ceresio\n\nFiscal Code: XXXXXXXXXXXXX (Example)\nTel: +39 031 XXXXXX | Email: info@windsurfceresio.com"
        }
        # Aggiungi altre lingue qui se necessario
    }

    t = traduzioni.get(lingua, traduzioni["italiano"]) # Default italiano

    pdf = FPDF('P', 'mm', 'A4')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15) # Margine inferiore
    pdf.set_left_margin(20) # Margine sinistro
    pdf.set_right_margin(20) # Margine destro


    # --- INTESTAZIONE MIGLIORATA ---
    # Logo a sinistra
    try:
        if os.path.exists(logo_path):
            pdf.image(logo_path, x=20, y=10, w=40) # Adatta w e y in base al tuo logo
        else:
            print(f"ATTENZIONE: Logo non trovato al percorso: {logo_path}")
    except Exception as e:
        print(f"Errore nel caricamento del logo: {e}")

    # Informazioni Azienda (allineate a destra o centro)
    pdf.set_xy(pdf.w - 80, 10) # Sposta a destra
    pdf.set_font('Arial', 'B', 12)
    pdf.multi_cell(60, 6, "ASSOCIAZIONE SPORTIVA DILETTANTISTICA CIRCOLO NAUTICO ALL SPORT CERESIO", 0, 'R')
    pdf.set_x(pdf.w - 80)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(60, 5, ",22018 Porlezza (CO)", 0, 'R')
    pdf.ln(10) # Spazio dopo l'intestazione

    # --- TITOLO RICEVUTA ---
    pdf.set_font('Arial', 'B', 18)
    pdf.cell(0, 10, t["titolo"], 0, 1, 'C')
    pdf.ln(8) # Spazio

    # --- DETTAGLI RICEVUTA E CLIENTE ---
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(40, 7, t["ricevuta_n"], 0, 0, 'L')
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 7, str(numero), 0, 1, 'L')

    pdf.set_font('Arial', 'B', 11)
    pdf.cell(40, 7, t["data_emissione"], 0, 0, 'L')
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 7, data, 0, 1, 'L')

    pdf.set_font('Arial', 'B', 11)
    pdf.cell(40, 7, t["ora_emissione"], 0, 0, 'L')
    pdf.set_font('Arial', '', 11)
     # >>> AGGIUNGI QUESTA RIGA DI DEBUG (che sarà la nuova riga 111 o 112 a seconda del posizionamento):
    print(f"DEBUG IN UTILS: Tipo di ora: {type(ora)}, Valore di ora: {ora}")
    pdf.cell(0, 7, ora, 0, 1, 'L')
   
    pdf.ln(5) # Spazio

    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 7, t["cliente"], 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 7, f"{nome} {cognome}", 0, 1, 'L')
    pdf.ln(8) # Spazio

    # --- SEZIONE MATERIALI ---
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, t["materiali"], 0, 1, 'L')

    # Intestazioni tabella materiali
    pdf.set_font('Arial', 'B', 10)
    # Larghezze delle colonne (somma deve essere circa la larghezza della pagina - margini, es. 210-40=170)
    col_widths = [30, 50, 30, 60] # Codice, Nome, Tipo, Produttore
    
    # Intestazioni della tabella
    pdf.cell(col_widths[0], 7, t["codice"], 1, 0, 'C')
    pdf.cell(col_widths[1], 7, t["nome_mat"], 1, 0, 'C')
    pdf.cell(col_widths[2], 7, t["tipo_mat"], 1, 0, 'C')
    pdf.cell(col_widths[3], 7, t["produttore_mat"], 1, 1, 'C') # 1 for new line

    # Dati materiali
    pdf.set_font('Arial', '', 10)
    for mat_item in materiali:
        # La tupla mat_item (proveniente da self.materiali_noleggiati) è:
        # (id_db, codice, nome, tipo, produttore, descrizione) 
        # Quindi, per stampare Codice, Nome, Tipo, Produttore, gli indici corretti sono 1, 2, 3, 4.
        
        codice_per_stampa = mat_item[1]       # Questo è il tuo 'codice' effettivo (es. "S002")
        nome_mat_per_stampa = mat_item[2]     # Questo è il tuo 'nome' effettivo
        tipo_mat_per_stampa = mat_item[3]     # Questo è il tuo 'tipo' effettivo
        produttore_per_stampa = mat_item[4]   # Questo è il tuo 'produttore' effettivo

        pdf.cell(col_widths[0], 7, str(codice_per_stampa), 1, 0, 'L')
        pdf.cell(col_widths[1], 7, str(nome_mat_per_stampa), 1, 0, 'L')
        pdf.cell(col_widths[2], 7, str(tipo_mat_per_stampa), 1, 0, 'L')
        pdf.cell(col_widths[3], 7, str(produttore_per_stampa), 1, 1, 'L')
    pdf.ln(8) # Spazio dopo la tabella

    # --- RIASSUNTO NOLEGGIO ---
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, "Riepilogo Noleggio:", 0, 1, 'L') # Aggiunto un titolo per la sezione
    pdf.set_font('Arial', '', 11)

    pdf.cell(60, 7, t["durata_contratto"], 0, 0, 'L')
    pdf.cell(0, 7, f"{durata} ore", 0, 1, 'L')

    pdf.cell(60, 7, t["pagamento"], 0, 0, 'L')
    pdf.cell(0, 7, metodo_pagamento, 0, 1, 'L')
    pdf.ln(5)

    # Totale
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(60, 10, t["totale"], 0, 0, 'L')
    pdf.cell(0, 10, f"Euro {importo_totale:.2f}", 0, 1, 'L')
    pdf.ln(15)

    # --- MESSAGGIO DI RINGRAZIAMENTO / NOTE LEGALI ---
    pdf.set_font('Arial', 'I', 10) # Corsivo
    pdf.multi_cell(0, 5, t["grazie"], 0, 'C')
    pdf.ln(5)

    pdf.set_font('Arial', '', 8) # Font più piccolo per note legali
    pdf.multi_cell(0, 4, t["note_legali"], 0, 'C')


    # --- SALVATAGGIO PDF ---
    current_date = datetime.now().strftime("%Y%m%d")
    receipt_filename = f"ricevuta_noleggio_{numero.replace('/', '-')}_{nome}_{cognome}_{current_date}.pdf"
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True) # Crea la directory se non esiste
    output_pdf_path = output_path / receipt_filename
    
    try:
        pdf.output(output_pdf_path)
        return str(output_pdf_path)
    except Exception as e:
        QMessageBox.critical(None, "Errore Creazione PDF", f"Impossibile creare il PDF: {e}")
        return None

def stampa_ricevuta_completa(nome, cognome, durata, metodo_pagamento, data, ora, materiali_noleggiati, lingua="italiano"):
    if not nome or not cognome or not materiali_noleggiati:
        return None, "Dati mancanti"

    importo_totale = 0
    for codice, nome_m, produttore in materiali_noleggiati:
        materiale = get_materiale_by_barcode(codice)
        if materiale:
            tipo = materiale["tipo"]
            prezzo_unitario = get_prezzo_orario_by_tipo(tipo)
            importo_totale += prezzo_unitario * durata

    anno_corrente = datetime.now().year
    numero = get_prossimo_numero_ricevuta(anno_corrente)

    try:
        path_pdf = genera_ricevuta_pdf_multilingua(
            numero, nome, cognome, materiali_noleggiati,
            data, ora, durata, metodo_pagamento, importo_totale, lingua
        )

        if not path_pdf or not Path(path_pdf).exists():
            return None, None

        for codice, _, _ in materiali_noleggiati:
            noleggio = get_noleggio_attivo_per_cliente(nome, cognome, codice)
            if noleggio:
                salva_ricevuta(numero, anno_corrente, noleggio["id"], str(path_pdf))
                aggiorna_importo_noleggio(noleggio["id"], importo_totale)
                break

        return path_pdf, numero
        
    except Exception as e:
        print(f"[ERRORE] stampa_ricevuta_completa: {e}")
        return None, None


def stampa_privacy(lingua: str, template_dir="Template_privacy") -> str:
    """
    Copia il file privacy della lingua selezionata nella cartella temporanea per la stampa.
    Apre il PDF con l'applicazione predefinita (macOS/Linux) o tenta la stampa diretta (Windows).
    Restituisce il percorso del file copiato o None se fallisce.
    """
    lingua = lingua.strip().lower()
    suffissi = {
        "italiano": "_IT.pdf",
        "nederlands": "_NL.pdf",
        "deutsch": "_DE.pdf",
        "français": "_FR.pdf",
        "english": "_EN.pdf"
    }

    suffisso = suffissi.get(lingua, "_IT.pdf")
    file_template = Path(template_dir) / f"gdpr{suffisso}"

    if not file_template.exists():
        QMessageBox.warning(None, "Template mancante", f"File non trovato: {file_template}.\nAssicurati che la cartella '{template_dir}' contenga il file '{file_template.name}'.")
        return None

    output_dir = Path("PrivacyStampate")
    output_dir.mkdir(parents=True, exist_ok=True)
    destinazione = output_dir / file_template.name

    try:
        shutil.copy(file_template, destinazione)
        
        # MODIFICA QUI: Logica di stampa aggiornata
        if os.name == 'posix': # macOS e Linux
            # 'open -p' non è supportato. Apriamo il file e l'utente dovrà stamparlo manualmente.
            os.system(f"open '{destinazione}'")
            QMessageBox.information(None, "Stampa Privacy", f"Documento privacy copiato. Si aprirà il file PDF, clicca su Stampa.")
        elif os.name == 'nt': # Windows
            # Tenta di stampare direttamente.
            os.startfile(str(destinazione), 'print')
            QMessageBox.information(None, "Stampa Privacy", f"Documento privacy copiato. Tentativo di stampa diretta.")
        else: # Altri sistemi (es. Linux con xdg-open)
            os.system(f"xdg-open '{destinazione}'")
            QMessageBox.information(None, "Stampa Privacy", f"Documento privacy copiato. Aprilo e clicca su Stampa: {destinazione}")
        
        return str(destinazione) # Restituisce il percorso del file copiato con successo
    except Exception as e:
        QMessageBox.critical(None, "Errore", f"Errore durante la copia o il tentativo di stampa:\n{e}")
        return None

    