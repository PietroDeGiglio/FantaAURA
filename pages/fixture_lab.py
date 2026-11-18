import streamlit as st
import pandas as pd
import os
import base64
from aura_engine import get_team_difficulties

TEAM_COLORS = {
    "Atalanta": "linear-gradient(135deg, #000000 50%, #1a5bb8 50%)", "Bologna": "linear-gradient(135deg, #002b5c 50%, #ba0f14 50%)",
    "Cagliari": "linear-gradient(135deg, #002350 50%, #b32a2a 50%)", "Como": "linear-gradient(135deg, #00509a 50%, #ffffff 50%)",
    "Empoli": "linear-gradient(135deg, #00509a 100%, #00509a 100%)", "Fiorentina": "linear-gradient(135deg, #482e92 100%, #482e92 100%)",
    "Frosinone": "linear-gradient(135deg, #ffd100 50%, #00509a 50%)", "Genoa": "linear-gradient(135deg, #ba0f14 50%, #002b5c 50%)",
    "Inter": "linear-gradient(135deg, #000000 50%, #005ca8 50%)", "Juventus": "linear-gradient(135deg, #ffffff 50%, #000000 50%)",
    "Lazio": "linear-gradient(135deg, #87d8f7 50%, #ffffff 50%)", "Lecce": "linear-gradient(135deg, #ffcc00 50%, #d10000 50%)",
    "Milan": "linear-gradient(135deg, #fb090b 50%, #000000 50%)", "Monza": "linear-gradient(135deg, #e3001b 50%, #ffffff 50%)",
    "Napoli": "linear-gradient(135deg, #00a0e0 100%, #00a0e0 100%)", "Parma": "linear-gradient(135deg, #ffd100 50%, #002d72 50%)",
    "Roma": "linear-gradient(135deg, #8e1f2f 50%, #f0b516 50%)", "Sassuolo": "linear-gradient(135deg, #000000 50%, #007a4d 50%)",
    "Torino": "linear-gradient(135deg, #8a1e32 100%, #8a1e32 100%)", "Udinese": "linear-gradient(135deg, #000000 50%, #ffffff 50%)",
    "Venezia": "linear-gradient(135deg, #ff6b00 33%, #000000 33%, #000000 66%, #007a4d 66%)", "Verona": "linear-gradient(135deg, #002d72 50%, #ffd100 50%)"
}

@st.cache_data
def load_calendar():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, "Calendario_Serie_A_2026-27.csv")
    if not os.path.exists(file_path): file_path = "Calendario_Serie_A_2026-27.csv"
    if not os.path.exists(file_path): return None
    return pd.read_csv(file_path)

@st.cache_data
def get_team_logo(team_name):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logo_path = os.path.join(base_dir, "loghi", f"{team_name}.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        return f"data:image/png;base64,{encoded}"
    return None

def show():
    st.markdown("<h2>FIXTURE LAB <span class='gold-text'>✦</span></h2>", unsafe_allow_html=True)
    st.markdown("<p class='muted-text'>Esplora il calendario della Serie A per pianificare la tua strategia sui portieri e sui blocchi difensivi.</p>", unsafe_allow_html=True)
    
    df_cal = load_calendar()
    if df_cal is None:
        st.warning("⚠️ Calendario non trovato nella cartella del progetto.")
        return

    cal_dict = get_team_difficulties()

    if 'fixture_giornata' not in st.session_state: st.session_state.fixture_giornata = 1

    st.write("")
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        if st.button("⬅️ Precedente", use_container_width=True, disabled=(st.session_state.fixture_giornata == 1)):
            st.session_state.fixture_giornata -= 1; st.rerun()
    with c2:
        giornate_list = list(range(1, 39))
        new_g = st.selectbox("Vai alla giornata", giornate_list, index=st.session_state.fixture_giornata - 1, label_visibility="collapsed")
        if new_g != st.session_state.fixture_giornata:
            st.session_state.fixture_giornata = new_g; st.rerun()
    with c3:
        if st.button("Successiva ➡️", use_container_width=True, disabled=(st.session_state.fixture_giornata == 38)):
            st.session_state.fixture_giornata += 1; st.rerun()
            
    st.markdown(f"<h3 style='text-align:center; color:#FFD700; margin-top: 15px;'>Giornata {st.session_state.fixture_giornata}</h3>", unsafe_allow_html=True)
    st.markdown("<hr style='border: 1px solid #1A1A1A; margin-bottom: 25px;'>", unsafe_allow_html=True)
    
    partite = df_cal[df_cal['Giornata'] == f"Giornata {st.session_state.fixture_giornata}"]
    col1, col2 = st.columns(2)
    
    for idx, row in enumerate(partite.itertuples()):
        casa, trasferta = str(row.Casa).strip(), str(row.Trasferta).strip()
        
        diff_casa = cal_dict.get(casa, {}).get(st.session_state.fixture_giornata, "🟠")
        diff_trasf = cal_dict.get(trasferta, {}).get(st.session_state.fixture_giornata, "🟠")
        
        logo_casa_b64 = get_team_logo(casa)
        icon_casa = f"<img src='{logo_casa_b64}' style='width: 32px; height: 32px; object-fit: contain;'>" if logo_casa_b64 else ""
        
        logo_trasferta_b64 = get_team_logo(trasferta)
        icon_trasferta = f"<img src='{logo_trasferta_b64}' style='width: 32px; height: 32px; object-fit: contain;'>" if logo_trasferta_b64 else ""

        card_html = f"""<div style="background-color: #0D0D0D; border: 1px solid #1A1A1A; border-radius: 12px; padding: 15px; margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center;"><div style="width: 42%; display: flex; align-items: center; justify-content: flex-end;"><span style="font-size: 0.9rem; margin-right: 8px;">{diff_casa}</span><span style="color: #FFFFFF; font-weight: 900; font-size: 1.15rem; margin-right: 12px; text-transform: uppercase;">{casa}</span>{icon_casa}</div><div style="width: 16%; text-align: center;"><span style="color: #666; font-size: 0.8rem; font-weight: 900; background: #111; padding: 4px 8px; border-radius: 6px; border: 1px solid #222;">VS</span></div><div style="width: 42%; display: flex; align-items: center; justify-content: flex-start;">{icon_trasferta}<span style="color: #FFFFFF; font-weight: 900; font-size: 1.15rem; margin-left: 12px; text-transform: uppercase;">{trasferta}</span><span style="font-size: 0.9rem; margin-left: 8px;">{diff_trasf}</span></div></div>"""
        
        if idx % 2 == 0:
            with col1: st.markdown(card_html, unsafe_allow_html=True)
        else:
            with col2: st.markdown(card_html, unsafe_allow_html=True)