    # Dashboard View
    if st.session_state.show_dashboard:
        st.markdown("<h2 style='text-align: center; color: #1E3F66;'>Dashboard Analisi Servizi</h2>", unsafe_allow_html=True)
        
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
        st.markdown("""
        <style>
        .metric-card {
            background-color: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
            margin-bottom: 20px;
        }
        .metric-value {
            font-size: 28px;
            font-weight: bold;
            color: #1E3F66;
        }
        .metric-label {
            font-size: 16px;
            color: #666;
            margin-top: 10px;
        }
        .section-title {
            color: #2D6A4F;
            border-bottom: 2px solid #95D5B2;
            padding-bottom: 10px;
            margin-top: 30px;
            margin-bottom: 20px;
            font-weight: 600;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown("<h3 class='section-title'>Statistiche Generali</h3>", unsafe_allow_html=True)
        
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
            st.markdown("<h3 class='section-title'>Servizi Più Richiesti</h3>", unsafe_allow_html=True)
            
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
                st.markdown("<h3 class='section-title'>Valore Medio per Servizio</h3>", unsafe_allow_html=True)
                
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
                st.markdown("<h3 class='section-title'>Andamento Mensile Preventivi</h3>", unsafe_allow_html=True)
                
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
            st.rerun()