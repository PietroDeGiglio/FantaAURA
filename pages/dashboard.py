import streamlit as st
from database.database import get_user, get_leagues
from components.empty_states import render_empty_leagues

def show():
    user = get_user()
    if not user: return
    
    raw_css = r"""
    <div class="particle-overlay"></div>
    <style>
    .particle-overlay { 
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; pointer-events: none; z-index: 0; 
        background-image: radial-gradient(1.5px 1.5px at 20px 30px, #FFD700, rgba(0,0,0,0)), 
                          radial-gradient(2px 2px at 40px 70px, rgba(212, 175, 55, 0.8), rgba(0,0,0,0)), 
                          radial-gradient(1px 1px at 90px 40px, #FFD700, rgba(0,0,0,0)), 
                          radial-gradient(2.5px 2.5px at 160px 120px, rgba(212, 175, 55, 0.5), rgba(0,0,0,0)), 
                          radial-gradient(1.5px 1.5px at 240px 180px, #FFD700, rgba(0,0,0,0)), 
                          radial-gradient(2px 2px at 300px 250px, rgba(212, 175, 55, 0.8), rgba(0,0,0,0)); 
        background-repeat: repeat; background-size: 300px 300px, 400px 400px, 500px 500px, 600px 600px, 700px 700px, 800px 800px; 
        animation: rain 35s linear infinite; opacity: 0.4; 
    }
    @keyframes rain { 
        0% { background-position: 0px 0px, 0px 0px, 0px 0px, 0px 0px, 0px 0px, 0px 0px; } 
        100% { background-position: 300px 1000px, 400px 1000px, 500px 1000px, 600px 1000px, 700px 1000px, 800px 1000px; } 
    }
    
    /* DISTRUZIONE DEI CONTRORNI ESTERNI GLOBALI */
    div[data-testid="stButton"] > button { border: 1px solid #1A1A1A !important; outline: none !important; }
    div[data-testid="stButton"] > button:hover { border: 1px solid #1A1A1A !important; }
    
    /* PULSANTI PRIMARI (CREA/APRI LEGA) = VERDE NEON */
    div[data-testid="stButton"] > button[kind="primary"] { 
        background: #0D0D0D !important; border: 1px solid #1A1A1A !important; border-left: 4px solid #39FF14 !important; 
        border-radius: 8px !important; transition: all 0.3s ease !important; color: #39FF14 !important; 
        height: auto !important; padding: 10px 20px !important; display: inline-block !important;
    }
    div[data-testid="stButton"] > button[kind="primary"] p { color: #39FF14 !important; font-weight: 800 !important; }
    div[data-testid="stButton"] > button[kind="primary"]:hover { 
        background: #111 !important; transform: translateY(-2px) !important; box-shadow: 0 0 15px rgba(57,255,20,0.3) !important; 
    }
    
    /* CARD DASHBOARD (TUTTI I BOTTONI NELLE COLONNE SUPERIORI CHE NON SONO PRIMARY) */
    [data-testid="column"] button[kind="secondary"],
    [data-testid="stColumn"] button[kind="secondary"] { 
        background: #0D0D0D !important; border-radius: 12px !important; padding: 20px 24px !important; 
        height: 110px !important; text-align: left !important; display: flex !important; flex-direction: column !important; 
        justify-content: flex-start !important; align-items: flex-start !important; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.5) !important; position: relative !important; transition: all 0.3s ease !important;
        border: 1px solid #1A1A1A !important; width: 100% !important;
    }
    [data-testid="column"] button[kind="secondary"] p,
    [data-testid="stColumn"] button[kind="secondary"] p { font-size: 1.2rem !important; font-weight: 800 !important; margin: 0 !important; }
    
    /* --- COLONNA 1 --- */
    [data-testid="column"]:nth-of-type(1) div.element-container:nth-of-type(1) button, 
    [data-testid="stColumn"]:nth-of-type(1) div.element-container:nth-of-type(1) button { border-left: 4px solid #FFD700 !important; }
    [data-testid="column"]:nth-of-type(1) div.element-container:nth-of-type(1) button p, 
    [data-testid="stColumn"]:nth-of-type(1) div.element-container:nth-of-type(1) button p { color: #FFD700 !important; }
    [data-testid="column"]:nth-of-type(1) div.element-container:nth-of-type(1) button p::after, 
    [data-testid="stColumn"]:nth-of-type(1) div.element-container:nth-of-type(1) button p::after { content: "Preparati all'asta con una strategia."; display: block !important; font-size: 0.85rem !important; color: #9CA3AF !important; font-weight: 500 !important; margin-top: 4px !important; }
    [data-testid="column"]:nth-of-type(1) div.element-container:nth-of-type(1) button:hover, 
    [data-testid="stColumn"]:nth-of-type(1) div.element-container:nth-of-type(1) button:hover { box-shadow: 0 0 15px rgba(255,215,0,0.4) !important; transform: translateY(-4px) !important; background: #151515 !important; }
    
    [data-testid="column"]:nth-of-type(1) div.element-container:nth-of-type(2) button, 
    [data-testid="stColumn"]:nth-of-type(1) div.element-container:nth-of-type(2) button { border-left: 4px solid #A855F7 !important; }
    [data-testid="column"]:nth-of-type(1) div.element-container:nth-of-type(2) button p, 
    [data-testid="stColumn"]:nth-of-type(1) div.element-container:nth-of-type(2) button p { color: #A855F7 !important; }
    [data-testid="column"]:nth-of-type(1) div.element-container:nth-of-type(2) button p::after, 
    [data-testid="stColumn"]:nth-of-type(1) div.element-container:nth-of-type(2) button p::after { content: "Costruisci e analizza la tua rosa."; display: block !important; font-size: 0.85rem !important; color: #9CA3AF !important; font-weight: 500 !important; margin-top: 4px !important; }
    [data-testid="column"]:nth-of-type(1) div.element-container:nth-of-type(2) button:hover, 
    [data-testid="stColumn"]:nth-of-type(1) div.element-container:nth-of-type(2) button:hover { box-shadow: 0 0 15px rgba(168,85,247,0.4) !important; transform: translateY(-4px) !important; background: #151515 !important; }
    
    [data-testid="column"]:nth-of-type(1) div.element-container:nth-of-type(3) button, 
    [data-testid="stColumn"]:nth-of-type(1) div.element-container:nth-of-type(3) button { border-left: 4px solid #FF8A00 !important; }
    [data-testid="column"]:nth-of-type(1) div.element-container:nth-of-type(3) button p, 
    [data-testid="stColumn"]:nth-of-type(1) div.element-container:nth-of-type(3) button p { color: #FF8A00 !important; }
    [data-testid="column"]:nth-of-type(1) div.element-container:nth-of-type(3) button p::after, 
    [data-testid="stColumn"]:nth-of-type(1) div.element-container:nth-of-type(3) button p::after { content: "Infortuni, squalifiche e notizie."; display: block !important; font-size: 0.85rem !important; color: #9CA3AF !important; font-weight: 500 !important; margin-top: 4px !important; }
    [data-testid="column"]:nth-of-type(1) div.element-container:nth-of-type(3) button:hover, 
    [data-testid="stColumn"]:nth-of-type(1) div.element-container:nth-of-type(3) button:hover { box-shadow: 0 0 15px rgba(255,138,0,0.4) !important; transform: translateY(-4px) !important; background: #151515 !important; }
    
    /* --- COLONNA 2 --- */
    [data-testid="column"]:nth-of-type(2) div.element-container:nth-of-type(1) button, 
    [data-testid="stColumn"]:nth-of-type(2) div.element-container:nth-of-type(1) button { border-left: 4px solid #39FF14 !important; }
    [data-testid="column"]:nth-of-type(2) div.element-container:nth-of-type(1) button p, 
    [data-testid="stColumn"]:nth-of-type(2) div.element-container:nth-of-type(1) button p { color: #39FF14 !important; }
    [data-testid="column"]:nth-of-type(2) div.element-container:nth-of-type(1) button p::after, 
    [data-testid="stColumn"]:nth-of-type(2) div.element-container:nth-of-type(1) button p::after { content: "Decisioni giuste, al momento giusto."; display: block !important; font-size: 0.85rem !important; color: #9CA3AF !important; font-weight: 500 !important; margin-top: 4px !important; }
    [data-testid="column"]:nth-of-type(2) div.element-container:nth-of-type(1) button:hover, 
    [data-testid="stColumn"]:nth-of-type(2) div.element-container:nth-of-type(1) button:hover { box-shadow: 0 0 15px rgba(57,255,20,0.4) !important; transform: translateY(-4px) !important; background: #151515 !important; }
    
    [data-testid="column"]:nth-of-type(2) div.element-container:nth-of-type(2) button, 
    [data-testid="stColumn"]:nth-of-type(2) div.element-container:nth-of-type(2) button { border-left: 4px solid #00D9FF !important; }
    [data-testid="column"]:nth-of-type(2) div.element-container:nth-of-type(2) button p, 
    [data-testid="stColumn"]:nth-of-type(2) div.element-container:nth-of-type(2) button p { color: #00D9FF !important; }
    [data-testid="column"]:nth-of-type(2) div.element-container:nth-of-type(2) button p::after, 
    [data-testid="stColumn"]:nth-of-type(2) div.element-container:nth-of-type(2) button p::after { content: "Scopri calendario e AURA Pairs."; display: block !important; font-size: 0.85rem !important; color: #9CA3AF !important; font-weight: 500 !important; margin-top: 4px !important; }
    [data-testid="column"]:nth-of-type(2) div.element-container:nth-of-type(2) button:hover, 
    [data-testid="stColumn"]:nth-of-type(2) div.element-container:nth-of-type(2) button:hover { box-shadow: 0 0 15px rgba(0,217,255,0.4) !important; transform: translateY(-4px) !important; background: #151515 !important; }
    
    [data-testid="column"]:nth-of-type(2) div.element-container:nth-of-type(3) button, 
    [data-testid="stColumn"]:nth-of-type(2) div.element-container:nth-of-type(3) button { border-left: 4px solid #A855F7 !important; }
    [data-testid="column"]:nth-of-type(2) div.element-container:nth-of-type(3) button p, 
    [data-testid="stColumn"]:nth-of-type(2) div.element-container:nth-of-type(3) button p { color: #A855F7 !important; }
    [data-testid="column"]:nth-of-type(2) div.element-container:nth-of-type(3) button p::after, 
    [data-testid="stColumn"]:nth-of-type(2) div.element-container:nth-of-type(3) button p::after { content: "Crea la coppia perfetta per i portieri."; display: block !important; font-size: 0.85rem !important; color: #9CA3AF !important; font-weight: 500 !important; margin-top: 4px !important; }
    [data-testid="column"]:nth-of-type(2) div.element-container:nth-of-type(3) button:hover, 
    [data-testid="stColumn"]:nth-of-type(2) div.element-container:nth-of-type(3) button:hover { box-shadow: 0 0 15px rgba(168,85,247,0.4) !important; transform: translateY(-4px) !important; background: #151515 !important; }
    
    /* --- COLONNA 3 --- */
    [data-testid="column"]:nth-of-type(3) div.element-container:nth-of-type(1) button, 
    [data-testid="stColumn"]:nth-of-type(3) div.element-container:nth-of-type(1) button { border-left: 4px solid #00D9FF !important; }
    [data-testid="column"]:nth-of-type(3) div.element-container:nth-of-type(1) button p, 
    [data-testid="stColumn"]:nth-of-type(3) div.element-container:nth-of-type(1) button p { color: #00D9FF !important; }
    [data-testid="column"]:nth-of-type(3) div.element-container:nth-of-type(1) button p::after, 
    [data-testid="stColumn"]:nth-of-type(3) div.element-container:nth-of-type(1) button p::after { content: "Analizza il vero valore dei giocatori."; display: block !important; font-size: 0.85rem !important; color: #9CA3AF !important; font-weight: 500 !important; margin-top: 4px !important; }
    [data-testid="column"]:nth-of-type(3) div.element-container:nth-of-type(1) button:hover, 
    [data-testid="stColumn"]:nth-of-type(3) div.element-container:nth-of-type(1) button:hover { box-shadow: 0 0 15px rgba(0,217,255,0.4) !important; transform: translateY(-4px) !important; background: #151515 !important; }
    
    [data-testid="column"]:nth-of-type(3) div.element-container:nth-of-type(2) button, 
    [data-testid="stColumn"]:nth-of-type(3) div.element-container:nth-of-type(2) button { border-left: 4px solid #FF3B5C !important; }
    [data-testid="column"]:nth-of-type(3) div.element-container:nth-of-type(2) button p, 
    [data-testid="stColumn"]:nth-of-type(3) div.element-container:nth-of-type(2) button p { color: #FF3B5C !important; }
    [data-testid="column"]:nth-of-type(3) div.element-container:nth-of-type(2) button p::after, 
    [data-testid="stColumn"]:nth-of-type(3) div.element-container:nth-of-type(2) button p::after { content: "Costruisci la formazione migliore."; display: block !important; font-size: 0.85rem !important; color: #9CA3AF !important; font-weight: 500 !important; margin-top: 4px !important; }
    [data-testid="column"]:nth-of-type(3) div.element-container:nth-of-type(2) button:hover, 
    [data-testid="stColumn"]:nth-of-type(3) div.element-container:nth-of-type(2) button:hover { box-shadow: 0 0 15px rgba(255,59,92,0.4) !important; transform: translateY(-4px) !important; background: #151515 !important; }
    </style>
    """
    
    st.markdown(raw_css.replace('\n', ' '), unsafe_allow_html=True)
    
    st.markdown(f"<h2 style='position:relative; z-index:1;'>Benvenuto, <span class='gold-text'>{user['name']}</span>.</h2>", unsafe_allow_html=True)
    st.markdown("<p class='muted-text' style='position:relative; z-index:1;'>La tua stagione. La tua strategia. La tua AURA.</p>", unsafe_allow_html=True)
    st.write("")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Auction Lab", use_container_width=True): st.session_state.page = "coming_soon"; st.rerun()
        if st.button("Squad Builder", use_container_width=True): st.session_state.page = "coming_soon"; st.rerun()
        if st.button("News", use_container_width=True): st.session_state.page = "coming_soon"; st.rerun()
    with col2:
        if st.button("Live Auction", use_container_width=True): st.session_state.page = "coming_soon"; st.rerun()
        if st.button("Fixture Lab", use_container_width=True): st.session_state.page = "fixture_lab"; st.rerun()
        if st.button("GK Lab", use_container_width=True): st.session_state.page = "gk_lab"; st.rerun()
    with col3:
        if st.button("Player Lab", use_container_width=True): st.session_state.page = "player_lab"; st.rerun()
        if st.button("Matchday", use_container_width=True): st.session_state.page = "coming_soon"; st.rerun()

    st.markdown("<hr style='position:relative; z-index:1;'>", unsafe_allow_html=True)
    
    col_l1, col_l2 = st.columns([3, 1])
    with col_l1:
        st.markdown("<h3 style='position:relative; z-index:1;'>Le tue leghe</h3>", unsafe_allow_html=True)
    with col_l2:
        if st.button("+ CREA LEGA", type="primary", use_container_width=True):
            st.session_state.page = "create_league"
            st.rerun()

    leagues = get_leagues(user['id'])
    
    if not leagues:
        render_empty_leagues()
        st.write("")
        col_c1, col_c2, col_c3 = st.columns([1,2,1])
        with col_c2:
            if st.button("+ CREA LA TUA PRIMA LEGA", type="primary", use_container_width=True, key="empty_create"):
                st.session_state.page = "create_league"
                st.rerun()
    else:
        for league in leagues:
            l_col1, l_col2 = st.columns([4, 1])
            with l_col1:
                st.markdown(f'''
                <div style="background-color: #0D0D0D; padding: 15px 20px; border-radius: 8px; border: 1px solid #1A1A1A; margin-bottom: 10px; position: relative; z-index: 1;">
                    <h4 style="margin:0; color: #FFD700;">{league['name']}</h4>
                    <p style="margin:5px 0 0 0; font-size:0.9rem; color:#888;">
                        {league['participants']} partecipanti • {league['budget']} FM • {league['fantasy_type']}
                    </p>
                </div>
                ''', unsafe_allow_html=True)
            with l_col2:
                st.write("")
                if st.button("Apri lega →", type="primary", key=f"apri_{league['id']}", use_container_width=True):
                    st.session_state.current_league_id = league['id']
                    st.session_state.page = "league"
                    st.rerun()