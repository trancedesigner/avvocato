    # Recent Quotes View
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
