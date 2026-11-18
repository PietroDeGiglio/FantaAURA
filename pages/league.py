import streamlit as st
from database.database import get_league_by_id
from components.empty_states import render_empty_roster

def show():
    league_id = st.session_state.get('current_league_id')
    if not league_id:
        st.session_state.page = "dashboard"
        st.rerun()
        return

    league = get_league_by_id(league_id)
    if not league:
        st.error("Lega non trovata.")
        return

    # Header Lega
    st.markdown(f"<h2>{league['name']}</h2>", unsafe_allow_html=True)
    
    # Dati Lega
    st.markdown(f"""
        <div style="display: flex; gap: 20px; margin-bottom: 30px; border-bottom: 1px solid #1A1A1A; padding-bottom: 15px;">
            <div><span style="color: #888; font-size: 0.85rem;">Format</span><br><b>{league['fantasy_type']}</b></div>
            <div><span style="color: #888; font-size: 0.85rem;">Partecipanti</span><br><b>{league['participants']}</b></div>
            <div><span style="color: #888; font-size: 0.85rem;">Budget</span><br><b>{league['budget']} FM</b></div>
            <div><span style="color: #888; font-size: 0.85rem;">Modificatore</span><br><b>{'Sì' if league['defense_modifier'] else 'No'}</b></div>
            <div><span style="color: #888; font-size: 0.85rem;">Rosa</span><br><b>{league['goalkeeper_slots']}-{league['defender_slots']}-{league['midfielder_slots']}-{league['forward_slots']}</b></div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<h3>La tua squadra</h3>", unsafe_allow_html=True)
    render_empty_roster()