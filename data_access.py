
import sqlite3
import os
from pathlib import Path  # ✅ nuova riga
from datetime import datetime

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


def inserisci_materiale(dati):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO materiali (codice, tipo, nome, produttore, provenienza, descrizione, note, codice_barre, foto_path, rig) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", dati)
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
    # MODIFICA QUI: Elenco esplicito di TUTTE le 14 colonne nell'ordine del tuo schema.
    cursor.execute("""
        SELECT id, codice, tipo, nome, produttore, provenienza, descrizione, note,
               codice_barre, foto_path, disponibile, barcode, rig, foto
        FROM materiali
    """)
    materiali = cursor.fetchall()
    conn.close()
    return materiali


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

def get_materiali_disponibili():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, codice, nome, tipo, produttore ,descrizione , note FROM materiali WHERE disponibile = 1")
    rows = cursor.fetchall()
    return [
        {
            "id": r[0],
            "codice": r[1],
            "nome": r[2],
            "tipo": r[3],
            "produttore": r[4],
            "descrizione": r[5],
            "note": r[6]
        }
        for r in rows
    ]

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

def get_materiale_by_id(materiale_id: int) -> dict:
    """
    Recupera un materiale dal database dato il suo ID.
    :param materiale_id: L'ID del materiale.
    :return: Un dizionario con i dati del materiale o None se non trovato.
    """
    conn = None
    try:
        conn = get_connection()
        conn.row_factory = sqlite3.Row # Per accedere ai risultati come dizionari
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Materiali WHERE id = ?", (materiale_id,))
        materiale_row = cursor.fetchone()
        if materiale_row:
            return dict(materiale_row)
        return None
    except sqlite3.Error as e:
        print(f"ERRORE (data_access): Errore nel recupero materiale per ID {materiale_id}: {e}")
        return None
    finally:
        if conn:
            conn.close()

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

def get_materiale_by_barcode(codice):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, codice, nome, tipo, produttore, descrizione, note FROM materiali WHERE codice = ?", (codice,))
    result = cursor.fetchone()
    conn.close()

    if result:
        # Costruiamo il dizionario esplicitamente usando i nomi delle colonne.
        # c.description contiene una tupla di 7-elementi per ogni colonna (nome, tipo_db, ecc.)
        # Estraiamo solo il nome della colonna (l'elemento 0 di ogni tupla)
        columns = [description[0] for description in cursor.description]
        
        # Creiamo un dizionario zippando i nomi delle colonne con i valori della riga
        # Questo garantisce un dizionario standard Python
        return dict(zip(columns, result))
    else:
        return None # Ritorna None se il materiale non è trovato

    #Situazione Noleggi

def get_noleggi_attivi() -> list:
    """
    Recupera tutti i noleggi attivi con i dettagli dei materiali associati.
    Un noleggio è considerato attivo se stato = 'attivo' nella tabella Noleggi.
    :return: Una lista di dizionari, dove ogni dizionario rappresenta un noleggio
             e include una lista dei suoi materiali.
    """
    conn = None
    noleggi_attivi = []
    try:
        conn = get_connection()
        conn.row_factory = sqlite3.Row # Per accedere ai risultati come dizionari
        cursor = conn.cursor()

        # Query CORRETTA con il nome della tabella 'dettagli_noleggio'
        sql_query = """
            SELECT 
                n.id AS noleggio_id,
                n.nome_cliente,
                n.cognome_cliente,
                n.data_noleggio,
                n.ora_inizio,
                n.durata_ore,
                n.metodo_pagamento,
                n.importo_totale,
                n.lingua,
                n.percorso_documento AS percorso_documento_privacy,
                dn.id_materiale,
                dn.codice_materiale
            FROM Noleggi n
            LEFT JOIN dettagli_noleggio dn ON n.id = dn.id_noleggio -- *** CORREZIONE QUI: dettagli_noleggio (singolare) ***
            WHERE n.stato = 'attivo'
            ORDER BY n.id, dn.id_materiale;
        """
        
        print(f"DEBUG (data_access): Esecuzione query: {sql_query}")
        cursor.execute(sql_query)

        rows = cursor.fetchall()
        
        # Raggruppa i dati per noleggio
        noleggi_map = {}
        for row in rows:
            noleggio_id = row['noleggio_id']
            if noleggio_id not in noleggi_map:
                noleggi_map[noleggio_id] = {
                    "id": noleggio_id,
                    "nome_cliente": row['nome_cliente'],
                    "cognome_cliente": row['cognome_cliente'],
                    "data_noleggio": row['data_noleggio'],
                    "ora_inizio": row['ora_inizio'],
                    "durata_ore": row['durata_ore'],
                    "metodo_pagamento": row['metodo_pagamento'],
                    "importo_totale": row['importo_totale'],
                    "lingua": row['lingua'],
                    "percorso_documento_privacy": row['percorso_documento_privacy'],
                    "materiali": [] # Lista per i materiali associati
                }
            
            # Aggiungi i dettagli del materiale solo se esistono (LEFT JOIN)
            if row['id_materiale'] is not None:
                materiale_info = {
                    "id_materiale": row['id_materiale'],
                    "codice": row['codice_materiale'],
                    "nome": get_materiale_by_id(row['id_materiale']).get('nome', 'Materiale Sconosciuto')
                }
                noleggi_map[noleggio_id]["materiali"].append(materiale_info)
            
        noleggi_attivi = list(noleggi_map.values())
        print(f"DEBUG (data_access): Recuperati {len(noleggi_attivi)} noleggi attivi.")
        return noleggi_attivi

    except sqlite3.Error as e:
        print(f"ERRORE CRITICO (data_access - get_noleggi_attivi): Errore SQL: {e}")
        return []
    finally:
        if conn:
            conn.close()

def chiudi_noleggio(noleggio_id: int) -> bool:
    """
    Chiude un noleggio e libera i materiali associati.
    :param noleggio_id: L'ID del noleggio da chiudere.
    :return: True se l'operazione ha successo, False altrimenti.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # 1. Aggiorna lo stato del noleggio a 'chiuso'
        cursor.execute("""
            UPDATE Noleggi
            SET stato = 'chiuso'
            WHERE id = ?
        """, (noleggio_id,))
        
        # 2. Recupera tutti gli ID dei materiali associati a questo noleggio dalla tabella dettagli_noleggio
        cursor.execute("""
            SELECT id_materiale FROM dettagli_noleggio WHERE id_noleggio = ?
        """, (noleggio_id,))
        material_ids_to_release = cursor.fetchall()

        # 3. Per ogni materiale, aggiorna la sua disponibilità a 1 (disponibile)
        for row in material_ids_to_release:
            materiale_id = row['id_materiale'] # Accedi come dizionario grazie a row_factory
            if not aggiorna_disponibilita_materiale_by_id(materiale_id, 1): # 1 significa 'disponibile'
                print(f"ATTENZIONE: Impossibile aggiornare la disponibilità per il materiale ID {materiale_id} del noleggio {noleggio_id}.")
                # Potresti voler gestire questo errore in modo più robusto, es. rollback o log.
        
        conn.commit() # Commit finale dopo tutte le operazioni
        print(f"DEBUG (data_access - chiudi_noleggio): Noleggio ID {noleggio_id} chiuso e materiali liberati.")
        return True
    except sqlite3.Error as e:
        print(f"ERRORE (data_access - chiudi_noleggio): Errore nella chiusura del noleggio {noleggio_id} o liberazione materiali: {e}")
        conn.rollback() # Esegue il rollback in caso di errore
        return False
    finally:
        if conn:
            conn.close()



def salva_ricevuta(
    numero_ricevuta_prog_int,  # Valore per la colonna 'numero_ricevuta' (es. 1)
    anno_ricevuta_prog_int,    # Valore per la colonna 'anno_ricevuta' (es. 2024)
    nome_cliente,
    cognome_cliente,
    data_creazione_str,    # Valore per la colonna 'data_creazione' (es. "2025-06-11")
    ora_ricevuta_str,      # Valore per la colonna 'ora_ricevuta' (es. "09:47")
    durata_ore,
    metodo_pagamento,
    importo_totale,
    percorso_file_pdf,
    id_noleggio_associato, # Valore per la colonna 'id_noleggio'
    numero_ricevuta_testo, # Valore per la colonna 'numero' (es. "0001/2024")
    anno_ricevuta_da_testo # Valore per la colonna 'anno' (l'anno numerico dalla stringa "0001/2024")
): 
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute('''
            INSERT INTO Ricevute (
                numero,           
                anno,             
                percorso_pdf,
                id_noleggio,
                data_creazione,   
                nome_cliente,
                cognome_cliente,
                durata_ore,
                metodo_pagamento,
                importo_totale,
                numero_ricevuta,  
                anno_ricevuta,    
                ora_ricevuta      
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            numero_ricevuta_testo,     # -> numero TEXT
            anno_ricevuta_da_testo,    # -> anno INTEGER
            percorso_file_pdf,         # -> percorso_pdf TEXT
            id_noleggio_associato,     # -> id_noleggio INTEGER
            data_creazione_str,        # -> data_creazione TEXT
            nome_cliente,              # -> nome_cliente TEXT
            cognome_cliente,           # -> cognome_cliente TEXT
            durata_ore,                # -> durata_ore INTEGER
            metodo_pagamento,          # -> metodo_pagamento TEXT
            importo_totale,            # -> importo_totale REAL
            numero_ricevuta_prog_int,  # -> numero_ricevuta INTEGER
            anno_ricevuta_prog_int,    # -> anno_ricevuta INTEGER
            ora_ricevuta_str           # -> ora_ricevuta TEXT
        ))
        conn.commit()
        print(f"DEBUG: Ricevuta {numero_ricevuta_testo} salvata nel DB.")
    except sqlite3.IntegrityError as e:
        print(f"Errore: Tentativo di salvare una ricevuta duplicata o violazione UNIQUE: {e}")
    except Exception as e:
        print(f"Errore durante il salvataggio della ricevuta nel DB: {e}")
    finally:
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

def inserisci_dettaglio_noleggio(id_noleggio, id_materiale, codice_materiale):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO DettagliNoleggio (id_noleggio, id_materiale, codice_materiale)
        VALUES (?, ?, ?)
    ''', (id_noleggio, id_materiale, codice_materiale))
    conn.commit()
    conn.close()


def get_prossimo_numero_ricevuta():
    conn = get_connection()
    anno_corrente = datetime.now().year
    prossimo_numero = 1

    try:
        # Tenta di leggere l'ultimo numero per l'anno corrente
        cur = conn.execute("SELECT UltimoNumeroRicevuta FROM Contatori WHERE Anno = ?", (anno_corrente,))
        riga = cur.fetchone()

        if riga:
            # Se l'anno esiste, incrementa l'ultimo numero
            prossimo_numero = riga[0] + 1
            cur.execute("UPDATE Contatori SET UltimoNumeroRicevuta = ? WHERE Anno = ?", (prossimo_numero, anno_corrente))
        else:
            # Se l'anno non esiste, inizia da 1 e inserisci la nuova riga
            cur.execute("INSERT INTO Contatori (Anno, UltimoNumeroRicevuta) VALUES (?, ?)", (anno_corrente, 1))

        conn.commit()
        return f"{prossimo_numero:04d}/{anno_corrente}" # Formatta come 0001/2025
    except sqlite3.Error as e:
        # QUESTO È IL DEBUG FONDAMENTALE: Stampa l'errore specifico del DB
        print(f"ERRORE SQL in get_prossimo_numero_ricevuta: {e}")
        conn.rollback()
        return None # O gestisci l'errore in modo diverso
    finally:
        conn.close()

    
    #Nuove funzioni per la gestione del Noleggio


def inserisci_noleggio(
    nome_cliente, cognome_cliente, data_noleggio, ora_noleggio, durata_ore,
    percorso_documento_privacy, lingua, metodo_pagamento, importo_totale,
    data_inizio,       # Questo l'abbiamo aggiunto prima
    ora_inizio         # <--- AGGIUNTO ANCHE QUESTO PARAMETRO ORA
    ):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO Noleggi (
                nome_cliente,
                cognome_cliente,
                data_inizio,
                ora_inizio,        -- Ora questo corrisponde al parametro
                durata_ore,
                stato,
                metodo_pagamento,
                importo_totale,
                data_creazione,
                percorso_documento,
                lingua,
                data_noleggio
            ) VALUES (?, ?, ?, ?, ?, 'attivo', ?, ?, CURRENT_TIMESTAMP, ?, ?, ?)
        """, (nome_cliente, cognome_cliente,
              data_inizio,
              ora_inizio,        # <--- USIAMO IL NUOVO PARAMETRO QUI
              durata_ore,
              metodo_pagamento,
              importo_totale,
              percorso_documento_privacy,
              lingua,
              data_noleggio))

        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Errore inserimento noleggio: {e}")
        return None
    finally:
        if conn:
            conn.close()


def inserisci_dettaglio_noleggio(id_noleggio, id_materiale, codice_materiale):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO DettagliNoleggio (id_noleggio, id_materiale, codice_materiale)
            VALUES (?, ?, ?)
        """, (id_noleggio, id_materiale, codice_materiale))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Errore inserimento dettaglio noleggio: {e}")
        return False
    finally:
        conn.close()

def aggiorna_disponibilita_materiale(id_materiale, disponibilita):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE Materiali SET disponibile = ? WHERE id = ?
        """, (disponibilita, id_materiale))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Errore aggiornamento disponibilità materiale: {e}")
        return False
    finally:
        conn.close()

def get_dettagli_materiali_by_noleggio_id(id_noleggio):
    """
    Recupera tutti i materiali (ID e codice) associati a un noleggio specifico
    dalla tabella dettagli_noleggio.
    Ritorna una lista di tuple (id_materiale, codice_materiale).
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id_materiale, codice_materiale
            FROM dettagli_noleggio
            WHERE id_noleggio = ?
        """, (id_noleggio,))
        materiali_dettaglio = cursor.fetchall()
        return materiali_dettaglio # Ritorna una lista di tuple, es: [(1, 'S001'), (2, 'V005')]
    except sqlite3.Error as e:
        print(f"Errore recupero dettagli materiali per noleggio {id_noleggio}: {e}")
        return []
    finally:
        conn.close()

def aggiorna_disponibilita_materiale_by_id(materiale_id: int, disponibilita: int) -> bool:
    """
    Aggiorna lo stato di disponibilità di un materiale dato il suo ID nel database.
    :param materiale_id: L'ID numerico del materiale nel database.
    :param disponibilita: 0 per non disponibile, 1 per disponibile.
    :return: True se l'aggiornamento ha avuto successo, False altrimenti.
    """
    conn = None
    try:
        conn = get_connection
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE Materiali
            SET disponibilita = ?
            WHERE id = ?
        """, (disponibilita, materiale_id))

        conn.commit()
        print(f"DEBUG (data_access): Materiale ID {materiale_id} aggiornato a disponibilita={disponibilita}.")
        return True
    except sqlite3.Error as e:
        print(f"ERRORE (data_access): Errore nell'aggiornare disponibilità materiale ID {materiale_id}: {e}")
        return False
    finally:
        if conn:
            conn.close()

def aggiorna_materiale(dati):
    conn = get_connection()
    cursor = conn.cursor()
    # MODIFICA QUI: L'ordine dei campi in 'dati' DEVE corrispondere a quello qui sotto.
    # 'dati' deve contenere 13 valori per i campi da aggiornare, e l'ULTIMO elemento deve essere l'ID.
    # Esempio ordine dati: (codice, tipo, nome, produttore, provenienza, descrizione, note,
    #                       codice_barre, foto_path, disponibile, barcode, rig, foto, id)
    sql = """
    UPDATE materiali SET
        codice = ?, tipo = ?, nome = ?, produttore = ?, provenienza = ?,
        descrizione = ?, note = ?, codice_barre = ?, foto_path = ?,
        disponibile = ?, barcode = ?, rig = ?, foto = ?  -- AGGIUNTI: disponibile, barcode, foto
    WHERE id = ?
    """
    try:
        cursor.execute(sql, dati) # Questa execute si aspetta ora 14 valori (13 campi + id)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Errore nell'aggiornamento del materiale: {e}")
        raise
    finally:
        conn.close()

def inserisci_materiale(dati):
    """
    Inserisce un nuovo materiale nel database.
    I dati devono essere una tupla nell'ordine:
    (codice, tipo, nome, produttore, provenienza, descrizione, note,
    codice_barre, foto_path, disponibile, barcode, rig, foto_blob_data)
    """
    conn = get_connection()
    cursor = conn.cursor()
    sql = """
    INSERT INTO materiali (
        codice, tipo, nome, produttore, provenienza, descrizione, note,
        codice_barre, foto_path, disponibile, barcode, rig, foto
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    try:
        cursor.execute(sql, dati)
        conn.commit()
    except sqlite3.IntegrityError as e:
        print(f"Errore di integrità nell'inserimento del materiale: {e}")
        raise # Rilancia l'eccezione in modo che gestione_inventario.py possa gestirla
    except sqlite3.Error as e:
        print(f"Errore generico nell'inserimento del materiale: {e}")
        raise
    finally:
        conn.close()
