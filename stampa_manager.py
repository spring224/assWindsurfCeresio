import os
import shutil
from pathlib import Path
from fpdf import FPDF
from datetime import datetime
from PySide6.QtWidgets import QMessageBox
from data_access import (
        get_materiale_by_barcode,
        get_prezzo_orario_by_tipo,
        get_prossimo_numero_ricevuta,
        salva_ricevuta,
        get_noleggio_attivo_per_cliente,
        aggiorna_importo_noleggio
    )

# --- COSTANTI GLOBALI PER LE DIRECTORY DI OUTPUT ---
RICEVUTE_OUTPUT_DIR = "Ricevute_Noleggi"
PRIVACY_OUTPUT_DIR = "PrivacyStampate"
# ---------------------------------------------------

def gestisci_stampa_ricevuta(
    nome_cliente,
    cognome_cliente,
    materiali_noleggiati_list,
    data_noleggio,
    ora_noleggio,
    durata_ore,
    metodo_pagamento,
    importo_totale,
    lingua,
    id_noleggio_corrente,
    numero_ricevuta_completo
):
    """
    Gestisce la logica per la generazione e il tentativo di stampa della ricevuta.
    Accetta tutti i dati necessari come argomenti.
    """
    
    # DEBUG: Dati ricevuti in gestisci_stampa_ricevuta
    print("\n--- DEBUG: Dati ricevuti in gestisci_stampa_ricevuta ---")
    print(f"Nome Cliente: {nome_cliente}")
    print(f"Cognome Cliente: {cognome_cliente}")
    print(f"Materiali Noleggiati: {materiali_noleggiati_list}")
    print(f"Data Noleggio: {data_noleggio}")
    print(f"Ora Noleggio: {ora_noleggio}")
    print(f"Durata Ore: {durata_ore}")
    print(f"Metodo Pagamento: {metodo_pagamento}")
    print(f"Importo Totale: {importo_totale}")
    print(f"Lingua: {lingua}")
    print(f"ID Noleggio Corrente: {id_noleggio_corrente}")
    print(f"Numero Ricevuta Completo: {numero_ricevuta_completo}")
    print("--------------------------------------------------\n")


    # Chiamata a genera_ricevuta_pdf_multilingua con TUTTI i parametri necessari
    output_pdf_path = genera_ricevuta_pdf_multilingua(
        nome_cliente,
        cognome_cliente,
        materiali_noleggiati_list,
        data_noleggio,
        ora_noleggio,
        durata_ore,
        metodo_pagamento,
        importo_totale,
        lingua,
        id_noleggio_corrente,
        numero_ricevuta_completo,
        datetime.now().year,        # 12° parametro: Anno corrente
        RICEVUTE_OUTPUT_DIR         # 13° parametro: Directory di output
    )

    # --- Apertura/Stampa del PDF (la tua logica esistente) ---
    print(f"DEBUG: output_pdf_path = {output_pdf_path}")
    if output_pdf_path:
        QMessageBox.information(None, "Ricevuta", f"Ricevuta salvata: {output_pdf_path}")
        print(f"DEBUG sono nell IF")
        try:
            if os.name == 'posix': # macOS e Linux
                os.system(f"open '{output_pdf_path}'")
                QMessageBox.information(None, "Stampa Ricevuta", f"La ricevuta si aprirà in una nuova finestra. Clicca su Stampa.")
            elif os.name == 'nt': # Windows
                os.startfile(output_pdf_path, 'print')
                QMessageBox.information(None, "Stampa Ricevuta", f"Tentativo di stampa diretta della ricevuta.")
            return True
        except Exception as e:
            QMessageBox.warning(None, "Errore Stampa", f"Errore durante l'apertura/stampa della ricevuta: {e}")
    else:
        QMessageBox.critical(None, "Errore Generazione Ricevuta", "Impossibile generare la ricevuta PDF.")


def genera_ricevuta_pdf_multilingua(
    # Quelli che erano i tuoi 11 parametri, più due nuovi
    nome_per_pdf,
    cognome_per_pdf,
    materiali_per_pdf,
    data_per_pdf,
    ora_per_pdf,
    durata_per_pdf,
    metodo_pagamento_per_pdf,
    importo_totale,
    lingua_per_pdf,
    id_noleggio_associato,
    numero_ricevuta_testo,
    anno_ricevuta_da_testo,     # Questo è il 12° parametro (anno)
    output_folder_path          # Questo è il 13° parametro (path cartella)
):
    """
    Genera un PDF di ricevuta noleggio multilingua usando FPDF.
    """
    # --- NON CREARE output_dir QUI, USIAMO output_folder_path DAL PARAMETRO ---
    output_directory = Path(output_folder_path) # Converti la stringa in oggetto Path
    output_directory.mkdir(parents=True, exist_ok=True) # Crea la directory se non esiste

    # Impostazioni generali del PDF
    pdf = FPDF('P', 'mm', 'A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font('helvetica', '', 10)

    # Dictionary per traduzioni
    translations = {
        'italiano': {
            'receipt_n': 'Ricevuta N.:',
            'issue_date': 'Data Emissione:',
            'issue_time': 'Ora Emissione:',
            'client': 'Cliente:',
            'rented_materials': 'Materiali Noleggiati:',
            'code': 'Codice',
            'material_name': 'Nome Materiale',
            'type': 'Tipo',
            'manufacturer': 'Produttore',
            'rental_summary': 'Riepilogo Noleggio:',
            'contract_duration': 'Durata Contratto:',
            'payment_type': 'Tipo di Pagamento:',
            'total': 'Totale:',
            'hours': 'ore',
            'thank_you': 'Grazie per aver scelto Windsurf Ceresio!',
            'address': 'Via Caduti In Guerra, 18 - 22018 Porlezza (CO)',
            'fiscal_code': 'Codice Fiscale:',
            'tel': 'Tel:',
            'email': 'Email:'
        },
        'inglese': {
            'receipt_n': 'Receipt No.:',
            'issue_date': 'Issue Date:',
            'issue_time': 'Issue Time:',
            'client': 'Client:',
            'rented_materials': 'Rented Materials:',
            'code': 'Code',
            'material_name': 'Material Name',
            'type': 'Type',
            'manufacturer': 'Manufacturer',
            'rental_summary': 'Rental Summary:',
            'contract_duration': 'Contract Duration:',
            'payment_type': 'Payment Type:',
            'total': 'Total:',
            'hours': 'hours',
            'thank_you': 'Thank you for choosing Windsurf Ceresio!',
            'address': 'Via Caduti In Guerra, 18 - 22018 Porlezza (CO)',
            'fiscal_code': 'Fiscal Code:',
            'tel': 'Tel:',
            'email': 'Email:'
        }
    }
    lang = translations.get(lingua_per_pdf.lower(), translations['italiano']) # Default italiano

    # Intestazione con logo (se hai un logo in "immagini/logo.png")
    # try:
    #     if os.path.exists('immagini/logo.png'):
    #         pdf.image('immagini/logo.png', x=10, y=8, w=30)
    #     else:
    #         print("Logo non trovato: immagini/logo.png")
    # except Exception as e:
    #     print(f"Errore caricamento logo: {e}")

    pdf.set_xy(50, 10)
    pdf.set_font('helvetica', 'B', 12)
    pdf.multi_cell(0, 5, 'ASD CIRCOLO NAUTICO\nALL SPORT CERESIO PORLEZZA', align='C')
    pdf.ln(5)

    # Titolo del documento
    pdf.set_font('helvetica', 'B', 16)
    pdf.cell(0, 10, 'Ricevuta Noleggio Materiale', 0, 1, 'C')
    pdf.ln(10)

    # Dati Ricevuta
    pdf.set_font('helvetica', '', 10)
    pdf.cell(50, 7, lang['receipt_n'], 0, 0, 'L')
    pdf.set_font('helvetica', 'B', 10)
    pdf.cell(0, 7, f"{numero_ricevuta_testo}", 0, 1, 'L')

    pdf.set_font('helvetica', '', 10)
    pdf.cell(50, 7, lang['issue_date'], 0, 0, 'L')
    pdf.set_font('helvetica', 'B', 10)
    pdf.cell(0, 7, datetime.now().strftime('%Y-%m-%d'), 0, 1, 'L')

    pdf.set_font('helvetica', '', 10)
    pdf.cell(50, 7, lang['issue_time'], 0, 0, 'L')
    pdf.set_font('helvetica', 'B', 10)
    pdf.cell(0, 7, datetime.now().strftime('%H:%M:%S'), 0, 1, 'L')
    pdf.ln(5)

    # Dati Cliente
    pdf.set_font('helvetica', '', 10)
    pdf.cell(0, 7, lang['client'], 0, 1, 'L')
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(0, 7, f"{nome_per_pdf} {cognome_per_pdf}", 0, 1, 'L')
    pdf.ln(5)

    # Dettagli Materiali Noleggiati (Tabella)
    pdf.set_font('helvetica', '', 10)
    pdf.cell(0, 7, lang['rented_materials'], 0, 1, 'L')
    pdf.ln(2)

    # Intestazione tabella materiali
    pdf.set_fill_color(200, 220, 255)
    pdf.set_font('helvetica', 'B', 9)
    pdf.cell(30, 7, lang['code'], 1, 0, 'C', 1)
    pdf.cell(60, 7, lang['material_name'], 1, 0, 'C', 1)
    pdf.cell(40, 7, lang['type'], 1, 0, 'C', 1)
    pdf.cell(60, 7, lang['manufacturer'], 1, 1, 'C', 1)

    # Dati materiali
    pdf.set_font('helvetica', '', 9)
    for material_id, codice, nome, tipo, produttore, descrizione in materiali_per_pdf:
        pdf.cell(30, 7, codice, 1, 0, 'C')
        pdf.cell(60, 7, nome, 1, 0, 'L')
        pdf.cell(40, 7, tipo, 1, 0, 'L')
        pdf.cell(60, 7, produttore, 1, 1, 'L')
    pdf.ln(5)

    # Riepilogo Noleggio
    pdf.set_font('helvetica', '', 10)
    pdf.cell(0, 7, lang['rental_summary'], 0, 1, 'L')
    pdf.ln(2)

    pdf.cell(60, 7, lang['contract_duration'], 0, 0, 'L')
    pdf.set_font('helvetica', 'B', 10)
    pdf.cell(0, 7, f"{durata_per_pdf} {lang['hours']}", 0, 1, 'L')

    pdf.set_font('helvetica', '', 10)
    pdf.cell(60, 7, lang['payment_type'], 0, 0, 'L')
    pdf.set_font('helvetica', 'B', 10)
    pdf.cell(0, 7, f"{metodo_pagamento_per_pdf if metodo_pagamento_per_pdf else 'N/A'}", 0, 1, 'L') # Gestisce N/A

    pdf.set_font('helvetica', '', 10)
    pdf.cell(60, 7, lang['total'], 0, 0, 'L')
    pdf.set_font('helvetica', 'B', 14)
    pdf.cell(0, 7, f"Euro {importo_totale:.2f}", 0, 1, 'L') # Formatta l'importo

    pdf.ln(10)

    # Messaggio di ringraziamento
    pdf.set_font('helvetica', 'I', 10)
    pdf.cell(0, 7, lang['thank_you'], 0, 1, 'C')
    pdf.ln(10)

    # Dati aziendali in fondo alla pagina (sempre gli stessi)
    pdf.set_font('helvetica', '', 8)
    pdf.cell(0, 4, 'Associazione Sportiva Dilettantistica Circolo Nautico All Sport Ceresio', 0, 1, 'C')
    pdf.cell(0, 4, lang['address'], 0, 1, 'C')
    pdf.cell(0, 4, f"{lang['fiscal_code']} CRTGLG71R05F712P", 0, 1, 'C')
    pdf.cell(0, 4, f"{lang['tel']} +39 031 XXXXXX | {lang['email']} windsurfporlezza@gmail.com", 0, 1, 'C')

    # Costruisci il percorso completo del file PDF
    # Modifica qui: assicurati che la data sia pulita da slash prima di usarla nel nome del file
    data_noleggio_pulita_per_nome_file = data_per_pdf.  replace("/", "-")
    file_name = f"ricevuta_noleggio_{numero_ricevuta_testo.replace('/', '-')}_{nome_per_pdf.replace(' ', '')}_{cognome_per_pdf.replace(' ', '')}_{data_noleggio_pulita_per_nome_file}.pdf"
    pdf_path = output_directory / file_name # Usa la directory di output corretta
    pdf.output(str(pdf_path)) # Salva il PDF
    
    print(f"--- DEBUG (genera_ricevuta_pdf_multilingua): debug per nome file ---")
    print(f"  numero_ricevuta_testo: {numero_ricevuta_testo} (tipo: {type(numero_ricevuta_testo)})")
    print(f"  nome_per_pdf: {nome_per_pdf} (tipo: {type(nome_per_pdf)})")
    print(f"  cognome_per_pdf: {cognome_per_pdf} (tipo: {type(cognome_per_pdf)})")
    print(f"  data_noleggio_pulita_per_nome_file: {data_noleggio_pulita_per_nome_file} (tipo: {type(data_noleggio_pulita_per_nome_file)})")
    print(f"  PDF_PATH: {pdf_path}")


    return str(pdf_path) # Restituisci il percorso completo del PDF generato


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

    
