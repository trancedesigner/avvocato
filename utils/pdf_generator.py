import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image

def generate_pdf(client_data, selected_services, fees):
    """
    Genera un file PDF contenente il preventivo per i servizi legali
    
    Args:
        client_data (dict): Dati del cliente
        selected_services (list): Servizi selezionati
        fees (dict): Dettaglio costi calcolati
        
    Returns:
        bytes: Il file PDF come bytes
    """
    buffer = io.BytesIO()
    
    # Creazione del documento PDF
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # Stili
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='RightAlign',
        parent=styles['Normal'],
        alignment=2,  # 2 indica allineamento a destra
    ))
    
    styles.add(ParagraphStyle(
        name='Center',
        parent=styles['Normal'],
        alignment=1,  # 1 indica allineamento al centro
    ))
    
    # Sovrascrivere lo stile esistente invece di aggiungerne uno nuovo
    styles['Title'].alignment = 1
    styles['Title'].fontSize = 16
    styles['Title'].spaceAfter = 12
    
    styles.add(ParagraphStyle(
        name='SubTitle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=10
    ))
    
    # Contenuto del documento
    elements = []
    
    # Intestazione
    elements.append(Paragraph("PREVENTIVO SERVIZI LEGALI", styles['Title']))
    
    current_date = datetime.now().strftime("%d/%m/%Y")
    elements.append(Paragraph(f"Data: {current_date}", styles['RightAlign']))
    elements.append(Spacer(1, 0.5*cm))
    
    # Dati cliente
    elements.append(Paragraph("Dati del Cliente", styles['SubTitle']))
    
    client_info = [
        ["Nome e Cognome:", f"{client_data['nome']} {client_data['cognome']}"],
        ["Codice Fiscale:", client_data['codice_fiscale']],
        ["Email:", client_data['email']],
        ["Telefono:", client_data['telefono'] if client_data['telefono'] else "Non specificato"],
        ["Indirizzo:", client_data['indirizzo'] if client_data['indirizzo'] else "Non specificato"]
    ]
    
    client_table = Table(client_info, colWidths=[4*cm, 10*cm])
    client_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.white),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    
    elements.append(client_table)
    elements.append(Spacer(1, 0.5*cm))
    
    # Valore del bene
    elements.append(Paragraph("Informazioni sulla pratica", styles['SubTitle']))
    
    case_info = [
        ["Valore del bene:", f"€ {client_data['valore_bene']:,.2f}"]
    ]
    
    case_table = Table(case_info, colWidths=[4*cm, 10*cm])
    case_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.white),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    
    elements.append(case_table)
    elements.append(Spacer(1, 0.5*cm))
    
    # Servizi richiesti
    elements.append(Paragraph("Servizi richiesti", styles['SubTitle']))
    
    services_data = []
    for i, service in enumerate(selected_services, 1):
        services_data.append([str(i), service['name']])
    
    if services_data:
        services_table = Table(services_data, colWidths=[1*cm, 13*cm])
        services_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.white),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(services_table)
    else:
        elements.append(Paragraph("Nessun servizio selezionato", styles['Normal']))
    
    elements.append(Spacer(1, 1*cm))
    
    # Dettaglio costi
    elements.append(Paragraph("Dettaglio Costi", styles['SubTitle']))
    
    costs_data = [
        ["Onorari professionali:", f"€ {fees['professional_fee']:,.2f}"],
        ["Spese forfettarie (15%):", f"€ {fees['expenses']:,.2f}"],
        ["Cassa previdenza avvocati (4%):", f"€ {fees['cpa']:,.2f}"],
        ["IVA (22%):", f"€ {fees['iva']:,.2f}"],
        ["Totale:", f"€ {fees['total']:,.2f}"]
    ]
    
    costs_table = Table(costs_data, colWidths=[9*cm, 5*cm])
    costs_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.white),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('BACKGROUND', (0, 4), (-1, 4), colors.grey),
        ('TEXTCOLOR', (0, 4), (-1, 4), colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (0, 4), (-1, 4), 'Helvetica-Bold'),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ]))
    
    elements.append(costs_table)
    elements.append(Spacer(1, 1*cm))
    
    # Note legali
    elements.append(Paragraph("Note:", styles['SubTitle']))
    elements.append(Paragraph("Preventivo calcolato secondo i parametri del D.M. 55/2014 per le prestazioni professionali legali.", styles['Normal']))
    elements.append(Paragraph("Questo preventivo ha validità di 30 giorni dalla data di emissione.", styles['Normal']))
    elements.append(Paragraph("Per accettazione del preventivo, si prega di contattare lo studio legale ai recapiti indicati.", styles['Normal']))
    
    # Piè di pagina
    elements.append(Spacer(1, 2*cm))
    elements.append(Paragraph("Documento generato automaticamente - Tutti i diritti riservati", styles['Center']))
    
    # Build PDF
    doc.build(elements)
    
    # Get PDF bytes
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes
