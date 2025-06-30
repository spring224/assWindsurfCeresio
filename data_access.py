
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

# Funzione per ottenere tutti i soci (dovrà essere aggiornata anche nel DialogoListaSoci)
def get_all_soci():
    conn = get_connection()
    conn.row_factory = sqlite3.Row # QUESTA RIGA È FONDAMENTALE
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM soci ORDER BY cognome, nome")
    soci = cursor.fetchall()
    conn.close()
    return [dict(row) for row in soci] # Converte le Row in dizionari


def insert_socio(nome, cognome, email, quota_pagata):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO soci (nome, cognome, email, quota_pagata) VALUES (?, ?, ?, ?)",
        (nome, cognome, email, int(quota_pagata))
    )
    conn.commit()
    conn.close()

# Funzione per inserire un nuovo socio (aggiornata per i nuovi campi)
def insert_socio_esteso(dati):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO soci (
            nome, cognome, indirizzo, telefono, email,
            data_nascita, luogo_nascita, codice_fiscale,
            quota_pagata, quota_associazione, anno, attivo, foto,
            sesso, cap, citta, provincia, nazione,
            tipo_tesseramento, numero_tessera, data_emissione, data_scadenza
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            dati["nome"],
            dati["cognome"],
            dati["indirizzo"], # Ora 'indirizzo' sarà solo via e numero civico
            dati["telefono"],
            dati["email"],
            dati["data_nascita"],
            dati["luogo_nascita"],
            dati["codice_fiscale"],
            dati["quota_pagata"],  # Preso dal dizionario
            dati["quota_associazione"], # Preso dal dizionario
            dati["anno"],
            dati["attivo"],
            dati["foto"],
            dati["sesso"],          # Nuovo
            dati["cap"],            # Nuovo
            dati["citta"],          # Nuovo
            dati["provincia"],      # Nuovo
            dati["nazione"],        # Nuovo
            dati["tipo_tesseramento"], # Nuovo
            dati["numero_tessera"],    # Nuovo
            dati["data_emissione"],    # Nuovo
            dati["data_scadenza"]      # Nuovo
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
        # Recupera i nomi delle colonne dal cursore per rendere il codice più robusto
        # in caso di futuri cambiamenti allo schema
        columns = [description[0] for description in cursor.description]
        return dict(zip(columns, row))
    else:
        return None
    
# Funzione per aggiornare un socio (aggiornata per i nuovi campi)
def update_socio_esteso(id_socio, dati):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE soci
        SET 
            nome = ?, cognome = ?, indirizzo = ?, telefono = ?, email = ?, 
            data_nascita = ?, luogo_nascita = ?, codice_fiscale = ?,
            quota_pagata = ?, quota_associazione = ?, anno = ?, attivo = ?, foto = ?,
            sesso = ?, cap = ?, citta = ?, provincia = ?, nazione = ?,
            tipo_tesseramento = ?, numero_tessera = ?, data_emissione = ?, data_scadenza = ?
        WHERE id = ?
    """, (
        dati["nome"], dati["cognome"], dati["indirizzo"], dati["telefono"], dati["email"],
        dati["data_nascita"], dati["luogo_nascita"], dati["codice_fiscale"],
        dati["quota_pagata"], dati["quota_associazione"], dati["anno"], dati["attivo"], dati["foto"],
        dati["sesso"], dati["cap"], dati["citta"], dati["provincia"], dati["nazione"],
        dati["tipo_tesseramento"], dati["numero_tessera"], dati["data_emissione"], dati["data_scadenza"],
        id_socio
    ))
    conn.commit()
    conn.close()
    
# Funzione per marcare la quota come pagata con valore fisso e anno corrente
def mark_quota_pagata(socio_id):
    conn = None # Inizializza conn a None per la finally bloc
    print(f"DEBUG sono nella Mark_quota_pagata socio ID {socio_id}")
    try:
        conn = get_connection() # Ottieni la connessione UNA VOLTA
        cursor = conn.cursor()  # Ottieni il cursore correttamente chiamando il metodo

        current_year = datetime.now().year # Anno corrente
        fixed_quota_amount = 35.0 # Valore fisso della quota

        # Aggiorna quota_pagata, quota_associazione e anno
        cursor.execute("UPDATE soci SET quota_pagata = 1, quota_associazione = ?, anno = ? WHERE id = ?",
                       (fixed_quota_amount, current_year, socio_id))
        
        print(f"DEBUG (data_access): Aggiornamento quota per socio ID {socio_id} - quota_pagata=1, quota_associazione={fixed_quota_amount}, anno={current_year}")
        
        conn.commit()
        return True
    except sqlite3.Error as e:
        # Questo print ora verrà raggiunto se c'è un errore SQL
        print(f"ERRORE (data_access - mark_quota_pagata): Errore nel marcare la quota come pagata: {e}")
        return False
    except Exception as e:
        # Questo cattura altri errori generici (come quello del cursore sbagliato se lo fosse stato)
        print(f"ERRORE GENERALE (data_access - mark_quota_pagata): {e}")
        return False
    finally:
        if conn:
            conn.close()


# Funzioni placeholder per futuro utilizzo
def update_socio(id_socio, nome, cognome, email, quota_pagata):
    pass

def delete_socio(id_socio):
    pass


def get_socio_photo_blob(id_socio):
    pass

def save_socio_photo_blob(id_socio, blob_data):
    pass



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
        conn.row_factory = sqlite3.Row 
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

# data_access.py

# ... (il resto degli import e delle funzioni precedenti) ...

def carica_listino():
    conn = None
    listino = []
    try:
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        # Seleziona anche nome_materiale
        cursor.execute("SELECT id, tipo, nome_materiale, descrizione, prezzo_orario FROM ListinoNoleggio ORDER BY tipo, nome_materiale")
        listino = [dict(row) for row in cursor.fetchall()]
        return listino
    except sqlite3.Error as e:
        print(f"ERRORE (data_access - carica_listino): Errore nel caricare il listino: {e}")
        return []
    finally:
        if conn:
            conn.close()

def salva_listino(righe_listino):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        conn.execute("BEGIN TRANSACTION")
        cursor.execute("DELETE FROM ListinoNoleggio")

        # Inserisci le nuove righe, includendo nome_materiale
        sql_insert = "INSERT INTO ListinoNoleggio (tipo, nome_materiale, descrizione, prezzo_orario) VALUES (?, ?, ?, ?)"
        
        data_to_insert = []
        for riga in righe_listino:
            # Assicurati che 'nome_materiale' sia presente nel dizionario riga
            data_to_insert.append((riga['tipo'], riga['nome_materiale'], riga['descrizione'], riga['prezzo_orario']))
        
        if data_to_insert:
            cursor.executemany(sql_insert, data_to_insert)
        
        conn.commit()
        return True, None
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        print(f"ERRORE (data_access - salva_listino): Errore nel salvare il listino: {e}")
        return False, str(e)
    finally:
        if conn:
            conn.close()

# NUOVA FUNZIONE per ottenere tipi e nomi dal database Materiali
def get_all_material_types_and_names():
    conn = None
    materials = []
    try:
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        # Seleziona tipo e nome distinti da Materiali
        cursor.execute("SELECT DISTINCT tipo, nome FROM Materiali ORDER BY tipo, nome")
        # Restituisce una lista di tuple (tipo, nome) o dizionari se preferisci
        materials = [(row['tipo'], row['nome']) for row in cursor.fetchall()]
        return materials
    except sqlite3.Error as e:
        print(f"ERRORE (data_access - get_all_material_types_and_names): Errore nel caricare tipi e nomi materiali: {e}")
        return []
    finally:
        if conn:
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
            INSERT INTO dettagli_noleggio (id_noleggio, id_materiale, codice_materiale)
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
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE Materiali
            SET disponibile = ?
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

# Nel file data_access.py

# --- Funzione inserisci_materiale ---

def inserisci_materiale(dati):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Estrai le chiavi (nomi delle colonne) e i valori dal dizionario
        columns = ', '.join(dati.keys())
        placeholders = ', '.join(['?' for _ in dati.keys()]) # Crea '?', '?', ...
        values = tuple(dati.values()) # Converti i valori in una tupla

        sql = f"INSERT INTO Materiali ({columns}) VALUES ({placeholders})"
        cursor.execute(sql, values) # <--- Ora passiamo una tupla di valori

        conn.commit()
        print(f"DEBUG (data_access - inserisci_materiale): Materiale '{dati.get('nome', '')}' inserito con successo.")
        return True
    except sqlite3.Error as e:
        print(f"ERRORE (data_access - inserisci_materiale): Errore generico nell'inserimento del materiale: {e}")
        return False
    finally:
        if conn:
            conn.close()

# --- Funzione aggiorna_materiale ---
# data_access.py

# ... (il resto degli import e delle funzioni precedenti) ...

def aggiorna_materiale(material_id, dati): # <--- MODIFICA QUI: aggiunto material_id
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Costruisci la parte SET della query dinamicamente
        set_clauses = []
        values = []
        for key, value in dati.items():
            set_clauses.append(f"{key} = ?")
            values.append(value)

        # Aggiungi l'ID alla fine dei valori per la clausola WHERE
        values.append(material_id)

        query = f"UPDATE Materiali SET {', '.join(set_clauses)} WHERE id = ?"
        cursor.execute(query, tuple(values))
        conn.commit()
        print(f"DEBUG (data_access - aggiorna_materiale): Materiale ID {material_id} aggiornato.")
        return True
    except sqlite3.Error as e:
        print(f"ERRORE (data_access - aggiorna_materiale): Errore nell'aggiornare il materiale {material_id}: {e}")
        return False
    finally:
        if conn:
            conn.close()

# ... (il resto delle funzioni) ...

# --- Funzione carica_materiali ---
# Rimuovi 'barcode' dalla SELECT
def carica_materiali():
    conn = None
    materiali = []
    try:
        conn = get_connection()
        conn.row_factory = sqlite3.Row  # Questo permette di accedere ai dati per nome colonna
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, codice, tipo, nome, produttore, provenienza, descrizione,
                   note, codice_barre, foto_path, disponibile, rig, foto
            FROM materiali ORDER BY tipo, nome
        """)
        materiali = [dict(row) for row in cursor.fetchall()]
        return materiali
    except sqlite3.Error as e:
        print(f"ERRORE (data_access - carica_materiali): Errore nel caricamento dei materiali: {e}")
        return []
    finally:
        if conn:
            conn.close()


# --- Funzione get_materiale_by_id ---
# Rimuovi 'barcode' dalla SELECT
def get_materiale_by_id(material_id):
    conn = None
    materiale = None
    try:
        conn = get_connection()
        conn.row_factory = sqlite3.Row # Per accedere ai risultati per nome colonna
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, codice, tipo, nome, produttore, provenienza, descrizione,
                   note, codice_barre, foto_path, disponibile, rig, foto
            FROM materiali WHERE id = ?
        """, (material_id,))
        result = cursor.fetchone()
        if result:
            materiale = dict(result) # Converte sqlite3.Row in dict
        return materiale
    except sqlite3.Error as e:
        print(f"ERRORE (data_access - get_materiale_by_id): Errore nel caricamento del materiale per ID: {e}")
        return None
    finally:
        if conn:
            conn.close()

# --- Funzione carica_materiali_rig ---
# Se questa funzione seleziona tutti i campi, aggiorna la SELECT
def carica_materiali_rig():
    conn = None
    materiali_rig = []
    try:
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, codice, tipo, nome, produttore, provenienza, descrizione,
                   note, codice_barre, foto_path, disponibile, rig, foto
            FROM materiali WHERE tipo = 'Rig' ORDER BY nome
        """)
        materiali_rig = [dict(row) for row in cursor.fetchall()]
        return materiali_rig
    except sqlite3.Error as e:
        print(f"ERRORE (data_access - carica_materiali_rig): Errore nel caricamento dei Rig: {e}")
        return []
    finally:
        if conn:
            conn.close()

# --- Funzione carica_materiali_per_tipo ---
# Se questa funzione seleziona tutti i campi, aggiorna la SELECT
def carica_materiali_per_tipo(tipo_selezionato):
    conn = None
    materiali_per_tipo = []
    try:
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, codice, tipo, nome, produttore, provenienza, descrizione,
                   note, codice_barre, foto_path, disponibile, rig, foto
            FROM materiali WHERE tipo = ? ORDER BY nome
        """, (tipo_selezionato,))
        materiali_per_tipo = [dict(row) for row in cursor.fetchall()]
        return materiali_per_tipo
    except sqlite3.Error as e:
        print(f"ERRORE (data_access - carica_materiali_per_tipo): Errore nel caricamento dei materiali per tipo: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_all_material_types() -> list[str]:
    """
    Recupera tutti i tipi di materiale distinti dalla tabella Materiali.
    """
    conn = None
    tipi = []
    try:
        conn = get_connection()
        # Non impostiamo row_factory qui perché vogliamo una tupla semplice
        # per accedere a row[0] (il valore del tipo).
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT tipo FROM Materiali ORDER BY tipo")
        
        for row in cursor.fetchall():
            tipi.append(row[0]) # Accede al primo elemento della tupla (il 'tipo')
    except sqlite3.Error as e:
        print(f"ERRORE (data_access - get_all_material_types): Errore nel recupero dei tipi di materiale: {e}")
    finally:
        if conn:
            conn.close()
    return tipi


def cerca_o_crea_cliente(nome: str, cognome: str, email: str = None, telefono: str = None, indirizzo: str = None, data_nascita: str = None, codice_fiscale: str = None, nazione: str = None) -> int:
    """
    Cerca un cliente esistente per nome, cognome ed email (se fornita).
    Se trovato, restituisce l'ID del cliente.
    Altrimenti, crea un nuovo cliente e restituisce il suo ID.
    Ora include anche la Nazione.
    """
    conn = None
    try:
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Tenta di trovare il cliente per nome, cognome ed email (se email è fornita e non vuota)
        # Nota: la ricerca per email univoca è spesso più affidabile se disponibile.
        # Qui cerchiamo per nome, cognome e, se fornita, email.
        if email:
            cursor.execute("SELECT id FROM Clienti WHERE nome = ? AND cognome = ? AND email = ?", (nome, cognome, email))
        else:
            cursor.execute("SELECT id FROM Clienti WHERE nome = ? AND cognome = ?", (nome, cognome))
        
        cliente_esistente = cursor.fetchone()

        if cliente_esistente:
            print(f"DEBUG (data_access): Cliente '{nome} {cognome}' trovato, ID: {cliente_esistente['id']}")
            return cliente_esistente['id']
        else:
            # Cliente non trovato, inseriscine uno nuovo con la Nazione
            print(f"DEBUG (data_access): Cliente '{nome} {cognome}' non trovato, creazione nuovo cliente.")
            cursor.execute("""
                INSERT INTO Clienti (nome, cognome, email, telefono, indirizzo, data_nascita, codice_fiscale, nazione)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (nome, cognome, email, telefono, indirizzo, data_nascita, codice_fiscale, nazione))
            conn.commit()
            nuovo_id_cliente = cursor.lastrowid
            print(f"DEBUG (data_access): Nuovo cliente creato con ID: {nuovo_id_cliente}")
            return nuovo_id_cliente

    except sqlite3.Error as e:
        print(f"ERRORE (data_access - cerca_o_crea_cliente): Errore nella ricerca/creazione del cliente: {e}")
        return -1 # Indica errore
    finally:
        if conn:
            conn.close()

def salva_tessera(id_cliente: int, tipo_tessera: str, prezzo_totale: float, numero_item_totale: int, data_creazione: str) -> bool:
    """
    Salva una nuova tessera nel database, includendo il tipo di tessera (Lezione/Noleggio).
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Tessere (id_cliente, tipo_tessera, prezzo_totale, numero_item_totale, data_creazione)
            VALUES (?, ?, ?, ?, ?)
        """, (id_cliente, tipo_tessera, prezzo_totale, numero_item_totale, data_creazione))
        conn.commit()
        print(f"DEBUG (data_access): Tessera creata per cliente ID {id_cliente}, tipo '{tipo_tessera}', {numero_item_totale} items, prezzo {prezzo_totale}.")
        return True
    except sqlite3.Error as e:
        print(f"ERRORE (data_access - salva_tessera): Errore nel salvataggio della tessera: {e}")
        return False
    finally:
        if conn:
            conn.close()

def get_tessere(solo_attive: bool = True):
    """
    Recupera le tessere dal database.
    Se solo_attive è True, restituisce solo le tessere con item_usati < numero_item_totale e attiva = 1.
    Altrimenti, restituisce tutte le tessere.
    Restituisce una lista di dizionari (row_factory).
    """
    conn = None
    tessere = []
    try:
        conn = get_connection()
        conn.row_factory = sqlite3.Row # Per accedere ai risultati come dizionario
        cursor = conn.cursor()

        query = """
            SELECT 
                T.id, T.tipo_tessera, T.prezzo_totale, T.numero_item_totale, T.item_usati, 
                T.data_creazione, T.data_scadenza, T.attiva,
                C.nome, C.cognome, C.email, C.telefono, C.nazione
            FROM Tessere T
            JOIN Clienti C ON T.id_cliente = C.id
        """
        conditions = []
        if solo_attive:
            conditions.append("(T.item_usati < T.numero_item_totale AND T.attiva = 1)")

        # Aggiunto controllo per data_scadenza se la hai, altrimenti ignora o rimuovi.
        # Se la colonna data_scadenza è TEXT, potresti voler aggiungere un controllo sulla data corrente.
        # Per ora, la lasciamo come previsto dal tuo schema attuale.
        # if solo_attive:
        #     conditions.append("DATE(T.data_scadenza) >= DATE('now')") # Se data_scadenza è in formato 'YYYY-MM-DD'


        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY T.data_creazione DESC;"

        cursor.execute(query)
        tessere = [dict(row) for row in cursor.fetchall()]
        print(f"DEBUG (data_access - get_tessere): Recuperate {len(tessere)} tessere (solo_attive={solo_attive}).")
        return tessere

    except sqlite3.Error as e:
        print(f"ERRORE (data_access - get_tessere): Errore nel recupero delle tessere: {e}")
        return []
    finally:
        if conn:
            conn.close()

def usa_item_tessera(id_tessera: int) -> bool:
    """
    Incrementa il contatore item_usati per una tessera specifica.
    Se item_usati raggiunge numero_item_totale, imposta 'attiva' a 0.
    Restituisce True se l'operazione ha successo, False altrimenti.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # 1. Recupera lo stato attuale della tessera
        cursor.execute("SELECT numero_item_totale, item_usati FROM Tessere WHERE id = ?", (id_tessera,))
        tessera = cursor.fetchone()

        if not tessera:
            print(f"ERRORE (data_access - usa_item_tessera): Tessera con ID {id_tessera} non trovata.")
            return False

        numero_item_totale = tessera[0]
        item_usati_attuali = tessera[1]

        if item_usati_attuali >= numero_item_totale:
            print(f"AVVISO (data_access - usa_item_tessera): Tessera ID {id_tessera} già completamente utilizzata.")
            return False # La tessera è già esaurita

        # 2. Incrementa item_usati
        nuovi_item_usati = item_usati_attuali + 1
        # data_ora_utilizzo = datetime.now().strftime('%Y-%m-%d %H:%M:%S') # Potresti salvare questo in una tabella LogUtilizzoTessere se vuoi uno storico dettagliato

        query_update = "UPDATE Tessere SET item_usati = ?"
        params_update = [nuovi_item_usati]

        # 3. Se tutti gli item sono stati usati, imposta attiva a 0
        if nuovi_item_usati >= numero_item_totale:
            query_update += ", attiva = 0"
            print(f"DEBUG (data_access - usa_item_tessera): Tessera ID {id_tessera} completamente utilizzata, impostata a inattiva.")

        query_update += " WHERE id = ?"
        params_update.append(id_tessera)

        cursor.execute(query_update, tuple(params_update))
        conn.commit()
        print(f"DEBUG (data_access - usa_item_tessera): Item utilizzato per tessera ID {id_tessera}. Nuovi item usati: {nuovi_item_usati}.")
        return True

    except sqlite3.Error as e:
        print(f"ERRORE (data_access - usa_item_tessera): Errore nell'utilizzo dell'item per tessera ID {id_tessera}: {e}")
        return False
    finally:
        if conn:
            conn.close()

# --- FINE NUOVE FUNZIONI (DA AGGIUNGERE O VERIFICARE) --


def salva_lezione_programmata(id_tessera: int, data_lezione: str, ora_lezione: str, descrizione: str, note: str) -> int | None:
    """
    Salva una nuova lezione programmata nel database.
    Restituisce l'ID della lezione inserita o None in caso di errore.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO LezioniProgrammate 
            (id_tessera, data_lezione, ora_lezione, descrizione, note, confermata, completata) 
            VALUES (?, ?, ?, ?, ?, 0, 0)
        """, (id_tessera, data_lezione, ora_lezione, descrizione, note))
        conn.commit()
        print(f"DEBUG (data_access - salva_lezione_programmata): Lezione programmata salvata per tessera {id_tessera} il {data_lezione}.")
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"ERRORE (data_access - salva_lezione_programmata): Errore nel salvare la lezione programmata: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_lezioni_per_data(data: str) -> list:
    """
    Recupera tutte le lezioni programmate per una data specifica.
    Restituisce una lista di dizionari (row_factory).
    """
    conn = None
    lezioni = []
    try:
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                LP.id, LP.id_tessera, LP.data_lezione, LP.ora_lezione, 
                LP.descrizione, LP.note, LP.confermata, LP.completata,
                C.nome, C.cognome, T.tipo_tessera
            FROM LezioniProgrammate LP
            JOIN Tessere T ON LP.id_tessera = T.id
            JOIN Clienti C ON T.id_cliente = C.id
            WHERE LP.data_lezione = ?
            ORDER BY LP.ora_lezione ASC, C.cognome ASC, C.nome ASC;
        """, (data,))
        lezioni = [dict(row) for row in cursor.fetchall()]
        print(f"DEBUG (data_access - get_lezioni_per_data): Recuperate {len(lezioni)} lezioni per la data {data}.")
        return lezioni
    except sqlite3.Error as e:
        print(f"ERRORE (data_access - get_lezioni_per_data): Errore nel recupero delle lezioni per data: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_lezione_by_id(id_lezione: int):
    """
    Recupera i dettagli di una singola lezione programmata tramite ID.
    """
    conn = None
    try:
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                LP.id, LP.id_tessera, LP.data_lezione, LP.ora_lezione, 
                LP.descrizione, LP.note, LP.confermata, LP.completata,
                C.nome, C.cognome, T.tipo_tessera, T.numero_item_totale, T.item_usati
            FROM LezioniProgrammate LP
            JOIN Tessere T ON LP.id_tessera = T.id
            JOIN Clienti C ON T.id_cliente = C.id
            WHERE LP.id = ?;
        """, (id_lezione,))
        lezione = cursor.fetchone()
        return dict(lezione) if lezione else None
    except sqlite3.Error as e:
        print(f"ERRORE (data_access - get_lezione_by_id): Errore nel recupero della lezione: {e}")
        return None
    finally:
        if conn:
            conn.close()


def aggiorna_stato_lezione(id_lezione: int, confermata: int = None, completata: int = None) -> bool:
    """
    Aggiorna lo stato (confermata/completata) di una lezione programmata.
    Restituisce True se l'aggiornamento ha successo, False altrimenti.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        updates = []
        params = []
        if confermata is not None:
            updates.append("confermata = ?")
            params.append(confermata)
        if completata is not None:
            updates.append("completata = ?")
            params.append(completata)
        
        if not updates:
            print("AVVISO (data_access - aggiorna_stato_lezione): Nessun parametro di stato fornito per l'aggiornamento.")
            return False

        query = f"UPDATE LezioniProgrammate SET {', '.join(updates)} WHERE id = ?"
        params.append(id_lezione)

        cursor.execute(query, tuple(params))
        conn.commit()
        print(f"DEBUG (data_access - aggiorna_stato_lezione): Stato lezione ID {id_lezione} aggiornato.")
        return True
    except sqlite3.Error as e:
        print(f"ERRORE (data_access - aggiorna_stato_lezione): Errore nell'aggiornare lo stato della lezione: {e}")
        return False
    finally:
        if conn:
            conn.close()

def cancella_lezione_programmata(id_lezione: int) -> bool:
    """
    Cancella una lezione programmata dal database.
    Restituisce True se la cancellazione ha successo, False altrimenti.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM LezioniProgrammate WHERE id = ?", (id_lezione,))
        conn.commit()
        print(f"DEBUG (data_access - cancella_lezione_programmata): Lezione ID {id_lezione} cancellata.")
        return True
    except sqlite3.Error as e:
        print(f"ERRORE (data_access - cancella_lezione_programmata): Errore nel cancellare la lezione: {e}")
        return False
    finally:
        if conn:
            conn.close()

def get_tessere_per_selezione_lezione():
    """
    Recupera solo le tessere attive (non esaurite) con i dati del cliente
    per la selezione nella finestra di programmazione lezioni.
    """
    conn = None
    tessere = []
    try:
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        # Seleziona solo le tessere che hanno ancora item disponibili e sono attive
        cursor.execute("""
            SELECT 
                T.id, T.tipo_tessera, T.numero_item_totale, T.item_usati,
                C.nome, C.cognome
            FROM Tessere T
            JOIN Clienti C ON T.id_cliente = C.id
            WHERE T.item_usati < T.numero_item_totale AND T.attiva = 1
            ORDER BY C.cognome, C.nome;
        """)
        tessere = [dict(row) for row in cursor.fetchall()]
        return tessere
    except sqlite3.Error as e:
        print(f"ERRORE (data_access - get_tessere_per_selezione_lezione): Errore nel recupero tessere per selezione: {e}")
        return []
    finally:
        if conn:
            conn.close()

# --- FINE NUOVE FUNZIONI PER GESTIONE LEZIONI PROGRAMMATE ---