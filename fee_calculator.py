import pandas as pd

# Definizione degli scaglioni di valore secondo il DM 55-2014
SCAGLIONI = [
    {"min": 0, "max": 1100, "coefficiente": 1.0},
    {"min": 1100, "max": 5200, "coefficiente": 1.0},
    {"min": 5200, "max": 26000, "coefficiente": 1.0},
    {"min": 26000, "max": 52000, "coefficiente": 1.0},
    {"min": 52000, "max": 260000, "coefficiente": 1.0},
    {"min": 260000, "max": 520000, "coefficiente": 1.0},
    {"min": 520000, "max": None, "coefficiente": 1.0},  # "oltre 520000"
]

# Tariffe di base per tipo di servizio
TARIFFE_BASE = {
    "Consulenza": {
        0: 100,  # fino a 1.100
        1: 250,  # da 1.100 a 5.200
        2: 500,  # da 5.200 a 26.000
        3: 800,  # da 26.000 a 52.000
        4: 1300,  # da 52.000 a 260.000
        5: 2000,  # da 260.000 a 520.000
        6: 3000,  # oltre 520.000
    },
    "Contratti": {
        0: 150,
        1: 400,
        2: 700,
        3: 1200,
        4: 1800,
        5: 2500,
        6: 3500,
    },
    "Contenzioso": {
        0: 300,
        1: 650,
        2: 1200,
        3: 2000,
        4: 3500,
        5: 5000,
        6: 7000,
    },
    "Esecuzione": {
        0: 250,
        1: 550,
        2: 900,
        3: 1500,
        4: 2500,
        5: 3800,
        6: 5500,
    },
    "Famiglia": {
        0: 350,
        1: 750,
        2: 1300,
        3: 2200,
        4: 3800,
        5: 5500,
        6: 7500,
    },
    "Stragiudiziale": {
        0: 200,
        1: 450,
        2: 800,
        3: 1300,
        4: 2000,
        5: 3000,
        6: 4500,
    },
    "Amministrativo": {
        0: 250,
        1: 550,
        2: 1000,
        3: 1700,
        4: 3000,
        5: 4500,
        6: 6500,
    },
}

# Maggiorazioni per complessità della pratica
MAGGIORAZIONI = {
    "standard": 1.0,  # nessuna maggiorazione
    "media": 1.2,     # aumento del 20%
    "alta": 1.4,      # aumento del 40%
    "molto_alta": 1.8, # aumento dell'80% (massimo previsto dall'art. 4 comma 1)
}

def get_scaglione_index(valore):
    """
    Determina l'indice dello scaglione in base al valore
    """
    for i, scaglione in enumerate(SCAGLIONI):
        if scaglione["max"] is None:  # ultimo scaglione "oltre X"
            if valore > scaglione["min"]:
                return i
        elif scaglione["min"] <= valore <= scaglione["max"]:
            return i
    
    # Fallback all'ultimo scaglione
    return len(SCAGLIONI) - 1

def calcola_compenso(valore, servizio, complessita="standard"):
    """
    Calcola il compenso in base al valore, al tipo di servizio e alla complessità
    """
    # Verifica che il servizio esista nelle tariffe
    categoria_servizio = None
    for categoria in TARIFFE_BASE.keys():
        if categoria in servizio:
            categoria_servizio = categoria
            break
    
    # Se non trova una corrispondenza esatta, usa la categoria dal nome del servizio
    if categoria_servizio is None:
        for categoria in TARIFFE_BASE.keys():
            if categoria.lower() in servizio.lower():
                categoria_servizio = categoria
                break
    
    # Default a Consulenza se non trova corrispondenze
    if categoria_servizio is None:
        categoria_servizio = "Consulenza"
    
    # Determina lo scaglione
    scaglione_index = get_scaglione_index(valore)
    
    # Ottieni la tariffa base per quel servizio e scaglione
    tariffa_base = TARIFFE_BASE[categoria_servizio][scaglione_index]
    
    # Applica la maggiorazione per complessità
    maggiorazione = MAGGIORAZIONI.get(complessita, 1.0)
    compenso = tariffa_base * maggiorazione
    
    # Aggiungi rimborso spese forfettarie (15%)
    spese_forfettarie = compenso * 0.15
    
    # IVA (22%) e Cassa Avvocati (4%)
    cassa = compenso * 0.04
    imponibile = compenso + spese_forfettarie + cassa
    iva = imponibile * 0.22
    
    # Totale finale
    totale = imponibile + iva
    
    return {
        "compenso_base": compenso,
        "spese_forfettarie": spese_forfettarie,
        "cassa_avvocati": cassa,
        "imponibile": imponibile,
        "iva": iva,
        "totale": totale,
        "scaglione_index": scaglione_index
    }

def get_preventivo_dettagliato(valore, servizi_selezionati, complessita="standard"):
    """
    Genera un preventivo dettagliato per tutti i servizi selezionati
    """
    totale_preventivo = 0
    dettaglio_servizi = []
    
    for servizio in servizi_selezionati:
        calcolo = calcola_compenso(valore, servizio, complessita)
        totale_preventivo += calcolo["totale"]
        
        dettaglio_servizi.append({
            "nome_servizio": servizio,
            "compenso_base": calcolo["compenso_base"],
            "spese_forfettarie": calcolo["spese_forfettarie"],
            "cassa_avvocati": calcolo["cassa_avvocati"],
            "iva": calcolo["iva"],
            "totale": calcolo["totale"],
            "scaglione_index": calcolo["scaglione_index"]
        })
    
    return {
        "dettaglio_servizi": dettaglio_servizi,
        "totale_preventivo": totale_preventivo
    }
