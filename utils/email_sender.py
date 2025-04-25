import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime

def send_email_with_pdf(recipient_email, client_name, pdf_bytes):
    """
    Invia un'email con il preventivo allegato in formato PDF
    
    Args:
        recipient_email (str): Email del destinatario
        client_name (str): Nome del cliente per personalizzare l'email
        pdf_bytes (bytes): Il file PDF come bytes
        
    Returns:
        bool: True se l'invio è riuscito, False altrimenti
        str: Messaggio di esito dell'operazione
    """
    # VERSIONE PROVVISORIA: Simula l'invio dell'email senza inviare effettivamente
    
    # Get email credentials from environment variables (se presenti, ma non necessari per ora)
    sender_email = os.getenv("EMAIL_USER", "studio.provvisorio@example.com")
    
    try:
        # Logga i dettagli dell'email che verrebbe inviata
        print(f"[SIMULAZIONE INVIO EMAIL]")
        print(f"Da: {sender_email}")
        print(f"A: {recipient_email}")
        print(f"Oggetto: Preventivo Servizi Legali - {datetime.now().strftime('%d/%m/%Y')}")
        print(f"Contenuto: Preventivo per {client_name}, dimensione PDF: {len(pdf_bytes)} bytes")
        print(f"[FINE SIMULAZIONE]")
        
        # In questa versione provvisoria, consideriamo l'email come inviata con successo
        # ma in realtà non viene spedita
        return True, "Simulazione invio email completata con successo! (Modalità di sviluppo)"
        
    except Exception as e:
        print(f"Errore nella simulazione dell'invio dell'email: {str(e)}")
        return False, f"Errore nella simulazione dell'invio: {str(e)}"