import streamlit as st
import pandas as pd
import json
import os
import base64
import re
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
from calendar import month_name, month_abbr
import matplotlib.ticker as ticker
from matplotlib.colors import LinearSegmentedColormap
from utils.fee_calculator import calculate_fees
from utils.pdf_generator import generate_pdf
from utils.email_sender import send_email_with_pdf
import database

st.set_page_config(
    page_title="Preventivatore Servizi Legali",
    page_icon="⚖️",
    layout="wide"
)

# Carica lo stile CSS personalizzato
with open('.streamlit/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize database
database.initialize_database()

# Initialize session state
if 'services' not in st.session_state:
    # First, try to load from database
    st.session_state.services = database.load_services_from_db()
    
    # If database is empty and JSON exists, import from JSON
    if not st.session_state.services and os.path.exists('data/services.json'):
        with open('data/services.json', 'r') as f:
            json_services = json.load(f)
            if json_services:
                database.import_json_services(json_services)
                st.session_state.services = database.load_services_from_db()

if 'admin_view' not in st.session_state:
    st.session_state.admin_view = False

if 'show_recent_quotes' not in st.session_state:
    st.session_state.show_recent_quotes = False
    
if 'show_dashboard' not in st.session_state:
    st.session_state.show_dashboard = False

def toggle_admin_view():
    st.session_state.admin_view = not st.session_state.admin_view

def toggle_recent_quotes():
    st.session_state.show_recent_quotes = not st.session_state.show_recent_quotes
    if st.session_state.show_recent_quotes:
        st.session_state.show_dashboard = False

def toggle_dashboard():
    st.session_state.show_dashboard = not st.session_state.show_dashboard
    if st.session_state.show_dashboard:
        st.session_state.show_recent_quotes = False

def add_service(name, description, file_content=None):
    service_id = database.save_service_to_db(name, description, file_content)
    # Refresh services list
    st.session_state.services = database.load_services_from_db()

def delete_service(service_id):
    database.delete_service_from_db(service_id)
    # Refresh services list
    st.session_state.services = database.load_services_from_db()

def get_pdf_download_link(pdf_bytes, filename):
    """Generate a link to download the PDF file"""
    b64 = base64.b64encode(pdf_bytes).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}">Scarica Preventivo PDF</a>'
    return href

# Main application
# Display the banner image
st.image("images/legal_banner.svg", use_container_width=True)

# Admin toggle buttons in sidebar
st.sidebar.button("Modalità Amministratore", on_click=toggle_admin_view)
if st.session_state.admin_view:
    st.sidebar.button("Visualizza Preventivi Recenti", on_click=toggle_recent_quotes)
    st.sidebar.button("Dashboard Analisi Servizi", on_click=toggle_dashboard)

# Admin interface
if st.session_state.admin_view:
    st.header("Pannello Amministratore")
    
    # Dashboard View
    if st.session_state.show_dashboard:
        st.markdown("<h2 style='text-align: center; color: #1E3F66;'>Dashboard Analisi Servizi</h2>", unsafe_allow_html=True)
        
        # Display chart icon
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image("images/chart_icon.svg", width=150, use_container_width=False)
        
        # Get statistics
        stats = database.get_service_statistics()
        
        # Setup style for the plots
        plt.rcParams.update({
            'font.family': 'serif',
            'font.size': 12,
            'axes.titlesize': 16,
            'axes.labelsize': 14,
            'xtick.labelsize': 12,
            'ytick.labelsize': 12,
            'axes.spines.top': False,
            'axes.spines.right': False,
            'axes.grid': True,
            'grid.alpha': 0.3
        })
        
        # Create a branded color scheme
        legal_blue = ['#1E3F66', '#2E5984', '#3E73A2', '#4E8DC0', '#5EA7DE']
        legal_green = ['#2D6A4F', '#40916C', '#52B788', '#74C69D', '#95D5B2']
        legal_accent = ['#D62828', '#F77F00', '#FCBF49', '#EAE2B7']
        
        # Display summary statistics in cards with custom styling
        # CSS di stile è già caricato dal file esterno
        
        st.markdown("<h3 class='section-title'>📊 Statistiche Generali</h3>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{stats['total_stats']['total_quotes']}</div>
                <div class="metric-label">Totale Preventivi</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            avg_value = stats['total_stats']['avg_value'] or 0
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">€ {avg_value:,.2f}</div>
                <div class="metric-label">Valore Medio Beni</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col3:
            avg_fee = stats['total_stats']['avg_fee'] or 0
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">€ {avg_fee:,.2f}</div>
                <div class="metric-label">Compenso Medio</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Display service popularity chart
        if stats['service_counts']:
            st.markdown("<h3 class='section-title'>🏆 Servizi Più Richiesti</h3>", unsafe_allow_html=True)
            
            # Prepare data for chart
            service_df = pd.DataFrame(stats['service_counts'])
            
            # Filter non-zero counts and sort
            service_df = service_df[service_df['count'] > 0].sort_values('count', ascending=False)
            
            if not service_df.empty:
                # Limit to top 10 services for better visualization
                if len(service_df) > 10:
                    service_df = service_df.head(10)
                
                fig, ax = plt.subplots(figsize=(10, 6), facecolor='white')
                
                # Create color map
                cmap = LinearSegmentedColormap.from_list("LegalBlue", legal_blue)
                
                # Create horizontal bars with custom color
                bars = sns.barplot(
                    x='count', 
                    y='name', 
                    data=service_df, 
                    palette=sns.color_palette(legal_blue[:len(service_df)]), 
                    hue='name',
                    dodge=False,
                    ax=ax
                )
                
                # Remove the legend
                if ax.get_legend():
                    ax.get_legend().remove()
                
                # Add count labels to bars with enhanced styling
                for i, v in enumerate(service_df['count']):
                    ax.text(
                        v + 0.3, 
                        i, 
                        f"{v:,d}", 
                        va='center', 
                        fontweight='bold',
                        color='#1E3F66'
                    )
                
                # Enhance styling
                ax.set_title('Numero di Richieste per Servizio', fontweight='bold', pad=20)
                ax.set_xlabel('Numero di Richieste', labelpad=10)
                ax.set_ylabel('')
                
                # Format x-axis to show integers only
                ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
                
                # Add subtle grid lines for readability
                ax.grid(axis='x', linestyle='--', alpha=0.3)
                
                # Tight layout for better spacing
                fig.tight_layout()
                
                # Display in Streamlit with improved styling
                st.pyplot(fig)
            else:
                st.info("Nessun servizio è stato ancora richiesto.")
            
            # Display average values by service
            if stats['service_values']:
                st.markdown("<h3 class='section-title'>💰 Valore Medio per Servizio</h3>", unsafe_allow_html=True)
                
                # Display money icon for the section
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    st.image("images/money_icon.svg", width=100, use_container_width=False)
                
                # Prepare data
                values_df = pd.DataFrame(stats['service_values'])
                
                if not values_df.empty:
                    # Limit to top services if there are many
                    if len(values_df) > 8:
                        values_df = values_df.head(8)
                        
                    # Create two columns layout
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Chart for average asset value
                        fig1, ax1 = plt.subplots(figsize=(8, 6), facecolor='white')
                        
                        # Create blue color palette for values
                        bars = sns.barplot(
                            x='avg_value', 
                            y='name', 
                            data=values_df,
                            palette=sns.color_palette(legal_blue[:len(values_df)]),
                            hue='name', 
                            dodge=False,
                            ax=ax1
                        )
                        
                        # Remove legend
                        if ax1.get_legend():
                            ax1.get_legend().remove()
                        
                        # Add value labels
                        for i, v in enumerate(values_df['avg_value']):
                            ax1.text(
                                v + (v * 0.02),  # Position relative to value 
                                i, 
                                f"€ {v:,.0f}", 
                                va='center',
                                fontweight='bold',
                                color='#1E3F66'
                            )
                        
                        ax1.set_title('Valore Medio del Bene per Servizio', fontweight='bold', pad=20)
                        ax1.set_xlabel('Valore Medio (€)', labelpad=10)
                        ax1.set_ylabel('')
                        
                        # Format x-axis labels
                        ax1.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"€{x:,.0f}"))
                        
                        # Add subtle grid
                        ax1.grid(axis='x', linestyle='--', alpha=0.3)
                        
                        fig1.tight_layout()
                        st.pyplot(fig1)
                    
                    with col2:
                        # Chart for average fee
                        fig2, ax2 = plt.subplots(figsize=(8, 6), facecolor='white')
                        
                        # Create green color palette for fees
                        bars = sns.barplot(
                            x='avg_fee', 
                            y='name', 
                            data=values_df,
                            palette=sns.color_palette(legal_green[:len(values_df)]),
                            hue='name',
                            dodge=False,
                            ax=ax2
                        )
                        
                        # Remove legend
                        if ax2.get_legend():
                            ax2.get_legend().remove()
                        
                        # Add value labels
                        for i, v in enumerate(values_df['avg_fee']):
                            ax2.text(
                                v + (v * 0.02),  # Position relative to value
                                i, 
                                f"€ {v:,.0f}", 
                                va='center',
                                fontweight='bold',
                                color='#2D6A4F'
                            )
                        
                        ax2.set_title('Compenso Medio per Servizio', fontweight='bold', pad=20)
                        ax2.set_xlabel('Compenso Medio (€)', labelpad=10)
                        ax2.set_ylabel('')
                        
                        # Format x-axis labels
                        ax2.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"€{x:,.0f}"))
                        
                        # Add subtle grid
                        ax2.grid(axis='x', linestyle='--', alpha=0.3)
                        
                        fig2.tight_layout()
                        st.pyplot(fig2)
            
            # Display monthly trends
            if stats['monthly_counts']:
                st.markdown("<h3 class='section-title'>📈 Andamento Mensile Preventivi</h3>", unsafe_allow_html=True)
                
                # Prepare data
                monthly_df = pd.DataFrame(stats['monthly_counts'])
                
                if not monthly_df.empty:
                    # Convert month numbers to abbreviated month names
                    monthly_df['month_name'] = monthly_df.apply(
                        lambda x: f"{month_abbr[x['month']]} {x['year']}", axis=1
                    )
                    
                    fig, ax = plt.subplots(figsize=(12, 6), facecolor='white')
                    
                    # Create accent color for trend line
                    accent_color = legal_accent[2]  # Using a warm yellow-orange color
                    
                    # Plot line chart with enhanced styling
                    sns.lineplot(
                        x='month_name', 
                        y='count', 
                        data=monthly_df, 
                        marker='o', 
                        linewidth=3, 
                        markersize=10, 
                        color=accent_color,
                        ax=ax
                    )
                    
                    # Add point labels
                    for i, row in monthly_df.iterrows():
                        ax.text(
                            i, 
                            row['count'] + 0.3, 
                            str(int(row['count'])), 
                            ha='center',
                            fontweight='bold',
                            color=legal_accent[1]
                        )
                    
                    # Enhanced styling
                    ax.set_title('Andamento Mensile dei Preventivi', fontweight='bold', pad=20)
                    ax.set_xlabel('')
                    ax.set_ylabel('Numero di Preventivi', labelpad=10)
                    
                    # Force y-axis to start at 0 and use integer ticks
                    ax.set_ylim(bottom=0)
                    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
                    
                    # Add subtle grid
                    ax.grid(axis='y', linestyle='--', alpha=0.3)
                    
                    # Rotate x-axis labels for readability
                    plt.xticks(rotation=45, ha='right')
                    
                    # Fill area under the line
                    ax.fill_between(
                        range(len(monthly_df)), 
                        monthly_df['count'], 
                        alpha=0.2, 
                        color=accent_color
                    )
                    
                    # Adjust layout
                    fig.tight_layout()
                    
                    st.pyplot(fig)
        else:
            st.info("Non ci sono ancora dati sufficienti per generare analisi.")
        
        if st.button("Torna al pannello amministratore", key="back_from_dashboard"):
            st.session_state.show_dashboard = False
            st.rerun()    # Recent Quotes View
    elif st.session_state.show_recent_quotes:
        st.subheader("Preventivi Recenti")
        recent_quotes = database.get_recent_quotes(20)  # Get last 20 quotes
        
        if recent_quotes:
            for quote in recent_quotes:
                with st.expander(f"{quote['nome']} {quote['cognome']} - €{quote['total_fee']:,.2f} - {quote['created_at'].strftime('%d/%m/%Y')}"):
                    st.write(f"**Cliente:** {quote['nome']} {quote['cognome']}")
                    st.write(f"**Email:** {quote['email']}")
                    st.write(f"**Data preventivo:** {quote['created_at'].strftime('%d/%m/%Y %H:%M')}")
                    st.write(f"**Valore del bene:** €{quote['valore_bene']:,.2f}")
                    st.write(f"**Totale preventivo:** €{quote['total_fee']:,.2f}")
                    
                    st.write("**Servizi richiesti:**")
                    for service in quote['services']:
                        st.write(f"- {service}")
        else:
            st.info("Nessun preventivo recente disponibile.")
            
        if st.button("Torna al pannello amministratore", key="back_from_quotes"):
            st.session_state.show_recent_quotes = False
            st.rerun()
    else:
        # Services Management
        with st.expander("Aggiungi Nuovo Servizio", expanded=True):
            service_name = st.text_input("Nome del Servizio")
            service_description = st.text_area("Descrizione del Servizio")
            service_file = st.file_uploader("Carica documento informativo (opzionale)", type=["pdf", "doc", "docx", "txt"])
            
            if st.button("Aggiungi Servizio"):
                file_content = None
                if service_file is not None:
                    file_content = base64.b64encode(service_file.getvalue()).decode()
                
                if service_name and service_description:
                    add_service(service_name, service_description, file_content)
                    st.success(f"Servizio '{service_name}' aggiunto con successo!")
                else:
                    st.error("Nome e descrizione del servizio sono obbligatori.")
        
        st.header("Servizi Esistenti")
        if st.session_state.services:
            for service in st.session_state.services:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.subheader(service["name"])
                    st.write(service["description"])
                with col2:
                    if st.button("Elimina", key=f"delete_{service['id']}"):
                        delete_service(service['id'])
                        st.rerun()
        else:
            st.info("Nessun servizio disponibile. Aggiungi un nuovo servizio utilizzando il modulo sopra.")

# Client interface
else:
    st.header("Richiedi un Preventivo per Servizi Legali")
    
    # Display the service image
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("images/legal_service.svg", width=300, use_container_width=False)
    
    with st.form("client_form"):
        st.subheader("Dati personali")
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome *")
            cognome = st.text_input("Cognome *")
            email = st.text_input("Email *")
        
        with col2:
            telefono = st.text_input("Telefono")
            codice_fiscale = st.text_input("Codice Fiscale *")
            indirizzo = st.text_input("Indirizzo")
        
        st.subheader("Informazioni sulla pratica legale")
        valore_bene = st.number_input("Valore del bene in € *", min_value=0.0, format="%.2f")
        
        st.subheader("Servizi richiesti")
        if st.session_state.services:
            servizi_selezionati = {}
            for service in st.session_state.services:
                servizi_selezionati[service["id"]] = st.checkbox(f"{service['name']}", key=f"service_{service['id']}")
        else:
            st.info("Nessun servizio disponibile. Contattare l'amministratore.")
            servizi_selezionati = {}
        
        st.markdown("_* Campi obbligatori_")
        
        submit_button = st.form_submit_button("Calcola Preventivo")
    
    if submit_button:
        # Check if required fields are filled
        required_fields = [nome, cognome, email, codice_fiscale, valore_bene]
        if not all(required_fields):
            st.error("Per favore, completa tutti i campi obbligatori.")
        elif not any(servizi_selezionati.values()):
            st.error("Seleziona almeno un servizio.")
        else:
            # Get selected services
            selected_services = [s for s in st.session_state.services if servizi_selezionati.get(s["id"], False)]
            
            # Calculate fees based on asset value
            fees = calculate_fees(valore_bene, len(selected_services))
            
            # Display the fee calculation
            st.success("Preventivo calcolato con successo!")
            
            st.subheader("Riepilogo del preventivo")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Cliente:**", f"{nome} {cognome}")
                st.write("**Email:**", email)
                st.write("**Telefono:**", telefono if telefono else "Non specificato")
            
            with col2:
                st.write("**Codice Fiscale:**", codice_fiscale)
                st.write("**Valore del bene:**", f"€ {valore_bene:,.2f}")
                st.write("**Data preventivo:**", datetime.now().strftime("%d/%m/%Y"))
            
            st.markdown("---")
            st.subheader("Servizi richiesti:")
            
            for service in selected_services:
                st.write(f"- {service['name']}")
            
            st.markdown("---")
            st.subheader("Costi:")
            
            st.write("**Onorari professionali:**", f"€ {fees['professional_fee']:,.2f}")
            st.write("**Spese forfettarie (15%):**", f"€ {fees['expenses']:,.2f}")
            if 'cpa' in fees:
                st.write("**Cassa previdenza avvocati (4%):**", f"€ {fees['cpa']:,.2f}")
            if 'iva' in fees:
                st.write("**IVA (22%):**", f"€ {fees['iva']:,.2f}")
            st.markdown(f"### **Totale:** € {fees['total']:,.2f}")
            
            # Generate PDF
            client_data = {
                'nome': nome,
                'cognome': cognome,
                'email': email,
                'telefono': telefono,
                'codice_fiscale': codice_fiscale,
                'indirizzo': indirizzo,
                'valore_bene': valore_bene
            }
            
            # Save quote to database
            database.save_quote_to_db(client_data, selected_services, fees)
            
            pdf_bytes = generate_pdf(client_data, selected_services, fees)
            
            # Provide download link
            st.markdown(get_pdf_download_link(pdf_bytes, f"Preventivo_{cognome}_{nome}_{datetime.now().strftime('%Y%m%d')}.pdf"), unsafe_allow_html=True)
            
            # Email validation
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, email):
                st.warning("L'indirizzo email inserito non sembra valido. La funzione di invio email è disabilitata.")
            else:
                # Add button to send PDF via email
                if st.button("Invia il preventivo via email"):
                    with st.spinner("Invio dell'email in corso..."):
                        success, message = send_email_with_pdf(email, f"{nome} {cognome}", pdf_bytes)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
