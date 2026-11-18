import streamlit as st

def apply_theme():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
            
            :root {
                --bg-dark: #050505;
                --gold: #D4AF37;
                --gold-glow: rgba(212, 175, 55, 0.4);
                --text-main: #FFFFFF;
                --text-muted: #888888;
                --role-p: #FF8A00;
                --role-d: #39FF14;
                --role-c: #00D9FF;
                --role-a: #FF3B5C;
            }

            html, body, [class*="css"] {
                font-family: 'Plus Jakarta Sans', sans-serif !important;
                background-color: var(--bg-dark) !important;
                color: var(--text-main) !important;
            }

            /* CLEANUP DEFAULT */
            header[data-testid="stHeader"], [data-testid="stToolbar"], #MainMenu, footer, .stDeployButton { display: none !important; }
            div[data-testid="stSidebarNav"], section[data-testid="stSidebarNav"] { display: none !important; visibility: hidden !important; height: 0 !important; }
            
            .gold-text { color: var(--gold) !important; text-shadow: 0 0 15px var(--gold-glow); }
            
            /* SIDEBAR BASE */
            [data-testid="stSidebar"] {
                background: #050505 !important;
                border-right: 1px solid #111 !important;
            }
            [data-testid="stSidebar"] button {
                background: transparent !important; border: none !important;
                padding: 10px 15px !important; text-align: left !important; justify-content: flex-start !important; box-shadow: none !important;
            }

            /* INPUTS */
            .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>div {
                background-color: #0A0A0A !important; color: white !important; border: 1px solid #222 !important; border-radius: 8px;
            }

            /* BOTTONI GLOBALI (CREA LEGA, APRI LEGA, ECC.) - ORO */
            .main div[data-testid="stButton"] > button {
                background: transparent !important; 
                color: var(--gold) !important; 
                border: 1px solid var(--gold) !important; 
                font-weight: 800 !important; 
                border-radius: 8px !important;
                transition: all 0.3s ease !important;
            }
            .main div[data-testid="stButton"] > button p {
                color: var(--gold) !important;
                font-weight: 800 !important;
            }
            .main div[data-testid="stButton"] > button:hover {
                background: rgba(212, 175, 55, 0.1) !important; 
                transform: translateY(-2px) !important;
                box-shadow: 0 4px 15px rgba(212, 175, 55, 0.3) !important;
            }

            /* COLORI SICURI PER I FILTRI DEL DATA CENTER E PLAYER LAB */
            span[data-baseweb="tag"] { background-color: #111 !important; border: 1px solid #333 !important; border-radius: 6px !important; }
            span[title="Portiere"] { color: var(--role-p) !important; font-weight: 800 !important; }
            span[title="Difensore"] { color: var(--role-d) !important; font-weight: 800 !important; }
            span[title="Centrocampista"] { color: var(--role-c) !important; font-weight: 800 !important; }
            span[title="Attaccante"] { color: var(--role-a) !important; font-weight: 800 !important; }

            /* ROLE BADGES NELLA CARD DEL LISTONE */
            .badge-p { background-color: rgba(255,138,0,0.15); color: var(--role-p); padding: 4px 10px; border-radius: 6px; font-weight: 800; border: 1px solid rgba(255,138,0,0.3); }
            .badge-d { background-color: rgba(57,255,20,0.15); color: var(--role-d); padding: 4px 10px; border-radius: 6px; font-weight: 800; border: 1px solid rgba(57,255,20,0.3); }
            .badge-c { background-color: rgba(0,217,255,0.15); color: var(--role-c); padding: 4px 10px; border-radius: 6px; font-weight: 800; border: 1px solid rgba(0,217,255,0.3); }
            .badge-a { background-color: rgba(255,59,92,0.15); color: var(--role-a); padding: 4px 10px; border-radius: 6px; font-weight: 800; border: 1px solid rgba(255,59,92,0.3); }

            /* PLAYER ROW UI AURA NEL LISTONE */
            .player-row {
                display: flex; align-items: center; justify-content: space-between;
                background: linear-gradient(145deg, #111111 0%, #080808 100%);
                border: 1px solid #1A1A1A; border-radius: 12px;
                padding: 10px 20px; margin-bottom: 8px; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }
            
            .accent-p { border-left: 5px solid var(--role-p); }
            .accent-p:hover { border-color: var(--role-p); box-shadow: 0 4px 20px rgba(255, 138, 0, 0.25); transform: translateY(-2px); }
            .accent-d { border-left: 5px solid var(--role-d); }
            .accent-d:hover { border-color: var(--role-d); box-shadow: 0 4px 20px rgba(57, 255, 20, 0.25); transform: translateY(-2px); }
            .accent-c { border-left: 5px solid var(--role-c); }
            .accent-c:hover { border-color: var(--role-c); box-shadow: 0 4px 20px rgba(0, 217, 255, 0.25); transform: translateY(-2px); }
            .accent-a { border-left: 5px solid var(--role-a); }
            .accent-a:hover { border-color: var(--role-a); box-shadow: 0 4px 20px rgba(255, 59, 92, 0.25); transform: translateY(-2px); }

            .pr-left { display: flex; align-items: center; gap: 15px; width: 40%; }
            .pr-photo { width: 42px; height: 42px; background: linear-gradient(135deg, #222, #111); border-radius: 50%; display:flex; align-items:center; justify-content:center; color:#888; font-weight:bold; border: 1px solid #333; }
            .pr-info { display: flex; flex-direction: column; justify-content: center; }
            .pr-name { font-weight: 800; font-size: 1.05rem; margin: 0 0 2px 0; color: #FFF; letter-spacing: -0.5px; }
            .pr-team { font-size: 0.75rem; color: #9CA3AF; margin: 0; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; }
            
            .pr-role { width: 10%; text-align: left; }
            .pr-stats { display: flex; justify-content: flex-end; gap: 25px; width: 40%; padding-right: 15px;}
            .pr-stat-box { display: flex; flex-direction: column; align-items: flex-end; justify-content: center;}
            
            .highlight-box { background: rgba(212, 175, 55, 0.05); padding: 5px 15px; border-radius: 8px; border: 1px solid rgba(212, 175, 55, 0.2); }
            .pr-stat-val { font-weight: 800; font-size: 1.15rem; color: #FFF; line-height: 1; }
            .pr-stat-lbl { font-size: 0.65rem; color: #666; text-transform: uppercase; font-weight: 600; margin-top: 4px; }
            .pr-fvm-pers { color: var(--gold); text-shadow: 0 0 10px rgba(212, 175, 55, 0.3); }
    
        </style>
    """, unsafe_allow_html=True)