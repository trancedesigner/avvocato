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
st.title("Preventivatore Servizi Legali")

# Admin toggle buttons in sidebar
st.sidebar.button("Modalità Amministratore", on_click=toggle_admin_view)
if st.session_state.admin_view:
    st.sidebar.button("Visualizza Preventivi Recenti", on_click=toggle_recent_quotes)
    st.sidebar.button("Dashboard Analisi Servizi", on_click=toggle_dashboard)

# Admin interface
if st.session_state.admin_view:
    st.header("Pannello Amministratore")
    
    # Dashboard View
