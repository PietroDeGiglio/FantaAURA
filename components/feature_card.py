import streamlit as st

def render_feature_card(title, description, accent_color, page_key):
    button_key = f"btn_{title.replace(' ', '')}"
    
    # Iniezione CSS avanzata: Trasformiamo il bottone nativo di Streamlit in una bellissima Card
    css = f"""
    <style>
        div[data-testid="stButton"]:has(p:contains("{title}")) button {{
            background: rgba(15, 15, 15, 0.7) !important;
            backdrop-filter: blur(10px) !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
            border-left: 4px solid {accent_color} !important;
            border-radius: 14px !important;
            padding: 24px !important;
            height: 120px !important;
            text-align: left !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: flex-start !important;
            align-items: flex-start !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }}
        div[data-testid="stButton"]:has(p:contains("{title}")) button:hover {{
            background: rgba(25, 25, 25, 0.95) !important;
            border-color: {accent_color} !important;
            transform: translateY(-4px) !important;
            box-shadow: 0 10px 30px rgba(0,0,0,0.8), 0 0 20px {accent_color}40 !important;
        }}
        div[data-testid="stButton"]:has(p:contains("{title}")) p {{
            font-size: 1.15rem !important;
            font-weight: 700 !important;
            color: #FFF !important;
            margin: 0 0 8px 0 !important;
        }}
        /* Iniettiamo la descrizione sotto il titolo usando CSS */
        div[data-testid="stButton"]:has(p:contains("{title}")) p::after {{
            content: "\\A {description}";
            white-space: pre;
            font-size: 0.85rem !important;
            color: #9CA3AF !important;
            font-weight: 400 !important;
            line-height: 1.4 !important;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    
    # Renderizziamo il bottone pulito (il CSS farà tutto il resto)
    if st.button(title, key=button_key, use_container_width=True):
        st.session_state.page = page_key
        st.rerun()