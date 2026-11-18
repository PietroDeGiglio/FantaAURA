import streamlit as st
from database.database import get_user, create_league

def show():
    st.markdown("<h2>Crea la tua prima lega</h2>", unsafe_allow_html=True)
    st.markdown("<p class='muted-text'>Configura la tua stagione e inizia a costruire la tua strategia.</p>", unsafe_allow_html=True)
    st.write("")

    user = get_user()

    with st.container():
        name = st.text_input("Nome lega")
        
        col1, col2 = st.columns(2)
        with col1:
            participants = st.number_input("Numero partecipanti", min_value=2, max_value=20, value=8, step=2)
            fantasy_type = st.selectbox("Tipo di Fantacalcio", ["Classic", "Mantra"])
        with col2:
            budget = st.number_input("Budget iniziale", min_value=1, max_value=5000, value=500, step=100)
            defense_modifier = st.toggle("Modificatore difesa", value=True)
            
        st.markdown("<h4 style='margin-top: 20px;'>Configurazione Rosa</h4>", unsafe_allow_html=True)
        r_col1, r_col2, r_col3, r_col4 = st.columns(4)
        with r_col1:
            gk = st.number_input("Portieri", min_value=1, max_value=5, value=3)
        with r_col2:
            df = st.number_input("Difensori", min_value=1, max_value=15, value=8)
        with r_col3:
            mf = st.number_input("Centrocampisti", min_value=1, max_value=15, value=8)
        with r_col4:
            fw = st.number_input("Attaccanti", min_value=1, max_value=10, value=6)
            
        st.write("")
        if st.button("CREA LEGA", use_container_width=True, key="submit_league"):
            if name.strip() == "":
                st.error("Inserisci un nome per la lega.")
            else:
                league_id = create_league(
                    user['id'], name, participants, budget, fantasy_type, 
                    defense_modifier, gk, df, mf, fw
                )
                st.session_state.current_league_id = league_id
                st.session_state.page = "league"
                st.rerun()