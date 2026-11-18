import streamlit as st
import os
import base64
from database.database import init_db, get_user, create_user
from styles.theme import apply_theme
from components.sidebar import render_sidebar
# Aggiunta gk_lab agli import
from pages import dashboard, create_league, league, data_center, player_lab, coming_soon, data_import, fixture_lab, gk_lab

st.set_page_config(page_title="FantaAURA", page_icon="⚽", layout="wide", initial_sidebar_state="expanded")

init_db()
apply_theme()

if 'page' not in st.session_state:
    st.session_state.page = 'dashboard'

user = get_user()

if not user:
    st.markdown('<style>[data-testid="stSidebar"] {display: none !important;}</style>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.write("")
        st.write("")
        
        logo_main = os.path.join("assets", "ChatGPT Image 25 ago 2026, 12_30_41.png")
        if os.path.exists(logo_main):
            with open(logo_main, "rb") as f:
                encoded = base64.b64encode(f.read()).decode()
            st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{encoded}" style="max-width: 320px; width: 100%; pointer-events: none; filter: drop-shadow(0 0 25px rgba(255,215,0,0.2));"></div>', unsafe_allow_html=True)
        else:
            st.markdown("<h1 style='text-align: center; color: #FFD700;'>FANTAAURA</h1>", unsafe_allow_html=True)
            
        st.markdown("<h2 style='text-align: center; font-weight: 300; margin-top: 15px;'>Benvenuto in FantaAURA.</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #888; margin-bottom: 40px;'>Come ti chiami, allenatore?</p>", unsafe_allow_html=True)
        
        name_input = st.text_input("Il tuo nome", label_visibility="collapsed", placeholder="Inserisci il tuo nome...")
        
        st.write("")
        if st.button("INIZIA", use_container_width=True):
            if name_input.strip() != "":
                create_user(name_input.strip())
                st.rerun()
            else:
                st.error("L'AURA richiede un nome. Inseriscilo per continuare.")
else:
    render_sidebar()
    if st.session_state.page == 'dashboard':
        dashboard.show()
    elif st.session_state.page == 'data_center':
        data_center.show()
    elif st.session_state.page == 'player_lab':
        player_lab.show()
    elif st.session_state.page == 'create_league':
        create_league.show()
    elif st.session_state.page == 'league':
        league.show()
    elif st.session_state.page == 'coming_soon':
        coming_soon.show()
    elif st.session_state.page == 'data_import':
        data_import.show()
    elif st.session_state.page == 'fixture_lab':
        fixture_lab.show()
    elif st.session_state.page == 'gk_lab':
        gk_lab.show()