import os
import pandas as pd
import streamlit as st
from datetime import datetime
import base64

def load_services():
    """
    Carica i servizi disponibili dal file CSV
    """
    try:
        services_df = pd.read_csv('data/services.csv')
        return services_df
    except FileNotFoundError:
        # Se il file non esiste ancora, crea un DataFrame vuoto con le colonne necessarie
        return pd.DataFrame(columns=['id', 'nome_servizio', 'descrizione', 'categoria', 'documento'])

def save_services(services_df):
    """
    Salva i servizi nel file CSV
    """
    os.makedirs('data', exist_ok=True)
    services_df.to_csv('data/services.csv', index=False)

def load_uploaded_files():
    """
    Carica la lista dei file caricati
    """
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = {}
    return st.session_state.uploaded_files

def save_uploaded_file(file, service_id):
    """
    Salva un file caricato in memoria
    """
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = {}
    
    # Salva il contenuto del file in memoria
    content = file.read()
    st.session_state.uploaded_files[service_id] = {
        'filename': file.name,
        'content': content,
        'type': file.type
    }
    return True

def get_current_date_formatted():
    """
    Restituisce la data corrente formattata
    """
    now = datetime.now()
    return now.strftime("%d/%m/%Y")

def format_currency(amount):
    """
    Formatta un importo come valuta in Euro
    """
    return f"€ {amount:.2f}".replace('.', ',')

def validate_personal_info(personal_info):
    """
    Valida i dati personali inseriti
    """
    required_fields = ['nome', 'cognome', 'email', 'telefono']
    
    for field in required_fields:
        if not personal_info.get(field):
            return False, f"Il campo {field} è obbligatorio"
    
    # Validazione email
    if '@' not in personal_info.get('email', ''):
        return False, "L'indirizzo email non è valido"
    
    # Validazione telefono (semplice controllo numerico)
    phone = personal_info.get('telefono', '')
    if not all(c.isdigit() or c in '+ -' for c in phone):
        return False, "Il numero di telefono non è valido"
    
    return True, ""

def get_italian_scaglione_description(min_value, max_value):
    """
    Restituisce la descrizione dello scaglione in formato italiano
    """
    if max_value is None:
        return f"oltre € {min_value:,.2f}".replace(',', '.').replace('.00', '')
    else:
        return f"da € {min_value:,.2f} a € {max_value:,.2f}".replace(',', '.').replace('.00', '')
