
import sqlite3
import os
from pathlib import Path  # ✅ nuova riga

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "gestione_dati" / "applicazionedb.db"

#def get_connection():
 #   return sqlite3.connect(DB_PATH)

def get_connection():
    full_path = os.path.abspath(DB_PATH)
    #print("🚨 DATABASE USATO:", full_path)
    return sqlite3.connect(DB_PATH)

def get_all_soci():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, cognome, email, quota_pagata, anno, attivo, foto FROM soci")
    results = cursor.fetchall()
    conn.close()
    return results

def insert_socio(nome, cognome, email, quota_pagata):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO soci (nome, cognome, email, quota_pagata) VALUES (?, ?, ?, ?)",
        (nome, cognome, email, int(quota_pagata))
    )
    conn.commit()
    conn.close()

def insert_socio_esteso(dati):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO soci (
            nome, cognome, indirizzo, telefono, email,
            data_nascita, luogo_nascita, codice_fiscale,
            quota_pagata, quota_associazione, anno, attivo, foto
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            dati["nome"],
            dati["cognome"],
            dati["indirizzo"],
            dati["telefono"],
            dati["email"],
            dati["data_nascita"],
            dati["luogo_nascita"],
            dati["codice_fiscale"],
            0,  # quota_pagata default
            0.0,  # quota_associazione default
            dati["anno"],
            dati["attivo"],
            dati["foto"]
        )
    )
    conn.commit()
    conn.close()

def update_socio(id_socio, nome, cognome, email, quota_pagata):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE soci SET nome = ?, cognome = ?, email = ?, quota_pagata = ? WHERE id = ?",
        (nome, cognome, email, int(quota_pagata), int(id_socio))
    )
    conn.commit()
    conn.close()

def get_socio_by_id(id_socio):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM soci WHERE id = ?", (id_socio,))
    row = cursor.fetchone()
    conn.close()

    if row:
        columns = ["id", "nome", "cognome", "indirizzo", "telefono", "email", "data_nascita",
                   "codice_fiscale", "quota_pagata", "quota_associazione", "foto", "attivo", "anno", "luogo_nascita"]
        return dict(zip(columns, row))
    else:
        return None
    
def update_socio_esteso(id_socio, dati):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE soci
        SET nome = ?, cognome = ?, indirizzo = ?, telefono = ?, email = ?, 
            data_nascita = ?, codice_fiscale = ?, anno = ?, luogo_nascita = ?, foto = ?
        WHERE id = ?
    """, (
        dati["nome"], dati["cognome"], dati["indirizzo"], dati["telefono"], dati["email"],
        dati["data_nascita"], dati["codice_fiscale"], dati["anno"], dati["luogo_nascita"], dati["foto"],
        id_socio
    ))
    conn.commit()
    conn.close()
    
# Funzioni placeholder per futuro utilizzo
def update_socio(id_socio, nome, cognome, email, quota_pagata):
    pass

def delete_socio(id_socio):
    pass

def mark_quota_pagata(id_socio, stato=True):
    pass

def get_socio_photo_blob(id_socio):
    pass

def save_socio_photo_blob(id_socio, blob_data):
    pass


def inserisci_materiale(codice, tipo, nome, produttore, provenienza, descrizione, note, barcode, rig, foto_blob):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO materiali (
            codice, tipo, nome, produttore, provenienza, 
            descrizione, note, barcode, rig, foto
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        codice, tipo, nome, produttore, provenienza,
        descrizione, note, barcode, rig,
        sqlite3.Binary(foto_blob) if foto_blob else None
    ))
    conn.commit()
    conn.close()





def elimina_materiale(id_materiale):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM materiali WHERE id = ?', (id_materiale,))
    conn.commit()
    conn.close()


def carica_materiali():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, codice, tipo, nome, produttore, provenienza, descrizione, note, barcode, rig FROM materiali')
    risultati = cursor.fetchall()
    conn.close()
    return risultati


def carica_materiali_per_tipo(tipo):
    conn = get_connection()
    cursor = conn.cursor()
    #cursor.execute("PRAGMA table_info(materiali)")
    #cols = cursor.fetchall()
    #for col in cols:
     # print("➤ Colonna trovata:", col[1])
    cursor.execute('SELECT * FROM materiali WHERE tipo = ?', (tipo,))
    risultati = cursor.fetchall()
    conn.close()
    return risultati

def carica_materiali_rig():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM materiali WHERE rig = 1')
    risultati = cursor.fetchall()
    conn.close()
    return risultati

def recupera_foto_materiale(id_materiale):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT foto FROM materiali WHERE id = ?", (id_materiale,))
    risultato = cursor.fetchone()
    conn.close()
    if risultato and risultato[0]:
        return risultato[0]  # BLOB
    return None

def get_materiale_by_id(id_materiale):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM materiali WHERE id = ?", (id_materiale,))
    result = cursor.fetchone()
    conn.close()
    return result

#Sezione Gestione Noleggi

def inserisci_noleggio(nome, cognome, id_materiale, codice_materiale, data, ora, durata, doc_path, lingua):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Noleggi 
        (nome_cliente, cognome_cliente, id_materiale, codice_materiale, data_inizio, ora_inizio, durata_ore, percorso_documento, lingua_privacy)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (nome, cognome, id_materiale, codice_materiale, data, ora, durata, doc_path, lingua))
    conn.commit()
    conn.close()
    aggiorna_disponibilita_materiale(id_materiale, 0)

def aggiorna_disponibilita_materiale(id_materiale, disponibile):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE Materiali SET disponibile = ? WHERE id = ?', (disponibile, id_materiale))
    conn.commit()
    conn.close()

def get_materiale_by_barcode(barcode):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Materiali WHERE codice_barre = ?", (barcode,))
    result = cursor.fetchone()
    conn.close()
    return dict(result) if result else None

def aggiorna_disponibilita_materiale(id_materiale, disponibile):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Materiali SET disponibile = ? WHERE id = ?", (disponibile, id_materiale))
    conn.commit()
    conn.close()

def inserisci_noleggio(nome, cognome, id_materiale, codice_materiale,
                       data, ora, durata, percorso_documento, lingua, pagamento):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Noleggi (
            nome_cliente, cognome_cliente, id_materiale, codice_materiale,
            data_inizio, ora_inizio, durata_ore, percorso_documento,
            lingua_privacy, metodo_pagamento, stato
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'attivo')
    """, (nome, cognome, id_materiale, codice_materiale, data, ora, durata,
          percorso_documento, lingua, pagamento))
    conn.commit()
    conn.close()

    #Situazione Noleggi

def get_noleggi_attivi():
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()   
        cursor.execute("SELECT * FROM Noleggi WHERE stato = 'attivo'")
        righe = cursor.fetchall()
        conn.close()
        return righe

def chiudi_noleggio(id_noleggio, id_materiale):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Noleggi SET stato = 'chiuso' WHERE id = ?", (id_noleggio,))
    cursor.execute("UPDATE Materiali SET disponibile = 1 WHERE id = ?", (id_materiale,))
    conn.commit()
    conn.close()

def salva_ricevuta(numero, anno, id_noleggio, percorso_pdf):
    from datetime import datetime
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Ricevute (numero, anno, id_noleggio, percorso_pdf, data_creazione)
        VALUES (?, ?, ?, ?, ?)
    """, (numero, anno, id_noleggio, percorso_pdf, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_prossimo_numero_ricevuta(anno):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Ricevute WHERE anno = ?", (anno,))
    count = cursor.fetchone()[0] + 1
    conn.close()
    return f"{count:02}/{anno}"

def get_noleggio_attivo_per_cliente(nome, cognome, codice_materiale):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM Noleggi
        WHERE nome_cliente = ? AND cognome_cliente = ? AND codice_materiale = ? AND stato = 'attivo'
        ORDER BY id DESC LIMIT 1
    """, (nome, cognome, codice_materiale))
    result = cursor.fetchone()
    conn.close()
    return result

def carica_listino():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM ListinoNoleggio ORDER BY tipo")
    risultati = cur.fetchall()
    conn.close()
    return risultati

def salva_listino(lista_voci):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM ListinoNoleggio")
        for voce in lista_voci:
            tipo, descrizione, prezzo = voce
            cur.execute("""
                INSERT INTO ListinoNoleggio (tipo, descrizione, prezzo_orario)
                VALUES (?, ?, ?)
            """, (tipo, descrizione, prezzo))
        conn.commit()
        return True, ""
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def get_prezzo_orario_by_tipo(tipo):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT prezzo_orario FROM ListinoNoleggio WHERE tipo = ?", (tipo,))
    row = cur.fetchone()
    conn.close()
    return row["prezzo_orario"] if row else 0.0

def aggiorna_importo_noleggio(id_noleggio, importo):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE Noleggi SET importo_calcolato = ? WHERE id = ?", (importo, id_noleggio))
    conn.commit()
    conn.close()