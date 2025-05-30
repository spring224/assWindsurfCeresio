
import codicefiscale

def calcola_codice_fiscale(nome, cognome, sesso, data_nascita, luogo_nascita):
    # data_nascita in formato yyyy-MM-dd
    try:
        cf = codicefiscale.encode({
            "name": nome,
            "surname": cognome,
            "sex": sesso,
            "birthdate": data_nascita,
            "birthplace": luogo_nascita
        })
        return cf
    except Exception as e:
        return ""
