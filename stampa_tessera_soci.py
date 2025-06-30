# stampa_tessera_soci.py

import os
from PySide6.QtWidgets import QMessageBox
from PySide6.QtGui import QPixmap # Necessario per convertire BLOB in Pixmap
from PySide6.QtCore import QBuffer, QIODevice # Necessario per convertire Pixmap in BytesIO

from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, black
from reportlab.lib.utils import ImageReader
import qrcode
from PIL import Image as PilImage
from io import BytesIO

# Importa la funzione get_socio_photo_blob e get_socio_by_id da data_access
from data_access import get_socio_by_id, get_socio_photo_blob

# Definizione della directory per le foto dei soci (deve esistere)
FOTO_SOCI_DIR = os.path.join(os.path.dirname(__file__), "foto_soci")

def stampa_tessera_pdf(socio_id, parent_widget=None):
    CARD_WIDTH = 85.6 * mm
    CARD_HEIGHT = 53.98 * mm
    ORANGE_DUTCH = HexColor('#FF7F00')
    LOGO_PATH = os.path.join(os.path.dirname(__file__), "logo_onda.png") # Percorso assoluto

    socio = get_socio_by_id(socio_id)
    if not socio:
        QMessageBox.warning(parent_widget, "Errore", "Socio non trovato nel database. Impossibile stampare la tessera.")
        return

    os.makedirs("tessere_associati", exist_ok=True)
    output_filename = os.path.join("tessere_associati", f"tessera_{socio['nome']}_{socio['cognome']}_{socio['id']}.pdf")
    
    try:
        c = canvas.Canvas(output_filename, pagesize=(CARD_WIDTH, CARD_HEIGHT))

        # Logo
        try:
            if os.path.exists(LOGO_PATH):
                logo = ImageReader(LOGO_PATH)
                logo_width = CARD_WIDTH * 0.35
                logo_height = logo_width * (logo.getSize()[1] / logo.getSize()[0])
                c.drawImage(logo, 5 * mm, CARD_HEIGHT - logo_height - 5 * mm, width=logo_width, height=logo_height, mask='auto')
            else:
                c.setFont('Helvetica-Bold', 10)
                c.drawString(5 * mm, CARD_HEIGHT - 15 * mm, "LOGO MANCANTE")
        except Exception as e:
            print(f"Errore caricamento logo: {e}")
            c.setFont('Helvetica-Bold', 10)
            c.drawString(5 * mm, CARD_HEIGHT - 15 * mm, "ERRORE LOGO")

        # Dati socio
        text_x = 5 * mm
        text_y = CARD_HEIGHT - 30 * mm
        c.setFont('Helvetica-Bold', 8)
        c.drawString(text_x, text_y, "Numero Tessera:")
        c.setFont('Helvetica', 8)
        c.drawString(text_x + 25 * mm, text_y, str(socio.get('numero_tessera', 'N/A')))

        text_y -= 5 * mm
        c.setFont('Helvetica-Bold', 8)
        c.drawString(text_x, text_y, "Nome Associato:")
        c.setFont('Helvetica', 8)
        c.drawString(text_x + 25 * mm, text_y, f"{socio.get('nome', '')} {socio.get('cognome', '')}")

        text_y -= 5 * mm
        c.setFont('Helvetica-Bold', 8)
        c.drawString(text_x, text_y, "Anno Validità:")
        c.setFont('Helvetica', 8)
        c.drawString(text_x + 25 * mm, text_y, str(socio.get('anno', 'N/A'))) 

        text_y -= 5 * mm
        c.setFont('Helvetica-Bold', 8)
        c.drawString(text_x, text_y, "Scadenza:")
        c.setFont('Helvetica', 8)
        c.drawString(text_x + 25 * mm, text_y, socio.get('data_scadenza', 'N/A')) 

        # Foto Socio (carica dal BLOB, non da percorso file)
        photo_x = CARD_WIDTH - 25 * mm - 5 * mm
        photo_y = CARD_HEIGHT - 28 * mm - 5 * mm
        photo_width = 20 * mm
        photo_height = 28 * mm
        
        photo_blob = get_socio_photo_blob(socio_id) # Ottieni il BLOB direttamente
        if photo_blob:
            try:
                pixmap = QPixmap()
                pixmap.loadFromData(photo_blob)
                
                buffer = QBuffer()
                buffer.open(QIODevice.WriteOnly)
                pixmap.save(buffer, "PNG") # Salva come PNG per mantenere trasparenza se presente
                img_bytes = BytesIO(buffer.data())
                buffer.close() # Chiudi il buffer dopo averne copiato i dati
                img_bytes.seek(0) # Riposiziona il cursore all'inizio del buffer

                photo_image = ImageReader(img_bytes)
                c.drawImage(photo_image, photo_x, photo_y, width=photo_width, height=photo_height, preserveAspectRatio=True)
            except Exception as e:
                print(f"Errore caricamento foto socio da BLOB per PDF: {e}")
                c.rect(photo_x, photo_y, photo_width, photo_height)
                c.setFont('Helvetica', 6)
                c.setFillColor(black)
                c.drawCentredString(photo_x + photo_width / 2, photo_y + photo_height / 2 - 2 * mm, "Errore")
                c.drawCentredString(photo_x + photo_width / 2, photo_y + photo_height / 2 - 5 * mm, "Foto")
        else:
            c.rect(photo_x, photo_y, photo_width, photo_height)
            c.setFont('Helvetica', 6)
            c.setFillColor(black)
            c.drawCentredString(photo_x + photo_width / 2, photo_y + photo_height / 2 - 2 * mm, "Spazio")
            c.drawCentredString(photo_x + photo_width / 2, photo_y + photo_height / 2 - 5 * mm, "Foto Socio (non presente)")

        # QR code
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=3,
                border=2,
            )
            qr_data = (f"Numero Tessera: {socio.get('numero_tessera', 'N/A')}\n"
                       f"Nome: {socio.get('nome', '')} {socio.get('cognome', '')}\n"
                       f"Anno: {socio.get('anno', 'N/A')}\n"
                       f"Scadenza: {socio.get('data_scadenza', 'N/A')}")
            qr.add_data(qr_data)
            qr.make(fit=True)
            qr_img = qr.make_image(image_factory=PilImage)
            img_bytes = BytesIO()
            qr_img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            qr_image = ImageReader(img_bytes)
            qr_size = 15 * mm
            c.drawImage(qr_image, CARD_WIDTH - qr_size - 5 * mm, 5 * mm, width=qr_size, height=qr_size)
        except Exception as e:
            print(f"Errore generazione QR code: {e}")
            c.setFont('Helvetica-Bold', 8)
            c.setFillColor(black)
            c.drawString(CARD_WIDTH - 30 * mm, 15 * mm, "QR CODE")
            c.drawString(CARD_WIDTH - 30 * mm, 10 * mm, "MANCANTE")

        # Bordo arancione
        c.setStrokeColor(ORANGE_DUTCH)
        c.setLineWidth(0.5 * mm)
        c.rect(0.5 * mm, 0.5 * mm, CARD_WIDTH - 1 * mm, CARD_HEIGHT - 1 * mm)

        c.save()
        QMessageBox.information(parent_widget, "PDF generato", f"Tessera salvata in:\n{output_filename}")
    except Exception as e:
        QMessageBox.critical(parent_widget, "Errore Stampa Tessera", f"Errore durante la generazione o il salvataggio della tessera PDF: {e}")
        print(f"Errore dettagliato stampa_tessera_pdf: {e}")