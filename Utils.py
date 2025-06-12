# Utils.py (Aggiornato: contiene solo funzioni OCR e Camera)

import cv2
import pytesseract
from PySide6.QtWidgets import QFileDialog, QMessageBox # Mantenuto QFileDialog qui se la funzione OCR lo usa internamente


# Funzioni OCR
def processa_immagine_ocr(file_path):
    """
    Elabora un'immagine tramite OCR e restituisce un dizionario con 'nome' e 'cognome' estratti.
    Restituisce (None, messaggio_errore) in caso di problemi, altrimenti (dati_estratti, None).
    """
    if not file_path:
        return None, "Nessun file immagine fornito."

    try:
        img = cv2.imread(file_path)
        if img is None:
            return None, "Impossibile leggere l'immagine. Assicurati che il percorso sia corretto e il file non sia corrotto."
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Puoi aggiungere qui pre-processing avanzati per l'OCR se necessario (es. binarizzazione, denoising)
        # Esempio: _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        # text = pytesseract.image_to_string(thresh, lang='ita+eng')

        text = pytesseract.image_to_string(gray, lang='ita+eng') # Puoi specificare più lingue

        nome_estratto = ""
        cognome_estratto = ""
        
        lines = text.split('\n')
        nome_found = False
        cognome_found = False
        
        # Tentativo di estrazione nome/cognome con etichette esplicite
        for line in lines:
            if "nome" in line.lower() and not nome_found:
                parts = line.split(':')
                if len(parts) > 1:
                    nome_estratto = parts[1].strip()
                    nome_found = True
            if "cognome" in line.lower() and not cognome_found:
                parts = line.split(':')
                if len(parts) > 1:
                    cognome_estratto = parts[1].strip()
                    cognome_found = True
            if nome_found and cognome_found:
                break

        # Logica di fallback: estrai le prime due parole non numeriche se non trovati con etichette
        if not nome_found and not cognome_found:
            words = [word for word in text.split() if word.isalpha() and len(word) > 2] # Filtra parole lunghe e solo alfabetiche
            if len(words) >= 2:
                nome_estratto = words[0]
                cognome_estratto = words[1]
            elif len(words) == 1:
                cognome_estratto = words[0] # Se c'è solo una parola, la metto nel cognome
                
        return {'nome': nome_estratto, 'cognome': cognome_estratto}, None

    except Exception as e:
        return None, f"Errore durante l'elaborazione OCR: {e}"

# Funzioni Camera (attualmente segnaposto)
def camera_open():
    """
    Funzione segnaposto per l'apertura della camera.
    """
    print("Camera aperta (simulato).")
    pass

def camera_close():
    """
    Funzione segnaposto per la chiusura della camera.
    """
    print("Camera chiusa (simulato).")
    pass