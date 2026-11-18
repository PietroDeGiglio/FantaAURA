import streamlit as st
from aura_engine import get_exact_affinities
from components.player_row import get_team_logo_b64, get_top_player_for_role

def show():
    st.markdown("<h2>GK LAB (Incroci FantaLab) <span class='gold-text'>✦</span></h2>", unsafe_allow_html=True)
    st.markdown("<p class='muted-text'>Seleziona il tuo portiere principale. AURA calcolerà istantaneamente le migliori alternative per creare una coppia a prova di malus.</p>", unsafe_allow_html=True)

    affinities = get_exact_affinities()

    teams = sorted(list(affinities.keys()))
    if not teams:
        st.warning("⚠️ Impossibile generare la matrice.")
        return

    st.write("")
    
    # Selezioni solo la tua squadra
    team_base = st.selectbox("Seleziona la tua Squadra / Portiere Principale:", teams, index=teams.index("Milan") if "Milan" in teams else 0)
    gk_base = get_top_player_for_role(team_base, 'P')
    logo_base = get_team_logo_b64(team_base)
    img_base = f"<img src='{logo_base}' style='width: 50px; height: 50px;'>" if logo_base else ""

    st.markdown("<hr style='border: 1px solid #1A1A1A; margin: 25px 0;'>", unsafe_allow_html=True)

    # Elenca tutti gli incroci per questa squadra
    squadre_affini = affinities.get(team_base, [])
    
    if not squadre_affini:
        st.info(f"Nessun incrocio ottimale raccomandato per i portieri del {team_base}.")
        return

    st.markdown(f"### I Migliori Abbinamenti per <span style='color:#FFD700;'>{gk_base} ({team_base})</span>", unsafe_allow_html=True)
    st.write("")

    for idx, match in enumerate(squadre_affini):
        team_rivale = match['team']
        score = match['score']
        
        gk_rivale = get_top_player_for_role(team_rivale, 'P')
        logo_rivale = get_team_logo_b64(team_rivale)
        img_rivale = f"<img src='{logo_rivale}' style='width: 40px; height: 40px;'>" if logo_rivale else ""
        
        # Effetto visivo in base al punteggio
        if score >= 94: color = "#39FF14"; text = "SCELTA ELITE"
        elif score >= 91: color = "#00D9FF"; text = "OTTIMA SCELTA"
        elif score >= 88: color = "#FFD700"; text = "BUONA ALTERNATIVA"
        else: color = "#FFA500"; text = "RISCHIOSA"

        # HTML COMPATTATO SU UNA SINGOLA RIGA PER EVITARE IL BUG DI STREAMLIT
        card_html = f"""<div style="background-color: #0D0D0D; padding: 15px 25px; border-radius: 12px; border: 1px solid #1A1A1A; border-left: 4px solid {color}; margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 4px 15px rgba(0,0,0,0.3); transition: transform 0.2s;"><div style="display: flex; align-items: center; width: 45%;"><div style="font-size: 1.5rem; font-weight: 900; color: #444; margin-right: 20px; width: 30px;">#{idx + 1}</div>{img_rivale}<div style="margin-left: 15px;"><div style="font-weight: 800; font-size: 1.1rem; color: #fff; text-transform: uppercase;">{team_rivale}</div><div style="color: #888; font-size: 0.85rem;">{gk_rivale}</div></div></div><div style="width: 30%; text-align: center;"><span style="font-size: 0.75rem; letter-spacing: 1px; color: {color}; background: rgba(255,255,255,0.05); padding: 4px 8px; border-radius: 4px; border: 1px solid {color}40;">{text}</span></div><div style="width: 25%; text-align: right;"><div style="font-size: 0.8rem; color: #666; margin-bottom: 2px;">Indice Affinità</div><div style="font-size: 1.5rem; font-weight: 900; color: {color};">{score}%</div></div></div>"""
        
        st.markdown(card_html, unsafe_allow_html=True)
        
    st.write("")
    st.info("💡 **AURA Strategia:** Gli indici tengono conto delle difficoltà reali calcolate da FantaLab. Punta sempre ai portieri titolari delle squadre con affinità superiore al 91%.")