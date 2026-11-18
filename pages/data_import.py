import streamlit as st
import pandas as pd
import sqlite3
import os
import uuid
from engine.matching import get_player_match, normalize_name

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'fantaaura.db')

def clean_play_style(style_str):
    if not isinstance(style_str, str) or style_str.lower() == "nan" or not style_str:
        return None
        
    junk_keywords = [
        'italia', 'paesi bassi', 'francia', 'spagna', 'inghilterra', 'germania', 'brasile', 'argentina', 'portogallo',
        'belgio', 'svizzera', 'croazia', 'polonia', 'serbia', 'uruguay', 'colombia', 'nigeria', 'senegal',
        'serie a', 'world cup', 'uefa', 'friendly', 'fa cup', 'liga', 'ligue 1', 'premier league',
        'champions league', 'europa league', 'copa america', 'eredivisie', 'bundesliga', 'coppa', 'qualification'
    ]
    
    valid_traits = []
    parts = [p.strip() for p in style_str.split('|')]
    for part in parts:
        p_lower = part.lower()
        if len(part) <= 4: continue
        if any(junk in p_lower for junk in junk_keywords): continue
        valid_traits.append(part)
        
    return " | ".join(valid_traits) if valid_traits else None

def show():
    st.markdown("<h2>HISTORICAL DATA IMPORT <span class='gold-text'>✦</span></h2>", unsafe_allow_html=True)
    st.markdown("<p class='muted-text'>Sistema di acquisizione dati storici e correnti.</p>", unsafe_allow_html=True)
    st.write("")

    with st.container():
        st.markdown('''
        <div style="background-color: #0D0D0D; padding: 20px; border-radius: 8px; border: 1px solid #1A1A1A;">
            <h4 style="margin-top:0; color: #FFD700;">Configurazione Dataset</h4>
        </div>
        ''', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            season = st.selectbox("Stagione", ["2026/27", "2025/26", "2024/25", "2023/24", "2022/23"])
        with col2:
            source = st.selectbox("Sorgente Dati", ["manual_csv", "fantacalcio_export"])
        with col3:
            dataset_type = st.selectbox("Tipo", ["Statistiche Stagionali", "Caratteristiche Tattiche (Listone Definitivo)"])

    st.write("")
    uploaded_file = st.file_uploader("Carica il file dataset (.csv, .xlsx)", type=["csv", "xlsx"])

    if uploaded_file is not None:
        st.markdown("<hr style='border-color: #1A1A1A;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: #FFD700;'>Anteprima e Importazione</h3>", unsafe_allow_html=True)

        try:
            header_idx = 0 if "Caratteristiche" in dataset_type else 1
            
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file, header=header_idx) 
            else:
                df = pd.read_excel(uploaded_file, header=header_idx)
            
            st.dataframe(df.head(5), use_container_width=True)
            st.write(f"**Trovate {len(df)} righe.** Premi il pulsante per avviare il matching e salvare i dati.")
            
            if st.button("ESEGUI IMPORTAZIONE", type="primary", use_container_width=True):
                with st.spinner("Importazione nel database in corso..."):
                    conn = sqlite3.connect(DB_PATH)
                    cursor = conn.cursor()
                    
                    matched_count = 0
                    new_historical_count = 0
                    
                    for index, row in df.iterrows():
                        ext_id = str(row.get('Id', ''))
                        raw_name = str(row.get('Nome', ''))
                        team = str(row.get('Squadra', ''))
                        
                        # 🌟 ESTRAZIONE DEL RUOLO PER IL TIE-BREAKER
                        if "Caratteristiche" in dataset_type:
                            role = str(row.get('Ruolo standard', row.get('Ruolo Fantacalcio.it', '')))
                        else:
                            role = str(row.get('R', ''))
                        
                        # 🌟 PASSAGGIO DEL RUOLO AL MOTORE DI MATCHING
                        status, p_id, conf = get_player_match(DB_PATH, ext_id if ext_id != "nan" else None, source, raw_name, team, season, role)
                        
                        if status == 'NEEDS_REVIEW' or not p_id:
                            p_id = f"FA_HIST_{str(uuid.uuid4().hex)[:6].upper()}"
                            cursor.execute("INSERT INTO players (player_id, display_name, normalized_name) VALUES (?, ?, ?)", 
                                           (p_id, raw_name, normalize_name(raw_name)))
                            new_historical_count += 1
                        else:
                            matched_count += 1

                        if "Caratteristiche" in dataset_type:
                            raw_style = str(row.get('Stile di gioco', ''))
                            clean_style = clean_play_style(raw_style)

                            cursor.execute("""
                                INSERT INTO player_characteristics 
                                (player_id, tactical_position, detailed_roles, strengths, weaknesses, play_style)
                                VALUES (?, ?, ?, ?, ?, ?)
                                ON CONFLICT(player_id) DO UPDATE SET
                                tactical_position=excluded.tactical_position, detailed_roles=excluded.detailed_roles,
                                strengths=excluded.strengths, weaknesses=excluded.weaknesses, play_style=excluded.play_style
                            """, (
                                p_id,
                                str(row.get('Posizione', '')) if pd.notna(row.get('Posizione')) else None,
                                str(row.get('Ruoli', '')) if pd.notna(row.get('Ruoli')) else None,
                                str(row.get('Punti di forza', '')) if pd.notna(row.get('Punti di forza')) else None,
                                str(row.get('Debolezze', '')) if pd.notna(row.get('Debolezze')) else None,
                                clean_style
                            ))
                        else:
                            is_gk = str(row.get('R', '')) == 'P'
                            goals = int(row.get('Gf', 0) if pd.notna(row.get('Gf')) else 0) if not is_gk else 0
                            assists = int(row.get('Ass', 0) if pd.notna(row.get('Ass')) else 0)
                            
                            cursor.execute("""
                                INSERT INTO player_season_stats 
                                (player_id, season, appearances, goals, assists, yellow_cards, red_cards, mv, fm, data_quality)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'complete')
                                ON CONFLICT(player_id, season) DO UPDATE SET
                                appearances=excluded.appearances, goals=excluded.goals, assists=excluded.assists,
                                yellow_cards=excluded.yellow_cards, red_cards=excluded.red_cards,
                                mv=excluded.mv, fm=excluded.fm, data_quality='complete'
                            """, (
                                p_id, season, 
                                int(row.get('Pv', 0) if pd.notna(row.get('Pv')) else 0), goals, assists,
                                int(row.get('Amm', 0) if pd.notna(row.get('Amm')) else 0), int(row.get('Esp', 0) if pd.notna(row.get('Esp')) else 0),
                                float(row.get('Mv', 0.0) if pd.notna(row.get('Mv')) else 0.0), float(row.get('Fm', 0.0) if pd.notna(row.get('Fm')) else 0.0)
                            ))
                        
                        if ext_id and ext_id != "nan":
                            cursor.execute("INSERT OR IGNORE INTO player_external_ids (player_id, source, external_id) VALUES (?, ?, ?)", 
                                           (p_id, source, ext_id))
                    
                    conn.commit()
                    conn.close()
                    
                st.success(f"✅ Importazione perfetta: {matched_count} giocatori matchati grazie al Ruolo!")
                st.balloons()

        except Exception as e:
            st.error(f"Errore durante la lettura del file: {e}")
            st.cache_data.clear()