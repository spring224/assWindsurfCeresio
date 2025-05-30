from fpdf import FPDF
import os
from datetime import datetime
from pathlib import Path



def genera_ricevuta_pdf(numero, nome, cognome, materiale, data, ora, durata, pagamento, output_dir="Ricevute_Noleggi"):

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f"Ricevuta_{numero.replace('/', '_')}.pdf"
    percorso = output_dir / filename

    filename = f"Ricevuta_{numero.replace('/', '_')}.pdf"
    percorso = os.path.join(output_dir, filename)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Ricevuta Noleggio", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(100, 10, f"N. Ricevuta: {numero}", ln=True)
    pdf.cell(100, 10, f"Data: {data} alle {ora}", ln=True)
    pdf.cell(100, 10, f"Cliente: {nome} {cognome}", ln=True)
    pdf.cell(100, 10, f"Materiale: {materiale}", ln=True)
    pdf.cell(100, 10, f"Durata: {durata} ore", ln=True)
    pdf.cell(100, 10, f"Pagamento: {pagamento}", ln=True)

    pdf.output(percorso)
    return percorso

def calcola_prossimo_numero(anno, directory="Ricevute_Noleggi"):
    os.makedirs(directory, exist_ok=True)
    count = 1
    for nome_file in os.listdir(directory):
        if nome_file.endswith(".pdf") and f"/{anno}" in nome_file.replace("_", "/"):
            count += 1
    return f"{count:02}/{anno}"

def stampa_ricevuta(self):
    from utils import genera_ricevuta_pdf
    from data_access import get_materiale_by_barcode, get_prossimo_numero_ricevuta, salva_ricevuta
    from datetime import datetime

    nome = self.txt_nome.text().strip()
    cognome = self.txt_cognome.text().strip()
    barcode = self.txt_barcode.text().strip()
    durata = self.spin_durata.value()
    pagamento = self.pagamento_scelto or "N/D"
    data = self.date_edit.date().toString("yyyy-MM-dd")
    ora = self.time_edit.time().toString("HH:mm")

    if not nome or not cognome or not barcode:
        QMessageBox.warning(self, "Dati mancanti", "Completa tutti i dati prima di stampare la ricevuta.")
        return

    materiale = get_materiale_by_barcode(barcode)
    if not materiale:
        QMessageBox.warning(self, "Errore", "Materiale non trovato.")
        return

    materiale_str = f"{materiale['tipo']} {materiale['nome']} ({materiale['produttore']})"
    anno_corrente = datetime.now().year
    numero = get_prossimo_numero_ricevuta(anno_corrente)

    path_pdf = genera_ricevuta_pdf(
        numero, nome, cognome, materiale_str,
        data, ora, durata, pagamento
    )

    # Recupera id_noleggio attivo per quel cliente+materiale+data
    from data_access import get_noleggio_attivo_per_cliente
    noleggio = get_noleggio_attivo_per_cliente(nome, cognome, barcode)
    if noleggio:
        salva_ricevuta(numero, anno_corrente, noleggio["id"], path_pdf)
        QMessageBox.information(self, "Ricevuta generata", f"Ricevuta {numero} salvata in:\n{path_pdf}")
    else:
        QMessageBox.warning(self, "Attenzione", "Ricevuta generata ma nessun noleggio attivo associato trovato.")