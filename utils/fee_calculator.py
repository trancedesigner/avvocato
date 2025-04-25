def get_scaglione(valore):
    """Determina lo scaglione di appartenenza in base al valore della controversia secondo DM 55/2014"""
    if valore <= 1100:
        return 1
    elif valore <= 5200:
        return 2
    elif valore <= 26000:
        return 3
    elif valore <= 52000:
        return 4
    elif valore <= 260000:
        return 5
    elif valore <= 520000:
        return 6
    else:
        return 7

def calcola_onorario_base(scaglione):
    """Calcola l'onorario base secondo i parametri del DM 55/2014, Tabella 25 - Prestazioni di assistenza stragiudiziale"""
    # Tabella 25 - Prestazioni di assistenza stragiudiziale (valori ufficiali)
    tariffe_base = {
        1: 270,    # fino a € 1.100
        2: 1215,   # da € 1.100,01 a € 5.200
        3: 1890,   # da € 5.200,01 a € 26.000
        4: 2295,   # da € 26.000,01 a € 52.000
        5: 4320,   # da € 52.000,01 a € 260.000
        6: 5870,   # da € 260.000,01 a € 520.000
        7: 8770    # oltre € 520.000 (valore stimato in base alla progressione)
    }
    
    return tariffe_base.get(scaglione, 0)

def apply_complexity_factor(base_fee, num_services):
    """Applica un fattore di complessità basato sul numero di servizi selezionati"""
    if num_services == 1:
        return base_fee
    elif num_services == 2:
        return base_fee * 1.2  # Aumento del 20% per 2 servizi
    else:
        return base_fee * (1.2 + ((num_services - 2) * 0.1))  # +10% per ogni servizio aggiuntivo

def calculate_fees(asset_value, num_services=1):
    """
    Calcola le tariffe legali basate sul valore del bene e il numero di servizi
    secondo i parametri del DM 55/2014
    """
    # Determina lo scaglione di appartenenza
    scaglione = get_scaglione(asset_value)
    
    # Calcola l'onorario base
    base_fee = calcola_onorario_base(scaglione)
    
    # Applica fattore di complessità
    adjusted_fee = apply_complexity_factor(base_fee, num_services)
    
    # Calcola spese forfettarie (15%)
    expenses = adjusted_fee * 0.15
    
    # Cassa previdenza avvocati (4%)
    cpa = (adjusted_fee + expenses) * 0.04
    
    # IVA (22%)
    iva = (adjusted_fee + expenses + cpa) * 0.22
    
    # Totale
    total = adjusted_fee + expenses + cpa + iva
    
    return {
        'professional_fee': adjusted_fee,
        'expenses': expenses,
        'cpa': cpa,
        'iva': iva,
        'total': total
    }
