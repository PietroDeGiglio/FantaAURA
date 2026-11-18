import streamlit as st
import os
import base64

def render_sidebar():
    with st.sidebar:
        # ELEMENTO 1: LOGO
        logo_path = os.path.join("assets", "ChatGPT Image 25 ago 2026, 12_30_31.png")
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode()
            st.markdown(f'<div style="text-align:center; padding-top: 10px; margin-bottom: 25px;"><img src="data:image/png;base64,{encoded}" style="max-width: 200px; width: 100%; pointer-events: none;"></div>', unsafe_allow_html=True)
        else:
            st.markdown("<h2 style='text-align: center; margin-bottom: 25px;'><span style='color: white;'>FANTA</span><span style='color: #D4AF37;'>AURA</span></h2>", unsafe_allow_html=True)
            
        menu_items = [
            ("Dashboard", "dashboard", "#FFD700"),       # Oro
            ("Data Center", "data_center", "#39FF14"),   # Verde Neon
            ("Import Data", "data_import", "#39FF14"),   # Verde Neon (NUOVO)
            ("Auction Lab", "coming_soon", "#FFD700"),   # Oro
            ("Live Auction", "coming_soon", "#39FF14"),  # Verde Neon
            ("Player Lab", "player_lab", "#00D9FF"),     # Blu Neon
            ("Squad Builder", "coming_soon", "#A855F7"), # Viola Neon
            ("Fixture Lab", "fixture_lab", "#00D9FF"),   # Blu Neon
            ("GK Lab", "gk_lab", "#A855F7"),             # Viola Neon (NUOVO)
            ("Matchday", "coming_soon", "#FF3B5C"),      # Rosso Neon
            ("News", "coming_soon", "#FF8A00"),          # Arancione
            ("Settings", "coming_soon", "#888888")       # Grigio
        ]
        
        # ELEMENTI 2-13: I BOTTONI
        for label, page_key, color in menu_items:
            is_active = st.session_state.get('page', 'dashboard') == page_key
            # Usiamo sempre bottoni secondari nella sidebar per non farli infettare dall'oro globale
            if st.button(label, key=f"nav_{label.replace(' ', '')}", use_container_width=True):
                st.session_state.page = page_key
                st.rerun()

        # ELEMENTO 14: CSS DI STILE (L'indice parte da 2 per colpire il primo bottone)
        css = "<style>\n"
        for i, (label, page_key, color) in enumerate(menu_items):
            nth = i + 2 
            is_active = st.session_state.get('page', 'dashboard') == page_key
            
            if is_active:
                css += f"""
                [data-testid="stSidebar"] div.element-container:nth-child({nth}) button {{
                    opacity: 1 !important; border-left: 4px solid {color} !important;
                    background: linear-gradient(90deg, {color}26 0%, transparent 100%) !important;
                }}
                [data-testid="stSidebar"] div.element-container:nth-child({nth}) button p {{
                    color: {color} !important; font-weight: 800 !important; text-shadow: 0 0 8px {color}66 !important;
                }}
                """
            else:
                css += f"""
                [data-testid="stSidebar"] div.element-container:nth-child({nth}) button {{
                    opacity: 0.8 !important; transition: all 0.3s ease;
                }}
                [data-testid="stSidebar"] div.element-container:nth-child({nth}) button p {{
                    color: {color} !important; font-weight: 600 !important;
                }}
                [data-testid="stSidebar"] div.element-container:nth-child({nth}) button:hover {{
                    opacity: 1 !important; border-left: 4px solid {color} !important;
                    background: linear-gradient(90deg, {color}1A 0%, transparent 100%) !important;
                }}
                [data-testid="stSidebar"] div.element-container:nth-child({nth}) button:hover p {{
                    font-weight: 800 !important; text-shadow: 0 0 8px {color}66 !important;
                }}
                """
        css += "</style>"
        st.markdown(css, unsafe_allow_html=True)